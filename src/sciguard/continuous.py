"""Continuous envelopes require an externally justified global Lipschitz bound."""
import numpy as np


def continuous_upper_envelope(grid_points,upper_grid,query_points,lipschitz,metric="euclidean"):
    g=np.asarray(grid_points,float); u=np.asarray(upper_grid,float); q=np.asarray(query_points,float)
    if g.ndim!=2 or q.ndim!=2 or not len(g) or g.shape[1]!=q.shape[1] or u.shape!=(len(g),):
        raise ValueError("aligned grid/query points and grid bounds required")
    if not np.isfinite(g).all() or not np.isfinite(q).all() or not np.isfinite(u).all() or ((u<0)|(u>1)).any():
        raise ValueError("finite points and bounded upper risks required")
    if not np.isfinite(lipschitz) or lipschitz<0: raise ValueError("valid global Lipschitz bound required")
    if metric!="euclidean": raise ValueError("only euclidean metric implemented")
    out=np.empty(len(q))
    for start in range(0,len(q),4096):
        d=np.linalg.norm(q[start:start+4096,None,:]-g[None,:,:],axis=2)
        out[start:start+4096]=np.minimum(1.,np.min(u[None,:]+lipschitz*d,axis=1))
    return out


def certify_continuous(grid_points,upper_grid,query_points,tau,lipschitz):
    from .core import _validate_options
    _validate_options(tau,.05)
    upper=continuous_upper_envelope(grid_points,upper_grid,query_points,lipschitz)
    return upper,upper<=tau
