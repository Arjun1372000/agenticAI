from dataclasses import dataclass
from pathlib import Path

import pandas as pd


TIMESTAMP_FORMAT = "%Y.%m.%d.%H.%M.%S"


@dataclass(frozen=True)
class TestConfig:
    name: str
    path: Path
    channels: int


def get_test_configs(dataset_root: str | Path) -> dict[str, TestConfig]:
    """
    Return the three NASA/IMS experiment configurations.
    """
    root = Path(dataset_root)

    return {
        "test1": TestConfig(
            name="1st_test",
            path=root / "1st_test" / "1st_test",
            channels=8,
        ),
        "test2": TestConfig(
            name="2nd_test",
            path=root / "2nd_test" / "2nd_test",
            channels=4,
        ),
        "test3": TestConfig(
            name="3rd_test",
            path=root / "3rd_test" / "4th_test" / "txt",
            channels=4,
        ),
    }


def list_vibration_files(dataset_dir: str | Path) -> list[Path]:
    """
    Return all vibration files in chronological filename order.
    """
    dataset_dir = Path(dataset_dir)

    if not dataset_dir.exists():
        raise FileNotFoundError(
            f"Dataset directory does not exist: {dataset_dir}"
        )

    if not dataset_dir.is_dir():
        raise NotADirectoryError(
            f"Expected a directory, got: {dataset_dir}"
        )

    files = sorted(
        path
        for path in dataset_dir.iterdir()
        if path.is_file()
    )

    if not files:
        raise FileNotFoundError(
            f"No vibration files found in: {dataset_dir}"
        )

    return files


def load_vibration_file(path: str | Path) -> pd.DataFrame:
    """
    Load one NASA/IMS vibration file.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Vibration file does not exist: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Expected a file, got: {path}"
        )

    df = pd.read_csv(
        path,
        sep="\t",
        header=None,
    )

    if df.empty:
        raise ValueError(
            f"Vibration file is empty: {path}"
        )

    df = df.apply(
        pd.to_numeric,
        errors="coerce",
    )

    if df.isna().any().any():
        raise ValueError(
            f"Vibration file contains non-numeric values: {path}"
        )

    return df


def validate_test_directory(config: TestConfig) -> None:
    """
    Verify that a configured experiment exists and has the
    expected number of vibration channels.
    """
    files = list_vibration_files(config.path)

    sample = load_vibration_file(files[0])

    if sample.shape[1] != config.channels:
        raise ValueError(
            f"{config.name} expected {config.channels} channels, "
            f"but found {sample.shape[1]}"
        )


def parse_timestamp(path: str | Path) -> pd.Timestamp:
    """
    Extract the timestamp encoded in a NASA/IMS filename.
    """
    filename = Path(path).name

    try:
        return pd.to_datetime(
            filename,
            format=TIMESTAMP_FORMAT,
        )
    except ValueError as exc:
        raise ValueError(
            f"Filename does not contain a valid timestamp: {filename}"
        ) from exc