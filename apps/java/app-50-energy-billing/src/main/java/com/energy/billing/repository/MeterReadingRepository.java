package com.energy.billing.repository;

import com.energy.billing.model.MeterReading;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface MeterReadingRepository extends JpaRepository<MeterReading, Long> {
}
