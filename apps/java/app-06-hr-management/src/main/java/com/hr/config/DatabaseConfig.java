package com.hr.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.core.JdbcTemplate;

import javax.sql.DataSource;

@Configuration
public class DatabaseConfig {
    @Bean
    public JdbcTemplate hrJdbcTemplate(DataSource dataSource) {
        return new JdbcTemplate(dataSource);
    }
}
