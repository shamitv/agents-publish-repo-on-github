package com.legal.service;

import com.legal.model.LegalCase;
import com.legal.repository.CaseRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class CaseService {

    @Autowired
    private CaseRepository caseRepository;

    public List<LegalCase> listAll() {
        return caseRepository.findAll();
    }

    public List<LegalCase> findByClient(String username) {
        return caseRepository.findByClientOwner(username);
    }

    public Optional<LegalCase> getById(Long id) {
        return caseRepository.findById(id);
    }

    public LegalCase create(LegalCase legalCase) {
        legalCase.setCreatedAt(LocalDateTime.now());
        legalCase.setStatus("ACTIVE");
        return caseRepository.save(legalCase);
    }
}
