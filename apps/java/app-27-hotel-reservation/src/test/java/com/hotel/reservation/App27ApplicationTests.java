package com.hotel.reservation;

import com.hotel.reservation.model.User;
import com.hotel.reservation.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.password.PasswordEncoder;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class App27ApplicationTests {

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
        testUser.setPassword(passwordEncoder.encode("supersecurepwd"));
        testUser.setRole("GUEST");
        
        User saved = userRepository.save(testUser);
        assertNotNull(saved.getId());
        assertTrue(saved.getPassword().startsWith("$2a$"));
        assertTrue(passwordEncoder.matches("supersecurepwd", saved.getPassword()));
    }
}
