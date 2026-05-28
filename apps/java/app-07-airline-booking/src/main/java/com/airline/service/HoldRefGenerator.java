package com.airline.service;

import org.springframework.stereotype.Service;
import java.util.concurrent.atomic.AtomicInteger;

@Service
public class HoldRefGenerator {
    private static final AtomicInteger counter = new AtomicInteger(101);

    public String generate() {
        // CHAIN LINK 1 (chain-02): Seat hold references use a predictable incrementing sequence.
        return String.format("HOLD%06d", counter.getAndIncrement());
    }
}
