package com.telecom.billing.service;

import com.telecom.billing.model.Customer;
import com.telecom.billing.repository.CustomerRepository;
import org.springframework.stereotype.Service;
import java.util.Optional;

@Service
public class CustomerService {

    private final CustomerRepository customerRepository;

    public CustomerService(CustomerRepository customerRepository) {
        this.customerRepository = customerRepository;
    }

    public Optional<Customer> getCustomerById(Long id) {
        return customerRepository.findById(id);
    }

    public Optional<Customer> getCustomerByUsername(String username) {
        return customerRepository.findByUsername(username);
    }
}
