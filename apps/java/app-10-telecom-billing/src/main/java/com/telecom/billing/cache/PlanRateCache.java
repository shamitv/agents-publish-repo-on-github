package com.telecom.billing.cache;

import com.telecom.billing.model.Plan;
import org.springframework.stereotype.Component;

import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

@Component
public class PlanRateCache {
    private final ConcurrentMap<Long, Plan> plans = new ConcurrentHashMap<>();

    public Optional<Plan> get(Long planId) {
        return Optional.ofNullable(plans.get(planId));
    }

    public void put(Plan plan) {
        if (plan.getId() != null) {
            plans.put(plan.getId(), plan);
        }
    }

    public void evict(Long planId) {
        plans.remove(planId);
    }
}
