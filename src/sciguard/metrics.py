"""Keep exact simulation truth distinct from Monte Carlo reference estimates."""
import numpy as np
from scipy.stats import beta,norm


def region_metrics(certified,true_safe):
    c=np.asarray(certified,bool); t=np.asarray(true_safe,bool)
    if c.shape!=t.shape or c.ndim!=1: raise ValueError("aligned 1D masks required")
    return {"containment":float(np.all(~c|t)),
            "ARR":float((c&t).sum()/t.sum()) if t.sum() else np.nan,
            "UCP":float((c&~t).sum()/c.sum()) if c.sum() else 0.,
            "n_certified":int(c.sum()),"n_true_safe":int(t.sum())}


def wilson_interval(values,alpha=.05):
    v=np.asarray(values,float)
    if v.ndim!=1 or not len(v) or not ((v==0)|(v==1)).all(): raise ValueError("binary replications required")
    n=len(v); p=v.mean(); z=norm.ppf(1-alpha/2); den=1+z*z/n
    mid=(p+z*z/(2*n))/den
    half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return p,max(0.,mid-half),min(1.,mid+half)


def reference_intervals(losses,delta=.01):
    """Two-sided Clopper-Pearson intervals, simultaneous across all columns."""
    from .core import _validate_losses
    x=_validate_losses(losses)
    if not 0<delta<1 or not ((x==0)|(x==1)).all(): raise ValueError("binary losses and 0<delta<1 required")
    n,k=x.shape; s=x.sum(axis=0); tail=delta/(2*k)
    lo=np.zeros(k); hi=np.ones(k)
    sel=s>0; lo[sel]=beta.ppf(tail,s[sel],n-s[sel]+1)
    sel=s<n; hi[sel]=beta.ppf(1-tail,s[sel]+1,n-s[sel])
    return lo,hi


def reference_region_metrics(certified,reference_risk,lower,upper,tau):
    c=np.asarray(certified,bool); r=np.asarray(reference_risk,float)
    lo=np.asarray(lower,float); hi=np.asarray(upper,float)
    if not c.shape==r.shape==lo.shape==hi.shape: raise ValueError("aligned inputs required")
    safe=hi<=tau; unsafe=lo>tau; ambiguous=~(safe|unsafe)
    out={"reference_"+k:v for k,v in region_metrics(c,r<=tau).items()}
    # These endpoints bracket actual containment on the reference-coverage event.
    out.update(containment_lower=float(np.all(~c|safe)),
               containment_upper=float(not np.any(c&unsafe)),
               ambiguous_environments=int(ambiguous.sum()),
               reference_halfwidth_max=float(np.max((hi-lo)/2)))
    return out
