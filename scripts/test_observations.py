import pandas as pd

from predictive_maintenance.observations import (
    get_bearing_observations,
)


def main():
    frame = pd.read_csv(
        "data/processed/test2_features.csv"
    )

    bearing = get_bearing_observations(
        frame,
        bearing_id=1,
    )

    print("Shape:", bearing.shape)

    print()
    print(bearing.head())

    print()
    print("Latest observation:")
    print(bearing.iloc[-1])


if __name__ == "__main__":
    main()