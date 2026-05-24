package com.pharma.tracking.controller;

import com.pharma.tracking.model.CustodyRecord;
import com.pharma.tracking.service.CustodyService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/custody")
public class CustodyController {

    private final CustodyService custodyService;

    public CustodyController(CustodyService custodyService) {
        this.custodyService = custodyService;
    }

    @PostMapping("/transfer")
    public ResponseEntity<CustodyRecord> transferBatch(
            @RequestParam Long batchId,
            @RequestParam String fromEntity,
            @RequestParam String toEntity) {
        CustodyRecord record = custodyService.recordTransfer(batchId, fromEntity, toEntity);
        return ResponseEntity.ok(record);
    }
}
