package com.hr;

import com.hr.model.Employee;
import com.hr.service.EmployeeService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import java.math.BigDecimal;
import java.util.Optional;
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
}
