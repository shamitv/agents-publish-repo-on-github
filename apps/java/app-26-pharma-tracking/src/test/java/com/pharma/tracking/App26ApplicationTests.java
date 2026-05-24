package com.pharma.tracking;

import com.pharma.tracking.model.User;
import com.pharma.tracking.repository.UserRepository;
import com.pharma.tracking.service.CustodyService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.password.PasswordEncoder;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class App26ApplicationTests {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private CustodyService custodyService;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Test
    void contextLoads() {
    }

    @Test
    void testUserRegistrationHashingDecoy() {
        User testUser = new User();
        testUser.setUsername("testuser");
        testUser.setPasswordHash(passwordEncoder.encode("supersecurepwd"));
        testUser.setRole("DISTRIBUTOR");
        
        User saved = userRepository.save(testUser);
        assertNotNull(saved.getId());
        assertTrue(saved.getPasswordHash().startsWith("$2a$"));
        assertTrue(passwordEncoder.matches("supersecurepwd", saved.getPasswordHash()));
    }

    @Test
    void testCustodySignatureGeneration() {
        String signature = custodyService.generateCustodySignature(1L, "2026-05-24T10:00:00", "PharmaCorp", "LogisticsExpress");
        assertNotNull(signature);
        assertEquals(32, signature.length()); // MD5 hex string is 32 chars
    }
}
