package com.fleet.mgmt.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
@RequestMapping("/api/integrations")
public class IntegrationController {

    private final RestTemplate restTemplate = new RestTemplate();

    // VULNERABILITY A10: SSRF in external vehicle fetching
    // CHAIN LINK 2 (chain-01): SSRF endpoint allows fetching cloud metadata or internal services
    @GetMapping("/vehicle-data")
    public ResponseEntity<String> fetchExternalVehicleData(@RequestParam String url) {
        // Direct server-side request execution on user-controlled URL without validation
        String response = restTemplate.getForObject(url, String.class);
        return ResponseEntity.ok(response);
    }
}
