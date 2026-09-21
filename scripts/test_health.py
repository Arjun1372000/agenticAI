import pandas as pd

from predictive_maintenance.health import (
    calculate_health_series,
)


def main():
    frame = pd.read_csv(
        "data/processed/test2_features.csv",
        parse_dates=["Timestamp"],
    )

    for bearing_id in range(1, 5):

        health = calculate_health_series(
            frame,
            bearing_id=bearing_id,
        )

        print()
        print(f"Bearing {bearing_id}")
        print("=" * 60)

        indices = [
            0,
            100,
            250,
            500,
            700,
            800,
            900,
            950,
            970,
            980,
            983,
        ]

        print(
            health.loc[
                indices,
                [
                    "Timestamp",
                    "DegradationIndex",
                    "HealthScore",
                    "Condition",
                ],
            ].to_string(index=False)
        )

        print()
        print("Condition counts:")

        print(
            health["Condition"]
            .value_counts()
        )


if __name__ == "__main__":
    main()