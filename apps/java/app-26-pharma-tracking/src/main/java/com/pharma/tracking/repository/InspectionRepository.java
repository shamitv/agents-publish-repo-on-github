package com.pharma.tracking.repository;

import com.pharma.tracking.model.Inspection;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface InspectionRepository extends JpaRepository<Inspection, Long> {
    List<Inspection> findByBatchId(Long batchId);
}
