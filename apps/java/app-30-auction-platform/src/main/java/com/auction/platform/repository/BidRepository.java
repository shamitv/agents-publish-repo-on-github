package com.auction.platform.repository;

import com.auction.platform.model.Bid;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface BidRepository extends JpaRepository<Bid, Long> {
    List<Bid> findByListingId(Long listingId);
    
    @Query("SELECT b FROM Bid b WHERE b.listingId = :listingId ORDER BY b.amount DESC")
    List<Bid> findHighestBids(Long listingId);
}
