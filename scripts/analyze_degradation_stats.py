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

    print("Overall feature statistics")
    print("=" * 60)

    print(
        df[FEATURES].describe().T
    )

    print()
    print("Selected points through the run")
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
        975,
        983,
    ]

    print(
        df.loc[
            indices,
            ["Timestamp"] + FEATURES,
        ].to_string(index=False)
    )

    print()
    print("Last 20 observations")
    print("=" * 60)

    print(
        df[
            ["Timestamp"] + FEATURES
        ].tail(20).to_string(index=False)
    )


if __name__ == "__main__":
    main()