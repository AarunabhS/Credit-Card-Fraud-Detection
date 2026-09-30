# Credit Card Fraud Detection: case study

## Problem and outcome

Flag rare fraud while making review capacity and missed-fraud uncertainty visible.

Average precision **0.7882**, precision **90.2%**, recall **74.3%**. Log loss **0.0030** versus baseline **0.0101**.

## Data and evaluation

The full 284,807-row Worldline/ULB benchmark replaces the 50,000-row development sample for the new evaluation. Duplicate removal leaves 283,726 records and 473 fraud labels. Time is a split variable, never a predictor. The source remains linked by TensorFlow’s official tutorial; data rights are ODbL/DbCL.

Three expanding chronological validation windows test stability. The forest uses 60 trees and at most 40,000 fitting rows per tree, keeping runtime bounded. An independent calibration reserve adjusts score scale. Investigation budgets and relative error costs are explicit assumptions; no recovered-dollar claim is made.

Model decisions use validation only. Preprocessing fits on fitting rows; probability calibration uses a disjoint reserve.
The test split is evaluated after model selection. Reusing known benchmarks during development is distinct from a new external validation.

## Findings, errors, and uncertainty

The [executed notebook](Fraud_Phase2.ipynb) displays results and uncertainty from the same Python implementation.
[Current report](results/phase2/REPORT.md), [reliability plot](results/phase2/reliability.png),
[validation stability](results/phase2/validation_stability.csv), and [uncertainty intervals](results/phase2/uncertainty.json)
show performance with its practical limits. [Error rows](results/phase2/errors.csv) expose failures rather than hiding them.

Run `python demo.py`, then open the local URL printed by the server. The demo scores public validation examples and compares frozen validation-derived review policies. Costs are hypothetical relative units; the cost recommendation uses validation outcomes only. The server binds to loopback, restricts routes and payload size, and writes no request data.

## Reproduce

Tested with the phase-one pinned Python requirements. Use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python fetch_full_data.py
python phase2.py
```

Phase-one results and notebooks remain available. Phase-two outputs are written to `results/phase2/`.
Model bundles and locally retained raw inputs are ignored by Git. Data downloaders verify pinned hashes and preserve differing existing inputs.
Install `requirements-dev.txt` for `python -m pytest -q` or to execute the notebook.

## Batch prediction with the phase-two model

```bash
python predict.py --model results/phase2/model.joblib --data examples/new_rows.csv --output results/phase2/local/new_predictions.csv
```
