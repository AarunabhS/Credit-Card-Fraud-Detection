import numpy as np
import pandas as pd
import pytest
from analysis import FEATURES, load_data, prepare_features


def example(n=100):
    frame = pd.DataFrame({k:np.linspace(0, 1, n) for k in FEATURES})
    frame["Time"] = np.arange(n)
    frame["Class"] = [0, 1]*(n//2)
    return frame


def test_target_and_time_never_become_predictors():
    X = prepare_features(example())
    assert "Class" not in X and "Time" not in X
    assert list(X.columns) == FEATURES


def test_chronological_partition_keeps_ties_together(tmp_path):
    frame = example()
    frame["Time"] = np.repeat(np.arange(50), 2)
    path = tmp_path/"input.csv"
    frame.to_csv(path, index=False)
    _, y, splits, info = load_data(path)
    assert info["time_ranges"]["train"][1] < info["time_ranges"]["validation"][0]
    assert info["time_ranges"]["validation"][1] < info["time_ranges"]["test"][0]
    assert len(np.concatenate(list(splits.values()))) == len(y)


def test_missing_schema_and_negative_amount_fail_clearly():
    with pytest.raises(ValueError, match="Missing required"):
        prepare_features(pd.DataFrame({"Amount":[1]}))
    frame = example()
    frame.loc[0,"Amount"] = -1
    with pytest.raises(ValueError, match="non-negative"):
        prepare_features(frame)
