package fr.uha.ensisa.ecg;

import java.util.List;
import java.util.Map;

import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
@CrossOrigin(origins = "*")
public class EcgController {

    private final PythonInferenceService pythonInferenceService;

    public EcgController(PythonInferenceService pythonInferenceService) {
        this.pythonInferenceService = pythonInferenceService;
    }

    // Page d'accueil
    @GetMapping("/")
    public Resource home() {
        return new ClassPathResource("static/index.html");
    }

    // Health check
    @GetMapping("/api/ecg/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of(
                "status", "ok",
                "service", "ecg-classification-app"
        ));
    }

    // Configuration (REQUIS PAR LE PROJET)
    @GetMapping("/config")
    public ResponseEntity<Map<String, Object>> config() {
        return ResponseEntity.ok(Map.of(
                "models", List.of("mlp", "cnn", "lstm"),
                "input_size", 96
        ));
    }

    // Classification ECG
    @PostMapping("/api/ecg/classify")
    public ResponseEntity<?> classify(@RequestBody Map<String, Object> payload) {
        try {
            String model = (String) payload.get("model");
            List<Double> signal = (List<Double>) payload.get("signal");

            // Validation inputs
            if (model == null || model.isBlank()) {
                return ResponseEntity.badRequest().body(Map.of(
                        "error", "Field 'model' is required."
                ));
            }

            if (signal == null || signal.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of(
                        "error", "Field 'signal' is required and must not be empty."
                ));
            }

            if (signal.size() != 96) {
                return ResponseEntity.badRequest().body(Map.of(
                        "error", "Signal must contain exactly 96 values."
                ));
            }

            // Appel au service Python
            Map<String, Object> result = pythonInferenceService.predict(model, signal);

            // Si erreur venant de Python
            if (result.containsKey("error")) {
                return ResponseEntity.status(500).body(result);
            }

            return ResponseEntity.ok(result);

        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of(
                    "error", "Unexpected error in classification.",
                    "details", e.getMessage()
            ));
        }
    }
}