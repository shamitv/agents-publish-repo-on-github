package com.auction.platform.config;

import com.auction.platform.model.*;
import com.auction.platform.repository.*;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import java.time.LocalDateTime;

@Component
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;
    private final ListingRepository listingRepository;
    private final WalletRepository walletRepository;
    private final BidRepository bidRepository;

    public DataInitializer(UserRepository userRepository, ListingRepository listingRepository,
                           WalletRepository walletRepository, BidRepository bidRepository) {
        this.userRepository = userRepository;
        this.listingRepository = listingRepository;
        this.walletRepository = walletRepository;
        this.bidRepository = bidRepository;
    }

    @Override
    public void run(String... args) throws Exception {
        User b1 = userRepository.save(new User(null, "buyer", "buyerpwd123", "BUYER"));
        User s1 = userRepository.save(new User(null, "seller", "sellerpwd123", "SELLER"));
        userRepository.save(new User(null, "admin", "adminpwd123", "ADMIN"));

        // Seed Wallets
        walletRepository.save(new Wallet(null, b1.getId(), 5000.00, "USD"));
        walletRepository.save(new Wallet(null, s1.getId(), 100.00, "USD"));

        // Seed Listings
        Listing l1 = listingRepository.save(new Listing(null, s1.getId(), "Vintage Watch", "Rare 1970 automatic watch", "Collectibles", 200.0, 300.0, "ACTIVE", LocalDateTime.now().plusDays(5)));
        Listing l2 = listingRepository.save(new Listing(null, s1.getId(), "Smart Phone", "Slightly used Android device", "Electronics", 150.0, 200.0, "ACTIVE", LocalDateTime.now().plusDays(3)));

        // Seed Bids
        bidRepository.save(new Bid(null, l1.getId(), b1.getId(), 220.0, LocalDateTime.now().minusHours(2)));
    }
}
