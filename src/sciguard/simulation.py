"""Row-local stress generators: no assurance-sample dependent normalization."""
from functools import lru_cache
import numpy as np
from numpy.polynomial.hermite import hermgauss
from scipy.optimize import brentq
from scipy.special import expit
from scipy.stats import norm


def ar1_cov(p=10,rho=.35):
    i=np.arange(p); return rho**np.abs(i[:,None]-i[None,:])


def outcome_probability(x):
    eta=1.5*(.75*x[:,0]-.65*x[:,1]+.45*x[:,2]+.55*x[:,0]*x[:,1]-.35*x[:,2]**2+.2*x[:,3])
    return expit(eta)


def draw_base(n,seed,p=10):
    gen=np.random.default_rng(seed)
    return (gen.multivariate_normal(np.zeros(p),ar1_cov(p),size=n),
            gen.random(n),gen.random((n,p)),gen.random(n))


def mean_shift(p=10):
    d=np.zeros(p); d[:4]=[.8,-.6,.4,.2]; d/=np.linalg.norm(d)
    return np.linalg.cholesky(ar1_cov(p))@d


@lru_cache(maxsize=256)
def logistic_intercept(m,strength=.55):
    """Population calibration for Z~N(0,1), not a batch mean adjustment."""
    if not 0<m<1: raise ValueError("interior missingness rate required")
    z,w=hermgauss(64)
    return brentq(lambda a: np.dot(w,expit(a+strength*np.sqrt(2)*z))/np.sqrt(np.pi)-m,-40,40)


def missing_mask(x,m,mechanism,uniforms,block_uniform,shift_mean=None):
    """X_0 is always observed in all four mechanism comparisons.

Severity m is marginal missingness among the remaining p-1 features. MAR
uses only the protected, observed X_0. MNAR uses the feature being hidden.
Structured missingness hides features 1:4 together; all eligible marginals m.
    """
    x=np.asarray(x,float); u=np.asarray(uniforms,float)
    if x.ndim!=2 or u.shape!=x.shape or not 0<=m<=1: raise ValueError("invalid mask inputs")
    if mechanism not in {"MCAR","MAR","MNAR","Structured"}: raise ValueError("unknown missingness mechanism")
    mask=np.zeros(x.shape,bool)
    if m==0: return mask
    if m==1: mask[:,1:]=True; return mask
    if mechanism in {"MCAR","Structured"}: mask[:,1:]=u[:,1:]<m
    else:
        mu=np.zeros(x.shape[1]) if shift_mean is None else np.asarray(shift_mean,float)
        z=x[:,[0]]-mu[0] if mechanism=="MAR" else x[:,1:]-mu[None,1:]
        probs=expit(logistic_intercept(float(m))+.55*z)
        mask[:,1:]=u[:,1:]<probs
    if mechanism=="Structured": mask[:,1:4]=(np.asarray(block_uniform)<m)[:,None]
    return mask


def environment_outputs(model,base,envs,impute,mechanism="MCAR",scores=False):
    xb,uy,um,ub=base
    losses=np.empty((len(xb),len(envs))); confidence=np.empty_like(losses)
    observed_rates=[]; direction=mean_shift(xb.shape[1])
    for k,(m,s) in enumerate(envs):
        mean=s*direction; x=xb+mean
        y=(uy<outcome_probability(x)).astype(int)
        mask=missing_mask(x,m,mechanism,um,ub,mean)
        xi=np.where(mask,impute[None,:],x)
        pred=model.predict(xi)
        losses[:,k]=(pred!=y).astype(float)
        if scores: confidence[:,k]=model.predict_proba(xi).max(axis=1)
        observed_rates.append(float(mask[:,1:].mean()))
    return losses,confidence if scores else None,np.array(observed_rates)


def correlated_bernoulli(n,probs,rho,rng):
    if not 0<=rho<=1: raise ValueError("rho must be in [0,1]")
    p=np.asarray(probs,float); gen=np.random.default_rng(rng)
    z=np.sqrt(rho)*gen.standard_normal((n,1))+np.sqrt(1-rho)*gen.standard_normal((n,len(p)))
    return (z<norm.ppf(p)[None,:]).astype(float)
