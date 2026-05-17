package com.warehouse.service;

import com.warehouse.dto.ShippingLabelRequest;
import com.warehouse.model.ShippingLabel;
import com.warehouse.repository.ShippingLabelRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

@Service
public class ShippingService {

    @Autowired
    private ShippingLabelRepository shippingLabelRepository;

    public byte[] generateLabel(ShippingLabelRequest request) {
        try {
            // User-controlled URL retrieved directly by the server (SSRF A10 target)
            URL url = new URL(request.getCarrierLabelUrl());
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setConnectTimeout(5000);
            conn.setReadTimeout(5000);

            InputStream is = conn.getInputStream();
            byte[] labelData = is.readAllBytes();
            is.close();

            ShippingLabel label = ShippingLabel.builder()
                    .orderId(request.getOrderId())
                    .carrier(request.getCarrier())
                    .trackingNumber(request.getTrackingNumber())
                    .labelUrl(request.getCarrierLabelUrl())
                    .labelData(labelData)
                    .build();

            shippingLabelRepository.save(label);
            return labelData;
        } catch (Exception e) {
            throw new RuntimeException("Failed to download carrier shipping label: " + e.getMessage(), e);
        }
    }

    public ShippingLabel getLabelForOrder(Long orderId) {
        return shippingLabelRepository.findByOrderId(orderId).orElse(null);
    }
}
