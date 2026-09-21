from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class RULTarget:
    failure_timestamp: pd.Timestamp


def add_rul_target(
    frame: pd.DataFrame,
    timestamp_column: str = "Timestamp",
) -> tuple[pd.DataFrame, RULTarget]:
    """
    Add RUL_Hours based on the final observation in the run.

    RUL is measured as elapsed time from each observation
    to the final timestamp of the experiment.
    """
    if timestamp_column not in frame.columns:
        raise ValueError(
            f"Missing timestamp column: {timestamp_column}"
        )

    result = frame.copy()

    result[timestamp_column] = pd.to_datetime(
        result[timestamp_column],
        errors="raise",
    )

    result = result.sort_values(
        timestamp_column
    ).reset_index(drop=True)

    failure_timestamp = result[timestamp_column].max()

    result["RUL_Hours"] = (
        failure_timestamp - result[timestamp_column]
    ).dt.total_seconds() / 3600.0

    result["RUL_Hours"] = result["RUL_Hours"].clip(
        lower=0
    )

    return result, RULTarget(
        failure_timestamp=failure_timestamp
    )