# Data source and schema

Source: [Worldline and the Machine Learning Group, Université Libre de Bruxelles (ULB)](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud).

Licence: **Database: Open Database Licence 1.0 (ODbL); contents: Database Contents Licence 1.0 (DbCL)**. Dataset rights are separate from project code.

A 50,000-row stratified sample (seed 42) of the deduplicated Worldline/ULB benchmark: 49,917 legitimate and 83 fraudulent transactions. The original has 284,807 rows and 492 frauds; removing 1,081 exact duplicate records precedes sampling. This is a public anonymized transaction benchmark, not synthetic data. The download URL is documented in TensorFlow's official [imbalanced-classification tutorial](https://www.tensorflow.org/tutorials/structured_data/imbalanced_data).

## Schema

CSV columns: `Time, V1, V2, V3, V4, V5, V6, V7, V8, V9, V10, V11, V12, V13, V14, V15, V16, V17, V18, V19, V20, V21, V22, V23, V24, V25, V26, V27, V28, Amount, Class`.

Target: `Class` — 0=legitimate; 1=fraud.
Extra columns are excluded by the explicit feature list in `analysis.py`.
Missing or non-binary labels are rejected, never inferred as negatives.
Numeric missing features are imputed from training data; completely missing numeric columns are rejected.

## Reproduce and verify

`python fetch_data.py` verifies the local file or downloads from the exact source above if it is missing.
Both the upstream bytes and the converted CSV are checked against the SHA-256 hashes in
[provenance.json](provenance.json). Existing differing files are left untouched.
CSV conversions are deterministic with the tested requirements.

See the [results report](../results/REPORT.md) for the actual cohort, partition sizes, and limitations.
