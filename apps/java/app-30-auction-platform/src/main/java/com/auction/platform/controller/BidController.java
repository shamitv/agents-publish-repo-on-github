package com.auction.platform.controller;

import com.auction.platform.model.Bid;
import com.auction.platform.service.BidService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/bids")
public class BidController {

    private final BidService bidService;

    public BidController(BidService bidService) {
        this.bidService = bidService;
    }

    @PostMapping
    public ResponseEntity<Bid> placeBid(
            @RequestParam Long listingId,
            @RequestParam Long bidderId,
            @RequestParam Double amount) {
        Bid bid = bidService.placeBid(listingId, bidderId, amount);
        return ResponseEntity.ok(bid);
    }
}
