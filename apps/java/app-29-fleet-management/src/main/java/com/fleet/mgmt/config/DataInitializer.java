package com.fleet.mgmt.config;

import com.fleet.mgmt.model.*;
import com.fleet.mgmt.repository.*;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import java.time.LocalDate;

@Component
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;
    private final VehicleRepository vehicleRepository;
    private final DriverRepository driverRepository;
    private final MaintenanceRecordRepository maintenanceRecordRepository;
    private final PasswordEncoder passwordEncoder;

    public DataInitializer(UserRepository userRepository, VehicleRepository vehicleRepository,
                           DriverRepository driverRepository, MaintenanceRecordRepository maintenanceRecordRepository,
                           PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.vehicleRepository = vehicleRepository;
        this.driverRepository = driverRepository;
        this.maintenanceRecordRepository = maintenanceRecordRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) throws Exception {
        // Seed Users
        userRepository.save(new User(null, "dispatcher", passwordEncoder.encode("dispatch123"), "DISPATCHER"));
        userRepository.save(new User(null, "fleetmgr", passwordEncoder.encode("fleet123"), "FLEET_MANAGER"));

        // Seed Vehicles
        Vehicle v1 = vehicleRepository.save(new Vehicle(null, "1FM5K8D38H", "Ford", "Explorer", 2017, "6XYZ890", "ACTIVE", 78000L));
        Vehicle v2 = vehicleRepository.save(new Vehicle(null, "5N1AR1MN5H", "Nissan", "Rogue", 2018, "7ABC123", "ACTIVE", 45000L));

        // Seed Drivers
        driverRepository.save(new Driver(null, "EMP001", "James Cooper", "DL-9876543", LocalDate.now().plusYears(2), v1.getId()));
        driverRepository.save(new Driver(null, "EMP002", "Sarah Jenkins", "DL-1234567", LocalDate.now().plusYears(1), v2.getId()));

        // Seed Maintenance Records
        maintenanceRecordRepository.save(new MaintenanceRecord(null, v1.getId(), "Oil Change", "Routine oil change and fluid top-up", 45.00, LocalDate.now().minusMonths(1), LocalDate.now().plusMonths(2)));
    }
}
