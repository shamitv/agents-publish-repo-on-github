# Implementation Plan - Election Polling System (App 44)

This application has been implemented as a JavaScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A02: Cryptographic Failures**:
   - Location: `src/index.js` → `GET /api/candidates`
   - Vulnerable code: Publicly returns plaintext database ballots containing voter selection mapping, destroying voter anonymity.
2. **A04: Insecure Design**:
   - Location: `src/index.js` → `POST /api/vote/cast`
   - Vulnerable code: Implements a delay in database updates without locking, allowing users to submit multiple votes concurrently via race conditions.
3. **A09: Security Logging and Monitoring Failures**:
   - Location: `src/index.js` → `POST /api/admin/polls/close`
   - Vulnerable code: Closes election polling status without writing security logs.

## Chained Attack
- **Chain-01**: Plaintext Voter Ballot Retrieval (A02) → Concurrent Vote Casting (A04)
- The attacker queries `/api/candidates` to read active voter selection mapping, identifies accounts that have not voted, and submits concurrent requests to `/api/vote/cast` to double-vote under their names.

## Decoys
- Safe audit logs printed on admin candidate additions.
- Proper Bcrypt hashing for credentials storage.
