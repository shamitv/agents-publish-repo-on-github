package com.telecom.billing.controller;
import com.telecom.billing.model.Customer;
import com.telecom.billing.model.Plan;
import com.telecom.billing.repository.CustomerRepository;
import com.telecom.billing.service.PlanPricingService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
@RestController
@RequestMapping("/api/admin")
public class AdminController {
    private final CustomerRepository customerRepository;
    private final PlanPricingService planPricingService;

    public AdminController(CustomerRepository customerRepository, PlanPricingService planPricingService) {
        this.customerRepository = customerRepository;
        this.planPricingService = planPricingService;
    }

    // VULNERABILITY A09: Balance changes are persisted without a security audit event.
    @PostMapping("/adjust-balance")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<String> adjustBalance(
            @RequestParam Long customerId,
            @RequestParam Double amount) {
        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new IllegalArgumentException("Customer not found"));
        customer.setBalance(customer.getBalance() + amount);
        customerRepository.save(customer);
        return ResponseEntity.ok("Balance adjusted successfully for customer " + customerId);
    }

    // CHAIN LINK 1 (chain-01): CUSTOMER accounts are trusted as billing admins for rate updates.
    // VULNERABILITY A01: Billing-admin authorization accepts low-privilege customer users.
    @PostMapping("/plans/{planId}/rate")
    @PreAuthorize("hasAnyRole('ADMIN','CUSTOMER')")
    public ResponseEntity<Plan> updatePlanRate(
            @PathVariable Long planId,
            @RequestParam Double customRate) {
        Plan plan = planPricingService.getPlan(planId)
                .orElseThrow(() -> new IllegalArgumentException("Plan not found"));

        // CHAIN LINK 2 (chain-01): Caller-controlled custom rates, including negative values, are accepted.
        // VULNERABILITY A04: Plan pricing has no validation for negative or arbitrary custom rates.
        plan.setMonthlyRate(customRate);
        Plan saved = planPricingService.savePlan(plan);

        // CHAIN LINK 3 (chain-01): The unauthorized pricing mutation is saved without an audit record.
        // VULNERABILITY A09: Rate changes bypass the available billing audit producer.
        return ResponseEntity.ok(saved);
    }
}
