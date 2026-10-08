# Revision validation report

## Scope and outcome

The public-data and synthetic analysis is executed end to end. The canonical notebook has
30 cells, including 13 executable cells, and eight embedded figures. Its source imports the
shared package used by the command-line analyses. MIMIC-IV is deliberately marked NOT RUN;
no credentialed data were supplied and no clinical benchmark result is represented as real.

## Scientific checks

The 18-test scientific-contract suite passes. It checks exact-binomial coverage and Holm
familywise error by count enumeration, rare/zero-event behavior, shared Gaussian multipliers,
unequal independent samples, overlapping groups, confidence ties, row-local missingness,
reference-interval boundaries, continuous envelopes, alpha spending and the MIMIC loader.
The MIMIC end-to-end fixture is synthetic software validation only; it is not clinical evidence.

The full configuration uses 500 calibration replications, 200 independently fitted nested
replications, 100 mechanism replications, 300 replications per sensitivity setting and
200 continuous-envelope replications. Independent reference samples have 20,000 rows.
Monte Carlo uncertainty and uncertainty in reference-risk classification are retained.

The main multiplier coverage estimate is 0.932 (nominal target 0.95); the rare-event stress
estimate is 0.775. Exact Bonferroni estimates are 0.960 and 0.995 respectively. These findings
are reported consistently, including in the abstract, rather than hidden by favorable examples.

## Execution and reproducibility

Both the full command-line workflow and the canonical notebook were run. Notebook execution
uses a fresh Python process with an in-process IPython shell, executing cells in order and
capturing their actual text and image output. Kernel socket binding is unavailable in this
runtime, so standard Jupyter-kernel execution could not be validated here. A standard nbclient
backend is included for environments that permit kernel sockets. No outputs were fabricated.

The final notebook metadata identifies its execution backend, completion state and duration.
The manifest records configuration, package versions, section timing, source hashes and
result-file hashes. Tables and numeric manuscript macros are generated from current CSVs;
table_provenance.json records their input hashes. The manuscript is compiled from LaTeX.
Scientific figures and document pages are rendered and visually checked.

The ZIP contains the source, notebook, tests, data, results, figures, manuscript, response,
protocol and historical archive. Use the ZIP for execution; the standalone notebook requires
its bundled modules and data. Requirements record the tested environment, not a guarantee
that every operating system or future dependency version behaves identically.

## Remaining requirements

Run the credentialed MIMIC-IV protocol after prospectively choosing a defensible risk tolerance
and rationale. Audit feature timing, temporal alignment, repeated-patient handling, dependence,
cohort support and practical value against the trivial baseline. The approximate calendar
interval padding is an explicit analysis choice requiring sensitivity analysis on actual data.
The public/synthetic studies do not establish clinical deployment suitability.

The revision clarifies established theory and adds useful evidence; it does not supply a new
minimax result or guarantee that the contribution meets JMLR's novelty standard. Author,
affiliation, funding, disclosure and public-code-release details still require author verification.
