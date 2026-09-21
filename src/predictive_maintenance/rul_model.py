from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

from predictive_maintenance.rul import add_rul_target


RUL_FEATURES = (
    "RMS",
    "Kurtosis",
    "Peak2Peak",
    "CrestFactor",
)


def prepare_rul_dataset(
    frame: pd.DataFrame,
    bearing_id: int = 1,
) -> tuple[pd.DataFrame, list[str]]:

    if bearing_id not in (1, 2, 3, 4):
        raise ValueError(
            "bearing_id must be 1, 2, 3, or 4"
        )

    prefix = f"B{bearing_id}"

    feature_columns = [
        f"{prefix}_{feature}"
        for feature in RUL_FEATURES
    ]

    required_columns = [
        "Timestamp",
        *feature_columns,
    ]

    missing = [
        column
        for column in required_columns
        if column not in frame.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    selected = frame[
        required_columns
    ].copy()

    selected, _ = add_rul_target(
        selected,
        timestamp_column="Timestamp",
    )

    return selected, feature_columns


def train_rul_model(
    train_frame: pd.DataFrame,
    feature_columns: list[str],
) -> XGBRegressor:

    model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        train_frame[feature_columns],
        train_frame["RUL_Hours"],
    )

    return model


def evaluate_rul_model(
    model: XGBRegressor,
    test_frame: pd.DataFrame,
    feature_columns: list[str],
) -> dict[str, float]:

    predictions = model.predict(
        test_frame[feature_columns]
    )

    predictions = np.clip(
        predictions,
        0,
        None,
    )

    actual = test_frame["RUL_Hours"].to_numpy()

    return {
        "mae_hours": float(
            mean_absolute_error(
                actual,
                predictions,
            )
        ),
        "rmse_hours": float(
            np.sqrt(
                mean_squared_error(
                    actual,
                    predictions,
                )
            )
        ),
        "r2": float(
            r2_score(
                actual,
                predictions,
            )
        ),
    }


def predict_rul(
    model: XGBRegressor,
    frame: pd.DataFrame,
    feature_columns: list[str],
) -> np.ndarray:

    predictions = model.predict(
        frame[feature_columns]
    )

    return np.clip(
        predictions,
        0,
        None,
    )


def save_rul_model(
    model: XGBRegressor,
    feature_columns: list[str],
    path: str | Path,
) -> None:

    path = Path(path)
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact = {
        "model": model,
        "feature_columns": feature_columns,
    }

    joblib.dump(
        artifact,
        path,
    )


def load_rul_model(
    path: str | Path,
) -> tuple[XGBRegressor, list[str]]:

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"RUL model not found: {path}"
        )

    artifact = joblib.load(path)

    return (
        artifact["model"],
        artifact["feature_columns"],
    )