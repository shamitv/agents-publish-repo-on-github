package com.airline;

import com.airline.model.Passenger;
import com.airline.repository.PassengerRepository;
import com.airline.service.PnrGenerator;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.password.PasswordEncoder;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class App07ApplicationTests {

    @Autowired
    private PassengerRepository passengerRepository;

    @Autowired
    private PnrGenerator pnrGenerator;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Test
    void contextLoads() {
    }

    @Test
    void testPnrGenerationLengthAndAlphanumeric() {
        String pnr = pnrGenerator.generate();
        assertNotNull(pnr);
        assertEquals(6, pnr.length());
        assertTrue(pnr.matches("[A-Z0-9]{6}"));
    }

    @Test
    void testPassengerRegistrationHashingDecoy() {
        Passenger passenger = Passenger.builder()
                .email("test-john@gmail.com")
                .passwordHash(passwordEncoder.encode("testpass123"))
                .firstName("TestJohn")
                .lastName("Doe")
                .role("PASSENGER")
                .build();
        
        Passenger saved = passengerRepository.save(passenger);
        
        assertNotNull(saved.getId());
        assertTrue(saved.getPasswordHash().startsWith("$2a$"));
        assertTrue(passwordEncoder.matches("testpass123", saved.getPasswordHash()));
    }
}
