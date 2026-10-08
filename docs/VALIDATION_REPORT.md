# Revision validation report

## Scope and outcome

The public-data and synthetic analysis is executed end to end, and the credentialed
MIMIC-IV v3.1 benchmark has now also been completed locally. The canonical notebook imports
the shared package used by the command-line analyses and contains the recorded MIMIC aggregate
outputs. No patient-level MIMIC data are bundled.

## Scientific checks

The 18-test scientific-contract suite passes. It checks exact-binomial coverage and Holm
familywise error by count enumeration, rare/zero-event behavior, shared Gaussian multipliers,
unequal independent samples, overlapping groups, confidence ties, row-local missingness,
reference-interval boundaries, continuous envelopes, alpha spending and the MIMIC loader.
The synthetic MIMIC end-to-end fixture remains software validation only. Separately, the
credentialed v3.1 run produced aggregate cohort, result, diagnostic, missingness and manifest
outputs under the frozen protocol.

The full configuration uses 500 calibration replications, 200 independently fitted nested
replications, 100 mechanism replications, 300 replications per sensitivity setting and
200 continuous-envelope replications. Independent reference samples have 20,000 rows.
Monte Carlo uncertainty and uncertainty in reference-risk classification are retained.

The main multiplier coverage estimate is 0.932 (nominal target 0.95); the rare-event stress
estimate is 0.775. Exact Bonferroni estimates are 0.960 and 0.995 respectively. These findings
are reported consistently, including in the abstract, rather than hidden by favorable examples.

## Execution and reproducibility

Both the full command-line workflow and the canonical notebook were run. The notebook preserves
the recorded text and image outputs from the completed public, synthetic, and credentialed-data
analyses. Twenty of its 21 code cells have recorded execution counts; the final repository-level
integrity cell is supplied for re-execution and the equivalent checks were run independently with
`scripts/verify_artifacts.py`. Local filesystem paths in displayed output were replaced with
portable placeholders; numerical results were not changed. No outputs were fabricated.

The final notebook metadata identifies its execution backend, completion state and duration.
The manifest records configuration, package versions, section timing, source hashes and
result-file hashes. Tables and numeric manuscript macros are generated from current CSVs;
table_provenance.json records their input hashes. The manuscript is compiled from LaTeX.
Scientific figures and document pages are rendered and visually checked.

The public repository contains the source, notebook, tests, public data, aggregate results,
figures, manuscript, response documents, and frozen protocols. Historical review materials,
credentialed clinical data, patient-level derivatives, fitted clinical models, local paths, and
build caches are excluded. The standalone notebook requires the repository's bundled modules
and public data. Requirements record the tested environment, not a guarantee that every
operating system or future dependency version behaves identically.

## Remaining requirements

The completed MIMIC-IV run should not be interpreted as clinical validation. The operational
0--1-risk tolerance is permissive and the always-survive baseline is also certified. A secondary
false-negative-risk analysis now requires sensitivity of at least 0.80 and certifies only 3 of
60 eligible conditions, but this operational target is not asserted to be a clinical standard.
Future clinical work should prospectively justify the task-specific loss, decision threshold,
and tolerance. The approximate calendar-interval padding remains an explicit analysis choice
requiring sensitivity analysis. Broader external datasets and clinical feature-timing audits
are still needed before any deployment-suitability claim.

The revision clarifies established theory and adds useful evidence; it does not supply a new
minimax result or guarantee that the contribution meets JMLR's novelty standard. Funding and
disclosure details still require author verification before submission.
