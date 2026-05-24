package com.telecom.billing.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(401).body(Map.of("message", "Authentication failed"));
        }
        return ResponseEntity.ok(Map.of(
                "username", userDetails.getUsername(),
                "roles", userDetails.getAuthorities()
        ));
    }

    @GetMapping("/me")
    public ResponseEntity<Map<String, Object>> me(@AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(401).body(Map.of("message", "Not logged in"));
        }
        return ResponseEntity.ok(Map.of(
                "username", userDetails.getUsername(),
                "roles", userDetails.getAuthorities()
        ));
    }
}
