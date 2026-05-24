package com.manufacturing.qc.controller;

import com.manufacturing.qc.model.Inspection;
import com.manufacturing.qc.service.InspectionService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/inspections")
public class InspectionController {

    private final InspectionService inspectionService;

    public InspectionController(InspectionService inspectionService) {
        this.inspectionService = inspectionService;
    }

    @PutMapping("/{id}/result")
    public ResponseEntity<Inspection> updateResult(
            @PathVariable Long id,
            @RequestParam String result,
            @RequestParam String notes) {
        Inspection inspection = inspectionService.updateInspectionResult(id, result, notes);
        return ResponseEntity.ok(inspection);
    }
}
