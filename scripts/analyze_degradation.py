import pandas as pd
import matplotlib.pyplot as plt

from predictive_maintenance.rul import add_rul_target


FEATURES = [
    "RMS",
    "Kurtosis",
    "Peak2Peak",
    "CrestFactor",
]


def main():
    frame = pd.read_csv(
        "data/processed/test2_features.csv",
        parse_dates=["Timestamp"],
    )

    df, target = add_rul_target(frame)

    print("Dataset shape:", df.shape)
    print()

    print("Failure timestamp:")
    print(target.failure_timestamp)

    print()

    print("Feature correlation with RUL:")

    columns = [
        "B1_RMS",
        "B1_Kurtosis",
        "B1_Peak2Peak",
        "B1_CrestFactor",
        "RUL_Hours",
    ]

    correlation = (
        df[columns]
        .corr()["RUL_Hours"]
        .sort_values()
    )

    print(correlation)

    print()

    print("First and last Bearing 1 observations:")

    print(
        df[
            [
                "Timestamp",
                "B1_RMS",
                "B1_Kurtosis",
                "B1_Peak2Peak",
                "B1_CrestFactor",
                "RUL_Hours",
            ]
        ].iloc[[0, -1]]
    )

    fig, axes = plt.subplots(
        4,
        1,
        figsize=(12, 12),
        sharex=True,
    )

    for axis, feature in zip(axes, FEATURES):

        column = f"B1_{feature}"

        axis.plot(
            df["Timestamp"],
            df[column],
        )

        axis.set_ylabel(feature)
        axis.grid(alpha=0.2)

    axes[-1].set_xlabel("Time")

    plt.suptitle(
        "Bearing 1 Feature Evolution — Test 2"
    )

    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    main()