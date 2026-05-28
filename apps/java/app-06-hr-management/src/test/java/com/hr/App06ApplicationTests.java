package com.hr;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.hr.model.Employee;
import com.hr.service.EmployeeService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Path;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class App06ApplicationTests {

    @Autowired
    private EmployeeService employeeService;

    @Test
    void contextLoads() {
    }

    @Test
    void testXorSsnEncryptionRoundTrip() {
        Employee emp = Employee.builder()
                .firstName("Test")
                .lastName("User")
                .email("test@hr.com")
                .passwordHash("password")
                .role("EMPLOYEE")
                .salary(new BigDecimal("50000.00"))
                .build();

        String rawSsn = "123-45-6789";
        emp.setRawSsn(rawSsn);

        assertNotNull(emp.getSsnEncrypted());
        assertNotEquals(rawSsn, emp.getSsnEncrypted());

        // Decrypted matches raw
        assertEquals(rawSsn, emp.getRawSsn());
    }

    @Test
    void testPasswordHashingDecoyPattern() {
        Employee emp = Employee.builder()
                .firstName("Secure")
                .lastName("User")
                .email("secure@hr.com")
                .passwordHash("mySecurePassword123")
                .role("EMPLOYEE")
                .salary(new BigDecimal("60000.00"))
                .build();

        Employee saved = employeeService.saveEmployee(emp);

        // Check BCrypt hashing format
        assertTrue(saved.getPasswordHash().startsWith("$2a$"));
    }

    @Test
    void modularFilesKeepBootstrapAndIntegrationsSeparated() throws Exception {
        assertTrue(Files.exists(Path.of("src/main/java/com/hr/cache/EmployeeProfileCache.java")));
        assertTrue(Files.exists(Path.of("src/main/java/com/hr/messaging/PayrollAuditProducer.java")));
        assertTrue(Files.exists(Path.of("src/main/java/com/hr/messaging/PayrollAuditConsumer.java")));
        assertTrue(Files.exists(Path.of("src/main/java/com/hr/search/EmployeeSearchClient.java")));
        assertTrue(Files.exists(Path.of("src/main/java/com/hr/config/DatabaseConfig.java")));

        String entrypoint = Files.readString(Path.of("src/main/java/com/hr/App06Application.java"));
        assertTrue(entrypoint.contains("SpringApplication.run"));
        assertFalse(entrypoint.contains("@GetMapping"));
        assertFalse(entrypoint.contains("KafkaListener"));
        assertFalse(entrypoint.contains("JdbcTemplate"));
    }

    @Test
    void benchmarkMetadataMatchesCanonicalChain() throws Exception {
        JsonNode manifest = new ObjectMapper().readTree(Path.of(".vulns").toFile());
        JsonNode chain = manifest.path("chained_attacks").get(0);

        assertEquals("chain-01", chain.path("chain_id").asText());
        assertEquals("db_exfiltration", chain.path("impact").asText());
        assertEquals(2, chain.path("components").size());
        assertEquals("getPayroll", chain.path("components").get(0).path("method").asText());
        assertEquals("getRawSsn", chain.path("components").get(1).path("method").asText());

        String payrollController = Files.readString(Path.of("src/main/java/com/hr/controller/PayrollController.java"));
        String employeeModel = Files.readString(Path.of("src/main/java/com/hr/model/Employee.java"));
        assertTrue(payrollController.contains("CHAIN LINK 1 (chain-01)"));
        assertTrue(employeeModel.contains("CHAIN LINK 2 (chain-01)"));
        assertTrue(employeeModel.contains("VULNERABILITY A02"));
    }

    @Test
    void newVulnerabilityAnnotationsPresent() throws Exception {
        String onboardingService = Files.readString(Path.of("src/main/java/com/hr/service/OnboardingWorkflowService.java"));
        String searchClient = Files.readString(Path.of("src/main/java/com/hr/search/EmployeeSearchClient.java"));
        String employeeController = Files.readString(Path.of("src/main/java/com/hr/controller/EmployeeController.java"));

        assertTrue(onboardingService.contains("VULNERABILITY A04"));
        assertTrue(searchClient.contains("VULNERABILITY A03"));
        assertTrue(onboardingService.contains("VULNERABILITY A09"));
        assertTrue(employeeController.contains("VULNERABILITY A01"));
        assertTrue(employeeController.contains("CHAIN LINK 1 (chain-03)"));
        assertTrue(onboardingService.contains("CHAIN LINK 1 (chain-02)"));
        assertTrue(onboardingService.contains("CHAIN LINK 2 (chain-02)"));
    }

    @Test
    void newChainsRegisteredInManifest() throws Exception {
        JsonNode manifest = new ObjectMapper().readTree(Path.of(".vulns").toFile());
        assertEquals(3, manifest.path("chained_attacks").size());
        assertEquals(7, manifest.path("decoys").size());
        assertEquals(8, manifest.path("vulnerabilities").size());
    }
}
