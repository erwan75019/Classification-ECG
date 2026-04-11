package fr.uha.ensisa.ecg;

import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class PythonInferenceService {

    private final RestTemplate restTemplate;
    private static final String PYTHON_API_URL = "http://ecg-inference-service:5000/predict";

    public PythonInferenceService() {
        this.restTemplate = new RestTemplate();
    }

    public Map<String, Object> predict(String model, List<Double> signal) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("model", model);
        requestBody.put("signal", signal);

        HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestBody, headers);

        try {
            ResponseEntity<Map> response = restTemplate.postForEntity(
                    PYTHON_API_URL,
                    requestEntity,
                    Map.class
            );
            return response.getBody();
        } catch (HttpStatusCodeException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Python service returned an error");
            error.put("status", e.getStatusCode().value());
            error.put("details", e.getResponseBodyAsString());
            return error;
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Unable to reach Python inference service");
            error.put("details", e.getMessage());
            return error;
        }
    }
}