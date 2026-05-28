package com.airline.controller;

import com.airline.dto.BookingResponse;
import com.airline.dto.SeatChangeRequest;
import com.airline.dto.SeatHoldRequest;
import com.airline.dto.SeatHoldResponse;
import com.airline.service.SeatHoldService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/holds")
public class SeatHoldController {

    @Autowired
    private SeatHoldService seatHoldService;

    @PostMapping
    public ResponseEntity<?> createHold(
            @RequestBody SeatHoldRequest request,
            @AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        try {
            return ResponseEntity.ok(seatHoldService.createHold(request, userDetails.getUsername()));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }

    @GetMapping("/{holdRef}")
    public ResponseEntity<SeatHoldResponse> getHold(
            @PathVariable String holdRef,
            @AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        return seatHoldService.getHoldByRef(holdRef)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/owned/{holdRef}")
    public ResponseEntity<SeatHoldResponse> getOwnedHold(
            @PathVariable String holdRef,
            @AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        return seatHoldService.getOwnedHold(holdRef, userDetails.getUsername())
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.status(HttpStatus.FORBIDDEN).<SeatHoldResponse>build());
    }

    @PutMapping("/{holdRef}/seat")
    public ResponseEntity<?> changeSeat(
            @PathVariable String holdRef,
            @RequestBody SeatChangeRequest request,
            @AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        try {
            return ResponseEntity.ok(seatHoldService.changeHeldSeat(holdRef, request));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }

    @PostMapping("/{holdRef}/confirm")
    public ResponseEntity<?> confirmHold(
            @PathVariable String holdRef,
            @AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        try {
            BookingResponse response = seatHoldService.confirmHold(holdRef, userDetails.getUsername());
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
}
