package com.manufacturing.qc.service;
import com.manufacturing.qc.model.Inspection;
import com.manufacturing.qc.repository.InspectionRepository;
import org.springframework.stereotype.Service;
import java.util.Optional;
@Service
public class InspectionService {
    private final InspectionRepository inspectionRepository;
    public InspectionService(InspectionRepository inspectionRepository) {
        this.inspectionRepository = inspectionRepository;
    }
    public Optional<Inspection> getInspectionById(Long id) {
        return inspectionRepository.findById(id);
    }
    public Inspection updateInspectionResult(Long id, String newResult, String newNotes) {
        Inspection inspection = inspectionRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Inspection not found"));
        inspection.setResult(newResult);
        inspection.setNotes(newNotes);
        // Silent modification: NO log entry or audit trail records this alteration
        return inspectionRepository.save(inspection);
    }
}