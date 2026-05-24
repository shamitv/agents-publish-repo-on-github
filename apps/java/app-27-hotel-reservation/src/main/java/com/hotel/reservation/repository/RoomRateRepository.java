package com.hotel.reservation.repository;

import com.hotel.reservation.model.RoomRate;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface RoomRateRepository extends JpaRepository<RoomRate, Long> {
}
