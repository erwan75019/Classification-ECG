from typing import Any, Dict, Sequence

import numpy as np

from model_registry import ModelRegistry
from preprocessing_service import PreprocessingService


CLASS_LABELS = {
    0: "normal",
    1: "myocardial_infarction",
}


class InferenceService:
    def __init__(
        self,
        model_registry: ModelRegistry,
        preprocessing_service: PreprocessingService,
    ) -> None:
        self.model_registry = model_registry
        self.preprocessing_service = preprocessing_service

    def predict(self, signal: Sequence[float], model_name: str) -> Dict[str, Any]:
        """
        Exécute une prédiction ECG à partir d'un signal brut et d'un nom de modèle.
        """
        normalized_model_name = model_name.strip().lower()

        model = self.model_registry.get_model(normalized_model_name)
        processed_signal = self.preprocessing_service.preprocess(
            signal, normalized_model_name
        )

        raw_prediction = model.predict(processed_signal, verbose=0)
        probability = self._extract_positive_class_probability(raw_prediction)

        class_index = 1 if probability >= 0.5 else 0
        predicted_class = CLASS_LABELS[class_index]

        return {
            "predictedClass": predicted_class,
            "classIndex": class_index,
            "probability": round(probability, 6),
            "modelUsed": normalized_model_name,
            "inputLength": len(signal),
        }

    def _extract_positive_class_probability(self, raw_prediction: np.ndarray) -> float:
        """
        Convertit la sortie brute du modèle en probabilité de la classe positive.
        Gère les cas les plus fréquents :
        - sortie sigmoïde : [[0.87]]
        - sortie softmax binaire : [[0.12, 0.88]]
        """
        prediction = np.asarray(raw_prediction)

        if prediction.ndim == 2 and prediction.shape == (1, 1):
            return float(prediction[0][0])

        if prediction.ndim == 2 and prediction.shape[0] == 1 and prediction.shape[1] >= 2:
            return float(prediction[0][1])

        if prediction.ndim == 1 and prediction.shape[0] == 1:
            return float(prediction[0])

        raise ValueError(
            f"Unsupported prediction output shape: {prediction.shape}. "
            "Expected (1,1), (1,2) or equivalent binary output."
        )