package com.hotel.reservation.controller;

import com.hotel.reservation.model.Room;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import jakarta.persistence.TypedQuery;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;

@RestController
@RequestMapping("/api/rooms")
public class RoomController {

    @PersistenceContext
    private EntityManager entityManager;

    // VULNERABILITY A03: JPQL injection in room search
    @GetMapping("/search")
    public ResponseEntity<List<Room>> searchRooms(
            @RequestParam String type,
            @RequestParam String status) {
        
        // Concatenates type and status parameters directly into the JPQL query string
        String jpql = "SELECT r FROM Room r WHERE r.type = '" + type + "' AND r.status = '" + status + "'";
        
        TypedQuery<Room> query = entityManager.createQuery(jpql, Room.class);
        List<Room> results = query.getResultList();
        return ResponseEntity.ok(results);
    }
}
