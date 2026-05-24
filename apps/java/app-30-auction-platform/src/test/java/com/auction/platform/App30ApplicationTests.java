package com.auction.platform;

import com.auction.platform.model.User;
import com.auction.platform.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class App30ApplicationTests {

    @Autowired
    private UserRepository userRepository;

    @Test
    void contextLoads() {
    }

    @Test
    void testUserPlaintextPasswordDecoy() {
        User testUser = new User();
        testUser.setUsername("testuser");
        testUser.setPassword("plainpwd123");
        testUser.setRole("BUYER");
        
        User saved = userRepository.save(testUser);
        assertNotNull(saved.getId());
        assertEquals("plainpwd123", saved.getPassword());
    }
}
