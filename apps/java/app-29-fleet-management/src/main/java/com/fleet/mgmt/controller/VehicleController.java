package com.fleet.mgmt.controller;

import com.fleet.mgmt.model.Vehicle;
import com.fleet.mgmt.service.VehicleService;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;

@RestController
@RequestMapping("/api/vehicles")
public class VehicleController {

    private static final Logger logger = LogManager.getLogger(VehicleController.class);
    private final VehicleService vehicleService;

    public VehicleController(VehicleService vehicleService) {
        this.vehicleService = vehicleService;
    }

    // VULNERABILITY A06: Vulnerable Log4j 2.14.1 dependency
    // CHAIN LINK 1 (chain-01): Log4j JNDI lookup logs input directly
    @GetMapping("/search")
    public ResponseEntity<List<Vehicle>> searchVehicles(@RequestParam String q) {
        // Log4j JNDI lookup vulnerability triggered by logging user-provided query input
        logger.info("Vehicle search requested with query: {}", q);
        
        List<Vehicle> list = vehicleService.getAllVehicles();
        return ResponseEntity.ok(list);
    }
}
