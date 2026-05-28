package com.airline.controller;

import com.airline.model.Booking;
import com.airline.model.Flight;
import com.airline.repository.BookingRepository;
import com.airline.repository.FlightRepository;
import com.airline.repository.PassengerRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import java.util.Optional;

@Controller
public class WebController {

    @Autowired
    private FlightRepository flightRepository;

    @Autowired
    private BookingRepository bookingRepository;

    @Autowired
    private PassengerRepository passengerRepository;

    @GetMapping("/flights/{id}/seats")
    public String seatSelection(
            @PathVariable Long id,
            @AuthenticationPrincipal UserDetails userDetails,
            Model model) {
        
        if (userDetails == null) {
            return "redirect:/";
        }

        Optional<Flight> flightOpt = flightRepository.findById(id);
        if (flightOpt.isEmpty()) {
            return "redirect:/dashboard";
        }

        passengerRepository.findByEmail(userDetails.getUsername()).ifPresent(p -> {
            model.addAttribute("currentUser", p);
        });

        model.addAttribute("flight", flightOpt.get());
        return "seat-map";
    }

    @GetMapping("/checkin/{pnr}")
    public String checkInPage(
            @PathVariable String pnr,
            @AuthenticationPrincipal UserDetails userDetails,
            Model model) {
        
        if (userDetails == null) {
            return "redirect:/";
        }

        Optional<Booking> bookingOpt = bookingRepository.findByPnr(pnr);
        if (bookingOpt.isEmpty()) {
            return "redirect:/dashboard";
        }

        Booking booking = bookingOpt.get();
        if (!booking.getPassenger().getEmail().equals(userDetails.getUsername())) {
            return "redirect:/dashboard";
        }

        passengerRepository.findByEmail(userDetails.getUsername()).ifPresent(p -> {
            model.addAttribute("currentUser", p);
        });

        model.addAttribute("booking", booking);
        return "checkin";
    }

    @GetMapping("/checkin/{pnr}/pass")
    public String boardingPass(
            @PathVariable String pnr,
            @AuthenticationPrincipal UserDetails userDetails,
            Model model) {
        
        if (userDetails == null) {
            return "redirect:/";
        }

        Optional<Booking> bookingOpt = bookingRepository.findByPnr(pnr);
        if (bookingOpt.isEmpty()) {
            return "redirect:/dashboard";
        }

        Booking booking = bookingOpt.get();
        if (!booking.getPassenger().getEmail().equals(userDetails.getUsername())) {
            return "redirect:/dashboard";
        }

        if (!booking.getStatus().equals("CHECKED_IN")) {
            return "redirect:/checkin/" + pnr;
        }

        passengerRepository.findByEmail(userDetails.getUsername()).ifPresent(p -> {
            model.addAttribute("currentUser", p);
        });

        model.addAttribute("booking", booking);
        return "boarding-pass";
    }

    @GetMapping("/staff/boarding")
    @PreAuthorize("hasRole('AIRLINE_STAFF')")
    public String staffBoarding(
            @AuthenticationPrincipal UserDetails userDetails,
            Model model) {
        if (userDetails == null) {
            return "redirect:/";
        }
        passengerRepository.findByEmail(userDetails.getUsername()).ifPresent(p -> {
            model.addAttribute("currentUser", p);
        });
        return "staff-boarding";
    }
}
