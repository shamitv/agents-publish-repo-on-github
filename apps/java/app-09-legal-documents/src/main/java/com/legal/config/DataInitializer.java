package com.legal.config;

import com.legal.model.Document;
import com.legal.model.LegalCase;
import com.legal.model.User;
import com.legal.repository.CaseRepository;
import com.legal.repository.DocumentRepository;
import com.legal.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private CaseRepository caseRepository;

    @Autowired
    private DocumentRepository documentRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) throws Exception {
        if (userRepository.count() > 0) {
            return;
        }

        // 1. Seed Users (passwords securely BCrypt-hashed)
        userRepository.save(User.builder()
                .username("attorney")
                .passwordHash(passwordEncoder.encode("attorney123"))
                .role("ATTORNEY")
                .build());

        userRepository.save(User.builder()
                .username("client_acme")
                .passwordHash(passwordEncoder.encode("client123"))
                .role("CLIENT")
                .build());

        userRepository.save(User.builder()
                .username("client_zenith")
                .passwordHash(passwordEncoder.encode("client123"))
                .role("CLIENT")
                .build());

        userRepository.save(User.builder()
                .username("admin")
                .passwordHash(passwordEncoder.encode("admin123"))
                .role("ADMIN")
                .build());

        // 2. Seed 4 Legal Cases
        LegalCase case1 = caseRepository.save(LegalCase.builder()
                .title("Acme vs Globex Corp Patent Infringement")
                .description("Litigation concerning violation of proprietary automated inventory tracking algorithms and server schematics.")
                .clientOwner("client_acme")
                .status("ACTIVE")
                .createdAt(LocalDateTime.now().minusDays(10))
                .build());

        LegalCase case2 = caseRepository.save(LegalCase.builder()
                .title("Zenith Mfg FTC Antitrust Investigation")
                .description("Regulatory inquiry regarding market share consolidation, vendor exclusivity terms, and anti-competitive practices.")
                .clientOwner("client_zenith")
                .status("ACTIVE")
                .createdAt(LocalDateTime.now().minusDays(8))
                .build());

        LegalCase case3 = caseRepository.save(LegalCase.builder()
                .title("Acme Corp IRS Corporate Tax Audit")
                .description("Auditing of offshore subsidiary tax filings, asset valuations, and transfer pricing documentation (FY 2024-2025).")
                .clientOwner("client_acme")
                .status("ACTIVE")
                .createdAt(LocalDateTime.now().minusDays(5))
                .build());

        LegalCase case4 = caseRepository.save(LegalCase.builder()
                .title("Merger Acquisition Briefing: Acme & Zenith")
                .description("Confidential preliminary evaluation of merger opportunities, share conversions, and executive board restructured mappings.")
                .clientOwner("client_acme")
                .status("CLOSED")
                .createdAt(LocalDateTime.now().minusDays(12))
                .build());

        // 3. Seed 10 Sensitive Legal Documents (Plaintext columns storage - A02 Target)
        documentRepository.save(Document.builder()
                .caseId(case1.getId())
                .title("Patent Violation Brief Sheet")
                .filename("globex_patent_brief_2026.txt")
                .fileContentPlaintext("CONFIDENTIAL PATENT ANALYSIS:\nGlobex has replicated the custom sorting engine in our warehouse firmware line-for-line. Exhibit A shows standard code comparisons in the CPU stack. Damages are estimated at $4.5 Million.")
                .uploadedBy("attorney")
                .createdAt(LocalDateTime.now().minusDays(9))
                .build());

        documentRepository.save(Document.builder()
                .caseId(case1.getId())
                .title("Mutual NDA Agreement")
                .filename("acme_globex_nda.txt")
                .fileContentPlaintext("MUTUAL NON-DISCLOSURE AGREEMENT:\nBoth corporations agree not to disclose technical or operational specifications regarding automated logistics. Violation carries automatic injunction penalties of $1 Million per breach.")
                .uploadedBy("client_acme")
                .createdAt(LocalDateTime.now().minusDays(9))
                .build());

        documentRepository.save(Document.builder()
                .caseId(case1.getId())
                .title("CEO Deposition Transcript")
                .filename("deposition_acme_ceo.txt")
                .fileContentPlaintext("DEPOSITION TRANSCRIPT - JOHN DOE (CEO, ACME):\nQ: When did you first notice Globex copying your algorithmic pipeline?\nA: In November 2025, during an open API integration audit. The endpoint mappings were identical.")
                .uploadedBy("attorney")
                .createdAt(LocalDateTime.now().minusDays(7))
                .build());

        documentRepository.save(Document.builder()
                .caseId(case2.getId())
                .title("FTC Exclusivity Excerpts")
                .filename("ftc_exclusivity_audit.txt")
                .fileContentPlaintext("ATTORNEY WORK PRODUCT - PRIVILEGED:\nFTC investigators possess copies of internal emails outlining pricing penalties for distributors who buy competitor units. We must argue these are optional discounts, not forced exclusivity.")
                .uploadedBy("attorney")
                .createdAt(LocalDateTime.now().minusDays(7))
                .build());

        documentRepository.save(Document.builder()
                .caseId(case2.getId())
                .title("FTC Civil Investigative Demand")
                .filename("ftc_civil_demand_2026.txt")
                .fileContentPlaintext("CIVIL INVESTIGATIVE DEMAND:\nThe Zenith Mfg Corporation is required to surrender all board meeting minutes discussing competitive acquisitions between 2023 and 2026.")
                .uploadedBy("client_zenith")
                .createdAt(LocalDateTime.now().minusDays(6))
                .build());

        documentRepository.save(Document.builder()
                .caseId(case3.getId())
                .title("Offshore Subsidiary Balance Sheet")
                .filename("cayman_islands_holdings_2025.txt")
                .fileContentPlaintext("ACME CAYMAN HOLDINGS PLC:\nTotal cash reserves: $14.2 Million. Intangible assets transferred from US parent for $100. Tax liability in the Cayman Islands: 0.00%.")
                .uploadedBy("client_acme")
                .createdAt(LocalDateTime.now().minusDays(4))
                .build());

        documentRepository.save(Document.builder()
                .caseId(case3.getId())
                .title("IRS Revenue Agent Interview Prep")
                .filename("irs_interview_guidance.txt")
                .fileContentPlaintext("PRIVILEGED LEGAL STRATEGY:\nFor the IRS interview on May 24, do not volunteer details about the Cayman IP transfer. If asked directly, define the valuation using the safe harbor licensing formulas.")
                .uploadedBy("attorney")
                .createdAt(LocalDateTime.now().minusDays(3))
                .build());

        documentRepository.save(Document.builder()
                .caseId(case4.getId())
                .title("Acme & Zenith Preliminary Valuation")
                .filename("acme_zenith_merger_eval.txt")
                .fileContentPlaintext("MERGER AND ACQUISITION ANALYSIS:\nAcme proposes an all-stock transaction converting 1.2 Zenith shares into 1 Acme share. Zenith is currently valued at $22 Million.")
                .uploadedBy("attorney")
                .createdAt(LocalDateTime.now().minusDays(11))
                .build());

        documentRepository.save(Document.builder()
                .caseId(case4.getId())
                .title("Target Executive Compensation Agreement")
                .filename("exec_comp_package.txt")
                .fileContentPlaintext("GOLDEN PARACHUTE TERMS:\nUpon merger completion, Zenith CEO will receive $1.8 Million severance. Chief Legal Officer package is fixed at $950,000.")
                .uploadedBy("attorney")
                .createdAt(LocalDateTime.now().minusDays(11))
                .build());

        documentRepository.save(Document.builder()
                .caseId(case4.getId())
                .title("Board Vote Resolution")
                .filename("merger_board_vote.txt")
                .fileContentPlaintext("RESOLVED:\nThe Acme board of directors unanimously approves the merger prospectus and authorizes legal counsel to submit the merger registration forms on June 1, 2026.")
                .uploadedBy("client_acme")
                .createdAt(LocalDateTime.now().minusDays(10))
                .build());
    }
}
