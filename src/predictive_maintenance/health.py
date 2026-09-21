from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class HealthAssessment:
    health_score: float
    condition: str
    degradation_index: float


HEALTH_FEATURES = (
    "RMS",
    "Kurtosis",
    "Peak2Peak",
)


def fit_healthy_baseline(
    frame: pd.DataFrame,
    bearing_id: int,
    healthy_fraction: float = 0.10,
) -> tuple[pd.Series, pd.Series]:

    if bearing_id not in (1, 2, 3, 4):
        raise ValueError("bearing_id must be 1, 2, 3, or 4")

    if not 0 < healthy_fraction <= 1:
        raise ValueError(
            "healthy_fraction must be between 0 and 1"
        )

    prefix = f"B{bearing_id}"

    columns = [
        f"{prefix}_RMS",
        f"{prefix}_Kurtosis",
        f"{prefix}_Peak2Peak",
    ]

    baseline_size = max(
        1,
        int(len(frame) * healthy_fraction),
    )

    baseline = (
        frame
        .sort_values("Timestamp")
        .iloc[:baseline_size]
    )

    center = baseline[columns].median()

    # Use IQR as a more stable measure of healthy variation.
    q1 = baseline[columns].quantile(0.25)
    q3 = baseline[columns].quantile(0.75)

    scale = q3 - q1

    for column in columns:
        if pd.isna(scale[column]) or scale[column] <= 0:
            std = baseline[column].std()

            if pd.isna(std) or std <= 0:
                scale[column] = 1.0
            else:
                scale[column] = std

    return center, scale


def calculate_health_series(
    frame: pd.DataFrame,
    bearing_id: int,
    healthy_fraction: float = 0.10,
    smoothing_window: int = 24,
) -> pd.DataFrame:

    if smoothing_window < 1:
        raise ValueError(
            "smoothing_window must be at least 1"
        )

    prefix = f"B{bearing_id}"

    feature_columns = [
        f"{prefix}_RMS",
        f"{prefix}_Kurtosis",
        f"{prefix}_Peak2Peak",
    ]

    center, scale = fit_healthy_baseline(
        frame,
        bearing_id,
        healthy_fraction,
    )

    result = frame[
        ["Timestamp"] + feature_columns
    ].copy()

    for column in feature_columns:
        result[f"{column}_normalized"] = (
            result[column] - center[column]
        ) / scale[column]

    normalized_columns = [
        f"{column}_normalized"
        for column in feature_columns
    ]

    # We are interested mainly in degradation in the
    # positive direction: features becoming unusually large.
    result["RawDegradationIndex"] = (
        result[normalized_columns]
        .clip(lower=0)
        .mean(axis=1)
    )

    # A persistent change matters more than one isolated spike.
    result["DegradationIndex"] = (
        result["RawDegradationIndex"]
        .rolling(
            window=smoothing_window,
            min_periods=1,
        )
        .median()
    )

    # Convert degradation to an intuitive 0-100 health score.
    result["HealthScore"] = (
        100
        * np.exp(
            -result["DegradationIndex"] / 8.0
        )
    ).clip(0, 100)

    result["Condition"] = pd.cut(
        result["DegradationIndex"],
        bins=[
            -np.inf,
            2.0,
            20.0,
            np.inf,
        ],
        labels=[
            "Healthy",
            "Degraded",
            "Severe",
        ],
    )

    return result


def assess_latest(
    frame: pd.DataFrame,
    bearing_id: int,
) -> HealthAssessment:

    result = calculate_health_series(
        frame,
        bearing_id,
    )

    latest = result.iloc[-1]

    return HealthAssessment(
        health_score=float(latest["HealthScore"]),
        condition=str(latest["Condition"]),
        degradation_index=float(
            latest["DegradationIndex"]
        ),
    )