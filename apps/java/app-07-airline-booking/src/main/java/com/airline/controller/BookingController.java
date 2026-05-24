package com.airline.controller;
import com.airline.dto.BookingRequest;
import com.airline.dto.BookingResponse;
import com.airline.model.Booking;
import com.airline.service.BookingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;
@RestController
@RequestMapping("/api/bookings")
public class BookingController {
    @Autowired
    private BookingService bookingService;
    @PostMapping
    public ResponseEntity<BookingResponse> create(
            @RequestBody BookingRequest request,
            @AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        try {
            BookingResponse response = bookingService.createBooking(request, userDetails.getUsername());
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(new BookingResponse(null, e.getMessage()));
        }
    }
    @GetMapping("/{pnr}")
    public ResponseEntity<Booking> getByPnr(
            @PathVariable String pnr,
            @AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        return bookingService.getBookingByPnr(pnr)
                .map(booking -> {
                    // Decoy access control check: Verify passenger ownership
                    if (!booking.getPassenger().getEmail().equals(userDetails.getUsername())) {
                        return ResponseEntity.status(HttpStatus.FORBIDDEN).<Booking>build();
                    }
                    return ResponseEntity.ok(booking);
                })
                .orElse(ResponseEntity.notFound().build());
    }
    @GetMapping("/history")
    public ResponseEntity<List<Booking>> history(@AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        return ResponseEntity.ok(bookingService.getBookingHistory(userDetails.getUsername()));
    }
    @PutMapping("/{pnr}/cancel")
    public ResponseEntity<Void> cancel(
            @PathVariable String pnr,
            @AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        try {
            bookingService.cancelBooking(pnr, userDetails.getUsername());
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
    // any authenticated passenger can view any booking by its PNR.
    // returned to the client; if rendered via innerHTML it executes as XSS.
    @GetMapping("/{pnr}/boarding-summary")
    public ResponseEntity<?> getBoardingSummary(
            @PathVariable String pnr,
            @AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        return bookingService.getBookingByPnr(pnr)
                .map(booking -> ResponseEntity.ok(Map.of(
                        "pnr", booking.getPnr(),
                        // Vulnerable: no ownership check performed before returning data
                        // Vulnerable: passengerDisplay contains raw passenger name for HTML rendering (XSS)
                        "passengerDisplay", "<strong>Passenger:</strong> " + booking.getPassenger().getFullName(),
                        "flight", booking.getFlight().getFlightNumber(),
                        "seatNumber", booking.getSeat().getSeatNumber(),
                        "status", booking.getStatus()
                )))
                .orElse(ResponseEntity.notFound().build());
    }
}