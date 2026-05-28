package com.hr.controller;

import com.hr.model.OnboardingRequest;
import com.hr.model.OnboardingState;
import com.hr.service.OnboardingWorkflowService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/onboarding")
public class OnboardingController {

    @Autowired
    private OnboardingWorkflowService onboardingWorkflowService;

    @PostMapping
    @PreAuthorize("hasRole('HR_ADMIN')")
    public ResponseEntity<OnboardingRequest> createOnboarding(@RequestBody Map<String, Object> payload) {
        Long employeeId = Long.valueOf(payload.get("employeeId").toString());
        String requestedBy = (String) payload.get("requestedBy");
        OnboardingRequest request = onboardingWorkflowService.createOnboarding(employeeId, requestedBy);
        return ResponseEntity.ok(request);
    }

    @GetMapping("/{id}")
    @PreAuthorize("hasRole('HR_ADMIN')")
    public ResponseEntity<OnboardingRequest> getOnboarding(@PathVariable Long id) {
        return onboardingWorkflowService.getOnboarding(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PutMapping("/{id}/transition")
    @PreAuthorize("hasRole('HR_ADMIN')")
    public ResponseEntity<?> transitionState(@PathVariable Long id, @RequestBody Map<String, Object> payload) {
        String targetStateStr = (String) payload.get("targetState");
        OnboardingState targetState = OnboardingState.fromString(targetStateStr);
        OnboardingRequest request = onboardingWorkflowService.transition(id, targetState);
        return ResponseEntity.ok(request);
    }

    @GetMapping
    @PreAuthorize("hasRole('HR_ADMIN')")
    public ResponseEntity<List<OnboardingRequest>> listOnboarding(@AuthenticationPrincipal UserDetails userDetails) {
        List<OnboardingRequest> requests = onboardingWorkflowService.listOnboardingByRequestedBy(userDetails.getUsername());
        return ResponseEntity.ok(requests);
    }
}
