package com.airline.config;

import com.airline.model.Passenger;
import com.airline.repository.PassengerRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.header.writers.XXssProtectionHeaderWriter;

import java.util.Optional;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    @Autowired
    private PassengerRepository passengerRepository;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable()) // Disable CSRF to ease API testing and demonstration
            .headers(headers -> headers
                .frameOptions(frame -> frame.disable()) // Allow H2 console frames
                .xssProtection(xss -> xss.headerValue(XXssProtectionHeaderWriter.HeaderValue.ENABLED_MODE_BLOCK))
            )
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/", "/register", "/api/flights/search", "/h2-console/**", "/css/**", "/js/**").permitAll()
                .requestMatchers("/api/flights").hasRole("AIRLINE_STAFF")
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/")
                .loginProcessingUrl("/login")
                .defaultSuccessUrl("/dashboard", true)
                .usernameParameter("email")
                .passwordParameter("password")
                .permitAll()
            )
            .sessionManagement(session -> session
                // VULNERABILITY A07: Session fixation protection is disabled, so login keeps the old session ID.
                .sessionFixation(fixation -> fixation.none())
            )
            .logout(logout -> logout
                .logoutUrl("/logout")
                .logoutSuccessUrl("/?logout=true")
                .invalidateHttpSession(true)
                .deleteCookies("JSESSIONID")
                .permitAll()
            );

        return http.build();
    }

    @Bean
    public UserDetailsService userDetailsService() {
        return email -> {
            Optional<Passenger> opt = passengerRepository.findByEmail(email);
            if (opt.isEmpty()) {
                throw new UsernameNotFoundException("User not found: " + email);
            }
            Passenger p = opt.get();
            return User.withUsername(p.getEmail())
                    .password(p.getPasswordHash())
                    .roles(p.getRole())
                    .build();
        };
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(); // BCrypt is secure (decoy)
    }
}
