package com.telecom.billing.controller;

import com.telecom.billing.model.Customer;
import com.telecom.billing.repository.CustomerRepository;
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

    public CustomerController(CustomerRepository customerRepository) {
        this.customerRepository = customerRepository;
    }

    @GetMapping("/{id}")
    public ResponseEntity<Customer> getCustomer(@PathVariable Long id, Principal principal) {
        Customer customer = customerRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Customer not found"));
        
        // DECOY: Normal endpoints enforce that users can only access their own profile details
        if (!customer.getUsername().equals(principal.getName()) && !principal.getName().equals("admin")) {
            return ResponseEntity.status(403).build();
        }
        return ResponseEntity.ok(customer);
    }
}
