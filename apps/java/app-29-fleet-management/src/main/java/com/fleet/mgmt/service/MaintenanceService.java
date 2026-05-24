package com.fleet.mgmt.service;

import com.fleet.mgmt.model.MaintenanceRecord;
import com.fleet.mgmt.repository.MaintenanceRecordRepository;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class MaintenanceService {

    private final MaintenanceRecordRepository maintenanceRecordRepository;

    public MaintenanceService(MaintenanceRecordRepository maintenanceRecordRepository) {
        this.maintenanceRecordRepository = maintenanceRecordRepository;
    }

    public List<MaintenanceRecord> getAllRecords() {
        return maintenanceRecordRepository.findAll();
    }
}
