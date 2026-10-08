# Statistical Assurance Regions

Statistical Assurance Regions (SARs) certify the prespecified deployment environments in which a frozen predictive pipeline remains below a risk tolerance. **SciGuard** is the reference Python implementation used for the accompanying JMLR study of joint missingness and distribution shift.

## Current release scope

This repository contains:

- simultaneous and finite-sample SAR procedures;
- simulation, WDBC, and continuous-environment experiments;
- the executable Jupyter notebook used for the study;
- aggregate MIMIC-IV results and figures, without patient-level data;
- a secondary class-sensitive analysis based on false-negative risk
  \(R_{\mathrm{FN}}(e)\), with \(\tau_{\mathrm{FN}}=0.20\);
- tests, manuscript source, and generated manuscript tables.

In the prespecified class-sensitive MIMIC-IV analysis, **3 of 60 eligible model-environment combinations were certified** by the primary exact Bonferroni procedure. This result should be interpreted together with the sparse-event eligibility rules and limitations documented in the notebook.

## Install

```bash
git clone https://github.com/dfmaale/sciguard-sar.git
cd sciguard-sar
python -m pip install -e ".[experiments,notebook,test]"
```

## Validate and reproduce

```bash
python -m unittest discover -s tests -v
python scripts/run_analysis.py --profile smoke
SCIGUARD_RUN_MIMIC=1 MIMIC_IV_PATH=/path/to/mimic-iv python scripts/execute_notebook.py
```

The canonical notebook is `notebooks/SciGuard_JMLR_Reproducible_Analysis_MIMIC_IV.ipynb`. Complete execution of its MIMIC-IV sections requires authorized local data; the public simulation and WDBC analyses can be regenerated independently with `scripts/run_analysis.py`.

For a quick notebook execution, set `SCIGUARD_PROFILE=smoke`. The default profile is `full`. Non-notebook reproduction is available through:

```bash
python scripts/run_analysis.py --profile full
python scripts/render_results.py
python scripts/export_manuscript.py
```

## MIMIC-IV access and privacy

MIMIC-IV is credentialed and is **not redistributed** here. This repository contains only code, configurations, aggregate outputs, and figures. Do not commit raw MIMIC-IV tables, row-level derivatives, trained clinical models, credentials, or local data paths.

Credentialed users can follow [`docs/MIMIC_REPRODUCTION.md`](docs/MIMIC_REPRODUCTION.md) to reproduce the analysis locally.

## Repository map

| Path | Purpose |
|---|---|
| `src/sciguard/` | SciGuard inference and experiment implementation |
| `tests/` | Scientific-contract and software tests |
| `notebooks/` | Canonical reproducibility notebook |
| `config/` | Prespecified analysis configuration |
| `results/full/` | Full simulation and WDBC aggregate outputs |
| `results/mimic_aggregate/` | Public class-sensitive aggregate results |
| `figures/` | Publication and assurance-region figures |
| `manuscript/` | JMLR LaTeX source and generated tables |
| `docs/` | Audit, validation, and reproduction notes |

## Citation

Please use the metadata in [`CITATION.cff`](CITATION.cff). A version-specific Zenodo DOI will be added after the first GitHub release is archived.

## License

The software is distributed under the [MIT License](LICENSE). MIMIC-IV remains governed by its own PhysioNet data-use requirements.
