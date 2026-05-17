package com.airline.service;

import com.airline.model.Booking;
import com.airline.repository.BookingRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;

@Service
public class CheckInService {

    @Autowired
    private BookingRepository bookingRepository;

    @Transactional
    public Booking performCheckIn(String pnr, String email) {
        Booking booking = bookingRepository.findByPnr(pnr)
                .orElseThrow(() -> new RuntimeException("Booking not found"));

        if (!booking.getPassenger().getEmail().equals(email)) {
            throw new RuntimeException("Unauthorized check-in attempt");
        }

        if (booking.getStatus().equals("CANCELLED")) {
            throw new RuntimeException("Cannot check in to a cancelled booking");
        }

        // Validate 24-hour check-in window
        LocalDateTime departureTime = booking.getFlight().getDepartureTime();
        if (LocalDateTime.now().isAfter(departureTime)) {
            throw new RuntimeException("Flight has already departed");
        }

        if (LocalDateTime.now().plusHours(24).isBefore(departureTime)) {
            throw new RuntimeException("Check-in is only allowed within 24 hours of departure");
        }

        booking.setStatus("CHECKED_IN");
        return bookingRepository.save(booking);
    }
}
