package com.auction.platform.controller;

import com.auction.platform.model.Listing;
import com.auction.platform.service.ListingService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;

@RestController
@RequestMapping("/api/listings")
public class ListingController {

    private final ListingService listingService;

    public ListingController(ListingService listingService) {
        this.listingService = listingService;
    }

    @GetMapping
    @PreAuthorize("hasRole('SELLER')")
    public ResponseEntity<List<Listing>> getListings() {
        return ResponseEntity.ok(listingService.getAllListings());
    }
}
