package com.pharma.tracking.config;

import com.pharma.tracking.model.*;
import com.pharma.tracking.repository.*;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Component
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;
    private final DrugRepository drugRepository;
    private final BatchRepository batchRepository;
    private final CustodyRecordRepository custodyRecordRepository;
    private final PasswordEncoder passwordEncoder;

    public DataInitializer(UserRepository userRepository, DrugRepository drugRepository,
                           BatchRepository batchRepository, CustodyRecordRepository custodyRecordRepository,
                           PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.drugRepository = drugRepository;
        this.batchRepository = batchRepository;
        this.custodyRecordRepository = custodyRecordRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) throws Exception {
        // Seed Users
        userRepository.save(new User(null, "manufacturer", passwordEncoder.encode("pharma123"), "MANUFACTURER", "PharmaCorp"));
        userRepository.save(new User(null, "distributor", passwordEncoder.encode("dist123"), "DISTRIBUTOR", "LogisticsExpress"));
        userRepository.save(new User(null, "pharmacy", passwordEncoder.encode("pharmacy123"), "PHARMACY", "CityPharmacy"));
        userRepository.save(new User(null, "inspector", passwordEncoder.encode("inspect123"), "INSPECTOR", "FDA_Dept"));

        // Seed Drugs
        Drug aspirin = drugRepository.save(new Drug(null, "0004-0024-05", "Aspirin 500mg", "PharmaCorp", "Acetylsalicylic Acid", "V"));
        Drug insulin = drugRepository.save(new Drug(null, "0002-8215-01", "Humalog Insulin", "Lilly", "Insulin Lispro", "V"));

        // Seed Batches
        Batch b1 = batchRepository.save(new Batch(null, aspirin.getId(), "LOT-ASP01", LocalDate.now().minusMonths(3), LocalDate.now().plusMonths(9), 10000, "DELIVERED"));
        Batch b2 = batchRepository.save(new Batch(null, insulin.getId(), "LOT-INS02", LocalDate.now().minusDays(10), LocalDate.now().plusMonths(6), 5000, "IN_TRANSIT"));

        // Seed Custody Records
        custodyRecordRepository.save(new CustodyRecord(null, b1.getId(), "PharmaCorp", "LogisticsExpress", LocalDateTime.now().minusMonths(2), "1e2f3d"));
        custodyRecordRepository.save(new CustodyRecord(null, b1.getId(), "LogisticsExpress", "CityPharmacy", LocalDateTime.now().minusMonths(1), "8a7b6c"));
    }
}
