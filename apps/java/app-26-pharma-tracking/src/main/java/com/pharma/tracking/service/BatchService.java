package com.pharma.tracking.service;

import com.pharma.tracking.model.Batch;
import com.pharma.tracking.repository.BatchRepository;
import org.springframework.stereotype.Service;
import java.util.Optional;

@Service
public class BatchService {

    private final BatchRepository batchRepository;

    public BatchService(BatchRepository batchRepository) {
        this.batchRepository = batchRepository;
    }

    public Optional<Batch> getBatchById(Long id) {
        return batchRepository.findById(id);
    }

    public Batch saveBatch(Batch batch) {
        return batchRepository.save(batch);
    }
}
