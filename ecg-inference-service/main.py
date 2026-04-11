from flask import Flask, jsonify, request

from inference_service import InferenceService
from model_registry import ModelRegistry
from preprocessing_service import PreprocessingService


app = Flask(__name__)

model_registry = ModelRegistry()
model_registry.load_models()

preprocessing_service = PreprocessingService()
inference_service = InferenceService(model_registry, preprocessing_service)


@app.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "ecg-inference-service",
        }
    ), 200


@app.route("/models", methods=["GET"])
def models():
    return jsonify(
        {
            "availableModels": model_registry.get_available_models(),
        }
    ), 200


@app.route("/predict", methods=["POST"])
def predict():
    try:
        payload = request.get_json(silent=True)

        if payload is None:
            return jsonify({"error": "Request body must be valid JSON."}), 400

        model_name = payload.get("model")
        signal = payload.get("signal")

        if not model_name:
            return jsonify({"error": "Field 'model' is required."}), 400

        if signal is None:
            return jsonify({"error": "Field 'signal' is required."}), 400

        result = inference_service.predict(signal, model_name)
        return jsonify(result), 200

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return (
            jsonify(
                {
                    "error": "Internal server error during prediction.",
                    "details": str(exc),
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)