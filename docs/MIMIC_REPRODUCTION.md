# Reproducing the MIMIC-IV analyses

MIMIC-IV is a credentialed PhysioNet dataset. This repository does not download or redistribute it. Researchers must independently obtain access, complete the required training, and comply with the applicable data-use agreement.

## Required local layout

Set `MIMIC_IV_PATH` to the local MIMIC-IV root containing:

```text
hosp/patients.csv.gz
hosp/admissions.csv.gz
```

The older `core/` layout is also recognized by the loader. Never place the credentialed dataset inside this Git repository.

## Prespecification

Before examining deployment results, review `config/mimic_protocol.json` and freeze the dataset version, temporal domains, models, missingness levels, eligibility rule, risk tolerance, scientific rationale, familywise error level, and bootstrap settings.

The secondary class-sensitive analysis uses false-negative loss among mortality cases, a required sensitivity of 80%, and `tau_FN = 0.20` at `alpha = 0.05`. Its primary procedure is the exact Clopper-Pearson Bonferroni upper bound, with exact Holm testing as a secondary check.

## Run locally

```bash
export MIMIC_IV_PATH=/absolute/path/to/mimic-iv
export SCIGUARD_RUN_MIMIC=1
python scripts/execute_notebook.py
```

Or run the main protocol directly:

```bash
python scripts/run_mimic.py --data /absolute/path/to/mimic-iv --config config/mimic_protocol.json
```

## Public-output rule

Only aggregate tables, configurations, figures, and non-identifying logs may be published. Before committing locally generated output, verify that it contains no identifiers (`subject_id`, `hadm_id`, or `stay_id` values), row-level clinical data, patient-level predictions, trained model files, credentials, or absolute local paths.

The public class-sensitive outputs used for the current release are under `results/mimic_aggregate/` and `figures/mimic_class_sensitive/`.
