from pathlib import Path

from predictive_maintenance.build_features import build_test2_features


def main():
    dataset_dir = Path(
        "bearing-dataset/2nd_test/2nd_test"
    )

    output_path = Path(
        "data/processed/test2_features.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    features = build_test2_features(dataset_dir)

    features.to_csv(
        output_path,
        index=False,
    )

    print()
    print("Feature extraction complete.")
    print("Output:", output_path)
    print("Rows:", len(features))
    print("Columns:", len(features.columns))

    print()
    print(features.head())


if __name__ == "__main__":
    main()