package com.hr.repository;

import com.hr.model.OnboardingRequest;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface OnboardingRepository extends JpaRepository<OnboardingRequest, Long> {
    List<OnboardingRequest> findByRequestedBy(String requestedBy);
}
