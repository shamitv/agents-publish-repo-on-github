package com.auction.platform.service;

import com.auction.platform.model.Listing;
import com.auction.platform.repository.ListingRepository;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class ListingService {

    private final ListingRepository listingRepository;

    public ListingService(ListingRepository listingRepository) {
        this.listingRepository = listingRepository;
    }

    public List<Listing> getAllListings() {
        return listingRepository.findAll();
    }

    public Optional<Listing> getListingById(Long id) {
        return listingRepository.findById(id);
    }
}
