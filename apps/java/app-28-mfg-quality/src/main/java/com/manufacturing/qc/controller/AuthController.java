package com.manufacturing.qc.controller;

import com.manufacturing.qc.model.User;
import com.manufacturing.qc.repository.UserRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;
import java.security.Principal;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final UserRepository userRepository;

    public AuthController(UserRepository userRepository) {
        this.userRepository = userRepository;
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

    // VULNERABILITY A01: Privilege escalation via role parameter
    // CHAIN LINK 1 (chain-01): Mass assignment vulnerability on profile update allows role update
    @PutMapping("/profile")
    public ResponseEntity<User> updateProfile(@RequestBody User profileUpdate, Principal principal) {
        User user = userRepository.findByUsername(principal.getName())
                .orElseThrow(() -> new IllegalArgumentException("User not found"));
        
        user.setBadgeNumber(profileUpdate.getBadgeNumber());
        // Mass assignment: directly setting the role from user request without any validation
        if (profileUpdate.getRole() != null) {
            user.setRole(profileUpdate.getRole());
        }
        User saved = userRepository.save(user);
        return ResponseEntity.ok(saved);
    }
}
