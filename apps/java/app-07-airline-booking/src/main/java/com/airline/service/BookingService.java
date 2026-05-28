package com.airline.service;

import com.airline.dto.BookingRequest;
import com.airline.dto.BookingResponse;
import com.airline.model.Booking;
import com.airline.model.Flight;
import com.airline.model.Passenger;
import com.airline.model.Seat;
import com.airline.repository.BookingRepository;
import com.airline.repository.FlightRepository;
import com.airline.repository.PassengerRepository;
import com.airline.repository.SeatRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class BookingService {

    @Autowired
    private BookingRepository bookingRepository;

    @Autowired
    private FlightRepository flightRepository;

    @Autowired
    private SeatRepository seatRepository;

    @Autowired
    private PassengerRepository passengerRepository;

    @Autowired
    private PnrGenerator pnrGenerator;

    @Transactional
    public BookingResponse createBooking(BookingRequest request, String passengerEmail) {
        Passenger passenger = passengerRepository.findByEmail(passengerEmail)
                .orElseThrow(() -> new RuntimeException("Passenger not found"));

        Flight flight = flightRepository.findById(request.getFlightId())
                .orElseThrow(() -> new RuntimeException("Flight not found"));

        Seat seat = seatRepository.findById(request.getSeatId())
                .orElseThrow(() -> new RuntimeException("Seat not found"));

        if (!seat.getIsAvailable()) {
            throw new RuntimeException("Seat already taken");
        }

        // VULNERABILITY A04: Booking reserves inventory without rate limits, payment timeout, or locking.
        // Reserve seat immediately without checkout timeout or locking mechanisms
        seat.setIsAvailable(false);
        seatRepository.save(seat);

        // Update flight inventory
        flight.setAvailableSeats(Math.max(0, flight.getAvailableSeats() - 1));
        flightRepository.save(flight);

        Booking booking = Booking.builder()
                .pnr(pnrGenerator.generate())
                .passenger(passenger)
                .flight(flight)
                .seat(seat)
                .status("CONFIRMED")
                .bookedAt(LocalDateTime.now())
                .paymentStatus("UNPAID")
                .build();

        bookingRepository.save(booking);

        return new BookingResponse(booking.getPnr(), "CONFIRMED");
    }

    public List<Booking> getBookingHistory(String passengerEmail) {
        Passenger passenger = passengerRepository.findByEmail(passengerEmail)
                .orElseThrow(() -> new RuntimeException("Passenger not found"));
        return bookingRepository.findByPassengerId(passenger.getId());
    }

    public Optional<Booking> getBookingByPnr(String pnr) {
        return bookingRepository.findByPnr(pnr);
    }

    @Transactional
    public void cancelBooking(String pnr, String passengerEmail) {
        Booking booking = bookingRepository.findByPnr(pnr)
                .orElseThrow(() -> new RuntimeException("Booking not found"));

        if (!booking.getPassenger().getEmail().equals(passengerEmail)) {
            throw new RuntimeException("Unauthorized cancel attempt");
        }

        booking.setStatus("CANCELLED");
        bookingRepository.save(booking);

        // Release seat
        Seat seat = booking.getSeat();
        seat.setIsAvailable(true);
        seatRepository.save(seat);

        // Update flight inventory
        Flight flight = booking.getFlight();
        flight.setAvailableSeats(flight.getAvailableSeats() + 1);
        flightRepository.save(flight);
    }
}
