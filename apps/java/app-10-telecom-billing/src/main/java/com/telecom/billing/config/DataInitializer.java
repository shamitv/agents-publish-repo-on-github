package com.telecom.billing.config;

import com.telecom.billing.model.*;
import com.telecom.billing.repository.*;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import java.time.LocalDateTime;
import java.util.List;

@Component
public class DataInitializer implements CommandLineRunner {

    private final PlanRepository planRepository;
    private final CustomerRepository customerRepository;
    private final UsageRecordRepository usageRecordRepository;
    private final InvoiceRepository invoiceRepository;
    private final PasswordEncoder passwordEncoder;

    public DataInitializer(PlanRepository planRepository, CustomerRepository customerRepository,
                           UsageRecordRepository usageRecordRepository, InvoiceRepository invoiceRepository,
                           PasswordEncoder passwordEncoder) {
        this.planRepository = planRepository;
        this.customerRepository = customerRepository;
        this.usageRecordRepository = usageRecordRepository;
        this.invoiceRepository = invoiceRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) throws Exception {
        // Seed Plans
        Plan basic = planRepository.save(new Plan(null, "Basic Plan", 29.99, 10, 500));
        Plan premium = planRepository.save(new Plan(null, "Premium Plan", 59.99, 50, 2000));

        // Seed Customers
        Customer alice = new Customer(null, "Alice Smith", "alice@telecom.com", "555-0192", "alice",
                passwordEncoder.encode("alice123"), "CUSTOMER", basic.getId(), "ACTIVE", 0.0, LocalDateTime.now());
        customerRepository.save(alice);

        Customer admin = new Customer(null, "Admin Joe", "admin@telecom.com", "555-0100", "admin",
                passwordEncoder.encode("admin123"), "ADMIN", premium.getId(), "ACTIVE", 150.0, LocalDateTime.now());
        customerRepository.save(admin);

        // Seed Usage Records
        usageRecordRepository.save(new UsageRecord(null, alice.getId(), "DATA", 2.5, LocalDateTime.now().minusDays(5)));
        usageRecordRepository.save(new UsageRecord(null, alice.getId(), "VOICE", 45.0, LocalDateTime.now().minusDays(4)));
        usageRecordRepository.save(new UsageRecord(null, alice.getId(), "SMS", 12.0, LocalDateTime.now().minusDays(3)));

        // Seed Invoices
        invoiceRepository.save(new Invoice(null, alice.getId(), "2026-04", 29.99, "PENDING", LocalDateTime.now().minusDays(1)));
        invoiceRepository.save(new Invoice(null, alice.getId(), "2026-03", 29.99, "PAID", LocalDateTime.now().minusMonths(1)));
    }
}
