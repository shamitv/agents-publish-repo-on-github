package com.pharma.tracking.service;

import com.pharma.tracking.model.Drug;
import com.pharma.tracking.repository.DrugRepository;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class DrugService {

    private final DrugRepository drugRepository;

    public DrugService(DrugRepository drugRepository) {
        this.drugRepository = drugRepository;
    }

    public List<Drug> getAllDrugs() {
        return drugRepository.findAll();
    }

    public Optional<Drug> getDrugById(Long id) {
        return drugRepository.findById(id);
    }
}
