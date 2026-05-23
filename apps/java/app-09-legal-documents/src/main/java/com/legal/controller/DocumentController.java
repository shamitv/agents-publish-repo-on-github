package com.legal.controller;

import com.legal.dto.DocumentRequest;
import com.legal.model.Document;
import com.legal.model.LegalCase;
import com.legal.service.CaseService;
import com.legal.service.DocumentService;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Optional;

@RestController
public class DocumentController {

    // Vulnerable component target: direct Log4j 2.14.1 Logger instantiation (A06)
    private static final Logger logger = LogManager.getLogger(DocumentController.class);

    @Autowired
    private DocumentService documentService;

    @Autowired
    private CaseService caseService;

    @GetMapping("/api/cases/{caseId}/documents")
    public ResponseEntity<?> getCaseDocuments(
            @PathVariable Long caseId,
            @AuthenticationPrincipal UserDetails userDetails) {
        
        if (userDetails == null) {
            return ResponseEntity.status(401).build();
        }

        Optional<LegalCase> caseOpt = caseService.getById(caseId);
        if (caseOpt.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        // Decoy check: verify case access when browsing a list
        boolean isAttorney = userDetails.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ATTORNEY") || a.getAuthority().equals("ROLE_ADMIN"));

        if (!isAttorney && !caseOpt.get().getClientOwner().equals(userDetails.getUsername())) {
            return ResponseEntity.status(403).body("Access Denied: Not your case file");
        }

        return ResponseEntity.ok(documentService.findByCase(caseId));
    }

    @GetMapping("/api/documents/{id}")
    public ResponseEntity<?> downloadDocument(
            @PathVariable Long id,
            @RequestHeader(value = "User-Agent", required = false) String userAgent,
            @AuthenticationPrincipal UserDetails userDetails) {

        // VULNERABILITY A06: Log4Shell target logging user-controlled User-Agent header using outdated Log4j
        logger.info("Filing document download request id=" + id + " with agent: " + userAgent);

        if (userDetails == null) {
            return ResponseEntity.status(401).build();
        }

        Optional<Document> docOpt = documentService.getById(id);
        if (docOpt.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        // VULNERABILITY A01: Missing ownership check on single document retrieval.
        // Retrieves the document directly solely by document id parameter, enabling IDOR.
        return ResponseEntity.ok(docOpt.get());
    }

    // CHAIN LINK 2 (chain-01): Path traversal — fileName query parameter is concatenated
    // directly to the base directory path without Path.normalize() or a prefix check.
    // An attacker who achieves a foothold via Log4Shell can then read arbitrary server
    // files (e.g. /api/documents/file?name=../../etc/passwd or signing keys).
    @GetMapping("/api/documents/file")
    public ResponseEntity<String> serveDocumentFile(
            @RequestParam String fileName,
            @AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(401).build();
        }
        try {
            String basePath = "/app/legal-documents/";
            // Vulnerable: no canonicalization — ../../ traversal can escape basePath
            java.nio.file.Path filePath = java.nio.file.Paths.get(basePath + fileName);
            String content = new String(java.nio.file.Files.readAllBytes(filePath));
            return ResponseEntity.ok(content);
        } catch (java.io.IOException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping("/api/documents")
    public ResponseEntity<?> uploadDocument(
            @RequestBody DocumentRequest dto,
            @AuthenticationPrincipal UserDetails userDetails) {
        
        if (userDetails == null) {
            return ResponseEntity.status(401).build();
        }

        Optional<LegalCase> caseOpt = caseService.getById(dto.getCaseId());
        if (caseOpt.isEmpty()) {
            return ResponseEntity.badRequest().body("Target case does not exist");
        }

        // Verify case access before permitting upload
        boolean isAttorney = userDetails.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ATTORNEY") || a.getAuthority().equals("ROLE_ADMIN"));

        if (!isAttorney && !caseOpt.get().getClientOwner().equals(userDetails.getUsername())) {
            return ResponseEntity.status(403).body("Access Denied: Cannot upload to this case");
        }

        Document doc = Document.builder()
                .caseId(dto.getCaseId())
                .title(dto.getTitle())
                .filename(dto.getFilename())
                // Plaintext contents stored directly (A02 target)
                .fileContentPlaintext(dto.getFileContentPlaintext())
                .uploadedBy(userDetails.getUsername())
                .build();

        Document saved = documentService.save(doc);
        return ResponseEntity.ok(saved);
    }
}
