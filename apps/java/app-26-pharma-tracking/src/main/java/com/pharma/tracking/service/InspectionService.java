package com.pharma.tracking.service;

import com.pharma.tracking.model.Inspection;
import com.pharma.tracking.repository.InspectionRepository;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class InspectionService {

    private final InspectionRepository inspectionRepository;

    public InspectionService(InspectionRepository inspectionRepository) {
        this.inspectionRepository = inspectionRepository;
    }

    public List<Inspection> getInspectionsByBatch(Long batchId) {
        return inspectionRepository.findByBatchId(batchId);
    }

    public Inspection saveInspection(Inspection inspection) {
        return inspectionRepository.save(inspection);
    }
}
