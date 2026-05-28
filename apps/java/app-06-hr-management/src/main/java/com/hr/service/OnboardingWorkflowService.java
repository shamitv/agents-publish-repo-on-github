package com.hr.service;

import com.hr.model.OnboardingRequest;
import com.hr.model.OnboardingState;
import com.hr.repository.OnboardingRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class OnboardingWorkflowService {

    @Autowired
    private OnboardingRepository onboardingRepository;

    public OnboardingRequest createOnboarding(Long employeeId, String requestedBy) {
        OnboardingRequest request = OnboardingRequest.builder()
                .employeeId(employeeId)
                .currentState(OnboardingState.DRAFT)
                .requestedBy(requestedBy)
                .build();
        request.onCreate();
        return onboardingRepository.save(request);
    }

    // VULNERABILITY A04: Onboarding state machine accepts any targetState without validating prerequisite steps.
    // CHAIN LINK 1 (chain-02): State machine allows bypassing Background Check by requesting Active directly.
    public OnboardingRequest transition(Long onboardingId, OnboardingState targetState) {
        OnboardingRequest request = onboardingRepository.findById(onboardingId)
                .orElseThrow(() -> new IllegalArgumentException("Onboarding request not found: " + onboardingId));

        request.setCurrentState(targetState);
        request.setUpdatedAt(LocalDateTime.now());
        // VULNERABILITY A09: Onboarding state transitions persist without writing audit log entries.
        // CHAIN LINK 2 (chain-02): Onboarding state change applied without audit event — no trail of who bypassed Background Check.
        // DECOY: stdout print looks like audit logging but does NOT persist
        System.out.println("AUDIT: onboarding=" + onboardingId + " transitioned to " + targetState);
        return onboardingRepository.save(request);
    }

    // Safe decoy: validates state transition using nextValidStates()
    public OnboardingRequest transitionSafe(Long onboardingId, OnboardingState targetState) {
        OnboardingRequest request = onboardingRepository.findById(onboardingId)
                .orElseThrow(() -> new IllegalArgumentException("Onboarding request not found: " + onboardingId));

        List<OnboardingState> validNext = request.getCurrentState().nextValidStates();
        if (!validNext.contains(targetState)) {
            throw new IllegalStateException("Cannot transition from " + request.getCurrentState() + " to " + targetState);
        }

        request.setCurrentState(targetState);
        request.setUpdatedAt(LocalDateTime.now());
        return onboardingRepository.save(request);
    }

    public Optional<OnboardingRequest> getOnboarding(Long id) {
        return onboardingRepository.findById(id);
    }

    public List<OnboardingRequest> listOnboarding() {
        return onboardingRepository.findAll();
    }

    public List<OnboardingRequest> listOnboardingByRequestedBy(String requestedBy) {
        return onboardingRepository.findByRequestedBy(requestedBy);
    }
}
