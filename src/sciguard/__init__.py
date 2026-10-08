"""SciGuard: explicit finite-sample and asymptotic environment assurance."""
__version__="0.2.0"
from .core import AssuranceResult,certify,certify_independent,multiplier_critical_value
from .groups import certify_overlapping_groups
from .continuous import continuous_upper_envelope,certify_continuous
from .baselines import ltt_holm_certify,holm_reject,atc_threshold,atc_predicted_risk
from .metrics import region_metrics,reference_intervals,reference_region_metrics,wilson_interval
