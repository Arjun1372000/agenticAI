from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException


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


@app.get("/")
def root():
    return {
        "name": "Predictive Maintenance API",
        "status": "running",
    }


@app.get("/api/bearings/{bearing_id}/latest")
def get_latest(bearing_id: int):
    if bearing_id not in (1, 2, 3, 4):
        raise HTTPException(
            status_code=400,
            detail="bearing_id must be 1, 2, 3, or 4",
        )

    df = load_features()

    observations = df[
        [
            "Timestamp",
            f"B{bearing_id}_RMS",
            f"B{bearing_id}_Kurtosis",
            f"B{bearing_id}_Peak2Peak",
            f"B{bearing_id}_CrestFactor",
        ]
    ]

    latest = observations.iloc[-1]

    return {
        "bearing_id": bearing_id,
        "timestamp": latest["Timestamp"].isoformat(),
        "rms": float(latest[f"B{bearing_id}_RMS"]),
        "kurtosis": float(latest[f"B{bearing_id}_Kurtosis"]),
        "peak_to_peak": float(
            latest[f"B{bearing_id}_Peak2Peak"]
        ),
        "crest_factor": float(
            latest[f"B{bearing_id}_CrestFactor"]
        ),
    }


@app.get("/api/bearings/{bearing_id}/history")
def get_history(
    bearing_id: int,
    limit: int = 100,
):
    if bearing_id not in (1, 2, 3, 4):
        raise HTTPException(
            status_code=400,
            detail="bearing_id must be 1, 2, 3, or 4",
        )

    if limit < 1 or limit > 984:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 984",
        )

    df = load_features()

    prefix = f"B{bearing_id}"

    columns = [
        "Timestamp",
        f"{prefix}_RMS",
        f"{prefix}_Kurtosis",
        f"{prefix}_Peak2Peak",
        f"{prefix}_CrestFactor",
    ]

    history = df[columns].tail(limit)

    records = []

    for _, row in history.iterrows():
        records.append(
            {
                "timestamp": row["Timestamp"].isoformat(),
                "rms": float(row[f"{prefix}_RMS"]),
                "kurtosis": float(
                    row[f"{prefix}_Kurtosis"]
                ),
                "peak_to_peak": float(
                    row[f"{prefix}_Peak2Peak"]
                ),
                "crest_factor": float(
                    row[f"{prefix}_CrestFactor"]
                ),
            }
        )

    return {
        "bearing_id": bearing_id,
        "count": len(records),
        "data": records,
    }