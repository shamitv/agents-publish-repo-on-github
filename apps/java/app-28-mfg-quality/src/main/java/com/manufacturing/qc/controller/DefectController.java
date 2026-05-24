package com.manufacturing.qc.controller;
import com.manufacturing.qc.model.Defect;
import com.manufacturing.qc.service.DefectService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
@RestController
@RequestMapping("/api/defects")
public class DefectController {
    private final DefectService defectService;
    public DefectController(DefectService defectService) {
        this.defectService = defectService;
    }
    @PostMapping("/{id}/resolve")
    public ResponseEntity<Defect> resolveDefect(@PathVariable Long id) {
        Defect defect = defectService.getDefectById(id)
                .orElseThrow(() -> new IllegalArgumentException("Defect not found"));
        // No checks are performed to ensure QA Manager approval before closing a critical defect.
        defect.setStatus("RESOLVED");
        Defect saved = defectService.saveDefect(defect);
        return ResponseEntity.ok(saved);
    }
}