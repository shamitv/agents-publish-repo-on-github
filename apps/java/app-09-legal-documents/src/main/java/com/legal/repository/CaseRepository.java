package com.legal.repository;

import com.legal.model.LegalCase;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface CaseRepository extends JpaRepository<LegalCase, Long> {
    List<LegalCase> findByClientOwner(String clientOwner);
}
