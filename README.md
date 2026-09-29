# Credit Card Fraud Detection

Identify rare fraudulent transactions while showing the trade-off between missed fraud and investigation workload.

**Start with the [executed notebook](Fraud_Detection.ipynb) or the [results report](results/REPORT.md).**
The report includes held-out predictions, a baseline, a precision–recall curve, confusion counts,
and the assumptions needed to interpret the results.

## Measured result

The validation-selected **random_forest** achieves test average precision **0.8666**,
precision **93.3%**, recall **87.5%**, and F1 **0.9032**.
Test log loss is **0.0073**; baseline log loss is **0.0119**.
These are the recorded benchmark results from the supplied input, not a deployment claim.

Only 16 fraud cases occur in the test sample and 8 in validation. The observed recall and chosen threshold therefore have substantial sampling uncertainty. Two days of anonymized 2013 transactions cannot establish production performance.

## Run locally

Tested with Python **3.13.2**. Use Python 3.12 or newer and the pinned requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python fetch_data.py
python analysis.py
```

After the documented public input is present, the analysis runs locally without cloud services or credentials.
The downloader verifies checksums and leaves a differing existing input untouched.
For your own labelled CSV, use `python analysis.py --data path/to/input.csv --output results/custom_run`.
The data must match the [documented schema](data/README.md).

For predictions on new unlabelled rows, first run training, then:

```bash
python predict.py --data examples/new_rows.csv --output results/new_predictions.csv
```

The model bundle contains the fitted preprocessing and the validation-selected threshold.
Positive-score meanings: 0=legitimate; 1=fraud. Score scales reflect the training benchmark.

## Data and modelling choices

A 50,000-row stratified sample (seed 42) of the deduplicated Worldline/ULB benchmark: 49,917 legitimate and 83 fraudulent transactions. The original has 284,807 rows and 492 frauds; removing 1,081 exact duplicate records precedes sampling. This is a public anonymized transaction benchmark, not synthetic data. The download URL is documented in TensorFlow's official [imbalanced-classification tutorial](https://www.tensorflow.org/tutorials/structured_data/imbalanced_data).

Chronological train/validation/test partitions; Time is excluded as a predictor. Compare class-weighted logistic regression and a bounded random forest. Select on validation average precision and tune the threshold on validation F2. Keep the later test transactions untouched.

Sources, licence, sampling, schema, and SHA-256 checksums are in [data/README.md](data/README.md).

## Reviewer map

| File | What it demonstrates |
|---|---|
| `analysis.py` | Input validation, preprocessing, bounded model comparison, held-out evaluation |
| `workflow.py` | Split isolation, validation-only decisions, metrics, report generation |
| `predict.py` | Batch inference using the saved pipeline |
| `Fraud_Detection.ipynb` | Executed walkthrough with current outputs |
| `results/REPORT.md` | Findings and limitations |
| `results/metrics.csv` | Validation and test metrics for every candidate |
| `results/predictions.csv` | Auditable held-out scores and labels |
| `results/splits.csv` | Split membership for every analysed row |
| `results/metrics.json` | Input hash, package versions, seed, and run settings |
| `tests/` | Input handling, leakage controls, metric correctness |

## Verification

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The notebook and CLI call the same implementation. Fixed seeds, pinned dependencies, and recorded input hashes
make the published run reproducible. Generated model files are local and ignored by Git.
See [REVIEW_NOTES.md](REVIEW_NOTES.md) for the repairs and remaining limits.
