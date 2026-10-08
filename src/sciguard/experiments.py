"""One implementation shared by the canonical notebook and command-line runs."""
from dataclasses import dataclass,asdict
from pathlib import Path
import hashlib,json,platform,time,sys
from datetime import datetime,timezone
import importlib.metadata
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier,ExtraTreesClassifier
from sklearn.model_selection import train_test_split
from .core import certify
from .baselines import ltt_holm_certify,atc_threshold,atc_predicted_risk
from .metrics import region_metrics,wilson_interval,reference_intervals,reference_region_metrics
from .continuous import continuous_upper_envelope
from .simulation import correlated_bernoulli,draw_base,outcome_probability,environment_outputs
from .design import hoeffding_sample_size,select_pilot_grid

METHODS=["pointwise","normal_bonferroni","multiplier","exact_bonferroni","hoeffding","holm"]
LABELS={"pointwise":"Pointwise normal","normal_bonferroni":"Bonferroni normal",
        "multiplier":"Multiplier","exact_bonferroni":"Bonferroni exact",
        "hoeffding":"Hoeffding","holm":"Exact Holm"}


@dataclass(frozen=True)
class RunConfig:
    profile:str="full"
    seed:int=20260927
    alpha:float=.05
    tau_calibration:float=.34
    tau_nested:float=.35
    calibration_reps:int=500
    sensitivity_reps:int=300
    continuous_reps:int=200
    nested_reps:int=200
    missingness_reps:int=100
    n_train:int=1200
    n_cal:int=400
    n_assure:int=1000
    n_reference:int=20000
    bootstrap_draws:int=2000
    wdbc_draws:int=5000
    reference_delta:float=.01
    hgb_iterations:int=60

    @classmethod
    def smoke(cls):
        return cls(profile="smoke",calibration_reps=8,sensitivity_reps=5,continuous_reps=5,
                   nested_reps=3,missingness_reps=3,n_train=300,n_cal=150,n_assure=250,
                   n_reference=500,bootstrap_draws=200,wdbc_draws=300,hgb_iterations=20)


def seeded(cfg,*parts):
    return int(np.random.SeedSequence([cfg.seed,*map(int,parts)]).generate_state(1)[0])


class AnalysisRun:
    def __init__(self,root,config):
        self.root=Path(root).resolve(); self.cfg=config
        self.out=self.root/"results"/config.profile
        self.fig=self.root/"figures"/config.profile
        self.out.mkdir(parents=True,exist_ok=True); self.fig.mkdir(parents=True,exist_ok=True)
        self.manifest={"schema":1,"status":"running","config":asdict(config),
                       "started_utc":datetime.now(timezone.utc).isoformat(),
                       "python":platform.python_version(),"platform":platform.platform(),
                       "packages":{},"sections":{},"external_benchmark":"not_run"}
        for package in ["numpy","pandas","scipy","scikit-learn","matplotlib","threadpoolctl"]:
            self.manifest["packages"][package]=importlib.metadata.version(package)
        self.manifest["input_sha256"]={}
        for path in sorted((self.root/"data").glob("*.csv")):
            self.manifest["input_sha256"][str(path.relative_to(self.root))]=hashlib.sha256(path.read_bytes()).hexdigest()
        self.flush()

    def flush(self):
        (self.out/"run_manifest.json").write_text(json.dumps(self.manifest,indent=2,allow_nan=False))

    def save(self,name,frame):
        frame.to_csv(self.out/(name+".csv"),index=False)
        return frame

    def section(self,name,fn):
        start=time.perf_counter(); print(f"Running {name} ({self.cfg.profile})",flush=True)
        try:
            result=fn(self)
            self.manifest["sections"][name]={"status":"completed","seconds":time.perf_counter()-start}
        except Exception as exc:
            self.manifest["sections"][name]={"status":"failed","error":str(exc)}
            self.manifest["status"]="failed"; self.flush(); raise
        self.flush(); print(f"Completed {name}: {time.perf_counter()-start:.1f}s",flush=True)
        return result

    def finish(self):
        self.manifest["status"]="completed_public_and_synthetic"
        self.manifest["ended_utc"]=datetime.now(timezone.utc).isoformat()
        self.manifest["output_sha256"]={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(self.out.glob("*.csv"))}
        self.manifest["source_sha256"]={str(p.relative_to(self.root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((self.root/"src").rglob("*.py"))}
        self.flush()


def summarize(frame,groups,metrics):
    rows=[]
    for key,d in frame.groupby(groups,sort=False,dropna=False):
        key=key if isinstance(key,tuple) else (key,)
        row=dict(zip(groups,key)); row["replications"]=len(d)
        for metric in metrics:
            v=d[metric].to_numpy(float); v=v[np.isfinite(v)]
            row[metric]=float(v.mean()) if len(v) else np.nan
            row[metric+"_mcse"]=float(v.std(ddof=1)/np.sqrt(len(v))) if len(v)>1 else np.nan
            if len(v) and set(np.unique(v))<={0.,1.} and ("containment" in metric or "coverage" in metric):
                _,lo,hi=wilson_interval(v); row[metric+"_lo"]=lo; row[metric+"_hi"]=hi
        rows.append(row)
    return pd.DataFrame(rows)


def _decisions(losses,cfg,seed,methods=METHODS,tau=None):
    tau=cfg.tau_calibration if tau is None else tau
    out={}
    for method in methods:
        start=time.perf_counter()
        if method=="holm":
            cert,_=ltt_holm_certify(losses.sum(axis=0),len(losses),tau,cfg.alpha)
            out[method]=(cert,None,time.perf_counter()-start)
        else:
            result=certify(losses,tau,alpha=cfg.alpha,method=method,n_boot=cfg.bootstrap_draws,rng=seed)
            out[method]=(result.certified,result.upper,time.perf_counter()-start)
    return out


def calibration(run):
    cfg=run.cfg; truth=pd.read_csv(run.root/"data/simulation_true_risks.csv")
    probs=truth.Risk.to_numpy(); rows=[]
    for r in range(cfg.calibration_reps):
        x=correlated_bernoulli(cfg.n_assure,probs,.55,seeded(cfg,10,r))
        for method,(c,u,seconds) in _decisions(x,cfg,seeded(cfg,11,r)).items():
            mm=region_metrics(c,probs<=cfg.tau_calibration)
            mm.update(rep=r,method=method,simultaneous_coverage=float(np.all(probs<=u)) if u is not None else np.nan,inference_seconds=seconds)
            rows.append(mm)
    rep=run.save("calibration_replications",pd.DataFrame(rows))
    summary=run.save("calibration_summary",summarize(rep,["method"],["simultaneous_coverage","containment","ARR","UCP","n_certified","inference_seconds"]))
    return rep,summary


def sensitivity(run):
    cfg=run.cfg; p=pd.read_csv(run.root/"data/simulation_true_risks.csv").Risk.to_numpy()
    settings=[(500,.55),(1000,.55),(5000,.55),(1000,.1),(1000,.9)]
    rows=[]
    for j,(n,rho) in enumerate(settings):
        for r in range(cfg.sensitivity_reps):
            x=correlated_bernoulli(n,p,rho,seeded(cfg,20,j,r))
            for method,(c,u,seconds) in _decisions(x,cfg,seeded(cfg,21,j,r)).items():
                mm=region_metrics(c,p<=cfg.tau_calibration)
                mm.update(n=n,rho=rho,rep=r,method=method,inference_seconds=seconds,
                          simultaneous_coverage=float(np.all(p<=u)) if u is not None else np.nan)
                rows.append(mm)
    rep=run.save("sensitivity_replications",pd.DataFrame(rows))
    summary=run.save("sensitivity_summary",summarize(rep,["n","rho","method"],["simultaneous_coverage","containment","ARR","UCP","inference_seconds"]))
    pivot=rep.pivot(index=["n","rho","rep"],columns="method",values="ARR")
    gains=[]
    for baseline in ["normal_bonferroni","exact_bonferroni","holm"]:
        delta=(pivot["multiplier"]-pivot[baseline]).rename("ARR_gain").reset_index(); delta["baseline"]=baseline; gains.append(delta)
    gains=pd.concat(gains,ignore_index=True)
    run.save("paired_efficiency_gains",summarize(gains,["n","rho","baseline"],["ARR_gain"]))
    return rep,summary


def bootstrap_and_stress(run):
    cfg=run.cfg; rows=[]; repeats=5 if cfg.profile=="smoke" else 25
    p=pd.read_csv(run.root/"data/simulation_true_risks.csv").Risk.to_numpy()
    for n,k in [(500,25),(1000,25),(1000,125)]:
        risks=np.resize(p,k); x=correlated_bernoulli(n,risks,.55,seeded(cfg,30,n,k))
        for b in [200,1000,5000]:
            for r in range(repeats):
                start=time.perf_counter(); result=certify(x,cfg.tau_calibration,n_boot=b,rng=seeded(cfg,31,r),method="multiplier")
                rows.append(dict(n=n,K=k,B=b,rep=r,critical=result.critical_value,n_certified=int(result.certified.sum()),seconds=time.perf_counter()-start))
    boot=run.save("bootstrap_runtime_replications",pd.DataFrame(rows))
    run.save("bootstrap_runtime_summary",summarize(boot,["n","K","B"],["critical","n_certified","seconds"]))
    # Bounded continuous and rare-event losses test regimes unlike the main surface.
    rows=[]; reps=10 if cfg.profile=="smoke" else 200
    for j,scenario in enumerate(["bounded_continuous","rare_binary","high_dimensional_binary"]):
        n,k=(1000,125) if j==2 else (500,25)
        probs=np.linspace(.002,.08,k) if j==1 else np.resize(p,k)
        tau=.035 if j==1 else cfg.tau_calibration
        for r in range(reps):
            rng=np.random.default_rng(seeded(cfg,32,j,r))
            if j==0:
                # Beta marginals: non-Gaussian bounded losses with known means.
                x=rng.beta(probs*4,(1-probs)*4,size=(n,k))
                methods=["pointwise","normal_bonferroni","multiplier","hoeffding"]
            else:
                x=correlated_bernoulli(n,probs,.55,rng); methods=METHODS
            for method,(c,u,seconds) in _decisions(x,cfg,seeded(cfg,33,j,r),methods,tau).items():
                mm=region_metrics(c,probs<=tau); mm.update(rep=r,scenario=scenario,n=n,K=k,method=method,simultaneous_coverage=float(np.all(probs<=u)) if u is not None else np.nan)
                rows.append(mm)
    stress=run.save("stress_replications",pd.DataFrame(rows))
    run.save("stress_summary",summarize(stress,["scenario","method"],["simultaneous_coverage","containment","ARR","UCP"]))
    return boot,stress


def models(cfg,seed):
    return {"Logistic regression":make_pipeline(StandardScaler(),LogisticRegression(max_iter=3000)),
            "HistGradientBoosting":HistGradientBoostingClassifier(max_iter=cfg.hgb_iterations,max_leaf_nodes=15,learning_rate=.08,random_state=seed)}


def nested(run):
    cfg=run.cfg; envs=[(m,s) for m in [0,.1,.2,.3] for s in [0,.15,.3,.45]]
    rows=[]; atc_rows=[]; reference_rows=[]; fit_rows=[]
    for r in range(cfg.nested_reps):
        xt,ut,_,_=draw_base(cfg.n_train,seeded(cfg,40,r)); yt=(ut<outcome_probability(xt)).astype(int)
        xc,uc,_,_=draw_base(cfg.n_cal,seeded(cfg,41,r)); yc=(uc<outcome_probability(xc)).astype(int)
        assurance=draw_base(cfg.n_assure,seeded(cfg,42,r)); reference=draw_base(cfg.n_reference,seeded(cfg,43,r)); imp=xt.mean(axis=0)
        for name,model in models(cfg,seeded(cfg,44,r)).items():
            t=time.perf_counter(); model.fit(xt,yt); fit_seconds=time.perf_counter()-t
            threshold=atc_threshold(model.predict_proba(xc).max(axis=1),model.predict(xc)==yc)
            la,scores,rate=environment_outputs(model,assurance,envs,imp,scores=True)
            lt,_,_=environment_outputs(model,reference,envs,imp)
            risk=lt.mean(axis=0)
            # Delta/2 allocates reference error across the two models per refit.
            lo,hi=reference_intervals(lt,cfg.reference_delta/2)
            for k,(m,s) in enumerate(envs): reference_rows.append(dict(rep=r,Model=name,Missingness=m,Shift=s,reference_risk=risk[k],lower=lo[k],upper=hi[k],n_reference=cfg.n_reference,realized_missingness=rate[k]))
            for method,(cert,upper,seconds) in _decisions(la,cfg,seeded(cfg,45,r),METHODS[1:],cfg.tau_nested).items():
                mm=reference_region_metrics(cert,risk,lo,hi,cfg.tau_nested)
                mm.update(rep=r,Model=name,method=method,inference_seconds=seconds)
                rows.append(mm)
            predicted=atc_predicted_risk(scores,threshold)
            atc_rows.append(dict(rep=r,Model=name,MAE=float(np.mean(np.abs(predicted-risk))),bias=float(np.mean(predicted-risk)),RMSE=float(np.sqrt(np.mean((predicted-risk)**2))),source_threshold=threshold))
            fit_rows.append(dict(rep=r,Model=name,fit_seconds=fit_seconds,nominal_reference_risk=risk[0],reference_safe_fraction=float(np.mean(risk<=cfg.tau_nested))))
        if (r+1)%25==0: print(f"  nested refits {r+1}/{cfg.nested_reps}",flush=True)
    rep=run.save("nested_replications",pd.DataFrame(rows))
    summary=run.save("nested_summary",summarize(rep,["Model","method"],["reference_containment","containment_lower","containment_upper","reference_ARR","reference_UCP","reference_n_certified","ambiguous_environments","reference_halfwidth_max","inference_seconds"]))
    atc=run.save("atc_prediction_replications",pd.DataFrame(atc_rows))
    run.save("atc_prediction_summary",summarize(atc,["Model"],["MAE","bias","RMSE"]))
    run.save("nested_reference_risks",pd.DataFrame(reference_rows))
    fits=run.save("nested_fit_replications",pd.DataFrame(fit_rows))
    run.save("nested_fit_summary",summarize(fits,["Model"],["fit_seconds","nominal_reference_risk","reference_safe_fraction"]))
    return rep,summary


def missingness(run):
    cfg=run.cfg; envs=[(m,s) for m in [0,.1,.2,.3] for s in [0,.15,.3,.45]]
    rows=[]; details=[]
    for r in range(cfg.missingness_reps):
        xt,ut,_,_=draw_base(cfg.n_train,seeded(cfg,50,r)); yt=(ut<outcome_probability(xt)).astype(int)
        model=models(cfg,seeded(cfg,51,r))["Logistic regression"].fit(xt,yt)
        assurance=draw_base(cfg.n_assure,seeded(cfg,52,r)); reference=draw_base(cfg.n_reference,seeded(cfg,53,r))
        for mechanism in ["MCAR","MAR","MNAR","Structured"]:
            la,_,rate=environment_outputs(model,assurance,envs,xt.mean(axis=0),mechanism)
            lt,_,_=environment_outputs(model,reference,envs,xt.mean(axis=0),mechanism)
            risk=lt.mean(axis=0); lo,hi=reference_intervals(lt,cfg.reference_delta/4)
            for k,(m,s) in enumerate(envs): details.append(dict(rep=r,Mechanism=mechanism,Missingness=m,Shift=s,realized_missingness=rate[k],reference_risk=risk[k],lower=lo[k],upper=hi[k]))
            for method,(cert,u,seconds) in _decisions(la,cfg,seeded(cfg,54,r),["multiplier","exact_bonferroni","holm"],cfg.tau_nested).items():
                mm=reference_region_metrics(cert,risk,lo,hi,cfg.tau_nested)
                mm.update(rep=r,Mechanism=mechanism,method=method,mean_reference_risk=float(risk.mean()))
                rows.append(mm)
    rep=run.save("missingness_replications",pd.DataFrame(rows))
    summary=run.save("missingness_summary",summarize(rep,["Mechanism","method"],["reference_containment","containment_lower","containment_upper","reference_ARR","reference_UCP","ambiguous_environments","mean_reference_risk"]))
    run.save("missingness_environment_detail",pd.DataFrame(details))
    return rep,summary


def wdbc(run):
    cfg=run.cfg; d=pd.read_csv(run.root/"data/wdbc_sklearn.csv")
    x=d.drop(columns="target").to_numpy(float); y=d.target.to_numpy(int)
    xt,xa,yt,ya=train_test_split(x,y,test_size=.35,stratify=y,random_state=42)
    mu=xt.mean(axis=0); sd=xt.std(axis=0); rng=np.random.default_rng(cfg.seed)
    noise=rng.normal(size=xa.shape); unif=rng.random(xa.shape)
    fitted={"Logistic regression":make_pipeline(StandardScaler(),LogisticRegression(max_iter=3000)),
            "Extra Trees":ExtraTreesClassifier(n_estimators=500 if cfg.profile=="full" else 50,max_features="sqrt",random_state=42,n_jobs=1),
            "HistGradientBoosting":HistGradientBoostingClassifier(max_iter=cfg.hgb_iterations,max_leaf_nodes=15,random_state=42)}
    rows=[]; grids=[]
    for name,model in fitted.items():
        model.fit(xt,yt)
        specs=[("primary",[0,.05,.1,.2,.3,.4],[0,.1,.2,.3,.4,.5])]
        if name=="Logistic regression": specs += [(f"{q}x{q}",np.linspace(0,.4,q),np.linspace(0,.5,q)) for q in [4,6,10]]
        for design,ms,ss in specs:
            envs=[(m,s) for m in ms for s in ss]; losses=[]
            for m,s in envs:
                xi=np.where(unif<m,mu[None,:],xa+s*sd[None,:]*noise)
                losses.append((model.predict(xi)!=ya).astype(float))
            losses=np.column_stack(losses)
            # Each model/design is a separate assurance family. Model selection
            # from these separate tables has no across-model coverage guarantee.
            for method in ["multiplier","normal_bonferroni","exact_bonferroni","holm"]:
                start=time.perf_counter()
                if method=="holm":
                    cert08,_=ltt_holm_certify(losses.sum(axis=0),len(ya),.08,cfg.alpha)
                    cert10,_=ltt_holm_certify(losses.sum(axis=0),len(ya),.10,cfg.alpha)
                    risk=losses.mean(axis=0); upper=np.full(len(envs),np.nan); crit=np.nan
                else:
                    result=certify(losses,.08,method=method,alpha=cfg.alpha,n_boot=cfg.wdbc_draws,rng=seeded(cfg,60))
                    risk=result.risks; upper=result.upper; crit=result.critical_value
                    cert08=upper<=.08; cert10=upper<=.10
                grids.append(dict(Model=name,design=design,method=method,K=len(envs),n=len(ya),nominal_risk=risk[0],critical=crit,certified_008=int(cert08.sum()),certified_010=int(cert10.sum()),certified_fraction=float(cert08.mean()),inference_seconds=time.perf_counter()-start))
                for k,(m,s) in enumerate(envs): rows.append(dict(Model=name,design=design,method=method,Missingness=m,Shift=s,risk=risk[k],upper=upper[k],certified_008=cert08[k],certified_010=cert10[k]))
    detail=run.save("wdbc_detail",pd.DataFrame(rows)); summary=run.save("wdbc_summary",pd.DataFrame(grids))
    return detail,summary


def continuous(run):
    cfg=run.cfg
    grid=np.array([(m,s) for m in np.linspace(0,.4,5) for s in np.linspace(0,.6,5)])
    query=np.array([(m,s) for m in np.linspace(0,.4,81) for s in np.linspace(0,.6,81)])
    risk=lambda g:.24+.12*g[:,0]+.10*g[:,1]+.05*g[:,0]*g[:,1]
    pg,pq=risk(grid),risk(query); tau=.32; lr=np.hypot(.15,.12); rows=[]
    for r in range(cfg.continuous_reps):
        x=correlated_bernoulli(cfg.n_assure,pg,.55,seeded(cfg,70,r))
        for method in ["multiplier","exact_bonferroni","hoeffding"]:
            res=certify(x,tau,method=method,n_boot=cfg.bootstrap_draws,rng=seeded(cfg,71,r))
            u=continuous_upper_envelope(grid,res.upper,query,lr); cert=u<=tau
            mm=region_metrics(cert,pq<=tau); mm.update(rep=r,method=method,grid_coverage=float(np.all(pg<=res.upper)),dense_mesh_coverage=float(np.all(pq<=u)))
            rows.append(mm)
            if r==0 and method=="multiplier":
                run.save("continuous_example",pd.DataFrame(dict(Missingness=query[:,0],Shift=query[:,1],risk=pq,upper=u,certified=cert)))
                for factor in [.5,1.,2.]:
                    out=continuous_upper_envelope(grid,res.upper,query,lr*factor)
                    run.save(f"continuous_L_factor_{factor:g}",pd.DataFrame(dict(Missingness=query[:,0],Shift=query[:,1],upper=out)))
    rep=run.save("continuous_replications",pd.DataFrame(rows))
    summary=run.save("continuous_summary",summarize(rep,["method"],["grid_coverage","dense_mesh_coverage","containment","ARR","UCP"]))
    return rep,summary


def pilot_design(run):
    cfg=run.cfg; grid=np.array([(m,s) for m in np.linspace(0,.4,11) for s in np.linspace(0,.6,11)])
    p=.24+.12*grid[:,0]+.1*grid[:,1]+.05*grid[:,0]*grid[:,1]
    rows=[]
    for r in range(10 if cfg.profile=="smoke" else 200):
        pilot=correlated_bernoulli(300,p,.55,seeded(cfg,80,r))
        _,indices=select_pilot_grid(grid,pilot.mean(axis=0),.32,bandwidth=.015)
        assurance=correlated_bernoulli(cfg.n_assure,p[indices],.55,seeded(cfg,81,r))
        result=certify(assurance,.32,method="exact_bonferroni")
        mm=region_metrics(result.certified,p[indices]<=.32)
        mm.update(rep=r,K_selected=len(indices),simultaneous_coverage=float(np.all(p[indices]<=result.upper)))
        rows.append(mm)
    rep=run.save("pilot_design_replications",pd.DataFrame(rows))
    run.save("pilot_design_summary",pd.DataFrame([{**rep.mean(numeric_only=True).to_dict(),"replications":len(rep)}]))
    plan=pd.DataFrame([dict(K=k,margin=m,alpha=cfg.alpha,hoeffding_n=hoeffding_sample_size(k,cfg.alpha,m)) for k in [25,100,500] for m in [.02,.05,.10]])
    run.save("sample_size_planning",plan)
    return rep,plan


SECTIONS={"calibration":calibration,"sensitivity":sensitivity,"bootstrap_and_stress":bootstrap_and_stress,
          "nested":nested,"missingness":missingness,"wdbc":wdbc,"continuous":continuous,"pilot_design":pilot_design}
