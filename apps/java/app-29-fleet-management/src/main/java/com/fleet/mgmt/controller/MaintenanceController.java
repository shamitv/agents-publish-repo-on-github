package com.fleet.mgmt.controller;

import com.fleet.mgmt.model.MaintenanceRecord;
import com.fleet.mgmt.service.MaintenanceService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;

@RestController
@RequestMapping("/api/maintenance")
public class MaintenanceController {

    private final MaintenanceService maintenanceService;

    public MaintenanceController(MaintenanceService maintenanceService) {
        this.maintenanceService = maintenanceService;
    }

    // DECOY: Normal security checks properly require FLEET_MANAGER role to view service history
    @GetMapping
    @PreAuthorize("hasRole('FLEET_MANAGER')")
    public ResponseEntity<List<MaintenanceRecord>> getRecords() {
        return ResponseEntity.ok(maintenanceService.getAllRecords());
    }
}
