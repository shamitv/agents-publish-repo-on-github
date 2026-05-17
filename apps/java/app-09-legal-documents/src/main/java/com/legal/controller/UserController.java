package com.legal.controller;

import com.legal.model.User;
import com.legal.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserRepository userRepository;

    @GetMapping("/me")
    public ResponseEntity<?> getProfile(@AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(401).body("Unauthenticated");
        }
        
        return userRepository.findByUsername(userDetails.getUsername())
                .map(user -> {
                    Map<String, Object> profile = new HashMap<>();
                    profile.put("username", user.getUsername());
                    profile.put("role", user.getRole());
                    return ResponseEntity.ok(profile);
                })
                .orElse(ResponseEntity.status(401).build());
    }
}
