from pathlib import Path

import pandas as pd

from predictive_maintenance.data import (
    list_vibration_files,
    load_vibration_file,
    parse_timestamp,
)
from predictive_maintenance.features import extract_features


def build_test2_features(dataset_dir: str | Path) -> pd.DataFrame:
    """
    Build a feature table for the NASA/IMS Test 2 dataset.

    One row represents one vibration recording.
    Each bearing contributes four features.
    """
    files = list_vibration_files(dataset_dir)

    rows = []

    for index, file_path in enumerate(files, start=1):
        print(f"Processing {index}/{len(files)}: {file_path.name}")

        df = load_vibration_file(file_path)

        row = {
            "Timestamp": parse_timestamp(file_path),
        }

        for bearing_index in range(4):
            signal = df.iloc[:, bearing_index].to_numpy()

            features = extract_features(signal)

            prefix = f"B{bearing_index + 1}"

            row[f"{prefix}_RMS"] = features.rms
            row[f"{prefix}_Kurtosis"] = features.kurtosis
            row[f"{prefix}_Peak2Peak"] = features.peak_to_peak
            row[f"{prefix}_CrestFactor"] = features.crest_factor

        rows.append(row)

    result = pd.DataFrame(rows)

    result = result.sort_values("Timestamp")
    result = result.reset_index(drop=True)

    return result