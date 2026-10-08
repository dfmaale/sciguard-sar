"""Planning utilities. Pilot choices must precede independent assurance data."""
import numpy as np


def hoeffding_sample_size(n_environments,alpha=.05,margin=.05):
    if int(n_environments)!=n_environments or n_environments<1 or not 0<alpha<1 or not 0<margin<=1:
        raise ValueError("positive K, 0<alpha<1 and 0<margin<=1 required")
    return int(np.ceil(np.log(n_environments/alpha)/(2*margin**2)))


def alpha_spending(round_number,alpha=.05):
    if int(round_number)!=round_number or round_number<1 or not 0<alpha<1:
        raise ValueError("positive integer round and valid alpha required")
    return alpha/(round_number*(round_number+1))


def select_pilot_grid(candidate_points,pilot_risks,tau,bandwidth=.08):
    """Refine near the pilot boundary; retain coordinate extremes.

No validity is attributed to the pilot. Condition on its selected finite family
and evaluate it on untouched assurance rows, or certify a full fixed superset.
"""
    g=np.asarray(candidate_points,float); r=np.asarray(pilot_risks,float)
    if g.ndim!=2 or r.shape!=(len(g),) or not np.isfinite(g).all() or not np.isfinite(r).all():
        raise ValueError("finite aligned points and risks required")
    chosen=np.abs(r-tau)<=bandwidth
    for j in range(g.shape[1]):
        chosen[np.argmin(g[:,j])]=True; chosen[np.argmax(g[:,j])]=True
    return g[chosen],np.flatnonzero(chosen)
