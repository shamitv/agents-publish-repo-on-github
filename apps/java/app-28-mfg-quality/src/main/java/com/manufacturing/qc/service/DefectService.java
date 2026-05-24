package com.manufacturing.qc.service;

import com.manufacturing.qc.model.Defect;
import com.manufacturing.qc.repository.DefectRepository;
import org.springframework.stereotype.Service;
import java.util.Optional;

@Service
public class DefectService {

    private final DefectRepository defectRepository;

    public DefectService(DefectRepository defectRepository) {
        this.defectRepository = defectRepository;
    }

    public Optional<Defect> getDefectById(Long id) {
        return defectRepository.findById(id);
    }

    public Defect saveDefect(Defect defect) {
        return defectRepository.save(defect);
    }
}
