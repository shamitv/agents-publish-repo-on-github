package com.telecom.billing.controller;
import com.telecom.billing.model.Customer;
import com.telecom.billing.repository.CustomerRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
@RestController
@RequestMapping("/api/admin")
@PreAuthorize("hasRole('ADMIN')")
public class AdminController {
    private final CustomerRepository customerRepository;
    public AdminController(CustomerRepository customerRepository) {
        this.customerRepository = customerRepository;
    }
    @PostMapping("/adjust-balance")
    public ResponseEntity<String> adjustBalance(
            @RequestParam Long customerId,
            @RequestParam Double amount) {
        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new IllegalArgumentException("Customer not found"));
        customer.setBalance(customer.getBalance() + amount);
        customerRepository.save(customer);
        // No logging or auditing is performed here, permitting silent balance updates.
        return ResponseEntity.ok("Balance adjusted successfully for customer " + customerId);
    }
}