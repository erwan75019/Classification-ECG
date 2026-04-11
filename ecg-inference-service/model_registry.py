from pathlib import Path
from typing import Dict

from tensorflow.keras.models import load_model


BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"


class ModelRegistry:
    def __init__(self) -> None:
        self._models: Dict[str, object] = {}
        self._model_paths = {
            "mlp": MODELS_DIR / "mlp_ecg.keras",
            "cnn": MODELS_DIR / "cnn_ecg.keras",
            "lstm": MODELS_DIR / "lstm_ecg.keras",
        }

    def load_models(self) -> None:
        """
        Ne force plus le chargement au démarrage.
        On laisse le service démarrer même si les modèles posent problème.
        """
        for model_name, model_path in self._model_paths.items():
            if model_path.exists():
                print(f"[INFO] Model declared for '{model_name}': {model_path}")
            else:
                print(f"[WARN] Model file not found for '{model_name}': {model_path}")

    def get_model(self, model_name: str):
        normalized_name = model_name.strip().lower()

        if normalized_name not in self._model_paths:
            raise ValueError(
                f"Unknown model '{model_name}'. Allowed values: {list(self._model_paths.keys())}"
            )

        if normalized_name in self._models:
            return self._models[normalized_name]

        model_path = self._model_paths[normalized_name]

        if not model_path.exists():
            raise ValueError(
                f"Model file not found for '{normalized_name}': {model_path}"
            )

        try:
            model = load_model(model_path, compile=False)
            self._models[normalized_name] = model
            return model
        except Exception as exc:
            raise ValueError(
                f"Unable to load model '{normalized_name}' from '{model_path}': {exc}"
            ) from exc

    def get_available_models(self) -> list[str]:
        return [
            model_name
            for model_name, model_path in self._model_paths.items()
            if model_path.exists()
        ]