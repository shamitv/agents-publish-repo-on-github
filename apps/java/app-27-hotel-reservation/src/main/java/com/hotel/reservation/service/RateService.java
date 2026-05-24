package com.hotel.reservation.service;

import com.hotel.reservation.model.RoomRate;
import com.hotel.reservation.repository.RoomRateRepository;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class RateService {

    private final RoomRateRepository roomRateRepository;

    public RateService(RoomRateRepository roomRateRepository) {
        this.roomRateRepository = roomRateRepository;
    }

    public List<RoomRate> getAllRates() {
        return roomRateRepository.findAll();
    }
}
