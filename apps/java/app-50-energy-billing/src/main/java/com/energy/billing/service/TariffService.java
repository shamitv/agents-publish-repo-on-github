package com.energy.billing.service;

import com.energy.billing.model.Tariff;
import com.energy.billing.repository.TariffRepository;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class TariffService {

    private final TariffRepository tariffRepository;

    public TariffService(TariffRepository tariffRepository) {
        this.tariffRepository = tariffRepository;
    }

    public List<Tariff> getAllTariffs() {
        return tariffRepository.findAll();
    }
}
