from __future__ import annotations

import pandas as pd


FEATURE_NAMES = (
    "RMS",
    "Kurtosis",
    "Peak2Peak",
    "CrestFactor",
)


def get_bearing_observations(
    frame: pd.DataFrame,
    bearing_id: int,
) -> pd.DataFrame:
    """
    Convert the wide feature table into observations for one bearing.

    Returns one row per timestamp.
    """
    if bearing_id not in (1, 2, 3, 4):
        raise ValueError("bearing_id must be 1, 2, 3, or 4")

    prefix = f"B{bearing_id}"

    required_columns = [
        "Timestamp",
        f"{prefix}_RMS",
        f"{prefix}_Kurtosis",
        f"{prefix}_Peak2Peak",
        f"{prefix}_CrestFactor",
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

    result = frame[required_columns].copy()

    result = result.rename(
        columns={
            f"{prefix}_RMS": "rms",
            f"{prefix}_Kurtosis": "kurtosis",
            f"{prefix}_Peak2Peak": "peak_to_peak",
            f"{prefix}_CrestFactor": "crest_factor",
        }
    )

    result["bearing_id"] = bearing_id

    result = result[
        [
            "Timestamp",
            "bearing_id",
            "rms",
            "kurtosis",
            "peak_to_peak",
            "crest_factor",
        ]
    ]

    return result