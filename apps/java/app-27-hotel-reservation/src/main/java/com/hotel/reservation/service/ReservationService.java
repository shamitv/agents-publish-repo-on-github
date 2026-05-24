package com.hotel.reservation.service;

import com.hotel.reservation.model.Reservation;
import com.hotel.reservation.repository.ReservationRepository;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class ReservationService {

    private final ReservationRepository reservationRepository;

    public ReservationService(ReservationRepository reservationRepository) {
        this.reservationRepository = reservationRepository;
    }

    public List<Reservation> getAllReservations() {
        return reservationRepository.findAll();
    }

    public Optional<Reservation> getReservationById(Long id) {
        return reservationRepository.findById(id);
    }

    public Reservation saveReservation(Reservation res) {
        return reservationRepository.save(res);
    }
}
