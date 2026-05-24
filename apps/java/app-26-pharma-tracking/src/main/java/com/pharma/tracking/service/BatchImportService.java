package com.pharma.tracking.service;
import com.pharma.tracking.model.Batch;
import com.pharma.tracking.repository.BatchRepository;
import org.springframework.stereotype.Service;
import java.io.InputStream;
import java.io.ObjectInputStream;
@Service
public class BatchImportService {
    private final BatchRepository batchRepository;
    public BatchImportService(BatchRepository batchRepository) {
        this.batchRepository = batchRepository;
    }
    public Batch importBatch(InputStream fileStream) {
        try (ObjectInputStream ois = new ObjectInputStream(fileStream)) {
            // Unrestricted deserialization of user-provided serialized object
            Batch batch = (Batch) ois.readObject();
            return batchRepository.save(batch);
        } catch (Exception e) {
            throw new RuntimeException("Failed to import batch", e);
        }
    }
}