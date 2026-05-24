package com.energy.billing.config;

import com.energy.billing.model.*;
import com.energy.billing.repository.*;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Component
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;
    private final CustomerRepository customerRepository;
    private final MeterRepository meterRepository;
    private final MeterReadingRepository meterReadingRepository;
    private final TariffRepository tariffRepository;
    private final InvoiceRepository invoiceRepository;
    private final PasswordEncoder passwordEncoder;

    public DataInitializer(UserRepository userRepository, CustomerRepository customerRepository,
                           MeterRepository meterRepository, MeterReadingRepository meterReadingRepository,
                           TariffRepository tariffRepository, InvoiceRepository invoiceRepository,
                           PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.customerRepository = customerRepository;
        this.meterRepository = meterRepository;
        this.meterReadingRepository = meterReadingRepository;
        this.tariffRepository = tariffRepository;
        this.invoiceRepository = invoiceRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) throws Exception {
        // Seed Customers
        Customer c1 = customerRepository.save(new Customer(null, "ACC-0912", "John Energy", "john@energy.com", "123 Volt Street", "RESIDENTIAL", "ACTIVE"));

        // Seed Users
        userRepository.save(new User(null, "customer", passwordEncoder.encode("cust123"), "CUSTOMER", c1.getId()));
        userRepository.save(new User(null, "billingadmin", passwordEncoder.encode("billing123"), "BILLING_ADMIN", null));

        // Seed Meters
        Meter m1 = meterRepository.save(new Meter(null, c1.getId(), "MTR-E-9901", "ELECTRIC", LocalDate.now().minusYears(1), LocalDate.now().minusDays(5)));

        // Seed Meter Readings
        meterReadingRepository.save(new MeterReading(null, m1.getId(), 1250.5, LocalDate.now().minusMonths(1), "technician", "MANUAL"));

        // Seed Tariffs
        tariffRepository.save(new Tariff(null, "RESIDENTIAL", 1, 0.12, LocalDate.now().minusYears(1), LocalDate.now().plusYears(1)));

        // Seed Invoices
        invoiceRepository.save(new Invoice(null, c1.getId(), "2026-04", 320.0, 38.40, "SENT", LocalDateTime.now().minusDays(2)));
    }
}
