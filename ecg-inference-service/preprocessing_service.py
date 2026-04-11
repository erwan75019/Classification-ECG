from pathlib import Path
from typing import Sequence

import joblib
import numpy as np


BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
SCALER_PATH = ARTIFACTS_DIR / "scaler.save"
EXPECTED_SIGNAL_LENGTH = 96


class PreprocessingService:
    def __init__(self) -> None:
        self.scaler = None
        self._load_scaler()

    def _load_scaler(self) -> None:
        if not SCALER_PATH.exists():
            print(f"[WARN] Scaler file not found: {SCALER_PATH}")
            self.scaler = None
            return

        try:
            self.scaler = joblib.load(SCALER_PATH)
            print(f"[INFO] Scaler loaded successfully from: {SCALER_PATH}")
        except Exception as exc:
            print(f"[WARN] Unable to load scaler from {SCALER_PATH}: {exc}")
            self.scaler = None

    def validate_signal(self, signal: Sequence[float]) -> np.ndarray:
        if signal is None:
            raise ValueError("Signal is required.")

        if not isinstance(signal, (list, tuple)):
            raise ValueError("Signal must be a list of numeric values.")

        if len(signal) != EXPECTED_SIGNAL_LENGTH:
            raise ValueError(
                f"Signal must contain exactly {EXPECTED_SIGNAL_LENGTH} values."
            )

        try:
            array = np.asarray(signal, dtype=np.float32)
        except (TypeError, ValueError) as exc:
            raise ValueError("Signal contains invalid numeric values.") from exc

        return array

    def scale_signal(self, signal_array: np.ndarray) -> np.ndarray:
        signal_2d = signal_array.reshape(1, -1)

        if self.scaler is None:
            return signal_2d

        return self.scaler.transform(signal_2d)

    def reshape_for_model(self, scaled_signal: np.ndarray, model_name: str) -> np.ndarray:
        normalized_name = model_name.strip().lower()

        if normalized_name == "mlp":
            return scaled_signal

        if normalized_name in {"cnn", "lstm"}:
            return scaled_signal.reshape((1, EXPECTED_SIGNAL_LENGTH, 1))

        raise ValueError(
            f"Unknown model '{model_name}'. Allowed values: ['mlp', 'cnn', 'lstm']"
        )

    def preprocess(self, signal: Sequence[float], model_name: str) -> np.ndarray:
        signal_array = self.validate_signal(signal)
        scaled_signal = self.scale_signal(signal_array)
        return self.reshape_for_model(scaled_signal, model_name)