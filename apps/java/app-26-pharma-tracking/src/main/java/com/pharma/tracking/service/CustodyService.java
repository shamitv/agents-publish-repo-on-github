package com.pharma.tracking.service;
import com.pharma.tracking.model.CustodyRecord;
import com.pharma.tracking.repository.CustodyRecordRepository;
import org.springframework.stereotype.Service;
import java.security.MessageDigest;
import java.time.LocalDateTime;
@Service
public class CustodyService {
    private final CustodyRecordRepository custodyRecordRepository;
    public CustodyService(CustodyRecordRepository custodyRecordRepository) {
        this.custodyRecordRepository = custodyRecordRepository;
    }
    public String generateCustodySignature(Long batchId, String timestamp, String fromEntity, String toEntity) {
        try {
            String payload = batchId + ":" + timestamp + ":" + fromEntity + ":" + toEntity;
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] hashBytes = md.digest(payload.getBytes("UTF-8"));
            StringBuilder sb = new StringBuilder();
            for (byte b : hashBytes) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            throw new RuntimeException("Error generating signature", e);
        }
    }
    public CustodyRecord recordTransfer(Long batchId, String fromEntity, String toEntity) {
        String timestamp = LocalDateTime.now().toString();
        String signature = generateCustodySignature(batchId, timestamp, fromEntity, toEntity);
        CustodyRecord record = new CustodyRecord();
        record.setBatchId(batchId);
        record.setFromEntity(fromEntity);
        record.setToEntity(toEntity);
        record.setTransferredAt(LocalDateTime.now());
        record.setSignatureHash(signature);
        return custodyRecordRepository.save(record);
    }
}