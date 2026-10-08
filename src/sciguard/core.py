"""Simultaneous risk bounds. Independent rows; arbitrary within-row dependence.

All moment estimates use ddof=0. The multiplier implementation is asymptotic;
exact_bonferroni and hoeffding provide finite-sample alternatives.
"""
from dataclasses import dataclass
import numpy as np
from scipy.stats import beta, norm


@dataclass
class AssuranceResult:
    risks: np.ndarray
    standard_errors: np.ndarray
    upper_bounds: np.ndarray
    certified: np.ndarray
    critical_value: float
    method: str
    guarantee: str
    sample_sizes: np.ndarray
    eligible: np.ndarray

    @property
    def se(self):
        return self.standard_errors

    @property
    def upper(self):
        return self.upper_bounds


def _validate_losses(loss_matrix):
    x = np.asarray(loss_matrix, dtype=float)
    if x.ndim != 2 or x.shape[0] < 2 or x.shape[1] < 1:
        raise ValueError("loss_matrix must have at least two rows and one column")
    if not np.isfinite(x).all() or ((x < 0) | (x > 1)).any():
        raise ValueError("losses must be finite and in [0,1]")
    return x


def _validate_options(tau, alpha):
    if not np.isfinite(tau) or not 0 <= tau <= 1:
        raise ValueError("tau must lie in [0,1]")
    if not np.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0,1)")


def _integer(value, name, minimum):
    if isinstance(value, (bool, np.bool_)) or not np.isscalar(value) or int(value) != value or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def gaussian_max_quantile(influences, alpha=.05, n_boot=5000, rng=None,
                          variance_floor=1e-12, chunk_size=256, sampler="auto"):
    """Quantile of max(-n^-1/2 sum xi_i psi_ik / sigma_k).

The covariance sampler is exactly the same *conditional Gaussian law* as
row multipliers, apart from floating-point arithmetic and Monte Carlo error.
It does not make the bootstrap's statistical guarantee finite-sample exact.
"""
    p = np.asarray(influences, float)
    _validate_options(.5, alpha)
    n_boot = _integer(n_boot, "n_boot", 100)
    chunk_size = _integer(chunk_size, "chunk_size", 1)
    if not np.isfinite(variance_floor) or variance_floor <= 0:
        raise ValueError("variance_floor must be positive")
    if p.ndim != 2 or p.shape[0] < 2 or not np.isfinite(p).all():
        raise ValueError("influences must be a finite n by K matrix")
    p = p - p.mean(axis=0)
    sd = np.sqrt(np.mean(p * p, axis=0))
    active = sd > variance_floor
    if sampler not in {"auto", "covariance", "rows"}:
        raise ValueError("sampler must be auto, covariance, or rows")
    if not active.any():
        return float("nan"), active
    z = p[:, active] / sd[active]
    n, k = z.shape
    gen = np.random.default_rng(rng)
    if sampler == "auto":
        sampler = "covariance" if k <= min(n, 2000) else "rows"
    if sampler == "covariance":
        cov = z.T @ z / n
        eigenvalues, eigenvectors = np.linalg.eigh((cov + cov.T) / 2)
        factor = eigenvectors * np.sqrt(np.maximum(eigenvalues, 0))
    maxima = np.empty(n_boot)
    for start in range(0, n_boot, chunk_size):
        b = min(chunk_size, n_boot - start)
        if sampler == "covariance":
            draws = gen.standard_normal((b, k)) @ factor.T
        else:
            draws = gen.standard_normal((b, n)) @ z / np.sqrt(n)
        maxima[start:start+b] = np.max(-draws, axis=1)
    # Nonnegative enlargement ensures upper >= empirical risk at high alpha.
    return max(0., float(np.quantile(maxima, 1-alpha, method="higher"))), active


def exact_binomial_upper(counts, sizes, tail):
    counts, sizes = np.broadcast_arrays(np.asarray(counts, float), np.asarray(sizes, float))
    if not 0 < tail < 1 or not np.isfinite(counts).all() or not np.isfinite(sizes).all():
        raise ValueError("invalid binomial inputs")
    if ((counts < 0) | (counts > sizes) | (counts != np.floor(counts)) | (sizes < 1) | (sizes != np.floor(sizes))).any():
        raise ValueError("counts and sizes must be valid integers")
    out = np.ones(counts.shape)
    use = counts < sizes
    out[use] = beta.ppf(1-tail, counts[use]+1, sizes[use]-counts[use])
    return out


def certify(loss_matrix, tau, alpha=.05, n_boot=5000, rng=None,
            variance_floor=1e-12, chunk_size=256, method="multiplier", sampler="auto"):
    """Certify all columns of one prespecified paired loss matrix jointly."""
    x = _validate_losses(loss_matrix)
    _validate_options(tau, alpha)
    n, k = x.shape
    risk = x.mean(axis=0)
    centered = x-risk
    se = np.sqrt(np.mean(centered**2, axis=0)/n)
    c = float("nan")
    if method == "multiplier":
        c, active = gaussian_max_quantile(centered, alpha, n_boot, rng, variance_floor, chunk_size, sampler)
        upper = np.ones(k)
        upper[active] = np.minimum(1., risk[active]+c*se[active])
        guarantee = "asymptotic simultaneous band; finite bootstrap Monte Carlo error"
    elif method in {"normal_bonferroni", "pointwise"}:
        c = max(0., float(norm.ppf(1-alpha/(k if method == "normal_bonferroni" else 1))))
        upper = np.minimum(1., risk+c*se)
        upper[se*np.sqrt(n) <= variance_floor] = 1.
        guarantee = "asymptotic simultaneous band" if method == "normal_bonferroni" else "marginal only; diagnostic, no familywise guarantee"
    elif method == "hoeffding":
        upper = np.minimum(1., risk+np.sqrt(np.log(k/alpha)/(2*n)))
        guarantee = "finite-sample simultaneous band for independent bounded rows"
    elif method == "exact_bonferroni":
        if not ((x == 0) | (x == 1)).all():
            raise ValueError("exact_bonferroni requires binary losses")
        upper = exact_binomial_upper(x.sum(axis=0), n, alpha/k)
        guarantee = "finite-sample simultaneous binomial band"
    else:
        raise ValueError(f"unknown method: {method}")
    return AssuranceResult(risk, se, upper, upper <= tau, c, method, guarantee,
                           np.full(k,n), np.ones(k,bool))


def multiplier_critical_value(loss_matrix, **kwargs):
    x = _validate_losses(loss_matrix)
    return gaussian_max_quantile(x-x.mean(axis=0), **kwargs)[0]


def certify_independent(environment_losses, tau, alpha=.05, n_boot=5000, rng=None,
                        variance_floor=1e-12, chunk_size=256, method="multiplier"):
    """Unequal independent samples; never truncate or pair unrelated subjects.

For Gaussian row multipliers, each nondegenerate standardized coordinate is
exactly N(0,1) conditionally. Independence gives its maximum quantile analytically.
"""
    _validate_options(tau, alpha)
    xs = [np.asarray(x,float) for x in environment_losses]
    if not xs or any(x.ndim != 1 for x in xs):
        raise ValueError("provide a nonempty sequence of 1D samples")
    for x in xs:
        _validate_losses(x[:,None])
    n = np.array([len(x) for x in xs]); k = len(xs)
    risk = np.array([x.mean() for x in xs])
    sd = np.array([x.std(ddof=0) for x in xs]); se = sd/np.sqrt(n)
    active = sd > variance_floor; c = float("nan"); upper = np.ones(k)
    if method == "multiplier":
        if active.any():
            c = max(0., float(norm.ppf(np.exp(np.log1p(-alpha)/active.sum()))))
            upper[active] = np.minimum(1., risk[active]+c*se[active])
        guarantee = "asymptotic simultaneous band; independent environment samples"
    elif method == "exact_bonferroni":
        if any(not ((x == 0) | (x == 1)).all() for x in xs):
            raise ValueError("binary losses required")
        upper = exact_binomial_upper([x.sum() for x in xs], n, alpha/k)
        guarantee = "finite-sample simultaneous binomial band"
    elif method == "hoeffding":
        upper = np.minimum(1., risk+np.sqrt(np.log(k/alpha)/(2*n)))
        guarantee = "finite-sample simultaneous bounded-loss band"
    else:
        raise ValueError("independent samples support multiplier, exact_bonferroni, hoeffding")
    return AssuranceResult(risk,se,upper,upper<=tau,c,method,guarantee,n,np.ones(k,bool))
