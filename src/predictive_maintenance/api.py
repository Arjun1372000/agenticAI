from __future__ import annotations

from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from predictive_maintenance.agent import ask_agent
from predictive_maintenance.health import calculate_health_series

from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title="Predictive Maintenance API",
    version="0.1.0",
)

FEATURE_FILE = Path(
    "data/processed/test2_features.csv"
)


class AgentRequest(BaseModel):
    question: str
    bearing_id: int = 1
    observation_index: int | None = None


def load_features() -> pd.DataFrame:

    if not FEATURE_FILE.exists():
        raise FileNotFoundError(
            f"Feature file not found: {FEATURE_FILE}"
        )

    return pd.read_csv(
        FEATURE_FILE,
        parse_dates=["Timestamp"],
    )


def validate_bearing_id(
    bearing_id: int,
) -> None:

    if bearing_id not in (1, 2, 3, 4):
        raise HTTPException(
            status_code=400,
            detail="bearing_id must be between 1 and 4",
        )


def validate_observation_index(
    observation_index: int,
    length: int,
) -> None:

    if (
        observation_index < 0
        or observation_index >= length
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                f"observation_index must be between "
                f"0 and {length - 1}"
            ),
        )


@app.get("/")
def root():

    return {
        "name": "Predictive Maintenance API",
        "status": "running",
    }


@app.get("/api/bearings/{bearing_id}/latest")
def get_latest(
    bearing_id: int,
):

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
        "observation_index": len(df) - 1,
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
    limit: int = 984,
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

    start_index = max(
        0,
        len(df) - limit,
    )

    history = df.iloc[
        start_index:
    ].copy()

    health = health.iloc[
        start_index:
    ].copy()

    records = []

    for offset in range(
        len(history)
    ):

        row = history.iloc[offset]
        health_row = health.iloc[offset]

        actual_index = (
            start_index + offset
        )

        records.append(
            {
                "observation_index": actual_index,
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


@app.get("/api/bearings/{bearing_id}/snapshot")
def get_snapshot(
    bearing_id: int,
    index: int,
):

    validate_bearing_id(bearing_id)

    df = load_features()

    validate_observation_index(
        index,
        len(df),
    )

    frame = df.iloc[
        : index + 1
    ].copy()

    prefix = f"B{bearing_id}"

    latest = frame.iloc[-1]

    health = calculate_health_series(
        frame,
        bearing_id=bearing_id,
    ).iloc[-1]

    return {
        "bearing_id": bearing_id,
        "observation_index": index,
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


@app.post("/api/agent/ask")
async def ask_diagnostic_agent(
    request: AgentRequest,
):

    validate_bearing_id(
        request.bearing_id
    )

    df = load_features()

    if request.observation_index is not None:
        validate_observation_index(
            request.observation_index,
            len(df),
        )

    try:

        result = await ask_agent(
            user_query=request.question,
            bearing_id=request.bearing_id,
            observation_index=request.observation_index,
        )

        return {
            "bearing_id": request.bearing_id,
            "observation_index":
                request.observation_index,
            "question": request.question,
            "answer": result["answer"],
            "tools_used": result["tools_used"],
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {exc}",
        ) from exc


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app.mount(
    "/",
    StaticFiles(
        directory=FRONTEND_DIR,
        html=True,
    ),
    name="frontend",
)