# MIMIC-IV manuscript integration update

The credentialed MIMIC-IV v3.1 run has been integrated into the JMLR manuscript.

## Main benchmark facts used in the manuscript

- Joined admissions: 546,028
- First eligible adult admission per patient: 223,452
- Source cohort: 106,864
- Source model-fitting rows: 85,491
- Source holdout rows: 21,373
- Deployment cohort: 35,114
- Excluded source/deployment-overlap rows: 81,474
- Models: logistic regression, histogram gradient boosting, always-survive comparator
- Added MCAR feature missingness: 0%, 10%, 20%, 30%
- Temporal-domain labels: 2017-2021, 2018-2022, 2019-2022, 2020-2022, 2021-2022, 2022-2022
- Prespecified operational 0-1-risk tolerance: tau = 0.35
- Familywise alpha: 0.05
- Minimum group size: 200
- Multiplier draws: 5,000
- Prespecified family size: 72 model-domain-missingness conditions
- Eligible conditions: 60
- Certified conditions: 60/60 under multiplier, exact-Bonferroni, Hoeffding, and Holm
- 2022-2022 group: n = 32; retained as ineligible and not certified
- Multiplier critical value: 2.537833
- Largest eligible multiplier upper risk: 0.046457
- Largest eligible exact-Bonferroni upper risk: 0.047370
- Largest eligible Hoeffding upper risk: 0.104399

## Important interpretation

The always-survive baseline is also certified under the operational tau = 0.35 threshold.
The manuscript therefore does not interpret certification as clinical safety. At zero added
missingness, logistic-regression AUROC ranges from 0.805 to 0.951 across the five eligible
temporal domains, but sensitivity at a 0.5 decision threshold is zero in four of the five
eligible domains and approximately 0.049 in the 2019-2022 domain. This demonstrates that a
statistically valid certificate inherits the scientific adequacy of the chosen loss, decision
threshold, and tolerance.

## Manuscript additions

- Abstract updated with completed credentialed MIMIC-IV evidence.
- Introduction contribution statement updated.
- Section 8 replaced with a completed MIMIC-IV external benchmark section.
- Added the MIMIC assurance-map figure.
- Added a compact MIMIC temporal-domain table.
- Discussion and Conclusion updated to reflect both the evidence and its class-imbalance limitation.
- Data and Code Availability updated to describe aggregate outputs and restricted-data handling.
