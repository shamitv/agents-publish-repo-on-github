package com.energy.billing;

import com.energy.billing.model.User;
import com.energy.billing.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.password.PasswordEncoder;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class App50ApplicationTests {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Test
    void contextLoads() {
    }

    @Test
    void testUserPasswordHashingDecoy() {
        User testUser = new User();
        testUser.setUsername("testuser");
        testUser.setPasswordHash(passwordEncoder.encode("supersecurepwd"));
        testUser.setRole("CUSTOMER");
        
        User saved = userRepository.save(testUser);
        assertNotNull(saved.getId());
        assertTrue(saved.getPasswordHash().startsWith("$2a$"));
        assertTrue(passwordEncoder.matches("supersecurepwd", saved.getPasswordHash()));
    }
}
