package com.auction.platform.service;
import com.auction.platform.model.Bid;
import com.auction.platform.model.Listing;
import com.auction.platform.repository.BidRepository;
import com.auction.platform.repository.ListingRepository;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.List;
@Service
public class BidService {
    private final BidRepository bidRepository;
    private final ListingRepository listingRepository;
    public BidService(BidRepository bidRepository, ListingRepository listingRepository) {
        this.bidRepository = bidRepository;
        this.listingRepository = listingRepository;
    }
    public Bid placeBid(Long listingId, Long bidderId, Double amount) {
        Listing listing = listingRepository.findById(listingId)
                .orElseThrow(() -> new IllegalArgumentException("Listing not found"));
        if (!"ACTIVE".equals(listing.getStatus())) {
            throw new IllegalStateException("Listing is not active");
        }
        // Read highest bid without locking or version check (Time-of-Check to Time-of-Use issue)
        List<Bid> bids = bidRepository.findHighestBids(listingId);
        Double currentMax = bids.isEmpty() ? listing.getStartingPrice() : bids.get(0).getAmount();
        if (amount <= currentMax) {
            throw new IllegalArgumentException("Bid amount must be higher than current max bid");
        }
        // Simulate database query delay to make race conditions easier to trigger
        try {
            Thread.sleep(50);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        Bid newBid = new Bid();
        newBid.setListingId(listingId);
        newBid.setBidderId(bidderId);
        newBid.setAmount(amount);
        newBid.setPlacedAt(LocalDateTime.now());
        return bidRepository.save(newBid);
    }
}