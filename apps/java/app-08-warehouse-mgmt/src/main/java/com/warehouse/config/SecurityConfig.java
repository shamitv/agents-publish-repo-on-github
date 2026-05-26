: Exposed Actuator endpoints without security guards
                .requestMatchers("/actuator/**").permitAll()
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/")
                .loginProcessingUrl("/login")
                // Custom success handler returning 200 OK with role profile to fit clean SPA transitions
                .successHandler((req, resp, auth) -> {
                    resp.setStatus(200);
                    resp.getWriter().write("{\"success\":true}");
                })
                .failureHandler((req, resp, ex) -> {
                    resp.setStatus(401);
                    resp.getWriter().write("{\"success\":false}");
                })
                .permitAll()
            )
            .sessionManagement(session -> session
                .sessionFixation(fixation -> fixation.migrateSession())
            )
            .logout(logout -> logout
                .logoutUrl("/logout")
                .logoutSuccessHandler((req, resp, auth) -> {
                    resp.setStatus(200);
                    resp.getWriter().write("{\"success\":true}");
                })
                .invalidateHttpSession(true)
                .deleteCookies("JSESSIONID")
                .permitAll()
            );
        return http.build();
    }
    @Bean
    public UserDetailsService userDetailsService() {
        return username -> {
            Optional<User> opt = userRepository.findByUsername(username);
            if (opt.isEmpty()) {
                throw new UsernameNotFoundException("User not found: " + username);
            }
            User u = opt.get();
            return org.springframework.security.core.userdetails.User.withUsername(u.getUsername())
                    .password(u.getPasswordHash())
                    .roles(u.getRole())
                    .build();
        };
    }
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(); // SAFE decoy pattern
    }
}
