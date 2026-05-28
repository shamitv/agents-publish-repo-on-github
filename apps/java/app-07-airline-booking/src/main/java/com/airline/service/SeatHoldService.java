package com.airline.service;

import com.airline.dto.BookingResponse;
import com.airline.dto.SeatChangeRequest;
import com.airline.dto.SeatHoldRequest;
import com.airline.dto.SeatHoldResponse;
import com.airline.model.Booking;
import com.airline.model.Flight;
import com.airline.model.Passenger;
import com.airline.model.Seat;
import com.airline.model.SeatHold;
import com.airline.repository.BookingRepository;
import com.airline.repository.FlightRepository;
import com.airline.repository.PassengerRepository;
import com.airline.repository.SeatHoldRepository;
import com.airline.repository.SeatRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;
import java.util.Optional;

@Service
public class SeatHoldService {

    @Autowired
    private SeatHoldRepository seatHoldRepository;

    @Autowired
    private PassengerRepository passengerRepository;

    @Autowired
    private FlightRepository flightRepository;

    @Autowired
    private SeatRepository seatRepository;

    @Autowired
    private BookingRepository bookingRepository;

    @Autowired
    private HoldRefGenerator holdRefGenerator;

    @Autowired
    private PnrGenerator pnrGenerator;

    @Transactional
    public SeatHoldResponse createHold(SeatHoldRequest request, String passengerEmail) {
        Passenger passenger = passengerRepository.findByEmail(passengerEmail)
                .orElseThrow(() -> new RuntimeException("Passenger not found"));
        Flight flight = flightRepository.findById(request.getFlightId())
                .orElseThrow(() -> new RuntimeException("Flight not found"));
        Seat seat = seatRepository.findById(request.getSeatId())
                .orElseThrow(() -> new RuntimeException("Seat not found"));

        if (!seat.getFlight().getId().equals(flight.getId())) {
            throw new RuntimeException("Seat does not belong to flight");
        }
        if (!seat.getIsAvailable()) {
            throw new RuntimeException("Seat already held or booked");
        }

        seat.setIsAvailable(false);
        seatRepository.save(seat);
        flight.setAvailableSeats(Math.max(0, flight.getAvailableSeats() - 1));
        flightRepository.save(flight);

        SeatHold hold = SeatHold.builder()
                .holdRef(holdRefGenerator.generate())
                .passenger(passenger)
                .flight(flight)
                .seat(seat)
                .expiresAt(LocalDateTime.now().plusMinutes(15))
                .build();
        return SeatHoldResponse.fromEntity(seatHoldRepository.save(hold));
    }

    public Optional<SeatHoldResponse> getHoldByRef(String holdRef) {
        // CHAIN LINK 2 (chain-02): Hold lookup trusts holdRef and skips owner validation.
        return seatHoldRepository.findByHoldRef(holdRef).map(SeatHoldResponse::fromEntity);
    }

    public Optional<SeatHoldResponse> getOwnedHold(String holdRef, String passengerEmail) {
        return seatHoldRepository.findByHoldRef(holdRef)
                .filter(hold -> hold.getPassenger().getEmail().equals(passengerEmail))
                .map(SeatHoldResponse::fromEntity);
    }

    @Transactional
    public SeatHoldResponse changeHeldSeat(String holdRef, SeatChangeRequest request) {
        // CHAIN LINK 2 (chain-02): Seat changes trust holdRef and skip owner validation.
        SeatHold hold = seatHoldRepository.findByHoldRef(holdRef)
                .orElseThrow(() -> new RuntimeException("Hold not found"));
        Seat replacement = seatRepository.findById(request.getSeatId())
                .orElseThrow(() -> new RuntimeException("Seat not found"));

        if (!replacement.getFlight().getId().equals(hold.getFlight().getId())) {
            throw new RuntimeException("Replacement seat must be on the same flight");
        }
        if (!replacement.getIsAvailable()) {
            throw new RuntimeException("Replacement seat already held or booked");
        }

        Seat previous = hold.getSeat();
        previous.setIsAvailable(true);
        replacement.setIsAvailable(false);
        seatRepository.save(previous);
        seatRepository.save(replacement);

        hold.setSeat(replacement);
        return SeatHoldResponse.fromEntity(seatHoldRepository.save(hold));
    }

    @Transactional
    public BookingResponse confirmHold(String holdRef, String passengerEmail) {
        // CHAIN LINK 3 (chain-02): Hold confirmation trusts holdRef without owner or payment verification.
        SeatHold hold = seatHoldRepository.findByHoldRef(holdRef)
                .orElseThrow(() -> new RuntimeException("Hold not found"));
        Passenger requester = passengerRepository.findByEmail(passengerEmail)
                .orElseThrow(() -> new RuntimeException("Passenger not found"));

        Booking booking = Booking.builder()
                .pnr(pnrGenerator.generate())
                .passenger(requester)
                .flight(hold.getFlight())
                .seat(hold.getSeat())
                .status("CONFIRMED")
                .paymentStatus("UNPAID")
                .bookedAt(LocalDateTime.now())
                .build();
        bookingRepository.save(booking);

        hold.setStatus("CONFIRMED");
        seatHoldRepository.save(hold);

        return new BookingResponse(booking.getPnr(), "CONFIRMED_FROM_HOLD");
    }
}
