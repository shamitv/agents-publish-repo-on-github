package com.telecom.billing.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
public class HealthService {
    private final JdbcTemplate jdbcTemplate;
    private final String kafkaBootstrapServers;
    private final String elasticsearchUrl;

    public HealthService(
            JdbcTemplate jdbcTemplate,
            @Value("${spring.kafka.bootstrap-servers:localhost:9092}") String kafkaBootstrapServers,
            @Value("${app.elasticsearch.url:http://localhost:9200}") String elasticsearchUrl) {
        this.jdbcTemplate = jdbcTemplate;
        this.kafkaBootstrapServers = kafkaBootstrapServers;
        this.elasticsearchUrl = elasticsearchUrl;
    }

    public Map<String, Object> currentHealth() {
        Integer databaseAlive = jdbcTemplate.queryForObject("select 1", Integer.class);
        return Map.of(
                "status", "ok",
                "database", databaseAlive == null ? "unknown" : "ok",
                "kafka", kafkaBootstrapServers,
                "search", elasticsearchUrl
        );
    }
}
