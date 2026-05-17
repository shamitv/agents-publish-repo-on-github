package com.airline.controller;

import com.airline.model.Booking;
import com.airline.service.CheckInService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/checkin")
public class CheckInController {

    @Autowired
    private CheckInService checkInService;

    @PostMapping("/{pnr}")
    public ResponseEntity<String> performCheckIn(
            @PathVariable String pnr,
            @AuthenticationPrincipal UserDetails userDetails) {
        
        if (userDetails == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }

        try {
            bookingCheckIn(pnr, userDetails.getUsername());
            return ResponseEntity.ok("Checked in successfully");
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }

    private Booking bookingCheckIn(String pnr, String email) {
        return checkInService.performCheckIn(pnr, email);
    }
}
