package com.manufacturing.qc.controller;

import com.manufacturing.qc.model.Product;
import com.manufacturing.qc.service.ProductService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    // DECOY: Normal security checks properly require QA_MANAGER role to view manufacturing specs
    @GetMapping
    @PreAuthorize("hasRole('QA_MANAGER')")
    public ResponseEntity<List<Product>> getProducts() {
        return ResponseEntity.ok(productService.getAllProducts());
    }
}
