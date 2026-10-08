# SciGuard: response to the second multi-agent review

Prepared October 2026. This document responds to the supplied simulated four-agent JMLR-style
review. It is not an actual editorial decision from JMLR.

## Overall response

We thank the reviewers for the substantially more favorable assessment. The final synthesis
judged the paper suitable for acceptance after minor revision, while identifying a small set of
technical and reporting points that could still be made more explicit. We addressed those points
without expanding the paper into a new model-comparison study or changing the completed numerical
results.

The final revision makes five targeted changes: (i) explicit rare-event guidance for the Gaussian
multiplier procedure, (ii) a recommended independent-pilot/sample-splitting workflow for any
data-driven Lipschitz bound, (iii) a concise discussion of grid growth and computational scaling,
(iv) clearer interpretation of the MIMIC-IV temporal labels and predictor scope, and (v) lighter
method-centered wording plus an explicit reminder that mesh recall is diagnostic only.

## 1. Rare-event guidance for the multiplier procedure

**Reviewer concern.** Sparse binary errors can make the studentized Gaussian approximation poor;
the adverse-regime experiment showed substantial multiplier undercoverage. The review requested a
prominent recommendation to use exact procedures when error counts are small.

**Revision.** Section 4.2 now states that, for Bernoulli loss, designs expected to yield fewer than
roughly 5-10 errors in any environment should default to exact Clopper-Pearson Bonferroni or exact
Holm certification rather than use the multiplier as the sole certificate. If sparse counts are
only discovered after assurance, the manuscript recommends reporting the exact procedures and
treating the multiplier result as diagnostic. The text explicitly says that 5-10 is practical
guidance rather than a theorem cutoff. Section 9 repeats the same rule in the practitioner-facing
method-selection paragraph.

**Location.** Section 4.2, "Dependence-aware multiplier route"; Section 9, "Choosing a method".

## 2. Data-driven Lipschitz constants in the continuous extension

**Reviewer concern.** Estimating the global Lipschitz constant from the same assurance data would
invalidate the continuous-region containment argument. The review requested an explicit
sample-splitting recommendation.

**Revision.** Section 5 now states that the largest empirical slope on the assurance grid is not a
valid global bound and that same-sample estimation of the Lipschitz constant invalidates the
containment argument. When a data-driven value is unavoidable, the recommended workflow is to use
an independent pilot sample to propose and freeze a conservative bound, then use a separate
assurance sample for the risk band. The text also clarifies that sample splitting removes
same-sample selection bias but cannot, by itself, establish unobserved between-grid smoothness;
external structural or mechanistic justification is still required.

**Location.** Section 5, "Environment Design and Continuous Regions".

## 3. Grid growth, curse of dimensionality, and scalability

**Reviewer concern.** Cartesian stress grids become exponentially large as the number of stress
axes grows, and the practical computational consequences should be discussed in the main text.

**Revision.** Section 5 now records the basic scaling relation K = G^d for d axes with G levels
each and recommends scientifically restricted axes or independent-pilot screening before freezing
the assurance family. Section 9 adds a dedicated scalability paragraph that connects grid growth
to the direct O(B n K) row-multiplier implementation and the O(n K^2 + K^3 + B K^2)
conditional-covariance alternative. The existing runtime table remains in the computational
appendix and is now explicitly referenced from the main discussion.

**Location.** Section 5, "Higher-dimensional stress spaces"; Section 9, "Scalability";
Appendix, "Computational Cost and Bootstrap Variability".

## 4. High-dimensional Gaussian-approximation discussion

**Reviewer concern.** The high-dimensional CLT discussion was technically dense relative to the
main narrative.

**Revision.** The main multiplier section now gives only the qualitative point that increasing K
requires additional uniform moment and variance conditions and that these asymptotic rates are not
used as practical sample-size rules. The conservative log^7(Kn)/n sufficient regime and related
references were moved to a short appendix note.

**Location.** Section 4.2; Appendix, "High-Dimensional Gaussian Approximation Note".

## 5. Sample-size planning versus assurance-region recall

**Reviewer concern.** The Hoeffding planning formula could be misread as guaranteeing a desired
assurance-region recall.

**Revision.** Section 5 now says explicitly that the formula controls additive band width only; it
does not guarantee a particular recall or a particular probability of certifying an environment.
The planning-table caption retains the same warning.

**Location.** Section 5; Appendix planning table.

## 6. MIMIC-IV temporal labels and predictor scope

**Reviewer concern.** The temporal intervals are approximate because MIMIC-IV shifts dates at the
patient level, and readers should be told exactly what predictor information was used.

**Revision.** Section 8 now states that the interval labels are approximate ordering intervals,
not literal shared calendar periods or exact secular trends. It also states that the fitted models
use only admission-level demographic and administrative variables: age, age-topcoding indicator,
gender, admission type, admission location, insurance, marital status, and race. No laboratory
measurements, vital signs, medications, or ICU time-series variables enter the models.

The section also begins with a high-level summary: all adequately sized tested conditions were far
below the permissive operational tolerance, including the always-survive comparator. This frames
the benchmark as a workflow and target-design demonstration rather than a clinical model-quality
claim.

**Location.** Section 8, "MIMIC-IV External Benchmark".

## 7. MIMIC-IV interpretation: certification is not clinical safety

**Reviewer concern.** The MIMIC-IV result must not be interpreted as a clinical-safety or
generalization guarantee.

**Revision.** This distinction remains explicit in the section opening, figure caption,
class-imbalance interpretation, discussion, and conclusion. The paper retains the fact that the
always-survive baseline is certified under the prespecified 0-1 loss and tau = 0.35. Rather than
hiding that result, the revision uses it to make the central design point: an assurance certificate
inherits the scientific adequacy of the chosen loss, threshold, and tolerance.

**Location.** Sections 8-10.

## 8. Continuous-region mesh recall

**Reviewer concern.** Dense-mesh recall in the continuous example could be over-interpreted as an
inferential guarantee.

**Revision.** Section 6.5 now states that the 81-by-81 mesh recall and containment values are
numerical diagnostic approximations only. Coverage of the continuous envelope comes from the
finite-grid band together with the externally justified smoothness bound, not from evaluating a
dense mesh.

**Location.** Section 6.5, "Continuous example and independent pilot".

## 9. Method-centered wording

**Reviewer concern.** Some residual phrases placed too much emphasis on the named software system.

**Revision.** Several occurrences of "SciGuard" were softened to "the workflow", "the proposed
workflow", "our empirical analysis", or "the environment-indexed assurance report". The name is
retained where it identifies the implementation, but the scientific claims are attached to the
methodology and its assumptions rather than to a branded system.

**Location.** Abstract, Introduction, Related Work, sampling section, and Conclusion.

## 10. Empirical breadth and modern tabular models

**Earlier reviewer concern.** One earlier review suggested adding XGBoost, LightGBM, TabNet, a
larger dataset, or additional ablations.

**Response.** We did not add another model in this final pass. The completed paper already includes
logistic regression, histogram gradient boosting, Extra Trees in the WDBC study, nested refits,
missingness-mechanism comparisons, grid-resolution and bootstrap-size ablations, adverse-regime
calibration, runtime analysis, and the credentialed MIMIC-IV evaluation. The later consolidated
review explicitly judged the empirical evidence sufficient and reduced the remaining decision to
minor revision. Adding another learner at this stage would broaden model comparison without
changing the assurance question and would risk obscuring the paper's methodological focus.

## 11. Runtime and reproducibility

**Reviewer concern.** Runtime and scalability should be visible to applied readers.

**Revision.** The main discussion now links computational complexity to grid dimension and points
readers to the existing timing study. The appendix continues to report timing and bootstrap
critical-value variability across n, K, and B. No new runtime numbers were fabricated or
recomputed for this prose-only revision.

**Location.** Section 9 and computational appendix.

## 12. Final scope after revision

No inferential theorem, simulation result, or MIMIC-IV numerical result was changed in response to
this review. The revision changes interpretation, guidance, organization, and the visibility of
assumptions. The paper continues to claim a scoped, auditable deployment-assurance workflow, not
clinical safety, universal distribution-shift robustness, or a new optimal high-dimensional
inference theory.

The supplied second-round review is retained privately by the authors and is not redistributed
in the public repository. Its point-by-point disposition is documented in this response for
traceability.
