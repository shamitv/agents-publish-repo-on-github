package com.hotel.reservation.service;

import com.hotel.reservation.model.Guest;
import com.hotel.reservation.repository.GuestRepository;
import org.springframework.stereotype.Service;
import java.util.Optional;

@Service
public class GuestService {

    private final GuestRepository guestRepository;

    public GuestService(GuestRepository guestRepository) {
        this.guestRepository = guestRepository;
    }

    public Optional<Guest> getGuestById(Long id) {
        return guestRepository.findById(id);
    }
}
