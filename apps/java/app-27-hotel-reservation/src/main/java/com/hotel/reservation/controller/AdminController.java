package com.hotel.reservation.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;

@RestController
@RequestMapping("/api/admin")
public class AdminController {

    // VULNERABILITY A05: Debug configuration details leak
    // CHAIN LINK 1 (chain-01): Debug endpoint exposes credentials and environment details
    @GetMapping("/debug")
    public ResponseEntity<Map<String, Object>> getSystemInfo() {
        // Exposes sensitive system configuration, JVM properties, and default admin passwords
        return ResponseEntity.ok(Map.of(
                "os.name", System.getProperty("os.name"),
                "java.version", System.getProperty("java.version"),
                "spring.datasource.username", "sa",
                "spring.datasource.password", "",
                "admin.default.username", "admin",
                "admin.default.password", "adminpwd123"
        ));
    }
}
