package com.telecom.billing.service;

import com.telecom.billing.model.UsageRecord;
import com.telecom.billing.repository.UsageRecordRepository;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class UsageService {

    private final UsageRecordRepository usageRecordRepository;

    public UsageService(UsageRecordRepository usageRecordRepository) {
        this.usageRecordRepository = usageRecordRepository;
    }

    public List<UsageRecord> getUsageByCustomer(Long customerId) {
        return usageRecordRepository.findByCustomerId(customerId);
    }
}
