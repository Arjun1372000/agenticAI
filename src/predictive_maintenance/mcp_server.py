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
        "Use the bearing diagnostic tools to assess current bearing "
        "condition, degradation trends, and maintenance priority. "
        "Health condition is a degradation assessment and does not by "
        "itself confirm physical failure."
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


@mcp.tool()
def get_bearing_health(
    bearing_id: int = 1,
) -> str:
    """Get the current health assessment of an industrial bearing."""

    validate_bearing_id(bearing_id)

    df = load_features()
    health = calculate_health_series(
        df,
        bearing_id=bearing_id,
    )

    latest_features = df.iloc[-1]
    latest_health = health.iloc[-1]

    prefix = f"B{bearing_id}"

    return (
        f"Bearing {bearing_id}\n"
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
    window: int = 24,
) -> str:
    """Analyze the recent degradation trend of an industrial bearing."""

    validate_bearing_id(bearing_id)

    if window < 5:
        raise ValueError(
            "window must be at least 5 observations"
        )

    if window > 984:
        raise ValueError(
            "window cannot exceed 984 observations"
        )

    df = load_features()

    health = calculate_health_series(
        df,
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

    first_degradation = float(
        recent["DegradationIndex"].iloc[0]
    )

    latest_degradation = float(
        recent["DegradationIndex"].iloc[-1]
    )

    first_health = float(
        recent["HealthScore"].iloc[0]
    )

    latest_health = float(
        recent["HealthScore"].iloc[-1]
    )

    if degradation_slope > 0.10:
        trend = "Increasing degradation"
    elif degradation_slope < -0.10:
        trend = "Improving / decreasing degradation"
    else:
        trend = "Relatively stable"

    return (
        f"Bearing {bearing_id}\n"
        f"Analysis window: {window} observations\n"
        f"Trend: {trend}\n"
        f"Degradation slope: "
        f"{degradation_slope:.4f} per observation\n"
        f"Health-score slope: "
        f"{health_slope:.4f} per observation\n"
        f"Starting degradation index: "
        f"{first_degradation:.2f}\n"
        f"Latest degradation index: "
        f"{latest_degradation:.2f}\n"
        f"Starting health score: "
        f"{first_health:.2f}\n"
        f"Latest health score: "
        f"{latest_health:.2f}"
    )


@mcp.tool()
def get_maintenance_recommendation(
    bearing_id: int = 1,
) -> str:
    """Generate a maintenance recommendation from bearing health evidence."""

    validate_bearing_id(bearing_id)

    df = load_features()

    health = calculate_health_series(
        df,
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
        f"Condition: {condition}\n"
        f"Health Score: {score:.2f}/100\n"
        f"Degradation Index: {degradation:.2f}\n"
        f"Recent Trend: {trend_text}\n"
        f"Maintenance Priority: {priority}\n"
        f"Recommended Action: {action}"
    )


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001,
    )