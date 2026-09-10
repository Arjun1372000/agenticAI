import numpy as np

from predictive_maintenance.features import extract_features


def main():
    rng = np.random.default_rng(42)

    signal = rng.normal(
        loc=0.0,
        scale=1.0,
        size=20480
    )

    features = extract_features(signal)

    print("Extracted features:")
    print(f"RMS:          {features.rms}")
    print(f"Kurtosis:     {features.kurtosis}")
    print(f"Peak-to-peak: {features.peak_to_peak}")
    print(f"Crest factor: {features.crest_factor}")


if __name__ == "__main__":
    main()