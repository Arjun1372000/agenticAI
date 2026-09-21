import pandas as pd


FEATURES = [
    "B1_RMS",
    "B1_Kurtosis",
    "B1_Peak2Peak",
    "B1_CrestFactor",
]


def main():
    df = pd.read_csv(
        "data/processed/test2_features.csv",
        parse_dates=["Timestamp"],
    )

    # Use the first 10% as the initial healthy operating window.
    baseline_size = int(len(df) * 0.10)

    baseline = df.iloc[:baseline_size]

    print("Healthy baseline statistics")
    print("=" * 60)

    for feature in FEATURES:
        median = baseline[feature].median()
        std = baseline[feature].std()

        print(
            f"{feature:<20} "
            f"median={median:.6f} "
            f"std={std:.6f}"
        )

    print()

    # Calculate rolling medians to expose persistent changes.
    window = 24

    for feature in FEATURES:
        df[f"{feature}_rolling"] = (
            df[feature]
            .rolling(
                window=window,
                min_periods=window,
            )
            .median()
        )

    print("Selected rolling values")
    print("=" * 60)

    indices = [
        100,
        200,
        300,
        400,
        500,
        600,
        700,
        800,
        850,
        900,
        925,
        950,
        960,
        970,
        980,
    ]

    columns = ["Timestamp"]

    for feature in FEATURES:
        columns.append(
            f"{feature}_rolling"
        )

    print(
        df.loc[
            indices,
            columns,
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()