package com.airline.service;

import org.springframework.stereotype.Service;
import java.util.concurrent.atomic.AtomicInteger;

@Service
public class PnrGenerator {
    // CHAIN LINK 1 (chain-01): Sequential counter replaces SecureRandom, making every
    // PNR trivially enumerable (BK000001, BK000002, ...). Individually this seems like
    // a minor implementation detail, but it is the prerequisite for the IDOR and XSS
    // links that follow.
    private static final AtomicInteger counter = new AtomicInteger(1);

    public String generate() {
        return String.format("BK%06d", counter.getAndIncrement());
    }
}
