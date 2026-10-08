"""Exact-binomial Holm certification and a separate ATC performance predictor."""
import numpy as np
from scipy.stats import binom
from .core import _validate_options


def holm_reject(pvalues,alpha=.05):
    _validate_options(.5,alpha)
    p=np.asarray(pvalues,float)
    if p.ndim!=1 or not len(p) or not np.isfinite(p).all() or ((p<0)|(p>1)).any():
        raise ValueError("pvalues must be a nonempty vector in [0,1]")
    reject=np.zeros(len(p),bool)
    for rank,idx in enumerate(np.argsort(p,kind="stable")):
        if p[idx] <= alpha/(len(p)-rank): reject[idx]=True
        else: break
    return reject


def ltt_holm_certify(error_counts,n,tau,alpha=.05):
    _validate_options(tau,alpha)
    s,ns=np.broadcast_arrays(np.asarray(error_counts,float),np.asarray(n,float))
    if s.ndim!=1 or not np.isfinite(s).all() or not np.isfinite(ns).all() or ((s<0)|(s>ns)|(s!=np.floor(s))|(ns<1)|(ns!=np.floor(ns))).any():
        raise ValueError("valid integer binomial counts/sample sizes required")
    # Lower-tail p-value for H0: R_k >= tau, valid at the boundary and above.
    p=binom.cdf(s,ns,tau)
    return holm_reject(p,alpha),p


def atc_threshold(confidence,correct):
    """Choose deterministic strict-'greater than' threshold, handling ties jointly.

Minimize |fraction(score > threshold) - source accuracy|. Scores use maximum
class probability (ATC-MC). A tie chooses the more conservative, larger threshold.
"""
    s=np.asarray(confidence,float); c=np.asarray(correct)
    if s.ndim!=1 or c.shape!=s.shape or not len(s) or not np.isfinite(s).all() or not ((c==0)|(c==1)).all():
        raise ValueError("aligned finite confidence and binary correctness required")
    unique,counts=np.unique(s,return_counts=True)
    thresholds=np.r_[np.nextafter(unique[0],-np.inf),unique]
    accuracy=np.r_[1.,1.-np.cumsum(counts)/len(s)]
    discrepancy=np.abs(accuracy-c.mean())
    return float(thresholds[np.flatnonzero(np.isclose(discrepancy,discrepancy.min(),atol=1e-14,rtol=0))[-1]])


def atc_predicted_risk(target_confidence,threshold):
    s=np.asarray(target_confidence,float)
    if not s.size or not np.isfinite(s).all(): raise ValueError("finite nonempty scores required")
    return 1.-np.mean(s>threshold,axis=0)
