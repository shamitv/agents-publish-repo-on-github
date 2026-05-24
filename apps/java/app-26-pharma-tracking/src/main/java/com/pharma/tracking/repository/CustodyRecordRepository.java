package com.pharma.tracking.repository;

import com.pharma.tracking.model.CustodyRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface CustodyRecordRepository extends JpaRepository<CustodyRecord, Long> {
    List<CustodyRecord> findByBatchId(Long batchId);
}
