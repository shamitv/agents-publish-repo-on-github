# Restaurant Review Platform

## Overview
A JavaScript Express application representing a food critique and restaurant review portal where users can search for dining spots, write critiques, and edit reviews.

## Business Domain
Local Services & Restaurant Reviews

## Tech Stack
- JavaScript (Node.js)
- Express
- SQLite (in-memory)

## Features
- User registration and login
- Restaurant list and search (vulnerable to SQLi)
- Parameterized restaurant profile lookup (Decoy: secure parameters)
- Edit restaurant reviews (vulnerable to IDOR)
- Session cookie verification (vulnerable to predictable session keys)

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/javascript/app-16-restaurant-reviews/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Predictable Session Hijacking → IDOR Review Sabotage"

An attacker guesses another user's session identifier, sets the hijacked session cookie, and calls the review editing endpoint to change high-rating reviews to low-rating ones.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Predictable session key generation via Math.random() | Medium | A07 | `src/index.js` → `POST /api/auth/login` |
| 2 | Review editing allows IDOR modification | Medium | A01 | `src/index.js` → `POST /api/reviews/:id/edit` |

**Attack narrative**:
1. The attacker observes that session cookies generated at login are numbers created via `Math.random()`.
2. The attacker guesses the active session ID of a food critic or user.
3. The attacker sets this hijacked cookie in their browser.
4. Using the hijacked session, the attacker makes a POST request to `/api/reviews/1/edit` to change the review rating or text.
5. The review is updated without checking if the hijacked user owns the review.

**Combined Impact**: `data_modification` — Attacker hijacks victim accounts and modifies client reviews.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/register` | None | Register new reviewer account |
| POST   | `/api/auth/login` | None | Authenticate reviewer (vulnerable to predictable session ID) |
| POST   | `/api/auth/logout` | Session | Clear session |
| GET    | `/api/restaurants/search` | None | Search restaurants (vulnerable to SQLi) |
| GET    | `/api/restaurants/:id` | None | Get specific restaurant details (Decoy: parameterized SQL) |
| GET    | `/api/reviews` | None | List all reviews |
| POST   | `/api/reviews/:id/edit` | Session | Edit an existing review (vulnerable to IDOR) |

## Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the application:
   ```bash
   npm start
   ```
3. The server runs on port `8016`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-16-restaurant-reviews .
   ```
2. Run the container:
   ```bash
   docker run -p 8016:8016 app-16-restaurant-reviews
   ```
