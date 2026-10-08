# SciGuard: response to the supplied review reports

Prepared September 27, 2026. This responds to the user's simulated multi-agent case review;
it is not an actual editorial decision or a submitted response to JMLR.

## Overall response

We agree that a major revision was warranted. The revision is not limited to prose or adding
another notebook cell. It replaces the competing implementations with one shared codebase,
reruns the available evidence, changes unsupported claims, and makes the missing external
validation explicit. It does **not** claim that the outstanding JMLR-level novelty or realistic
deployment-evidence concerns have been fully resolved.

The strongest new finding is unfavorable to a universal multiplier recommendation. In the
500-replication primary rerun its simultaneous coverage is 0.932; in the 200-replication
rare-event stress design it is 0.775. Exact Bonferroni coverage is 0.960 and 0.995,
respectively. These are simulation estimates with Monte Carlo uncertainty, not universal
probabilities. The complete results and intervals appear in the manuscript and current CSVs.

## 1. Novelty and the original theorem

**Concern:** The previous theorem essentially assumed the approximation it needed; SAR
was presented too strongly as a new statistical invention.

**Action:** The introduction, abstract and discussion now call SciGuard an applied-methods
and reproducibility framework. The paper explicitly identifies exact binomial bounds,
Hoeffding, Holm, multiplier inference, the Lipschitz extension, pilot splitting and alpha
spending as established constructions. The finite-family exact guarantee has a direct proof.
The multiplier statement has a fixed-dimensional CLT/covariance/quantile argument, with its
positive-variance and bootstrap-quantile requirements spelled out.

The high-dimensional discussion retains a conservative sufficient regime and acknowledges
later CCKK improvements. It does not claim an unproved sharp grouped-data rate. The finite
environment problem is explicitly recognized as an LTT instantiation, not separated from
LTT by a misleading distinction between “parameters” and “environments.”

**Status:** Reframing and technical clarification implemented. A new minimax theorem, sharp
non-asymptotic multiplier error rate, or optimal adaptive/sequential method remains open.

**Location:** Manuscript Sections 1-4; notebook Section 2; `core.py`, `baselines.py`.

## 2. Shared transformations and dependence

**Concern:** Reusing observations across stresses was described only as correlation.

**Action:** A row-construction lemma now writes each entire loss vector as a fixed measurable
function of one independent source row and its stress randomness. This proves row independence
while allowing arbitrary within-row dependence. Deterministic dependence between coordinates
does not itself invalidate a vector CLT. Conversely, cross-row normalization, repeated patients,
clusters and temporal dependence are explicitly outside that simple argument.

One multiplier is shared across all coordinates in a row. Grouped losses use ratio-estimator
influence vectors on a master sample. Unrelated environment samples are not artificially paired
or truncated. Tests include duplicated columns, a single subgroup versus the paired method,
unequal sample sizes, and covariance-versus-row Gaussian sampling.

**Status:** Implemented for the stated sampling assumptions. Actual EHR row independence
and temporal/hospital clustering are not established without the real-data audit.

**Location:** Manuscript Section 3 and Proposition 3; notebook Sections 2.1 and 11.1;
`core.py`, `groups.py`.

## 3. Finite-sample guarantees and unstable rare-event behavior

**Concern:** Asymptotic coverage was being used as a broad practical assurance claim.

**Action:** Added exact one-sided Clopper-Pearson Bonferroni bands, Hoeffding bands for bounded
loss, and exact-binomial Holm tests. Normal Bonferroni is named explicitly so it cannot be
confused with exact inference. The multiplier no longer raises an exception when all columns
are constant; it uses conservative bounds. The grouped method no longer automatically
certifies zero-error groups using a zero standard error.

Added continuous bounded losses, rare binary errors, and a 125-environment stress family.
The observed multiplier undercoverage is retained, explained, and reflected in the abstract
and method guidance. No empirical-variance floor is presented as a full correction for
low-event-count failures. The procedure must be selected prospectively; taking the most
favorable bound afterward is not an allowed shortcut.

**Status:** Implemented. Finite-sample claims still depend on the stated independent-sampling
and bounded/Bernoulli-loss model. Unbounded heavy tails and adversarial adaptive shifts are
not covered by these experiments.

**Location:** Manuscript Sections 4 and 6.4; notebook Sections 2 and 8; `core.py`; tests.

## 4. Empirical centerpiece and training variability

**Concern:** A hand-constructed risk surface dominated the paper, while fitted-pipeline
evidence used few refits.

**Action:** The fitted-model study now precedes calibration in the manuscript and uses
200 independent refits rather than 80. It uses shared training/assurance/reference rows across
logistic regression and histogram gradient boosting, while keeping the different sample roles
independent. The exact inference alternatives receive identical assurance losses. Model-fitting
time and nominal reference risk are exported. The copula experiment is labeled calibration-only.

Training variability is represented by repeated fitted pipelines, not claimed to be a new
unconditional finite-sample result for the multiplier. The revised protected feature and
shared stress coupling change the DGP; old and new numbers are not treated as identical designs.

**Status:** Implemented for controlled simulations. This does not replace natural-shift evidence.

**Location:** Manuscript Section 6.1; notebook Section 4; `experiments.py`, `simulation.py`.

## 5. “True” risks estimated with too few reference rows

**Concern:** The earlier 1,500-row Monte Carlo estimate was effectively used as exact truth.

**Action:** Increased the independent reference sample to 20,000 rows and added simultaneous
two-sided exact binomial intervals. The reference error budget is 0.01 over both models in
each nested refit, and 0.01 over all four mechanisms in each mechanism refit. Exported
environment-level intervals distinguish confirmed-safe, confirmed-unsafe and ambiguous cells.

Point-reference containment/ARR/UCP are labeled accordingly. Lower and upper containment
indicators bound the unknown indicator on the reference-coverage event; their mean bracket
is shown separately from Wilson intervals over replications. The paper does not claim that
the reference brackets are confidence intervals for true coverage or simultaneously valid
over all refits. All model/method settings also retain certified counts.

**Status:** Implemented uncertainty accounting. More reference sampling can still be useful
near the tolerance; uncertainty has not been declared eliminated.

**Location:** Manuscript equation (reference-containment construction) and Tables 1/3 as
numbered by the final compile; notebook Section 4; `metrics.py`.

## 6. MAR, MNAR and structured missingness

**Concern:** Mechanisms were arbitrarily parameterized, and the original MAR code could
mask the variable on which missingness depended.

**Action:** Feature 0 is always observed across mechanism comparisons. MAR depends only on
that driver. MNAR depends on the feature being hidden. Intercepts are calibrated against the
known simulation distribution with fixed Gaussian quadrature rather than each evaluation
batch. Tests verify that masking a subset of rows produces exactly the same masks as those
rows in a full batch, eliminating the former cross-row normalization.

All mechanisms use severity as marginal missingness among the nine eligible features.
Structured block failure maintains those marginals. The study now has 100 refits, exports
realized rates, and compares multiplier, exact Bonferroni and exact Holm. MNAR results remain
sensitivity scenarios and do not identify any actual clinical missingness law.

**Status:** Implemented. General conclusions about which mechanism is hardest are not claimed.

**Location:** Manuscript Section 6.2; notebook Section 5; `simulation.py`.

## 7. ATC comparison fairness

**Concern:** Reporting ATC unsafe-certification rates alongside formally controlled procedures
invited an apples-to-oranges superiority claim.

**Action:** Removed ATC from the certification comparison. It now appears in a separate table
of prediction MAE, bias and RMSE, using source-only calibration and target confidence scores.
The implementation handles tied confidence values consistently with a strict threshold.
Exact Holm and exact Bonferroni provide same-target certification comparators.

**Status:** Implemented. No invented “confidence-corrected ATC” guarantee was added.

**Location:** Manuscript Section 6.1 ATC paragraph/table; notebook Section 4.1; `baselines.py`.

## 8. When is multiplier computation worthwhile?

**Concern:** The original ARR improvement over Bonferroni was modest and insufficiently explained.

**Action:** Added paired ARR-gain estimates with MCSE against normal Bonferroni, exact
Bonferroni and exact Holm across n/correlation settings. At n=1,000, the paired gain over
normal Bonferroni increases from approximately 0.0005 at latent correlation 0.10 to 0.066
at 0.90. This is a finding within the chosen simulation, not a universal cutoff.

The practical rule now starts with required validity: prefer exact binary-loss methods when
finite-sample control is required; consider multiplier efficiency only where its approximation
is adequately supported. No near-nominal assertion is carried across rare-event regimes.
The HGB nested example also shows exact Holm can nearly match multiplier recall.

**Status:** Implemented quantitative comparison and scoped guidance. No minimax-optimality
or universal break-even correlation is claimed.

**Location:** Manuscript Section 6.4 and additional paired-gain table; notebook Section 7.

## 9. Environment design and Lipschitz uncertainty

**Concern:** Axes/ranges/resolution were left to users, and an unknown smoothness constant
was effectively assumed.

**Action:** Added a concrete independent-pilot selection rule, a full simulation of the selected
finite family, a conservative sample-size planning table, and explicit instructions about
prespecification and independent assurance. The planning inequality controls bound width,
not recall. It does not choose scientifically relevant axes without external knowledge.

The continuous experiment retains an analytically valid constant for its known bilinear
surface. Half/twice-constant outputs are labeled sensitivity analyses. The text explicitly
rejects estimating a global upper Lipschitz constant from maximum finite-grid slopes, even
with sample splitting. It gives the alpha-plus-delta error allocation if a separately justified
random global bound is available.

**Status:** Implemented practical workflow and corrected interpretation. A general globally
valid Lipschitz estimator or optimal adaptive design remains open.

**Location:** Manuscript Section 5; notebook Sections 9-10; `design.py`, `continuous.py`.

## 10. Repeated and sequential certification

**Concern:** Static assurance does not address repeated model updates.

**Action:** Added the standard alpha-spending construction alpha_t = alpha/[t(t+1)] with
fresh assurance data and conditional finite-sample inference. Its summable budget supplies a
simple valid route; it is not presented as a new efficient sequential theory or an evaluated
dynamic deployment system.

**Status:** Basic conservative argument implemented; advanced sequential SAR development
remains outside the current empirical study.

**Location:** Manuscript Section 4.3; notebook Section 10; `design.py`.

## 11. Model breadth, computation and ablations

**Concern:** Few model classes, insufficient bootstrap/grid/sample-size ablations, no timing.

**Action:** WDBC now includes logistic regression, Extra Trees and histogram gradient boosting.
The package includes n/dependence sensitivity, equally spaced grid-size ablations, repeated
bootstrap sizes/seeds and runtime summaries. The primary nonuniform 36-cell grid is explicitly
distinguished from the equally spaced 6-by-6 grid. The Gaussian covariance shortcut and its
computational complexity are documented and tested against row multipliers.

**Status:** Implemented for tabular models. No deep-network or large-scale performance claim
is made. The 125-cell stress test enlarges K; it is not a high-dimensional continuous geometry study.

**Location:** Manuscript Sections 6-7 and computational appendix; notebook Sections 6-8.

## 12. A genuine external distribution-shift benchmark

**Concern:** WDBC is small and semisynthetic; a real natural-shift benchmark is missing.

**Action:** Repaired and consolidated the MIMIC-IV protocol. Each admission is aligned to
the patient's anchor year before defining approximate temporal intervals. Ambiguous
source/deployment overlap is excluded. The first eligible adult admission is selected before
temporal filtering; top-coded age is retained. Outcome/length-of-stay variables are excluded
from predictors. Native and synthetic missingness are separately reported.

One family covers all models/domains/missingness. The protocol adds exact alternatives,
small-group handling, cohort flow, an always-survive baseline, prevalence and imbalance
diagnostics, a SAR map, and frozen-config/source-file hashes. The completed v3.1 run used the
prospectively recorded operational tolerance $	au=0.35$ for 0--1 loss and minimum group size 200.

**Status: EMPIRICALLY EXECUTED WITH IMPORTANT QUALIFICATION.** The credentialed MIMIC-IV v3.1
run contains 35,114 deployment admissions and 72 prespecified model-domain-missingness
conditions; 60 conditions met the group-size rule and all 60 were certified by multiplier,
exact-Bonferroni, Hoeffding and Holm procedures. The 32-patient 2022--2022 group was withheld.
The always-survive baseline was also certified, showing that this operational 0--1 loss and
tolerance are too permissive to support a clinical-utility claim. The benchmark therefore
resolves the missing execution requirement but not clinical validation.

**Location:** Manuscript Section 8; notebook Section 11; `mimic.py`, `config/mimic_protocol.json`.

## 13. Related work and safe-operating-envelope precedents

**Concern:** Nearby literatures and safety-envelope work were missing or only name-checked.

**Action:** Added weighted conformal, PAC-Bayes and non-CCK simultaneous-band context.
The discussion now compares the target and mechanism with perception-plus-planner safety,
operational-domain monitoring, and causal online safe-region learning. LTT is described
as a direct framework for the finite environment problem. Sources were checked against
primary papers/documentation and recorded in `SOURCE_NOTES.md`.

**Status:** Implemented focused positioning; an exhaustive priority claim is not made.

**Location:** Manuscript Section 2; bibliography; `SOURCE_NOTES.md`.

## 14. Writing and reproducibility

**Concern:** Repeated explanations, duplicate/irregular headings, weak figure intuition, and
inconsistent notebook/package/manuscript results.

**Action:** Replaced the manuscript with one coherent current source, a shorter contribution
statement, explicit limitations, and current CSV-derived tables/macros. Added a workflow
schematic, consistent method labels, Wilson intervals and reference-uncertainty captions.
The original versions remain in a historical archive. The canonical notebook now imports
the package and has sequential sections, no shadowed statistical functions, no premature
“analysis complete” declaration, and no silent fallback to unexecuted archived results.

Full/smoke outputs are isolated. The notebook checks all sections and exports a provenance
manifest. The test suite targets scientific failure modes rather than only shape checks.
Only the current manuscript and canonical notebook should be used for the next review.

**Status:** Implemented; execution and artifact checks are recorded separately in
`VALIDATION_REPORT.md`. The credentialed MIMIC-IV v3.1 run is now complete and reported
with its class-imbalance limitation.

## Before another journal submission

The natural-shift MIMIC-IV benchmark is complete, but its practical usefulness against the
trivial baseline reveals that a clinically meaningful loss/tolerance remains unresolved.
Audit clinical feature timing and temporal sensitivity, consider a prospectively specified
class-sensitive follow-up analysis, broaden external validation, decide with the supervisor
whether the applied contribution is sufficient for the intended venue or whether substantial
new theory is needed, establish a public code archive, and verify author, funding and disclosure
details. This revision does not promise acceptance or declare the paper ready for JMLR submission.
