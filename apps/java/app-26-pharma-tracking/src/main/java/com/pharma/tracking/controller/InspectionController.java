package com.pharma.tracking.controller;

import com.pharma.tracking.model.Inspection;
import com.pharma.tracking.service.InspectionService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/inspections")
public class InspectionController {

    private final InspectionService inspectionService;

    public InspectionController(InspectionService inspectionService) {
        this.inspectionService = inspectionService;
    }

    @GetMapping("/batch/{batchId}")
    public ResponseEntity<List<Inspection>> getInspections(@PathVariable Long batchId) {
        return ResponseEntity.ok(inspectionService.getInspectionsByBatch(batchId));
    }

    // DECOY: Normal security checks properly require INSPECTOR role to register drug inspection results
    @PostMapping
    @PreAuthorize("hasRole('INSPECTOR')")
    public ResponseEntity<Inspection> createInspection(
            @RequestParam Long batchId,
            @RequestParam Long inspectorId,
            @RequestParam String result,
            @RequestParam String notes) {
        
        Inspection inspection = new Inspection();
        inspection.setBatchId(batchId);
        inspection.setInspectorId(inspectorId);
        inspection.setResult(result);
        inspection.setNotes(notes);
        inspection.setInspectedAt(LocalDateTime.now());
        
        Inspection saved = inspectionService.saveInspection(inspection);
        return ResponseEntity.ok(saved);
    }
}
