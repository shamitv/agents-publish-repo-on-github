package com.manufacturing.qc.config;

import com.manufacturing.qc.model.*;
import com.manufacturing.qc.repository.*;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import java.time.LocalDateTime;

@Component
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;
    private final ProductRepository productRepository;
    private final InspectionRepository inspectionRepository;
    private final DefectRepository defectRepository;
    private final PasswordEncoder passwordEncoder;

    public DataInitializer(UserRepository userRepository, ProductRepository productRepository,
                           InspectionRepository inspectionRepository, DefectRepository defectRepository,
                           PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.productRepository = productRepository;
        this.inspectionRepository = inspectionRepository;
        this.defectRepository = defectRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) throws Exception {
        // Seed Users
        userRepository.save(new User(null, "worker", passwordEncoder.encode("worker123"), "WORKER", "B-101"));
        userRepository.save(new User(null, "inspector", passwordEncoder.encode("inspect123"), "INSPECTOR", "B-202"));
        userRepository.save(new User(null, "manager", passwordEncoder.encode("manager123"), "QA_MANAGER", "B-303"));

        // Seed Products
        Product p1 = productRepository.save(new Product(null, "SKU-ENG01", "Engine Block A1", "Line 1", "Automotive", "{\"weight\": \"150kg\"}"));
        Product p2 = productRepository.save(new Product(null, "SKU-ENG02", "Transmission Shaft S2", "Line 2", "Automotive", "{\"tolerance\": \"0.02mm\"}"));

        // Seed Inspections
        Inspection i1 = inspectionRepository.save(new Inspection(null, p1.getId(), 2L, "FAIL", "Cracks detected in casting", LocalDateTime.now().minusDays(1)));

        // Seed Defects
        defectRepository.save(new Defect(null, i1.getId(), "Structural Integrity", "CRITICAL", "Casting cracks in engine block", "OPEN"));
    }
}
