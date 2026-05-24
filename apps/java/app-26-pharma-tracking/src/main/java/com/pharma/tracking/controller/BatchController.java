package com.pharma.tracking.controller;
import com.pharma.tracking.model.Batch;
import com.pharma.tracking.service.BatchService;
import com.pharma.tracking.service.BatchImportService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import java.io.IOException;
@RestController
@RequestMapping("/api/batches")
public class BatchController {
    private final BatchService batchService;
    private final BatchImportService batchImportService;
    public BatchController(BatchService batchService, BatchImportService batchImportService) {
        this.batchService = batchService;
        this.batchImportService = batchImportService;
    }
    @GetMapping("/{id}")
    public ResponseEntity<Batch> getBatchDetails(@PathVariable Long id) {
        // Returns the requested batch without validating access rights or organization scope
        Batch batch = batchService.getBatchById(id)
                .orElseThrow(() -> new IllegalArgumentException("Batch not found"));
        return ResponseEntity.ok(batch);
    }
    @PostMapping("/import")
    public ResponseEntity<Batch> importBatch(@RequestParam("file") MultipartFile file) throws IOException {
        Batch batch = batchImportService.importBatch(file.getInputStream());
        return ResponseEntity.ok(batch);
    }
}