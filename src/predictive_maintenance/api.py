from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

from predictive_maintenance.health import calculate_health_series


app = FastAPI(
    title="Predictive Maintenance API",
    version="0.1.0",
)


FEATURE_FILE = Path(
    "data/processed/test2_features.csv"
)


def load_features() -> pd.DataFrame:
    if not FEATURE_FILE.exists():
        raise FileNotFoundError(
            f"Feature file not found: {FEATURE_FILE}"
        )

    return pd.read_csv(
        FEATURE_FILE,
        parse_dates=["Timestamp"],
    )


def validate_bearing_id(bearing_id: int) -> None:
    if bearing_id not in (1, 2, 3, 4):
        raise HTTPException(
            status_code=400,
            detail="bearing_id must be between 1 and 4",
        )


@app.get("/")
def root():
    return {
        "name": "Predictive Maintenance API",
        "status": "running",
    }


@app.get("/api/bearings/{bearing_id}/latest")
def get_latest(bearing_id: int):

    validate_bearing_id(bearing_id)

    df = load_features()

    prefix = f"B{bearing_id}"

    latest = df.iloc[-1]

    health = calculate_health_series(
        df,
        bearing_id=bearing_id,
    ).iloc[-1]

    return {
        "bearing_id": bearing_id,

        "timestamp": latest["Timestamp"].isoformat(),

        "features": {
            "rms": float(
                latest[f"{prefix}_RMS"]
            ),

            "kurtosis": float(
                latest[f"{prefix}_Kurtosis"]
            ),

            "peak_to_peak": float(
                latest[f"{prefix}_Peak2Peak"]
            ),

            "crest_factor": float(
                latest[f"{prefix}_CrestFactor"]
            ),
        },

        "health": {
            "score": float(
                health["HealthScore"]
            ),

            "condition": str(
                health["Condition"]
            ),

            "degradation_index": float(
                health["DegradationIndex"]
            ),
        },
    }


@app.get("/api/bearings/{bearing_id}/history")
def get_history(
    bearing_id: int,
    limit: int = 100,
):

    validate_bearing_id(bearing_id)

    if limit < 1 or limit > 984:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 984",
        )

    df = load_features()

    prefix = f"B{bearing_id}"

    health = calculate_health_series(
        df,
        bearing_id=bearing_id,
    )

    history = df.tail(limit).copy()
    health = health.tail(limit)

    records = []

    for index in range(len(history)):

        row = history.iloc[index]
        health_row = health.iloc[index]

        records.append(
            {
                "timestamp": row["Timestamp"].isoformat(),

                "rms": float(
                    row[f"{prefix}_RMS"]
                ),

                "kurtosis": float(
                    row[f"{prefix}_Kurtosis"]
                ),

                "peak_to_peak": float(
                    row[f"{prefix}_Peak2Peak"]
                ),

                "crest_factor": float(
                    row[f"{prefix}_CrestFactor"]
                ),

                "health_score": float(
                    health_row["HealthScore"]
                ),

                "degradation_index": float(
                    health_row["DegradationIndex"]
                ),

                "condition": str(
                    health_row["Condition"]
                ),
            }
        )

    return {
        "bearing_id": bearing_id,
        "count": len(records),
        "data": records,
    }