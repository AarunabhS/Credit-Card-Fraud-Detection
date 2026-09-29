"""Evaluate rare-fraud detection with chronological held-out transactions."""
from __future__ import annotations
import argparse
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from workflow import (SEED, binary_labels, input_metadata, numeric_features,
                      require_columns, run_experiment, write_report)

ROOT = Path(__file__).resolve().parent
FEATURES = [f"V{i}" for i in range(1, 29)] + ["Amount"]


def prepare_features(frame: pd.DataFrame) -> pd.DataFrame:
    X = numeric_features(frame, FEATURES)
    if (X.Amount.dropna() < 0).any():
        raise ValueError("Amount must be non-negative.")
    X["Amount"] = np.log1p(X.Amount)
    return X


def load_data(path: Path):
    frame = pd.read_csv(path)
    require_columns(frame, ["Time", "Class", *FEATURES])
    initial = len(frame)
    frame = frame.drop_duplicates(subset=["Time", "Class", *FEATURES]).reset_index(drop=True)
    time = pd.to_numeric(frame.Time, errors="raise")
    if time.isna().any() or not np.isfinite(time).all() or (time < 0).any():
        raise ValueError("Time must be finite, non-negative elapsed seconds.")
    frame = frame.assign(Time=time).sort_values("Time", kind="stable").reset_index(drop=True)
    y = binary_labels(frame.Class, "Class")
    X = prepare_features(frame)
    a, b = frame.Time.quantile([0.6, 0.8])
    splits = {
        "train": np.flatnonzero(frame.Time.to_numpy() < a),
        "validation": np.flatnonzero((frame.Time.to_numpy() >= a) & (frame.Time.to_numpy() < b)),
        "test": np.flatnonzero(frame.Time.to_numpy() >= b),
    }
    for name, rows in splits.items():
        if y.iloc[rows].nunique() != 2:
            raise ValueError(f"Chronological {name} partition must contain fraud and legitimate transactions.")
    info = {"rows_read": initial, "rows_used": len(frame), "duplicates_removed": initial-len(frame),
            "split_strategy": "chronological 60/20/20; ties in Time stay together",
            "time_ranges": {k: [float(frame.Time.iloc[v].min()), float(frame.Time.iloc[v].max())] for k,v in splits.items()}}
    return X, y, splits, info


def run(data: Path = ROOT / "data/transactions.csv", output: Path = ROOT / "results"):
    data, output = Path(data), Path(output)
    X, y, splits, info = load_data(data)
    models = {
        "baseline": DummyClassifier(strategy="prior"),
        "weighted_logistic": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
            LogisticRegression(class_weight="balanced", max_iter=700, random_state=SEED)),
        "random_forest": make_pipeline(SimpleImputer(strategy="median"),
            RandomForestClassifier(n_estimators=80, max_depth=12, min_samples_leaf=2,
                                   class_weight="balanced_subsample", n_jobs=2, random_state=SEED)),
    }
    summary, model, predictions = run_experiment(X, y, models, output,
        {"title": "Credit Card Fraud Detection", "class_names": ["Legitimate", "Fraud"], **input_metadata(data), **info}, splits=splits, beta=2)
    joblib.dump({"model": model, "threshold": summary["selected_threshold"], "features": FEATURES}, output / "model.joblib")
    predictions["Time"] = pd.read_csv(data).drop_duplicates(subset=["Time", "Class", *FEATURES]).sort_values("Time", kind="stable").reset_index(drop=True).Time.iloc[predictions.row_id].to_numpy()
    predictions.to_csv(output / "predictions.csv", index=False, float_format="%.8f")
    write_report(output, summary,
        "Detect fraudulent transactions using the anonymized Worldline/ULB benchmark. "
        f"This run evaluates {len(X):,} unique transactions. The default bundled input is a deterministic, "
        "prevalence-preserving 50,000-row sample of the deduplicated public dataset. "
        "Time orders the split and is excluded from model features. "
        "See `data/README.md` for attribution and sampling details.",
        "Average precision and fraud recall are more useful here than accuracy: predicting every transaction "
        "as legitimate already achieves very high accuracy. F2 threshold selection weights recall more than precision, "
        "but false alerts still consume investigation effort. The test partition covers later transactions, "
        "and the small number of fraud cases limits precision of the estimated recall. "
        "The benchmark spans only two days in 2013; its anonymized PCA features prevent business-level explanations. "
        "These are sample benchmark results, not production fraud-prevention guarantees.")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data/transactions.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    try:
        result = run(args.data, args.output)
    except (ValueError, OSError) as error:
        parser.exit(2, f"Input error: {error}\n")
    print(f"Selected {result['selected_model']}; test AP={result['test']['average_precision']:.4f}; report: {args.output / 'REPORT.md'}")


if __name__ == "__main__":
    main()
