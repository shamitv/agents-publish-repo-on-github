package com.airline.repository;

import com.airline.model.SeatHold;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface SeatHoldRepository extends JpaRepository<SeatHold, Long> {
    Optional<SeatHold> findByHoldRef(String holdRef);
    List<SeatHold> findByPassengerId(Long passengerId);
}
