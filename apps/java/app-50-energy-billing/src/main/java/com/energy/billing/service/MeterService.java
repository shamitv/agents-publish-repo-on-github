package com.energy.billing.service;

import com.energy.billing.model.Meter;
import com.energy.billing.repository.MeterRepository;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class MeterService {

    private final MeterRepository meterRepository;

    public MeterService(MeterRepository meterRepository) {
        this.meterRepository = meterRepository;
    }

    public List<Meter> getAllMeters() {
        return meterRepository.findAll();
    }
}
