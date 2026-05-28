# Overall Security Audit Metrics Report

This report aggregates security metrics, vulnerability counts, attack chain scenarios, and difficulty distributions across the entire corpus of 50 vulnerable applications.

## Executive Summary

- **Total Applications:** 50
- **Total Standalone Vulnerabilities:** 158
- **Total Chained Attack Scenarios:** 92

| Metric | Value |
|---|---|
| Total Apps | 50 |
| Total Standalone Vulns | 158 |
| Total Chained Attack Scenarios | 92 |
| Avg Vulns per App | 3.16 |
| Avg Chains per App | 1.84 |

## Standalone Vulnerabilities Analysis

### Distribution by OWASP Top 10 Category
| OWASP Category | Description | Count | % of Total |
|---|---|---|---|
| A01 | Broken Access Control | 29 | 18.4% |
| A02 | Cryptographic Failures | 16 | 10.1% |
| A03 | Injection | 25 | 15.8% |
| A04 | Insecure Design | 13 | 8.2% |
| A05 | Security Misconfiguration | 17 | 10.8% |
| A06 | Vulnerable and Outdated Components | 6 | 3.8% |
| A07 | Identification and Authentication Failures | 17 | 10.8% |
| A08 | Software and Data Integrity Failures | 12 | 7.6% |
| A09 | Security Logging and Monitoring Failures | 12 | 7.6% |
| A10 | Server-Side Request Forgery (SSRF) | 11 | 7.0% |

### Distribution by Severity
| Severity | Count | % of Total |
|---|---|---|
| Critical | 8 | 5.1% |
| High | 63 | 39.9% |
| Medium | 79 | 50.0% |
| Low | 8 | 5.1% |

### Top CWEs (Common Weakness Enumerations)
| CWE | Count | Description |
|---|---|---|
| CWE-639 | 25 | Authorization Bypass Through User-Controlled Key ('IDOR') |
| CWE-89 | 15 | Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection') |
| CWE-778 | 12 | Insufficient Logging |
| CWE-918 | 11 | Server-Side Request Forgery (SSRF) |
| CWE-502 | 9 | Deserialization of Untrusted Data |
| CWE-209 | 7 | Other Security Weakness |
| CWE-328 | 6 | Other Security Weakness |
| CWE-330 | 5 | Use of Insufficiently Random Values |
| CWE-312 | 5 | Other Security Weakness |
| CWE-200 | 4 | Other Security Weakness |
| CWE-79 | 4 | Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') |
| CWE-307 | 3 | Improper Restriction of Excessive Authentication Attempts |
| CWE-798 | 3 | Use of Hardcoded Credentials |
| CWE-16 | 3 | Other Security Weakness |
| CWE-256 | 3 | Other Security Weakness |

## Chained Attack Scenarios Analysis

### Distribution by Combined Impact
| Impact Category | Count | Description |
|---|---|---|
| `data_modification` | 29 | Attacker writes unauthorized changes to stored records |
| `account_takeover` | 22 | Attacker gains control of a victim user account |
| `db_exfiltration` | 21 | Attacker bulk-reads sensitive database records (PII, credentials, etc.) |
| `lateral_movement` | 20 | Attacker pivots from the compromised app to other internal systems |

### Distribution by Chain Difficulty
| Chain Difficulty | Count |
|---|---|
| Hard | 55 |
| Medium | 9 |

## Grouping by App Difficulty Level

Applications are categorized into Easy, Medium, and Hard difficulty levels. These levels reflect the difficulty of the vulnerability chains, number of standalone flaws, and sophistication of decoys.

### Difficulty Level Summary
| Difficulty Level | App Count | Standalone Vulns | Exploitation Chains |
|---|---|---|---|
| Easy | 8 | 24 | 16 |
| Medium | 36 | 115 | 66 |
| Hard | 6 | 19 | 10 |

### Easy Apps (8 Apps)

| App ID | Name | Language | Framework | Vulns | Chains |
|---|---|---|---|---|---|
| app-22 | Food Delivery Order System | Python | Fastapi | 3 | 2 |
| app-48 | Freelancer Marketplace | Python | Fastapi | 3 | 2 |
| app-07 | Airline Booking System | Java | Spring-boot | 3 | 2 |
| app-08 | Warehouse Management System | Java | Spring-boot | 3 | 2 |
| app-18 | Peer-to-Peer Lending Platform | Javascript | Express | 3 | 2 |
| app-20 | Fitness Tracking API | Javascript | Express | 3 | 2 |
| app-39 | Wedding Planning Platform | Javascript | Express | 3 | 2 |
| app-44 | Election Polling System | Javascript | Express | 3 | 2 |

### Medium Apps (36 Apps)

| App ID | Name | Language | Framework | Vulns | Chains |
|---|---|---|---|---|---|
| app-02 | Healthcare Patient Portal | Python | Django | 3 | 2 |
| app-03 | Banking Transaction Service | Python | Fastapi | 3 | 2 |
| app-04 | Real Estate Listing Platform | Python | Flask | 3 | 2 |
| app-21 | Insurance Claims Processor | Python | Flask | 3 | 2 |
| app-23 | Government Permit Application Portal | Python | Django | 3 | 2 |
| app-24 | Veterinary Clinic Management | Python | Fastapi | 3 | 2 |
| app-25 | Supply Chain Inventory Tracker | Python | Flask | 3 | 2 |
| app-46 | Charity Donation Platform | Python | Flask | 3 | 2 |
| app-49 | Sports League Management | Python | Flask | 3 | 2 |
| app-06 | Enterprise HR Management System | Java | Spring-boot | 4 | 1 |
| app-09 | Legal Document Management | Java | Spring-boot | 3 | 2 |
| app-10 | Telecom Billing Platform | Java | Spring-boot | 5 | 1 |
| app-27 | Hotel Reservation System | Java | Spring-boot | 3 | 2 |
| app-28 | Manufacturing Quality Control | Java | Spring-boot | 3 | 2 |
| app-30 | Auction Platform | Java | Spring-boot | 3 | 2 |
| app-11 | Social Media Analytics Dashboard | Typescript | Express | 5 | 1 |
| app-12 | Crypto Wallet Service | Typescript | Nestjs | 3 | 2 |
| app-13 | Project Management Tool | Typescript | Express | 3 | 2 |
| app-14 | Telemedicine Appointment System | Typescript | Express | 4 | 1 |
| app-15 | Digital Asset Management | Typescript | Express | 3 | 2 |
| app-31 | Event Ticketing Platform | Typescript | Express | 3 | 2 |
| app-32 | Customer Support Ticket System | Typescript | Express | 3 | 2 |
| app-33 | Recruitment ATS Platform | Typescript | Express | 3 | 2 |
| app-34 | Subscription Box Service | Typescript | Express | 3 | 2 |
| app-35 | Compliance Document Tracker | Typescript | Express | 3 | 2 |
| app-16 | Restaurant Review Platform | Javascript | Express | 3 | 2 |
| app-17 | IoT Device Dashboard | Javascript | Express | 4 | 1 |
| app-19 | Content Management System | Javascript | Express | 3 | 2 |
| app-36 | Parking Management System | Javascript | Express | 3 | 1 |
| app-37 | Agricultural Crop Planner | Javascript | Express | 3 | 2 |
| app-38 | Museum Collection Catalog | Javascript | Express | 3 | 2 |
| app-40 | Pet Adoption Portal | Javascript | Express | 3 | 2 |
| app-41 | Library Book Reservation System | Javascript | Express | 3 | 2 |
| app-42 | Construction Project Tracker | Javascript | Express | 3 | 2 |
| app-43 | Music Streaming Playlist Service | Javascript | Express | 3 | 2 |
| app-45 | Corporate Travel & Expense System | Javascript | Express | 3 | 2 |

### Hard Apps (6 Apps)

| App ID | Name | Language | Framework | Vulns | Chains |
|---|---|---|---|---|---|
| app-01 | E-Commerce Product Catalog API | Python | Flask | 3 | 1 |
| app-05 | Online Learning Management System | Python | Flask | 3 | 1 |
| app-47 | Smart Home Device Manager | Python | Fastapi | 3 | 2 |
| app-26 | Pharmaceutical Drug Tracking | Java | Spring-boot | 3 | 2 |
| app-29 | Vehicle Fleet Management | Java | Spring-boot | 3 | 2 |
| app-50 | Energy Utility Billing | Java | Spring-boot | 4 | 2 |
