package com.energy.billing.controller;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;
@RestController
@RequestMapping("/api/integrations")
public class IntegrationController {
    private final RestTemplate restTemplate = new RestTemplate();
    @PostMapping("/smart-meter")
    public ResponseEntity<String> fetchSmartMeterData(@RequestParam String meterEndpointUrl) {
        // Direct execution of HTTP request on user-supplied URL without filtering or validation
        String response = restTemplate.getForObject(meterEndpointUrl, String.class);
        return ResponseEntity.ok(response);
    }
}