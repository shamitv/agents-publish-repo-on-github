# Food Delivery Order System

## Overview
A FastAPI application representing a food delivery portal where users can browse menu items, place orders, and check status, while payment confirmation is handled via an external webhook.

## Business Domain
E-commerce & Food Delivery

## Tech Stack
- Python 3.10
- FastAPI
- SQLite (in-memory)

## Features
- User registration and login
- Browse menu items by category (e.g., Burgers, Pizza, Salads, Sides)
- Place food orders
- Retrieve details of specific orders
- Receive payment confirmation webhook from payment gateway

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/python/app-22-food-delivery/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Hardcoded Secret Key → Webhook Forgery → Free Orders"

An attacker recovers a hardcoded payment gateway secret from the codebase and uses it to forge payment confirmation webhooks, marking their orders as paid without paying.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Hardcoded payment gateway key in source code | Medium | A02 | `app.py` → `PAYMENT_SECRET` |
| 2 | Webhook endpoint validates authority via hardcoded key | Medium | A04 | `app.py` → `payment_webhook()` |

**Attack narrative**:
1. The attacker inspects the codebase (or client application environment where secrets might leak) to extract the hardcoded string `PAYMENT_SECRET`.
2. The attacker registers a customer account, browses the menu, and places a food order via `POST /api/orders`, receiving a pending order ID (e.g., `123`).
3. Instead of paying, the attacker sends a POST request directly to the webhook endpoint `/api/payment/webhook` with the payload `{"order_id": 123, "payment_status": "PAID", "auth_token": "mock_sk_live_51O1W2e3R4t5Y6u7I8o9P0a1S2d3F4g5H6j7K8l9Z0x1C2v3B4n5M"}`.
4. The server validates the token against the hardcoded secret and approves the payment state without checking signatures or origin IPs.

**Combined Impact**: `data_modification` — Attacker bypasses the payment flow and changes the order payment status to paid without actual authorization or cash flow.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/register` | None | Register new customer |
| POST   | `/api/auth/login` | None | Authenticate user and receive session cookie (vulnerable session cookie) |
| POST   | `/api/auth/logout` | Session | Terminate session |
| GET    | `/api/auth/me` | Session | Get current user status |
| GET    | `/api/menu` | None | List menu items (Decoy) |
| POST   | `/api/orders` | Session | Place a food order (vulnerable to missing rate limits) |
| GET    | `/api/orders/{order_id}` | Session | View details of an order |
| POST   | `/api/payment/webhook` | Token | Payment gateway webhook (vulnerable to forged requests) |

## Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   python app.py
   ```
3. The application runs on port `8092`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-22-food-delivery .
   ```
2. Run the container:
   ```bash
   docker run -p 8092:8092 app-22-food-delivery
   ```
