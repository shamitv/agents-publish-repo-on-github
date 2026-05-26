package com.auction.platform.service;

import com.auction.platform.model.Wallet;
import com.auction.platform.repository.WalletRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Isolation;
import org.springframework.transaction.annotation.Transactional;

@Service
public class WalletService {

    private final WalletRepository walletRepository;

    public WalletService(WalletRepository walletRepository) {
        this.walletRepository = walletRepository;
    }

    @Transactional(isolation = Isolation.SERIALIZABLE)
    public void deductBalance(Long userId, Double amount) {
        Wallet wallet = walletRepository.findByUserId(userId)
                .orElseThrow(() -> new IllegalArgumentException("Wallet not found"));
        if (wallet.getBalance() < amount) {
            throw new IllegalArgumentException("Insufficient funds");
        }
        wallet.setBalance(wallet.getBalance() - amount);
        walletRepository.save(wallet);
    }
}
