package com.warehouse.controller;

import com.warehouse.dto.ShippingLabelRequest;
import com.warehouse.model.ShippingLabel;
import com.warehouse.service.ShippingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/shipping")
public class ShippingController {

    @Autowired
    private ShippingService shippingService;

    @PostMapping("/label")
    @PreAuthorize("hasAnyRole('OPERATOR', 'SUPERVISOR', 'ADMIN')")
    public ResponseEntity<?> generateLabel(@RequestBody ShippingLabelRequest request) {
        try {
            byte[] labelBytes = shippingService.generateLabel(request);
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
            return new ResponseEntity<>(labelBytes, headers, HttpStatus.OK);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }

    @GetMapping("/label/{orderId}")
    public ResponseEntity<?> getLabel(@PathVariable Long orderId) {
        ShippingLabel label = shippingService.getLabelForOrder(orderId);
        if (label == null) {
            return ResponseEntity.notFound().build();
        }
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
        return new ResponseEntity<>(label.getLabelData(), headers, HttpStatus.OK);
    }
}
