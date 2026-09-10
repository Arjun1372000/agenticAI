from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class VibrationFeatures:
    rms: float
    kurtosis: float
    peak_to_peak: float
    crest_factor: float

    def as_dict(self) -> dict[str, float]:
        return {
            "rms": self.rms,
            "kurtosis": self.kurtosis,
            "peak_to_peak": self.peak_to_peak,
            "crest_factor": self.crest_factor,
        }


def extract_features(signal: Iterable[float]) -> VibrationFeatures:
    x = np.asarray(list(signal), dtype=float)

    if x.ndim != 1:
        raise ValueError("signal must be one-dimensional")

    if x.size == 0:
        raise ValueError("signal cannot be empty")

    if not np.isfinite(x).all():
        raise ValueError("signal contains NaN or infinite values")

    rms = float(np.sqrt(np.mean(x**2)))

    kurtosis = float(
        stats.kurtosis(
            x,
            fisher=False,
            bias=True,
        )
    )

    peak_to_peak = float(np.max(x) - np.min(x))

    crest_factor = (
        float(np.max(np.abs(x)) / rms)
        if rms > 0
        else 0.0
    )

    return VibrationFeatures(
        rms=rms,
        kurtosis=kurtosis,
        peak_to_peak=peak_to_peak,
        crest_factor=crest_factor,
    )