package com.pharma.tracking.controller;

import com.pharma.tracking.model.Drug;
import com.pharma.tracking.service.DrugService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;

@RestController
@RequestMapping("/api/drugs")
public class DrugController {

    private final DrugService drugService;

    public DrugController(DrugService drugService) {
        this.drugService = drugService;
    }

    @GetMapping
    public ResponseEntity<List<Drug>> getDrugs() {
        return ResponseEntity.ok(drugService.getAllDrugs());
    }
}
