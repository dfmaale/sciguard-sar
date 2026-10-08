#!/usr/bin/env python3
"""Export tables and prose macros from completed full-run CSVs; no copied numbers."""
from pathlib import Path
import sys,json,hashlib
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from sciguard.experiments import LABELS


def tex_escape(s):
    return str(s).replace("_",r"\_").replace("%",r"\%").replace("&",r"\&")


def table(path,headers,rows,align=None):
    align=align or "l"+"r"*(len(headers)-1)
    text=[r"\begin{tabular}{"+align+"}",r"\toprule"," & ".join(headers)+r" \\",r"\midrule"]
    text += [" & ".join(map(str,row))+r" \\" for row in rows]
    text += [r"\bottomrule",r"\end{tabular}"]
    path.write_text("\n".join(text)+"\n")


def number(v,d=3): return "--" if pd.isna(v) else f"{v:.{d}f}"
def interval(row,metric):
    if pd.isna(row[metric]): return "--"
    return f"{row[metric]:.3f} [{row[metric+'_lo']:.3f}, {row[metric+'_hi']:.3f}]"


def export():
    p=ROOT/"results/full"; out=ROOT/"manuscript/generated"; out.mkdir(exist_ok=True,parents=True)
    manifest=json.loads((p/"run_manifest.json").read_text())
    if manifest["status"]!="completed_public_and_synthetic": raise RuntimeError("full run is incomplete")
    for name,sha in manifest["output_sha256"].items():
        if hashlib.sha256((p/name).read_bytes()).hexdigest()!=sha: raise RuntimeError(f"CSV changed after run: {name}")
    s=pd.read_csv(p/"calibration_summary.csv")
    table(out/"calibration.tex",["Method",r"Coverage [95\% CI]",r"Containment [95\% CI]","ARR","UCP"],
          [[LABELS[r.method],interval(r,"simultaneous_coverage"),interval(r,"containment"),number(r.ARR),number(r.UCP,4)] for _,r in s.iterrows()])
    n=pd.read_csv(p/"nested_summary.csv")
    table(out/"nested.tex",["Model","Method",r"Reference containment [95\% CI]","ARR","Reference bracket"],
          [["LR" if r.Model=="Logistic regression" else "HGB",LABELS[r.method],interval(r,"reference_containment"),number(r.reference_ARR),f"[{r.containment_lower:.3f}, {r.containment_upper:.3f}]"] for _,r in n.iterrows()],"llrrr")
    w=pd.read_csv(p/"wdbc_summary.csv"); wp=w[w.design=="primary"]
    table(out/"wdbc.tex",["Model","Method","Nominal risk",r"Certified $\tau=.08$",r"Certified $\tau=.10$"],
          [[{"Logistic regression":"LR","Extra Trees":"Extra Trees","HistGradientBoosting":"HGB"}[r.Model],LABELS[r.method],number(r.nominal_risk),f"{r.certified_008}/36",f"{r.certified_010}/36"] for _,r in wp.iterrows()],"llrrr")
    grid=w[(w.Model=="Logistic regression")&(w.design!="primary")&(w.method.isin(["multiplier","exact_bonferroni"]))]
    table(out/"grid.tex",["Grid","Method",r"$K$",r"Certified $\tau=.08$","Fraction"],[[r.design,LABELS[r.method],r.K,r.certified_008,number(r.certified_fraction)] for _,r in grid.iterrows()],"llrrr")
    g=pd.read_csv(p/"paired_efficiency_gains.csv")
    table(out/"gains.tex",[r"$n$",r"$\rho$","Comparator","Paired ARR gain","MCSE"],[[int(r.n),f"{r.rho:.2f}",LABELS[r.baseline],number(r.ARR_gain),number(r.ARR_gain_mcse,4)] for _,r in g.iterrows()],"rrlrr")
    m=pd.read_csv(p/"missingness_summary.csv"); mm=m[m.method=="multiplier"]
    table(out/"missingness.tex",["Mechanism","Reference containment","Reference bracket","ARR","Ambiguous cells"],
          [[r.Mechanism,interval(r,"reference_containment"),f"[{r.containment_lower:.3f}, {r.containment_upper:.3f}]",number(r.reference_ARR),number(r.ambiguous_environments,2)] for _,r in mm.iterrows()])
    st=pd.read_csv(p/"stress_summary.csv"); st=st[st.method.isin(["normal_bonferroni","multiplier","exact_bonferroni","hoeffding"])]
    table(out/"stress.tex",["Scenario","Method",r"Coverage [95\% CI]","Containment","ARR"],
          [[{"bounded_continuous":"Continuous bounded","rare_binary":"Rare binary","high_dimensional_binary":"Larger binary family"}[r.scenario],LABELS[r.method],interval(r,"simultaneous_coverage"),number(r.containment),number(r.ARR)] for _,r in st.iterrows()],"llrrr")
    c=pd.read_csv(p/"continuous_summary.csv")
    table(out/"continuous.tex",["Method","Grid coverage","Mesh containment","Mesh recall","Mesh UCP"],
          [[LABELS[r.method],number(r.grid_coverage),number(r.containment),number(r.ARR),number(r.UCP,4)] for _,r in c.iterrows()])
    a=pd.read_csv(p/"atc_prediction_summary.csv")
    table(out/"atc.tex",["Model","MAE","Bias","RMSE"],[[r.Model,number(r.MAE),number(r.bias),number(r.RMSE)] for _,r in a.iterrows()])
    b=pd.read_csv(p/"bootstrap_runtime_summary.csv")
    table(out/"runtime.tex",[r"$n$",r"$K$",r"$B$","Critical mean","Critical MCSE","Mean seconds"],[[int(r.n),int(r.K),int(r.B),number(r.critical),number(r.critical_mcse,4),number(r.seconds,4)] for _,r in b.iterrows()])
    plan=pd.read_csv(p/"sample_size_planning.csv")
    table(out/"planning.tex",[r"$K$","Margin",r"Sufficient $n$"],[[int(r.K),f"{r.margin:.2f}",int(r.hoeffding_n)] for _,r in plan.iterrows()])
    macros={"CalMultCoverage":number(s.set_index("method").loc["multiplier","simultaneous_coverage"]),
            "CalPointCoverage":number(s.set_index("method").loc["pointwise","simultaneous_coverage"]),
            "CalExactCoverage":number(s.set_index("method").loc["exact_bonferroni","simultaneous_coverage"]),
            "RareMultCoverage":number(st[(st.scenario=="rare_binary")&(st.method=="multiplier")].simultaneous_coverage.iloc[0]),
            "MainMultARR":number(s.set_index("method").loc["multiplier","ARR"]),
            "MainExactARR":number(s.set_index("method").loc["exact_bonferroni","ARR"]),
            "NestedReps":str(manifest["config"]["nested_reps"]),"CalibrationReps":str(manifest["config"]["calibration_reps"]),
            "ReferenceN":str(manifest["config"]["n_reference"]),"MissingnessReps":str(manifest["config"]["missingness_reps"])}
    (out/"numbers.tex").write_text("\n".join("\\newcommand{\\"+k+"}{"+v+"}" for k,v in macros.items())+"\n")
    audit={"source_profile":"full","source_csv_sha256":manifest["output_sha256"],"generated_files":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob("*.tex"))}}
    (out/"table_provenance.json").write_text(json.dumps(audit,indent=2))
    print(f"Exported {len(audit['generated_files'])} manuscript inputs from full-run CSVs")

if __name__=="__main__": export()
