"""Publication figures generated exclusively from the selected current run."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .experiments import LABELS,METHODS

COLORS={"pointwise":"#9b9b9b","normal_bonferroni":"#d98b32","multiplier":"#287c8e",
        "exact_bonferroni":"#465a9b","hoeffding":"#7f6aa1","holm":"#4d8f59"}


def save_figure(fig,directory,name):
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=True)
    fig.savefig(directory/(name+".png"),dpi=220,bbox_inches="tight",facecolor="white")
    fig.savefig(directory/(name+".pdf"),bbox_inches="tight",facecolor="white")
    return fig


def calibration_figure(run):
    s=pd.read_csv(run.out/"calibration_summary.csv").set_index("method")
    r=pd.read_csv(run.out/"calibration_replications.csv")
    fig,axes=plt.subplots(1,2,figsize=(11.5,4.4),layout="constrained")
    band_methods=METHODS[:-1]
    for i,m in enumerate(band_methods):
        y=s.loc[m,"simultaneous_coverage"]; lo=s.loc[m,"simultaneous_coverage_lo"]; hi=s.loc[m,"simultaneous_coverage_hi"]
        axes[0].errorbar(i,y,yerr=[[y-lo],[hi-y]],fmt="o",color=COLORS[m],capsize=4)
    axes[0].axhline(.95,color="#a43138",ls="--",lw=1)
    axes[0].set(xticks=range(len(band_methods)),xticklabels=[LABELS[m] for m in band_methods],ylim=(.4,1.025),ylabel="Simultaneous coverage",title="A. Coverage with 95% Wilson intervals")
    values=[r.loc[r.method==m,"ARR"].to_numpy() for m in METHODS]
    violin=axes[1].violinplot(values,showextrema=False,showmedians=True)
    for body,m in zip(violin["bodies"],METHODS): body.set_facecolor(COLORS[m]); body.set_alpha(.65)
    axes[1].set(xticks=range(1,len(METHODS)+1),xticklabels=[LABELS[m] for m in METHODS],ylim=(0,1),ylabel="Assurance-region recall",title="B. Recall over the same replications")
    for ax in axes: ax.tick_params(axis="x",rotation=30,labelsize=8); ax.grid(axis="y",alpha=.15)
    return save_figure(fig,run.fig,"calibration")


def sensitivity_figure(run):
    s=pd.read_csv(run.out/"sensitivity_summary.csv")
    fig,axes=plt.subplots(2,2,figsize=(10.5,7),layout="constrained")
    methods=["normal_bonferroni","multiplier","exact_bonferroni","holm"]
    for row,(d,x,label) in enumerate([(s[s.rho==.55],"n","Assurance sample size"),(s[s.n==1000],"rho","Latent Gaussian correlation")]):
        for m in methods:
            v=d[d.method==m].sort_values(x)
            if m!="holm": axes[row,0].plot(v[x],v.simultaneous_coverage,"o-",color=COLORS[m],label=LABELS[m])
            axes[row,1].plot(v[x],v.ARR,"o-",color=COLORS[m],label=LABELS[m])
        axes[row,0].axhline(.95,color="#a43138",ls="--",lw=1)
        axes[row,0].set(ylim=(.84,1.01),ylabel="Simultaneous coverage",xlabel=label)
        axes[row,1].set(ylim=(0,1),ylabel="Assurance-region recall",xlabel=label)
    axes[0,0].set_title("A. Coverage versus sample size"); axes[0,1].set_title("B. Recall versus sample size")
    axes[1,0].set_title("C. Coverage versus dependence"); axes[1,1].set_title("D. Recall versus dependence")
    axes[0,1].legend(fontsize=8,loc="lower right")
    for ax in axes.flat: ax.grid(alpha=.15)
    return save_figure(fig,run.fig,"sensitivity")


def nested_figure(run):
    s=pd.read_csv(run.out/"nested_summary.csv")
    fig,axes=plt.subplots(1,2,figsize=(10.8,4.2),layout="constrained")
    methods=["normal_bonferroni","multiplier","exact_bonferroni","hoeffding","holm"]
    for ax,name in zip(axes,["Logistic regression","HistGradientBoosting"]):
        d=s[s.Model==name].set_index("method").loc[methods]
        ax.barh(np.arange(len(methods)),d.reference_ARR,color=[COLORS[m] for m in methods])
        ax.errorbar(d.reference_ARR,np.arange(len(methods)),xerr=1.96*d.reference_ARR_mcse,fmt="none",ecolor="black",capsize=3)
        ax.set(yticks=np.arange(len(methods)),yticklabels=[LABELS[m] for m in methods],xlim=(0,1),xlabel="Reference-based ARR (mean and 1.96 MCSE)",title=name)
        ax.invert_yaxis(); ax.grid(axis="x",alpha=.15)
    return save_figure(fig,run.fig,"nested")


def wdbc_figure(run):
    s=pd.read_csv(run.out/"wdbc_detail.csv"); d=s[(s.design=="primary")&(s.method=="exact_bonferroni")]
    names=["Logistic regression","Extra Trees","HistGradientBoosting"]
    fig,axes=plt.subplots(1,3,figsize=(12,4.1),layout="constrained")
    for ax,name in zip(axes,names):
        piv=d[d.Model==name].pivot(index="Missingness",columns="Shift",values="upper")
        im=ax.imshow(piv.values,origin="lower",aspect="auto",vmin=0,vmax=max(.2,d.upper.max()),cmap="viridis")
        for level,color in [(.08,"white"),(.10,"#ffcc66")]:
            if piv.values.min()<level<piv.values.max(): ax.contour(piv.values,levels=[level],colors=[color],linewidths=1.4)
        ax.set(xticks=range(len(piv.columns)),xticklabels=[f"{v:.1f}" for v in piv.columns],yticks=range(len(piv.index)),yticklabels=[f"{v:.2f}" for v in piv.index],xlabel="Feature-noise severity",title=name)
    axes[0].set_ylabel("MCAR feature missingness")
    fig.colorbar(im,ax=axes,label="Exact Bonferroni upper risk",shrink=.8)
    return save_figure(fig,run.fig,"wdbc")


def continuous_figure(run):
    d=pd.read_csv(run.out/"continuous_example.csv")
    risk=d.pivot(index="Missingness",columns="Shift",values="risk")
    upper=d.pivot(index="Missingness",columns="Shift",values="upper")
    xx,yy=np.meshgrid(risk.columns,risk.index)
    fig,axes=plt.subplots(1,2,figsize=(10.5,4),layout="constrained")
    for ax,z,title in zip(axes,[risk.values,upper.values],["A. Known analytic risk","B. Lipschitz upper envelope"]):
        im=ax.pcolormesh(xx,yy,z,shading="auto",cmap="viridis",vmin=.24,vmax=.4)
        ax.contour(xx,yy,risk.values,levels=[.32],colors="white",linewidths=1.5)
        if title.startswith("B.") and z.min()<.32<z.max(): ax.contour(xx,yy,z,levels=[.32],colors="#ffcc66",linewidths=1.5,linestyles="--")
        ax.set(xlabel="Shift severity",ylabel="Missingness severity",title=title)
    fig.colorbar(im,ax=axes,label="Risk / upper bound",shrink=.8)
    return save_figure(fig,run.fig,"continuous")


def missingness_figure(run):
    d=pd.read_csv(run.out/"missingness_summary.csv")
    fig,axes=plt.subplots(1,2,figsize=(10.8,4.2),layout="constrained")
    mechanisms=["MCAR","MAR","MNAR","Structured"]
    for j,m in enumerate(["multiplier","exact_bonferroni","holm"]):
        s=d[d.method==m].set_index("Mechanism").loc[mechanisms]
        axes[0].bar(np.arange(4)+(j-1)*.23,s.reference_ARR,width=.23,color=COLORS[m],label=LABELS[m])
    axes[0].set(xticks=range(4),xticklabels=mechanisms,ylabel="Reference-based ARR",ylim=(0,.55),title="A. Mechanism sensitivity")
    s=d[d.method=="multiplier"].set_index("Mechanism").loc[mechanisms]
    axes[1].vlines(range(4),s.containment_lower,s.containment_upper,color=COLORS["multiplier"],lw=6,alpha=.6)
    axes[1].scatter(range(4),s.reference_containment,color="black",s=20,label="Point-reference containment")
    axes[1].set(xticks=range(4),xticklabels=mechanisms,ylim=(.8,1.02),ylabel="Mean containment indicators",title="B. Reference uncertainty (multiplier)")
    axes[0].legend(fontsize=8); axes[1].legend(fontsize=8,loc="lower right")
    for ax in axes: ax.grid(axis="y",alpha=.15)
    return save_figure(fig,run.fig,"missingness")


def stress_figure(run):
    s=pd.read_csv(run.out/"stress_summary.csv")
    fig,ax=plt.subplots(figsize=(9,4.5),layout="constrained")
    scenarios=["bounded_continuous","rare_binary","high_dimensional_binary"]
    for j,m in enumerate(["normal_bonferroni","multiplier","exact_bonferroni","hoeffding"]):
        d=s[s.method==m].set_index("scenario")
        for i,scenario in enumerate(scenarios):
            if scenario not in d.index: continue
            v=d.loc[scenario]; y=v.simultaneous_coverage
            ax.errorbar(i+(j-1.5)*.13,y,yerr=[[y-v.simultaneous_coverage_lo],[v.simultaneous_coverage_hi-y]],fmt="o",color=COLORS[m],capsize=3,label=LABELS[m] if (i==0 or (m=="exact_bonferroni" and i==1)) else None)
    ax.axhline(.95,color="#a43138",ls="--",lw=1)
    ax.set(xticks=range(3),xticklabels=["Bounded continuous\n(n=500, K=25)","Rare binary\n(n=500, K=25)","Larger binary family\n(n=1000, K=125)"],ylim=(.65,1.025),ylabel="Simultaneous coverage",title="Stress tests expose the limits of Gaussian approximations")
    ax.legend(fontsize=8,ncol=2,loc="lower left"); ax.grid(axis="y",alpha=.15)
    return save_figure(fig,run.fig,"stress")


def schematic(run):
    from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
    fig,ax=plt.subplots(figsize=(10.5,3.4),layout="constrained"); ax.set_xlim(0,10.5); ax.set_ylim(0,3.4); ax.axis("off")
    boxes=[(.1,1.8,2.2,1.2,"Freeze pipeline + family\nIndependent design / pilot"),
           (3.0,1.8,2.2,1.2,"Paired loss matrix\nRows independent\nColumns may depend"),
           (6.0,1.8,2.2,1.2,"One multiplier per row\nShared across columns\nJoint maximum"),
           (3.0,.1,2.2,1.0,"Exact / Hoeffding route\nFinite-sample bound"),
           (8.5,.1,1.9,1.0,"Upper risk <= tolerance\nCertified inner set")]
    for x,y,w,h,label in boxes:
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=.05",facecolor="#edf3f7",edgecolor="#37667c")); ax.text(x+w/2,y+h/2,label,ha="center",va="center",fontsize=9)
    for a,b in [((2.35,2.4),(2.95,2.4)),((5.25,2.4),(5.95,2.4)),((4.1,1.75),(4.1,1.15)),((8.25,2.4),(9.4,1.15)),((5.25,.6),(8.45,.6))]: ax.add_patch(FancyArrowPatch(a,b,arrowstyle="-|>",mutation_scale=13,color="#37667c",linewidth=1.4))
    return save_figure(fig,run.fig,"workflow")


def generate_all(run):
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False,"savefig.dpi":220})
    names=[]
    for fn in [schematic,calibration_figure,sensitivity_figure,nested_figure,wdbc_figure,continuous_figure,missingness_figure,stress_figure]:
        fig=fn(run); names.append(fn.__name__); plt.close(fig)
    return names


def mimic_decision_map(results,directory,method="exact_bonferroni"):
    """Render only actual local benchmark outputs; no placeholder patient results."""
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    data=results[results.method==method]
    if data.empty: raise ValueError("requested MIMIC band is absent")
    names=list(dict.fromkeys(data.Model)); domains=sorted(data.TemporalDomain.unique())
    levels=sorted(data.Missingness.unique()); tau=float(data.tau.iloc[0])
    fig,axes=plt.subplots(1,len(names),figsize=(4.1*len(names),max(4.5,.45*len(domains)+2)),squeeze=False,layout="constrained")
    cmap=ListedColormap(["#bcbcbc","#d97b70","#f0c56e","#65ac92"])
    for ax,name in zip(axes[0],names):
        states=np.zeros((len(domains),len(levels))); upper=np.full_like(states,np.nan)
        for i,domain in enumerate(domains):
            for j,m in enumerate(levels):
                row=data[(data.Model==name)&(data.TemporalDomain==domain)&np.isclose(data.Missingness,m)].iloc[0]
                states[i,j]=0 if not row.eligible else (3 if row.certified else (2 if row.risk<=tau else 1))
                upper[i,j]=row.upper if row.eligible else np.nan
        ax.imshow(states,cmap=cmap,vmin=0,vmax=3,aspect="auto")
        ax.set(xticks=range(len(levels)),xticklabels=[f"{m:.0%}" for m in levels],yticks=range(len(domains)),yticklabels=domains,xlabel="Added MCAR feature missingness",title=name)
        for i,j in np.ndindex(upper.shape): ax.text(j,i,"n too small" if np.isnan(upper[i,j]) else f"{upper[i,j]:.3f}",ha="center",va="center",fontsize=8)
    axes[0,0].set_ylabel("Approximate admission interval")
    fig.suptitle(f"MIMIC-IV: {LABELS[method]} upper risks; tolerance {tau:g}")
    fig.legend(handles=[Patch(color=cmap.colors[0],label="Insufficient sample"),Patch(color=cmap.colors[1],label="Observed risk > tolerance"),Patch(color=cmap.colors[2],label="Observed risk low; uncertified"),Patch(color=cmap.colors[3],label="Certified")],loc="outside lower center",ncol=2,fontsize=8)
    return save_figure(fig,directory,"mimic_iv_sar")
