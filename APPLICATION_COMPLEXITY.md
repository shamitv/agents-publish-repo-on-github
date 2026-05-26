# Application Complexity Inventory

This file ranks each benchmark application by implementation complexity. The scale is based on the current repository shape: source-file count, endpoint/controller count, UI assets, services, repositories/models, cache layers, messaging/search/integration pieces, database/config components, and Docker Compose usage.

Endpoint counts are static estimates from source patterns, so they are meant as complexity signals rather than a runtime API contract.

## Complexity Scale

| Level | Label | Interpretation |
|-------|-------|----------------|
| 1 | Very Simple | Compact app, usually one backend file plus minimal support files. |
| 2 | Simple | Small app with a modest number of files or light framework structure. |
| 3 | Moderate | Noticeable separation of routes, data, and behavior, but limited infrastructure. |
| 4 | Complex | Layered app with multiple controllers/services/repositories or substantial domain logic. |
| 5 | Very Complex | Multi-layer app with many APIs plus integrations such as caches, messaging, search, multiple DB/config components, or Docker Compose. |

## Applications

| # | Application | Stack | Complexity | Basis |
|---|-------------|-------|------------|-------|
| 01 | [E-Commerce Product Catalog API](apps/python/app-01-ecommerce-catalog/README.md) | Python / Flask | 5 - Very Complex | 38 source files; 13 endpoints; UI; controllers, route modules, services, repositories; messaging, search, DB config; Docker Compose. |
| 02 | [Healthcare Patient Portal](apps/python/app-02-patient-portal/README.md) | Python / Django | 2 - Simple | 14 source files; Django app layout; UI assets; light model/data layer. |
| 03 | [Banking Transaction Service](apps/python/app-03-banking-service/README.md) | Python / FastAPI | 1 - Very Simple | 5 source files; 2 endpoints; UI assets; compact implementation. |
| 04 | [Real Estate Listing Platform](apps/python/app-04-real-estate/README.md) | Python / Flask | 1 - Very Simple | 5 source files; 4 endpoints; UI assets; compact implementation. |
| 05 | [Online Learning Management System](apps/python/app-05-learning-mgmt/README.md) | Python / Flask | 5 - Very Complex | 40 source files; 14 endpoints; many controllers, routes, services, repositories; workers and DB config; Docker Compose. |
| 06 | [Enterprise HR Management System](apps/java/app-06-hr-management/README.md) | Java / Spring Boot | 5 - Very Complex | 40 source files; 23 endpoints; UI; controllers, services, repositories; cache, messaging, search, DB config; Docker Compose. |
| 07 | [Airline Booking System](apps/java/app-07-airline-booking/README.md) | Java / Spring Boot | 5 - Very Complex | 36 source files; 20 endpoints; UI; multiple controllers, services, repositories, and domain models. |
| 08 | [Warehouse Management System](apps/java/app-08-warehouse-mgmt/README.md) | Java / Spring Boot | 5 - Very Complex | 35 source files; 23 endpoints; UI; controllers, services, repositories, LDAP/search integration. |
| 09 | [Legal Document Management](apps/java/app-09-legal-documents/README.md) | Java / Spring Boot | 4 - Complex | 21 source files; 9 endpoints; UI; controllers, services, repositories, and domain models. |
| 10 | [Telecom Billing Platform](apps/java/app-10-telecom-billing/README.md) | Java / Spring Boot | 5 - Very Complex | 34 source files; 15 endpoints; controllers, services, repositories; cache, messaging, search, DB config; Docker Compose. |
| 11 | [Social Media Analytics Dashboard](apps/typescript/app-11-social-analytics/README.md) | TypeScript / Express | 5 - Very Complex | 33 source files; 11 endpoints; UI; controllers, routes, services, repositories; cache, messaging, search, DB config; Docker Compose. |
| 12 | [Crypto Wallet Service](apps/typescript/app-12-crypto-wallet/README.md) | TypeScript / NestJS | 2 - Simple | 12 source files; 7 endpoints; UI assets; one controller, service, and DB helper. |
| 13 | [Project Management Tool](apps/typescript/app-13-project-mgmt/README.md) | TypeScript / Express | 1 - Very Simple | 5 source files; 3 endpoints; UI assets; compact implementation. |
| 14 | [Telemedicine Appointment System](apps/typescript/app-14-telemedicine/README.md) | TypeScript / Express | 4 - Complex | 22 source files; 7 endpoints; controllers, routes, services, repositories; cache, messaging, search, DB config; Docker Compose. |
| 15 | [Digital Asset Management](apps/typescript/app-15-digital-assets/README.md) | TypeScript / Express | 1 - Very Simple | 2 source files; 7 endpoints; compact single-file style. |
| 16 | [Restaurant Review Platform](apps/javascript/app-16-restaurant-reviews/README.md) | JavaScript / Express | 1 - Very Simple | 2 source files; 8 endpoints; compact single-file style. |
| 17 | [IoT Device Dashboard](apps/javascript/app-17-iot-dashboard/README.md) | JavaScript / Express | 5 - Very Complex | 25 source files; 8 endpoints; UI; controllers, routes, services, repositories; cache, messaging, search, DB config; Docker Compose. |
| 18 | [Peer-to-Peer Lending Platform](apps/javascript/app-18-p2p-lending/README.md) | JavaScript / Express | 1 - Very Simple | 2 source files; 8 endpoints; compact single-file style. |
| 19 | [Content Management System](apps/javascript/app-19-cms/README.md) | JavaScript / Express | 1 - Very Simple | 2 source files; 9 endpoints; compact single-file style. |
| 20 | [Fitness Tracking API](apps/javascript/app-20-fitness-tracker/README.md) | JavaScript / Express | 1 - Very Simple | 2 source files; 6 endpoints; compact single-file style. |
| 21 | [Insurance Claims Processor](apps/python/app-21-insurance-claims/README.md) | Python / Flask | 1 - Very Simple | 2 source files; 10 endpoints; compact single-file style. |
| 22 | [Food Delivery Order System](apps/python/app-22-food-delivery/README.md) | Python / FastAPI | 1 - Very Simple | 2 source files; 16 endpoints; compact single-file style. |
| 23 | [Government Permit Application Portal](apps/python/app-23-govt-permits/README.md) | Python / Django | 1 - Very Simple | 11 source files; small Django layout; light model/data layer. |
| 24 | [Veterinary Clinic Management](apps/python/app-24-vet-clinic/README.md) | Python / FastAPI | 1 - Very Simple | 2 source files; 14 endpoints; compact single-file style. |
| 25 | [Supply Chain Inventory Tracker](apps/python/app-25-supply-chain/README.md) | Python / Flask | 1 - Very Simple | 2 source files; 3 endpoints; compact single-file style. |
| 26 | [Pharmaceutical Drug Tracking](apps/java/app-26-pharma-tracking/README.md) | Java / Spring Boot | 4 - Complex | 25 source files; 12 endpoints; controllers, services, repositories, and domain models. |
| 27 | [Hotel Reservation System](apps/java/app-27-hotel-reservation/README.md) | Java / Spring Boot | 4 - Complex | 24 source files; 10 endpoints; controllers, services, repositories, and domain models. |
| 28 | [Manufacturing Quality Control](apps/java/app-28-mfg-quality/README.md) | Java / Spring Boot | 4 - Complex | 22 source files; 9 endpoints; controllers, services, repositories, and domain models. |
| 29 | [Vehicle Fleet Management](apps/java/app-29-fleet-management/README.md) | Java / Spring Boot | 4 - Complex | 21 source files; 8 endpoints; controllers, services, repositories, and domain models. |
| 30 | [Auction Platform](apps/java/app-30-auction-platform/README.md) | Java / Spring Boot | 4 - Complex | 22 source files; 8 endpoints; controllers, services, repositories, and domain models. |
| 31 | [Event Ticketing Platform](apps/typescript/app-31-event-ticketing/README.md) | TypeScript / Express | 1 - Very Simple | 2 source files; 6 endpoints; compact single-file style. |
| 32 | [Customer Support Ticket System](apps/typescript/app-32-support-tickets/README.md) | TypeScript / Express | 1 - Very Simple | 2 source files; 9 endpoints; compact single-file style. |
| 33 | [Recruitment ATS Platform](apps/typescript/app-33-recruitment-ats/README.md) | TypeScript / Express | 1 - Very Simple | 2 source files; 7 endpoints; compact single-file style. |
| 34 | [Subscription Box Service](apps/typescript/app-34-subscription-box/README.md) | TypeScript / Express | 1 - Very Simple | 2 source files; 7 endpoints; compact single-file style. |
| 35 | [Compliance Document Tracker](apps/typescript/app-35-compliance-tracker/README.md) | TypeScript / Express | 1 - Very Simple | 2 source files; 8 endpoints; compact single-file style. |
| 36 | [Parking Management System](apps/javascript/app-36-parking-mgmt/README.md) | JavaScript / Express | 5 - Very Complex | 27 source files; 9 endpoints; UI; controllers, routes, services, repositories; cache, messaging, search, DB config; Docker Compose. |
| 37 | [Agricultural Crop Planner](apps/javascript/app-37-crop-planner/README.md) | JavaScript / Express | 1 - Very Simple | 2 source files; 9 endpoints; compact single-file style. |
| 38 | [Museum Collection Catalog](apps/javascript/app-38-museum-catalog/README.md) | JavaScript / Express | 1 - Very Simple | 2 source files; 8 endpoints; compact single-file style. |
| 39 | [Wedding Planning Platform](apps/javascript/app-39-wedding-planner/README.md) | JavaScript / Express | 1 - Very Simple | 2 source files; 7 endpoints; compact single-file style. |
| 40 | [Pet Adoption Portal](apps/javascript/app-40-pet-adoption/README.md) | JavaScript / Express | 1 - Very Simple | 2 source files; 8 endpoints; compact single-file style. |
| 41 | [Library Book Reservation System](apps/javascript/app-41-library-reservation/README.md) | JavaScript / Express | 1 - Very Simple | 2 source files; 7 endpoints; compact single-file style. |
| 42 | [Construction Project Tracker](apps/javascript/app-42-construction-tracker/README.md) | JavaScript / Express | 1 - Very Simple | 2 source files; 8 endpoints; compact single-file style. |
| 43 | [Music Streaming Playlist Service](apps/javascript/app-43-music-streaming/README.md) | JavaScript / Express | 1 - Very Simple | 2 source files; 9 endpoints; compact single-file style. |
| 44 | [Election Polling System](apps/javascript/app-44-election-polling/README.md) | JavaScript / Express | 1 - Very Simple | 2 source files; 7 endpoints; compact single-file style. |
| 45 | [Corporate Travel & Expense System](apps/javascript/app-45-travel-expense/README.md) | JavaScript / Express | 1 - Very Simple | 2 source files; 7 endpoints; compact single-file style. |
| 46 | [Charity Donation Platform](apps/python/app-46-charity-donations/README.md) | Python / Flask | 1 - Very Simple | 2 source files; 8 endpoints; compact single-file style. |
| 47 | [Smart Home Device Manager](apps/python/app-47-smart-home/README.md) | Python / FastAPI | 1 - Very Simple | 2 source files; 14 endpoints; compact single-file style. |
| 48 | [Freelancer Marketplace](apps/python/app-48-freelancer-market/README.md) | Python / FastAPI | 1 - Very Simple | 2 source files; 14 endpoints; compact single-file style. |
| 49 | [Sports League Management](apps/python/app-49-sports-league/README.md) | Python / Flask | 1 - Very Simple | 2 source files; 1 endpoint; compact single-file style. |
| 50 | [Energy Utility Billing](apps/java/app-50-energy-billing/README.md) | Java / Spring Boot | 4 - Complex | 27 source files; 12 endpoints; controllers, services, repositories, and domain models. |
