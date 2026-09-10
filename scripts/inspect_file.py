from pathlib import Path

import pandas as pd


def main():
    dataset_dir = Path("bearing-dataset/3rd_test/4th_test/txt")

    files = sorted(path for path in dataset_dir.iterdir() if path.is_file())

    print("Number of files:", len(files))

    first_file = files[0]

    print("First file:", first_file)

    df = pd.read_csv(
        first_file,
        sep="\t",
        header=None,
    )

    print("Shape:", df.shape)

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nData types:")
    print(df.dtypes)


if __name__ == "__main__":
    main()