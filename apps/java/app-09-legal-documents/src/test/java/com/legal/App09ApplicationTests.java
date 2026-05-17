package com.legal;

import com.legal.model.LegalCase;
import com.legal.repository.CaseRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class App09ApplicationTests {

    @Autowired
    private CaseRepository caseRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Test
    void contextLoads() {
    }

    @Test
    void testPreseededCasesCount() {
        List<LegalCase> cases = caseRepository.findAll();
        assertFalse(cases.isEmpty());
        assertTrue(cases.size() >= 4);
    }

    @Test
    void testPasswordBCryptSecureHashingDecoy() {
        String rawPass = "attorney123";
        String hashed = passwordEncoder.encode(rawPass);
        assertTrue(hashed.startsWith("$2a$"));
        assertTrue(passwordEncoder.matches(rawPass, hashed));
    }
}
