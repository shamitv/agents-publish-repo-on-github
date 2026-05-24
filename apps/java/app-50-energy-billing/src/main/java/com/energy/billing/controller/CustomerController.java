package com.energy.billing.controller;

import com.energy.billing.model.Customer;
import com.energy.billing.repository.CustomerRepository;
import com.energy.billing.repository.UserRepository;
import com.energy.billing.model.User;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.security.Principal;

@RestController
@RequestMapping("/api/customers")
public class CustomerController {

    private final CustomerRepository customerRepository;
    private final UserRepository userRepository;

    public CustomerController(CustomerRepository customerRepository, UserRepository userRepository) {
        this.customerRepository = customerRepository;
        this.userRepository = userRepository;
    }

    @GetMapping("/{id}")
    public ResponseEntity<Customer> getCustomer(@PathVariable Long id, Principal principal) {
        Customer customer = customerRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Customer not found"));

        User currentUser = userRepository.findByUsername(principal.getName())
                .orElseThrow(() -> new IllegalArgumentException("User not found"));

        // DECOY: Normal access control check verifies that customers can only view their own account profile
        if ("CUSTOMER".equals(currentUser.getRole()) && !id.equals(currentUser.getCustomerId())) {
            return ResponseEntity.status(403).build();
        }
        return ResponseEntity.ok(customer);
    }
}
