"""Overlapping groups on a common independent master sample."""
import numpy as np
from .core import (_validate_losses, _validate_options, _integer, gaussian_max_quantile,
                   exact_binomial_upper, AssuranceResult)


def certify_overlapping_groups(loss_matrix, group_matrix, tau, alpha=.05,
                                B=5000, seed=20260927, min_group_size=25,
                                method="multiplier", sampler="auto"):
    x = _validate_losses(loss_matrix)
    _validate_options(tau,alpha)
    min_group_size = _integer(min_group_size,"min_group_size",2)
    g = np.asarray(group_matrix,float)
    if g.ndim == 1:
        g = g[:,None]
    if g.ndim != 2 or g.shape[0] != len(x) or g.shape[1] < 1 or not np.isfinite(g).all() or not ((g==0)|(g==1)).all():
        raise ValueError("group_matrix must be finite binary, with matching rows")
    n,q = x.shape; ng = g.sum(axis=0).astype(int); k = g.shape[1]*q
    risk = np.divide(g.T@x,ng[:,None],out=np.zeros((len(ng),q)),where=ng[:,None]>0)
    sizes = np.repeat(ng,q)
    eligible = sizes >= min_group_size
    # Empty/small groups remain in the family; no silent multiplicity reduction.
    denom = np.where(ng > 0, ng/n, 1)
    psi = (g[:,:,None]*(x[:,None,:]-risk[None,:,:])/denom[None,:,None]).reshape(n,k)
    sd = np.sqrt(np.mean(psi**2,axis=0)); se=sd/np.sqrt(n)
    flat = risk.ravel(); upper=np.ones(k); c=float("nan")
    if method == "multiplier":
        # Ignoring ineligible columns is valid because they can never certify.
        psi[:,~eligible]=0
        c,active=gaussian_max_quantile(psi,alpha,B,seed,sampler=sampler)
        upper[active]=np.minimum(1.,flat[active]+c*se[active])
        guarantee="asymptotic ratio-estimator band; nonvanishing group probabilities"
    elif method == "exact_bonferroni":
        if not ((x==0)|(x==1)).all():
            raise ValueError("binary losses required")
        upper[eligible]=exact_binomial_upper((g.T@x).ravel()[eligible],sizes[eligible],alpha/k)
        guarantee="finite-sample group-conditional binomial band under iid master rows"
    elif method == "hoeffding":
        upper[eligible]=np.minimum(1.,flat[eligible]+np.sqrt(np.log(k/alpha)/(2*sizes[eligible])))
        guarantee="finite-sample group-conditional bounded-loss band under iid master rows"
    else:
        raise ValueError("unknown group method")
    upper[~eligible]=1.
    flat[sizes==0]=np.nan; se[sizes==0]=np.nan
    return AssuranceResult(flat,se,upper,(upper<=tau)&eligible,c,method,guarantee,sizes,eligible)
