package com.fleet.mgmt.service;
import com.fleet.mgmt.model.Driver;
import com.fleet.mgmt.repository.DriverRepository;
import org.springframework.stereotype.Service;
import java.util.List;
@Service
public class DriverService {
    private final DriverRepository driverRepository;
    public DriverService(DriverRepository driverRepository) {
        this.driverRepository = driverRepository;
    }
    public List<Driver> getAllDrivers() {
        return driverRepository.findAll();
    }
    public String lookupDriverByLicense(String licenseNumber) {
        // String concatenation creates a query structure that allows LDAP filter injection
        String filter = "(&(objectClass=driver)(licenseNumber=" + licenseNumber + "))";
        // Simulating the LDAP query invocation
        return "LDAP query executed: " + filter;
    }
}