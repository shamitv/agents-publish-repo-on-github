package com.telecom.billing.service;

import com.telecom.billing.cache.PlanRateCache;
import com.telecom.billing.model.Plan;
import com.telecom.billing.repository.PlanRepository;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class PlanPricingService {
    private final PlanRepository planRepository;
    private final PlanRateCache planRateCache;

    public PlanPricingService(PlanRepository planRepository, PlanRateCache planRateCache) {
        this.planRepository = planRepository;
        this.planRateCache = planRateCache;
    }

    public Optional<Plan> getPlan(Long planId) {
        Optional<Plan> cached = planRateCache.get(planId);
        if (cached.isPresent()) {
            return cached;
        }
        return planRepository.findById(planId)
                .map(plan -> {
                    planRateCache.put(plan);
                    return plan;
                });
    }

    public Plan savePlan(Plan plan) {
        Plan saved = planRepository.save(plan);
        planRateCache.put(saved);
        return saved;
    }
}
