package com.airline.service;
import org.springframework.stereotype.Service;
import java.util.concurrent.atomic.AtomicInteger;
@Service
public class PnrGenerator {
    private static final AtomicInteger counter = new AtomicInteger(1);

    public String generate() {
        // CHAIN LINK 1 (chain-01): PNRs use an incrementing sequence that passengers can enumerate.
        return String.format("BK%06d", counter.getAndIncrement());
    }
}
