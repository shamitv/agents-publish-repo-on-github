package com.warehouse.config;

import com.unboundid.ldap.listener.InMemoryDirectoryServer;
import com.unboundid.ldap.listener.InMemoryDirectoryServerConfig;
import com.unboundid.ldap.listener.InMemoryListenerConfig;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ClassPathResource;
import org.springframework.ldap.core.LdapTemplate;
import org.springframework.ldap.core.support.LdapContextSource;

@Configuration
public class LdapConfig {

    private InMemoryDirectoryServer directoryServer;

    @PostConstruct
    public void startLdapServer() {
        try {
            InMemoryDirectoryServerConfig config = new InMemoryDirectoryServerConfig("dc=warehouse,dc=local");
            config.setListenerConfigs(InMemoryListenerConfig.createLDAPConfig("default", 8389));
            
            directoryServer = new InMemoryDirectoryServer(config);
            
            ClassPathResource resource = new ClassPathResource("ldap/warehouse.ldif");
            if (resource.exists()) {
                directoryServer.importFromLDIF(true, resource.getFile().getAbsolutePath());
            }
            
            directoryServer.startListening();
        } catch (Exception e) {
            System.err.println("Failed to start embedded UnboundID LDAP server: " + e.getMessage());
        }
    }

    @PreDestroy
    public void stopLdapServer() {
        if (directoryServer != null) {
            directoryServer.shutDown(true);
        }
    }

    @Bean
    public LdapContextSource contextSource() {
        LdapContextSource source = new LdapContextSource();
        source.setUrl("ldap://localhost:8389");
        source.setBase("dc=warehouse,dc=local");
        return source;
    }

    @Bean
    public LdapTemplate ldapTemplate(LdapContextSource contextSource) {
        return new LdapTemplate(contextSource);
    }
}
