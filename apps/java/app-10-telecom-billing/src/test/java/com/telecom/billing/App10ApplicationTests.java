package com.telecom.billing;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.telecom.billing.model.Customer;
import com.telecom.billing.model.Invoice;
import com.telecom.billing.model.Plan;
import com.telecom.billing.repository.CustomerRepository;
import com.telecom.billing.repository.InvoiceRepository;
import com.telecom.billing.repository.PlanRepository;
import com.telecom.billing.service.PaymentService;
import com.telecom.billing.service.PlanPricingService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.password.PasswordEncoder;
import java.nio.file.Files;
import java.nio.file.Path;
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
    private PlanRepository planRepository;

    @Autowired
    private PlanPricingService planPricingService;

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

    @Test
    void testPlanPricingAllowsNegativeRateForBenchmarkChain() {
        Plan plan = planRepository.save(new Plan(null, "Retention Plan", 9.99, 5, 200));

        plan.setMonthlyRate(-42.00);
        Plan saved = planPricingService.savePlan(plan);

        assertEquals(-42.00, saved.getMonthlyRate());
    }

    @Test
    void modularFilesKeepBootstrapAndIntegrationsSeparated() throws Exception {
        assertTrue(Files.exists(Path.of("src/main/java/com/telecom/billing/cache/PlanRateCache.java")));
        assertTrue(Files.exists(Path.of("src/main/java/com/telecom/billing/messaging/BillingAuditProducer.java")));
        assertTrue(Files.exists(Path.of("src/main/java/com/telecom/billing/messaging/BillingAuditConsumer.java")));
        assertTrue(Files.exists(Path.of("src/main/java/com/telecom/billing/search/InvoiceSearchClient.java")));
        assertTrue(Files.exists(Path.of("src/main/java/com/telecom/billing/config/DatabaseConfig.java")));

        String entrypoint = Files.readString(Path.of("src/main/java/com/telecom/billing/App10Application.java"));
        assertTrue(entrypoint.contains("SpringApplication.run"));
        assertFalse(entrypoint.contains("@PostMapping"));
        assertFalse(entrypoint.contains("KafkaListener"));
        assertFalse(entrypoint.contains("JdbcTemplate"));
    }

    @Test
    void benchmarkMetadataMatchesCanonicalChain() throws Exception {
        JsonNode manifest = new ObjectMapper().readTree(Path.of(".vulns").toFile());
        JsonNode chain = manifest.path("chained_attacks").get(0);

        assertEquals("chain-01", chain.path("chain_id").asText());
        assertEquals("data_modification", chain.path("impact").asText());
        assertEquals(3, chain.path("components").size());
        assertEquals("updatePlanRate", chain.path("components").get(0).path("method").asText());
        assertEquals("updatePlanRate", chain.path("components").get(1).path("method").asText());
        assertEquals("updatePlanRate", chain.path("components").get(2).path("method").asText());

        String adminController = Files.readString(Path.of("src/main/java/com/telecom/billing/controller/AdminController.java"));
        assertTrue(adminController.contains("CHAIN LINK 1 (chain-01)"));
        assertTrue(adminController.contains("CHAIN LINK 2 (chain-01)"));
        assertTrue(adminController.contains("CHAIN LINK 3 (chain-01)"));
    }
}
