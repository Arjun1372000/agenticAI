from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from mcp.server import MCPServer

from predictive_maintenance.health import calculate_health_series


FEATURE_FILE = Path("data/processed/test2_features.csv")

mcp = MCPServer(
    "Predictive Maintenance MCP",
    instructions=(
        "Use the diagnostic tools to assess historical bearing "
        "telemetry. When an observation index is supplied, all "
        "analysis must be based only on telemetry available up to "
        "that observation."
    ),
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
        raise ValueError(
            "bearing_id must be between 1 and 4"
        )


def get_as_of_frame(
    df: pd.DataFrame,
    observation_index: int | None,
) -> tuple[pd.DataFrame, int]:

    if observation_index is None:
        observation_index = len(df) - 1

    if observation_index < 0:
        raise ValueError(
            "observation_index cannot be negative"
        )

    if observation_index >= len(df):
        raise ValueError(
            f"observation_index must be between 0 and {len(df) - 1}"
        )

    frame = df.iloc[
        : observation_index + 1
    ].copy()

    return frame, observation_index


@mcp.tool()
def get_bearing_health(
    bearing_id: int = 1,
    observation_index: int | None = None,
) -> str:
    """Get bearing health at a specific historical observation."""

    validate_bearing_id(bearing_id)

    df = load_features()

    frame, observation_index = get_as_of_frame(
        df,
        observation_index,
    )

    health = calculate_health_series(
        frame,
        bearing_id=bearing_id,
    )

    latest_features = frame.iloc[-1]
    latest_health = health.iloc[-1]

    prefix = f"B{bearing_id}"

    return (
        f"Bearing {bearing_id}\n"
        f"Observation Index: {observation_index}\n"
        f"Timestamp: {latest_features['Timestamp']}\n"
        f"Condition: {latest_health['Condition']}\n"
        f"Health Score: {latest_health['HealthScore']:.2f}/100\n"
        f"Degradation Index: "
        f"{latest_health['DegradationIndex']:.2f}\n"
        f"RMS: {latest_features[f'{prefix}_RMS']:.6f}\n"
        f"Kurtosis: {latest_features[f'{prefix}_Kurtosis']:.6f}\n"
        f"Peak-to-Peak: "
        f"{latest_features[f'{prefix}_Peak2Peak']:.6f}\n"
        f"Crest Factor: "
        f"{latest_features[f'{prefix}_CrestFactor']:.6f}"
    )


@mcp.tool()
def get_bearing_trend(
    bearing_id: int = 1,
    observation_index: int | None = None,
    window: int = 24,
) -> str:
    """Analyze the recent degradation trend ending at a historical observation."""

    validate_bearing_id(bearing_id)

    if window < 5:
        raise ValueError(
            "window must be at least 5 observations"
        )

    df = load_features()

    frame, observation_index = get_as_of_frame(
        df,
        observation_index,
    )

    health = calculate_health_series(
        frame,
        bearing_id=bearing_id,
    )

    recent = health.tail(window).copy()

    x = np.arange(len(recent))

    degradation_slope = float(
        np.polyfit(
            x,
            recent["DegradationIndex"].to_numpy(),
            1,
        )[0]
    )

    health_slope = float(
        np.polyfit(
            x,
            recent["HealthScore"].to_numpy(),
            1,
        )[0]
    )

    if degradation_slope > 0.10:
        trend = "Increasing degradation"
    elif degradation_slope < -0.10:
        trend = "Decreasing degradation"
    else:
        trend = "Relatively stable"

    return (
        f"Bearing {bearing_id}\n"
        f"Observation Index: {observation_index}\n"
        f"Analysis Timestamp: {frame['Timestamp'].iloc[-1]}\n"
        f"Analysis Window: {len(recent)} observations\n"
        f"Trend: {trend}\n"
        f"Degradation Slope: "
        f"{degradation_slope:.4f} per observation\n"
        f"Health Score Slope: "
        f"{health_slope:.4f} per observation\n"
        f"Starting Degradation Index: "
        f"{recent['DegradationIndex'].iloc[0]:.2f}\n"
        f"Latest Degradation Index: "
        f"{recent['DegradationIndex'].iloc[-1]:.2f}\n"
        f"Starting Health Score: "
        f"{recent['HealthScore'].iloc[0]:.2f}\n"
        f"Latest Health Score: "
        f"{recent['HealthScore'].iloc[-1]:.2f}"
    )


@mcp.tool()
def get_maintenance_recommendation(
    bearing_id: int = 1,
    observation_index: int | None = None,
) -> str:
    """Generate a maintenance recommendation from historical bearing evidence."""

    validate_bearing_id(bearing_id)

    df = load_features()

    frame, observation_index = get_as_of_frame(
        df,
        observation_index,
    )

    health = calculate_health_series(
        frame,
        bearing_id=bearing_id,
    )

    latest = health.iloc[-1]
    recent = health.tail(24)

    degradation_slope = float(
        np.polyfit(
            np.arange(len(recent)),
            recent["DegradationIndex"].to_numpy(),
            1,
        )[0]
    )

    condition = str(latest["Condition"])
    score = float(latest["HealthScore"])
    degradation = float(latest["DegradationIndex"])

    if condition == "Healthy":
        priority = "Routine"
        action = (
            "Continue normal condition monitoring. "
            "No immediate maintenance action is indicated."
        )

    elif condition == "Degraded":
        priority = "Monitor"
        action = (
            "Increase monitoring frequency and schedule "
            "a condition inspection during the next maintenance window."
        )

    else:
        priority = "High"
        action = (
            "Prioritize bearing inspection and maintenance planning. "
            "Review vibration trends and confirm the physical condition "
            "before declaring failure."
        )

    trend_text = (
        "degradation is increasing"
        if degradation_slope > 0.10
        else "degradation is relatively stable"
    )

    return (
        f"Bearing {bearing_id}\n"
        f"Observation Index: {observation_index}\n"
        f"Timestamp: {frame['Timestamp'].iloc[-1]}\n"
        f"Condition: {condition}\n"
        f"Health Score: {score:.2f}/100\n"
        f"Degradation Index: {degradation:.2f}\n"
        f"Recent Trend: {trend_text}\n"
        f"Maintenance Priority: {priority}\n"
        f"Recommended Action: {action}"
    )


@mcp.tool()
def compare_bearings(
    observation_index: int | None = None,
) -> str:
    """Compare the health of all four bearings at the same historical observation."""

    df = load_features()

    frame, observation_index = get_as_of_frame(
        df,
        observation_index,
    )

    rows = []

    for bearing_id in range(1, 5):

        health = calculate_health_series(
            frame,
            bearing_id=bearing_id,
        )

        latest = health.iloc[-1]

        rows.append(
            {
                "bearing_id": bearing_id,
                "condition": str(
                    latest["Condition"]
                ),
                "health_score": float(
                    latest["HealthScore"]
                ),
                "degradation_index": float(
                    latest["DegradationIndex"]
                ),
            }
        )

    rows.sort(
        key=lambda row: row["health_score"]
    )

    output = [
        "Bearing Comparison",
        f"Observation Index: {observation_index}",
        f"Timestamp: {frame['Timestamp'].iloc[-1]}",
        "",
    ]

    for rank, row in enumerate(rows, start=1):

        output.append(
            f"{rank}. Bearing {row['bearing_id']} | "
            f"{row['condition']} | "
            f"Health Score: {row['health_score']:.2f} | "
            f"Degradation: {row['degradation_index']:.2f}"
        )

    output.extend(
        [
            "",
            f"Highest priority based on current health: "
            f"Bearing {rows[0]['bearing_id']}",
        ]
    )

    return "\n".join(output)


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001,
    )