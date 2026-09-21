import pandas as pd

from predictive_maintenance.rul import add_rul_target


def main():
    input_path = "data/processed/test2_features.csv"

    frame = pd.read_csv(input_path)

    result, target = add_rul_target(frame)

    print("Failure timestamp:")
    print(target.failure_timestamp)

    print()

    print("Rows:", len(result))
    print("Columns:", len(result.columns))

    print()

    print("First observation:")
    print(result.iloc[0][
        ["Timestamp", "RUL_Hours"]
    ])

    print()

    print("Last observation:")
    print(result.iloc[-1][
        ["Timestamp", "RUL_Hours"]
    ])

    print()

    print("RUL statistics:")
    print(result["RUL_Hours"].describe())


if __name__ == "__main__":
    main()