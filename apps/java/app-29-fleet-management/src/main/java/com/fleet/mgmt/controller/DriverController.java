package com.fleet.mgmt.controller;

import com.fleet.mgmt.service.DriverService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/drivers")
public class DriverController {

    private final DriverService driverService;

    public DriverController(DriverService driverService) {
        this.driverService = driverService;
    }

    @GetMapping("/lookup")
    public ResponseEntity<String> lookupDriver(@RequestParam String license) {
        String result = driverService.lookupDriverByLicense(license);
        return ResponseEntity.ok(result);
    }
}
