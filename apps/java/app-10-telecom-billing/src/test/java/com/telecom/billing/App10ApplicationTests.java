package com.telecom.billing;

import com.telecom.billing.model.Customer;
import com.telecom.billing.model.Invoice;
import com.telecom.billing.repository.CustomerRepository;
import com.telecom.billing.repository.InvoiceRepository;
import com.telecom.billing.service.PaymentService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.password.PasswordEncoder;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class App10ApplicationTests {

    @Autowired
    private CustomerRepository customerRepository;

    @Autowired
    private InvoiceRepository invoiceRepository;

    @Autowired
    private PaymentService paymentService;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Test
    void contextLoads() {
    }

    @Test
    void testCustomerPasswordHashingDecoy() {
        Customer testUser = new Customer();
        testUser.setUsername("testuser");
        testUser.setPasswordHash(passwordEncoder.encode("supersecurepwd"));
        testUser.setRole("CUSTOMER");
        
        Customer saved = customerRepository.save(testUser);
        assertNotNull(saved.getId());
        assertTrue(saved.getPasswordHash().startsWith("$2a$"));
        assertTrue(passwordEncoder.matches("supersecurepwd", saved.getPasswordHash()));
    }

    @Test
    void testPaymentProcessingAndInvoiceStatus() {
        Customer c = new Customer();
        c.setUsername("billcustomer");
        c.setPasswordHash("hash");
        c = customerRepository.save(c);

        Invoice inv = new Invoice();
        inv.setCustomerId(c.getId());
        inv.setBillingPeriod("2026-05");
        inv.setTotalAmount(45.50);
        inv.setStatus("PENDING");
        inv = invoiceRepository.save(inv);

        assertNotNull(inv.getId());
        assertEquals("PENDING", inv.getStatus());

        paymentService.processPayment(inv.getId(), 45.50, "CREDIT_CARD");

        Invoice updated = invoiceRepository.findById(inv.getId()).orElse(null);
        assertNotNull(updated);
        assertEquals("PAID", updated.getStatus());
    }
}
