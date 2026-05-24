package com.hotel.reservation.controller;

import com.hotel.reservation.model.Guest;
import com.hotel.reservation.repository.GuestRepository;
import com.hotel.reservation.repository.UserRepository;
import com.hotel.reservation.model.User;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.security.Principal;

@RestController
@RequestMapping("/api/guests")
public class GuestController {

    private final GuestRepository guestRepository;
    private final UserRepository userRepository;

    public GuestController(GuestRepository guestRepository, UserRepository userRepository) {
        this.guestRepository = guestRepository;
        this.userRepository = userRepository;
    }

    @GetMapping("/{id}")
    public ResponseEntity<Guest> getGuestDetails(@PathVariable Long id, Principal principal) {
        Guest guest = guestRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Guest not found"));
        
        User currentUser = userRepository.findByUsername(principal.getName())
                .orElseThrow(() -> new IllegalArgumentException("User not found"));

        // DECOY: Normal access control check verifies that guest can only view their own profile
        if ("GUEST".equals(currentUser.getRole()) && !id.equals(currentUser.getGuestId())) {
            return ResponseEntity.status(403).build();
        }
        return ResponseEntity.ok(guest);
    }
}
