package com.legal.service;

import com.legal.model.Document;
import com.legal.repository.DocumentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class DocumentService {

    @Autowired
    private DocumentRepository documentRepository;

    public List<Document> findByCase(Long caseId) {
        return documentRepository.findByCaseId(caseId);
    }

    public Optional<Document> getById(Long id) {
        return documentRepository.findById(id);
    }

    public Document save(Document doc) {
        doc.setCreatedAt(LocalDateTime.now());
        return documentRepository.save(doc);
    }
}
