# Implementation Plan — App 12: Crypto Wallet Service

## 1. Project Scaffold

### 1.1 Scaffold layout:
```
apps/typescript/app-12-crypto-wallet/
├── README.md
├── impl_plan.md
├── .vulns
├── Dockerfile
├── package.json
├── tsconfig.json
├── tsconfig.build.json
├── nest-cli.json
├── src/
│   ├── main.ts
│   ├── app.module.ts
│   ├── auth/
│   │   ├── auth.module.ts
│   │   ├── auth.guard.ts
│   └── wallet/
│       ├── wallet.module.ts
│       ├── wallet.controller.ts
│       └── wallet.service.ts
└── public/
    ├── index.html
    ├── css/
    │   └── main.css
    └── js/
        └── app.js
```

---

## 2. Mock Database

The database runs on an in-memory data structure:
- `users`: User profiles (username, password, role).
- `wallets`: Crypto wallets holding balances and cryptographic keys.
- `transactions`: Transfer history between wallets.

---

## 3. Backend REST API Endpoints

- `GET /`: Serves static SPA dashboard template.
- `POST /api/auth/login`: Process authentication parameters.
- `POST /api/auth/logout`: Clears authentication details.
- `GET /api/auth/me`: Retrieves currently authenticated user session.
- `GET /api/wallet`: Retrieves the user's wallet details and balance.
- `POST /api/wallet/transfer`: Initiates a crypto transfer to another wallet.
- `GET /api/wallet/transactions`: Lists the user's transfer history.

---

## 4. Frontend SPA Portal

Modern client-side Single Page Application (SPA) served under static routes. Contains:
- Crypto portal login panel.
- Dynamic Wallet Dashboard displaying balances and addresses.
- Transaction history list.
- Quick Transfer interface for sending funds instantly.
- Sleek, modern "Dark Crypto" theme using HTML5, CSS3, and vanilla JS.

---

## 5. Testing

Standard manual testing verifying:
- Login authentication flows.
- Wallet balance retrieval.
- Transferring funds between users.
