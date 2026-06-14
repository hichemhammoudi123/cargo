# Graphify Report — Cargo Delivery Service

**Generated:** 2026-06-14  
**Repository:** D:\cargo  
**Analysis Scope:** Full codebase (architecture docs, frontend source, mock data, status mapping engine)

---

## 1. Executive Summary

Centralized multi-carrier logistics platform unifying **DHL, FedEx, UPS, Chronopost** under a single `CarrierAdapter` interface. The core engine is a 3-tier status mapper (exact → regex → fuzzy) translating 64+ carrier codes into 12 unified internal codes. The React + Vite + Tailwind TypeScript SPA provides full CRUD, JWT mock authentication, and trilingual support (EN/FR/TR).

---

## 2. API — Complete Endpoints with JSON

### 2.1 Reference Table (20 endpoints)

| # | Method | Path | Purpose | Frontend Page |
|---|---|---|---|---|
| 1 | POST | `/api/v1/cargo/auth/login` | Authenticate & get JWT token | Login |
| 2 | POST | `/api/v1/cargo/rates` | Get carrier pricing | Rates |
| 3 | POST | `/api/v1/cargo/shipments` | Create a shipment | Shipments |
| 4 | GET | `/api/v1/cargo/shipments` | List shipments | Shipments |
| 5 | GET | `/api/v1/cargo/shipments/{id}` | Shipment detail + status history | ShipmentDetail |
| 6 | GET | `/api/v1/cargo/shipments/{id}/tracking` | Detailed tracking events | ShipmentDetail |
| 7 | POST | `/api/v1/cargo/shipments/{id}/cancel` | Cancel a shipment | ShipmentDetail |
| 8 | POST | `/api/v1/cargo/shipments/{id}/label` | Generate shipping label | ShipmentDetail |
| 9 | POST | `/api/v1/cargo/pickups` | Schedule a pickup | Pickups |
| 10 | POST | `/api/v1/cargo/webhooks/{carrierCode}` | Receive carrier push updates | WebhookLogs |
| 11 | POST | `/api/v1/cargo/addresses/validate` | Validate & normalize address | Shipments form |
| 12 | POST | `/api/v1/cargo/carriers` | Add a carrier | Carriers |
| 13 | GET | `/api/v1/cargo/carriers` | List carriers | Carriers |
| 14 | GET | `/api/v1/cargo/carriers/{code}` | Carrier detail | CarrierDetail |
| 15 | PUT | `/api/v1/cargo/carriers/{code}` | Update carrier settings | CarrierDetail |
| 16 | PATCH | `/api/v1/cargo/carriers/{code}/toggle` | Enable/disable carrier | CarrierDetail |
| 17 | POST | `/api/v1/cargo/carriers/{code}/test` | Test carrier API connection | CarrierDetail |
| 18 | POST | `/api/v1/cargo/carriers/{code}/services` | Add a service | CarrierDetail |
| 19 | PUT | `/api/v1/cargo/carriers/{code}/credentials` | Update API keys | CarrierDetail |
| 20 | DELETE | `/api/v1/cargo/carriers/{code}` | Delete a carrier | Carriers |

---

### 2.2 POST — Creation / Action

#### `POST /api/v1/cargo/auth/login`
Authenticate user and return a mock JWT token.

```json
// Request
{ "email": "admin@cargo.com", "password": "admin" }

// Response 200
{
  "success": true,
  "user": { "email": "admin@cargo.com", "name": "admin", "role": "admin" },
  "token": "mock-jwt-a1b2c3d4"
}
```

#### `POST /api/v1/cargo/rates`
Compare prices from all active carriers for a shipment.

```json
// Request
{
  "sender": { "country": "FR", "zipCode": "75001", "city": "Paris", "address": "12 Rue de Rivoli" },
  "recipient": { "country": "DE", "zipCode": "10115", "city": "Berlin", "address": "Friedrichstraße 100" },
  "packages": [{ "weight": 2.5, "weightUnit": "KG", "length": 30, "width": 20, "height": 15, "dimUnit": "CM" }],
  "options": { "carrierCodes": ["DHL", "FEDEX"], "serviceType": "EXPRESS" }
}

// Response 200
{
  "success": true,
  "data": [
    {
      "carrierCode": "DHL", "carrierName": "DHL Express",
      "serviceCode": "DHL_EXPRESS_WORLDWIDE", "serviceName": "Express Worldwide",
      "totalPrice": 45.30, "currency": "EUR",
      "estimatedTransitDays": 2, "estimatedDeliveryDate": "2026-06-13",
      "breakdown": [
        { "type": "BASE", "label": "Transport", "amount": 38.00 },
        { "type": "FUEL", "label": "Fuel surcharge", "amount": 5.30 },
        { "type": "INSURANCE", "label": "Insurance", "amount": 2.00 }
      ]
    },
    {
      "carrierCode": "FEDEX", "carrierName": "FedEx",
      "serviceCode": "FEDEX_PRIORITY", "serviceName": "FedEx Priority",
      "totalPrice": 48.50, "currency": "EUR",
      "estimatedTransitDays": 1, "estimatedDeliveryDate": "2026-06-12",
      "breakdown": [
        { "type": "BASE", "label": "Transport", "amount": 41.00 },
        { "type": "FUEL", "label": "Fuel surcharge", "amount": 5.50 },
        { "type": "INSURANCE", "label": "Insurance", "amount": 2.00 }
      ]
    }
  ]
}
```

#### `POST /api/v1/cargo/shipments`
Create a real shipment with a carrier. Payload: sender + recipient + packages + options.

```json
// Request (20+ fields)
{
  "carrierCode": "DHL", "serviceCode": "DHL_EXPRESS_WORLDWIDE", "reference": "ORD-2026-001234",
  "sender": { "company": "TechCorp Inc", "contactName": "John Doe", "email": "john@techcorp.com",
    "phone": "+33123456789", "country": "FR", "zipCode": "75001", "city": "Paris", "address": "12 Rue de Rivoli" },
  "recipient": { "company": "Berlin GmbH", "contactName": "Hans Schmidt", "email": "hans@berlin.de",
    "phone": "+4930123456", "country": "DE", "zipCode": "10115", "city": "Berlin", "address": "Friedrichstraße 100" },
  "packages": [{
    "reference": "PARCEL-001", "description": "Electronic components",
    "weight": 2.5, "weightUnit": "KG", "length": 30, "width": 20, "height": 15, "dimUnit": "CM",
    "declaredValue": 500.00, "declaredCurrency": "EUR"
  }],
  "options": { "insurance": { "amount": 500.00, "currency": "EUR" }, "signatureRequired": true }
}

// Response 201
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5", "status": "CREATED",
    "carrierCode": "DHL", "carrierTrackingNumber": "1234567890",
    "labelUrl": "https://api.dhl.com/labels/1234567890.pdf",
    "trackingUrl": "https://www.dhl.com/track/1234567890",
    "price": { "total": 45.30, "currency": "EUR", "breakdown": [
      { "type": "BASE", "amount": 38.00 }, { "type": "FUEL", "amount": 5.30 }, { "type": "INSURANCE", "amount": 2.00 }
    ]},
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z",
    "createdAt": "2026-06-11T10:30:00Z"
  }
}
```

#### `POST /api/v1/cargo/shipments/{id}/cancel`
Cancel a shipment. Status changes to `CANCELLED`.

```json
// Response
{
  "success": true,
  "data": { "id": "shp_a1b2c3d4e5", "status": "CANCELLED", "cancelledAt": "2026-06-11T12:00:00Z" }
}
```

#### `POST /api/v1/cargo/shipments/{id}/label`
Generate the shipping label in the requested format (PDF, ZPL).

```json
// Request
{ "format": "PDF" }

// Response
{
  "success": true,
  "data": { "labelUrl": "https://api.dhl.com/labels/1234567890.pdf", "format": "PDF", "size": "A6", "generatedAt": "2026-06-11T10:30:00Z" }
}
```

#### `POST /api/v1/cargo/pickups`
Schedule a carrier pickup.

```json
// Request
{
  "carrierCode": "DHL", "shipmentIds": ["shp_a1b2c3d4e5"],
  "pickupDate": "2026-06-12", "readyTime": "09:00", "closeTime": "17:00",
  "location": { "company": "TechCorp Inc", "contactName": "John Doe", "phone": "+33123456789",
    "country": "FR", "zipCode": "75001", "city": "Paris", "address": "12 Rue de Rivoli" },
  "totalPackages": 1, "totalWeight": 2.5, "weightUnit": "KG",
  "specialInstructions": "Ring at reception"
}

// Response
{
  "success": true,
  "data": {
    "id": "pck_001a2b3c", "carrierCode": "DHL", "carrierPickupId": "DHL-PICKUP-98765",
    "status": "CONFIRMED", "pickupDate": "2026-06-12",
    "readyTime": "09:00", "closeTime": "17:00",
    "confirmationNumber": "CONF-ABC-123"
  }
}
```

#### `POST /api/v1/cargo/webhooks/{carrierCode}`
Entry point for carrier push notifications. Always returns 200.

```json
// Request (sent by DHL)
{
  "shipmentId": "1234567890", "status": "DELIVERED", "statusDescription": "Shipment delivered",
  "timestamp": "2026-06-13T16:30:00Z",
  "location": { "city": "Berlin", "country": "DE", "zipCode": "10115" },
  "signedBy": "Hans Schmidt", "deliveryPhotoUrl": "https://dhl.com/proof/photo.jpg"
}

// Response (always 200)
{ "success": true, "message": "Webhook processed successfully" }
```

#### `POST /api/v1/cargo/addresses/validate`
Validate and normalize an address via the carrier (real-time check).

```json
// Request
{ "country": "FR", "zipCode": "75001", "city": "Paris", "address": "12 Rue de Rivoli", "carrierCode": "DHL" }

// Response
{
  "success": true,
  "data": {
    "valid": true,
    "normalizedAddress": { "country": "FR", "zipCode": "75001", "city": "PARIS", "address": "12 RUE DE RIVOLI" },
    "suggestions": [],
    "carrierValidation": { "code": "VALID", "message": "Address is valid" }
  }
}
```

#### `POST /api/v1/cargo/carriers`
Add a carrier with credentials, services, and capabilities.

```json
// Request (simplified payload — see service_cargo.md for full)
{
  "code": "CHRONOPOST", "name": "Chronopost", "adapterName": "ChronopostAdapter",
  "active": true, "website": "https://www.chronopost.fr",
  "services": [
    { "code": "CHRONO_13", "name": "Chrono 13h", "zones": ["FR", "MC"], "transitDays": 1,
      "features": ["SIGNATURE", "INSURANCE"], "active": true }
  ],
  "credentials": {
    "authType": "API_KEY", "apiKey": "chrono_api_key_12345",
    "accountNumber": "CHRONO-ACC-001", "endpoint": "https://api.chronopost.fr/v1"
  },
  "settings": { "timeoutMs": 15000, "retryMaxAttempts": 3, "rateLimitPerMinute": 60 }
}

// Response 201
{
  "success": true,
  "data": {
    "code": "CHRONOPOST", "name": "Chronopost", "active": true,
    "status": "PENDING_TEST", "message": "Carrier added. Run a connection test before using."
  }
}
```

#### `POST /api/v1/cargo/carriers/{code}/test`
Test the carrier API connection.

```json
// Response — Success
{
  "success": true,
  "data": {
    "status": "CONNECTED", "latencyMs": 245, "testedAt": "2026-06-11T15:00:00Z",
    "endpoint": "https://api.chronopost.fr/v1/health",
    "details": { "httpStatus": 200, "message": "API is reachable", "accountValid": true }
  }
}

// Response — Failure
{
  "success": false,
  "error": { "code": "CARRIER_CONNECTION_FAILED", "message": "Failed to connect to Chronopost API",
    "details": { "httpStatus": 401, "reason": "Invalid API key" } }
}
```

#### `POST /api/v1/cargo/carriers/{code}/services`
Add a service to the carrier's catalog.

```json
// Request
{
  "code": "DHL_EXPRESS_9", "name": "Express 9:00",
  "description": "Delivery before 9am next day",
  "maxWeight": 30, "maxWeightUnit": "KG",
  "zones": ["FR", "DE", "BE", "NL", "LU"],
  "transitDays": 1, "features": ["SIGNATURE", "INSURANCE"], "active": true
}
```

---

### 2.3 GET — Read / Query

#### `GET /api/v1/cargo/shipments`
Paginated list of shipments. Filters: `?status=IN_TRANSIT&page=1&limit=20`.

```json
// Response
{
  "success": true,
  "data": [
    {
      "id": "shp_a1b2c3d4e5", "status": "IN_TRANSIT",
      "carrierCode": "DHL", "carrierTrackingNumber": "1234567890",
      "reference": "ORD-2026-001234",
      "sender": { "company": "TechCorp Inc", "country": "FR" },
      "recipient": { "company": "Berlin GmbH", "country": "DE" },
      "price": { "total": 45.30, "currency": "EUR" },
      "createdAt": "2026-06-11T10:30:00Z"
    }
  ],
  "pagination": { "page": 1, "limit": 20, "total": 5 }
}
```

#### `GET /api/v1/cargo/shipments/{id}`
Full shipment detail with status history.

```json
// Response
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5", "status": "IN_TRANSIT",
    "statusHistory": [
      { "status": "CREATED", "timestamp": "2026-06-11T10:30:00Z" },
      { "status": "PICKED_UP", "timestamp": "2026-06-11T14:00:00Z" },
      { "status": "IN_TRANSIT", "timestamp": "2026-06-12T08:15:00Z" }
    ],
    "carrierCode": "DHL", "carrierTrackingNumber": "1234567890",
    "carrierShipmentId": "DE-2026-98765",
    "reference": "ORD-2026-001234",
    "labelUrl": "https://api.dhl.com/labels/1234567890.pdf",
    "trackingUrl": "https://www.dhl.com/track/1234567890",
    "sender": { "company": "TechCorp Inc", "country": "FR", "zipCode": "75001" },
    "recipient": { "company": "Berlin GmbH", "country": "DE", "zipCode": "10115" },
    "packages": [{ "reference": "PARCEL-001", "weight": 2.5, "trackingNumber": "1234567890-001" }],
    "price": { "total": 45.30, "currency": "EUR" },
    "createdAt": "2026-06-11T10:30:00Z",
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z"
  }
}
```

#### `GET /api/v1/cargo/shipments/{id}/tracking`
Tracking events with location, raw carrier status, and milestones.

```json
// Response
{
  "success": true,
  "data": {
    "shipmentId": "shp_a1b2c3d4e5", "carrierCode": "DHL",
    "carrierTrackingNumber": "1234567890",
    "currentStatus": {
      "code": "IN_TRANSIT", "label": "In transit",
      "location": "Frankfurt, Germany", "timestamp": "2026-06-12T08:15:00Z"
    },
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z",
    "events": [
      { "eventId": "evt_001", "code": "LABEL_CREATED", "label": "Label created",
        "description": "Shipping label generated",
        "location": "Paris, France", "timestamp": "2026-06-11T10:30:00Z",
        "carrierRawStatus": "Shipment information received" },
      { "eventId": "evt_002", "code": "PICKED_UP", "label": "Parcel collected",
        "location": "Paris, France", "timestamp": "2026-06-11T14:00:00Z",
        "carrierRawStatus": "Pickup scanned" },
      { "eventId": "evt_003", "code": "IN_TRANSIT", "label": "In transit",
        "location": "Frankfurt, Germany", "timestamp": "2026-06-12T08:15:00Z",
        "carrierRawStatus": "Departed from transit hub" }
    ],
    "milestones": {
      "created": "2026-06-11T10:30:00Z", "pickedUp": "2026-06-11T14:00:00Z",
      "inTransit": "2026-06-12T08:15:00Z",
      "outForDelivery": null, "delivered": null
    }
  }
}
```

#### `GET /api/v1/cargo/carriers`
Paginated carrier list. Filters: `?active=true&zone=FR&feature=INSURANCE&page=1&limit=20`.

```json
// Response
{
  "success": true,
  "data": [
    {
      "code": "DHL", "name": "DHL Express", "adapterName": "DhlAdapter",
      "active": true, "status": "CONNECTED", "lastTestedAt": "2026-06-10T08:00:00Z",
      "services": [
        { "code": "DHL_EXPRESS_WORLDWIDE", "name": "Express Worldwide", "active": true },
        { "code": "DHL_EXPRESS_12", "name": "Express 12:00", "active": true }
      ],
      "capabilities": { "labelFormats": ["PDF", "ZPL", "PNG"], "features": ["RATES", "TRACKING", "SIGNATURE", "INSURANCE", "SATURDAY"] }
    }
  ],
  "pagination": { "page": 1, "limit": 20, "total": 3 }
}
```

#### `GET /api/v1/cargo/carriers/{code}`
Full carrier detail.

```json
// Response
{
  "success": true,
  "data": {
    "code": "DHL", "name": "DHL Express", "adapterName": "DhlAdapter",
    "active": true, "status": "CONNECTED", "lastTestedAt": "2026-06-10T08:00:00Z",
    "services": [{
      "code": "DHL_EXPRESS_WORLDWIDE", "name": "Express Worldwide",
      "description": "International express delivery",
      "maxWeight": 70, "zones": ["WORLDWIDE"], "transitDays": 2,
      "features": ["SIGNATURE", "INSURANCE", "SATURDAY"], "active": true
    }],
    "capabilities": {
      "labelFormats": ["PDF", "ZPL", "PNG"],
      "features": ["RATES", "TRACKING", "SIGNATURE", "INSURANCE", "SATURDAY", "PICKUP"]
    },
    "settings": { "timeoutMs": 10000, "retryMaxAttempts": 3, "rateLimitPerMinute": 100, "webhookEnabled": true }
  }
}
```

---

### 2.4 PUT — Update

#### `PUT /api/v1/cargo/carriers/{code}`
Update carrier settings.

```json
// Request
{ "settings": { "timeoutMs": 15000, "retryMaxAttempts": 3 }, "active": true }
```

#### `PUT /api/v1/cargo/carriers/{code}/credentials`
Update API keys and secrets. Re-test connection after update.

```json
// Request
{
  "authType": "API_KEY", "apiKey": "new_dhl_api_key_67890",
  "apiSecret": "new_dhl_secret_12345", "webhookSecret": "whsec_new_abc456"
}

// Response
{
  "success": true,
  "data": {
    "code": "DHL", "credentialsUpdatedAt": "2026-06-11T16:00:00Z",
    "message": "Credentials updated. Re-test connection."
  }
}
```

---

### 2.5 PATCH — Partial Update

#### `PATCH /api/v1/cargo/carriers/{code}/toggle`
Enable or disable a carrier. Useful during outages or maintenance.

```json
// Request
{ "active": false, "reason": "API outage - maintenance" }

// Response
{
  "success": true,
  "data": { "code": "FEDEX", "active": false, "deactivatedAt": "2026-06-11T14:00:00Z" }
}
```

---

### 2.6 DELETE — Deletion

#### `DELETE /api/v1/cargo/shipments/{id}`
Permanently delete a shipment.

```json
// Response
{ "success": true, "data": { "deleted": true } }
```

#### `DELETE /api/v1/cargo/carriers/{code}`
Delete a carrier.

```json
// Response
{ "success": true, "data": { "deleted": true } }
```

---

## 3. Workflow

### 3.1 Shipment Lifecycle

```
CREATED ──→ VALIDATED ──→ PICKED_UP ──→ IN_TRANSIT ──→ OUT_FOR_DELIVERY ──→ DELIVERED
    │           │              │               │               │
    │           │              │               │               ├── DELIVERY_ATTEMPTED
    │           │              │               │               │       └── OUT_FOR_DELIVERY
    │           │              │               ├── CUSTOMS_HELD
    │           │              │               │       └── CUSTOMS_CLEARED → IN_TRANSIT
    │           │              ├── FAILED ──────┘
    │           ├── CANCELLED ─┘
    └───────────┘
```

**7 unified statuses:** CREATED → VALIDATED → PICKED_UP → IN_TRANSIT → OUT_FOR_DELIVERY → DELIVERED (terminal: DELIVERED, FAILED, CANCELLED)

### 3.2 Complete Workflow (10 steps)

```
 1. POST /api/v1/cargo/carriers                    → Add Chronopost
 2. POST /api/v1/cargo/carriers/CHRONOPOST/test    → Test connection
 3. GET  /api/v1/cargo/carriers                    → List available carriers
 4. POST /api/v1/cargo/rates                       → Compare DHL / FedEx prices
 5. POST /api/v1/cargo/addresses/validate          → Validate recipient address
 6. POST /api/v1/cargo/shipments                   → Create shipment
 7. POST /api/v1/cargo/pickups                     → Schedule pickup
 8. ← DHL Webhook (DELIVERED)                      → Automatic status update
 9. GET  /api/v1/cargo/shipments/{id}/tracking     → Track in real time
10. POST /api/v1/cargo/shipments/{id}/cancel       → Cancel if needed
```

### 3.3 Frontend ↔ Endpoint Mapping

```
Login (Page)            → POST auth/login
Rates (Page)            → POST cargo/rates
Shipments (Page)        → GET cargo/shipments  |  POST cargo/shipments  |  DELETE cargo/shipments/{id}
ShipmentDetail (Page)   → GET cargo/shipments/{id}  |  POST .../cancel  |  POST .../label  |  GET .../tracking
Carriers (Page)         → GET cargo/carriers  |  POST cargo/carriers  |  DELETE cargo/carriers/{code}
CarrierDetail (Page)    → GET cargo/carriers/{code}  |  PUT cargo/carriers/{code}
                          PATCH .../toggle  |  POST .../test  |  POST .../services  |  PUT .../credentials
Pickups (Page)          → POST cargo/pickups  |  POST cargo/pickups/{id}/cancel
WebhookLogs (Page)      → POST cargo/webhooks/{carrierCode} (logs)
Dashboard (Page)        → Aggregates stats from shipments + carriers
```

### 3.4 Data Models

**Table `shipments`** (20 fields): id, status (8-value enum), carrier_code, carrier_tracking_number, reference, label_url, sender (JSON), recipient (JSON), packages (JSON[]), price (decimal), insurance_amount, estimated_delivery_date, dates...

**Table `tracking_events`** (11 fields): id, shipment_id, code (12-value enum: LABEL_CREATED, PICKED_UP, IN_TRANSIT, ARRIVED_AT_HUB, DEPARTED_FROM_HUB, OUT_FOR_DELIVERY, DELIVERED, DELIVERY_ATTEMPTED, FAILED, RETURNED_TO_SENDER, CUSTOMS_HELD, CUSTOMS_CLEARED), location (JSON), carrier_raw_status, signed_by, delivery_photo_url...

**Table `carriers`** (12 fields): code (PK), name, adapter_name, active, status (enum: PENDING_TEST, CONNECTED, DISCONNECTED, ERROR), capabilities (JSON), settings (JSON), credentials (encrypted JSON)...

**Table `carrier_services`** (9 fields): id, carrier_code (FK), code, name, max_weight, zones (JSON[]), transit_days, features (JSON[]), active

---

## 4. Knowledge Graph Analysis

### 4.1 Statistics

| Metric | Value |
|---|---|
| Total Nodes | 40 |
| Total Edges | 48 |
| Communities | 4 |
| EXTRACTED edges | 43 (89.6%) |
| INFERRED edges | 5 (10.4%) |
| Average confidence score | 0.949 |

### 4.2 Community Map

#### Community 0 — Architecture & Adapters (7 nodes, blue)
`CarrierAdapter` interface implemented by 4 adapters (DHL, FedEx, UPS, Chronopost). Each adapter normalizes carrier concepts into `UnifiedStatusModel`.

#### Community 1 — Status Mapping Engine (6 nodes, green)
`StatusMapperEngine` with 3-level per-carrier matching. 64+ raw codes → 12 unified codes.

| Carrier | Codes | Exact | Regex | Fuzzy |
|---|---|---|---|---|
| DHL | 15 | 8 | 5 | 2 |
| FedEx | 16 | 9 | 5 | 2 |
| UPS | 18 | 10 | 6 | 2 |
| Chronopost | 15 | 7 | 5 | 3 |

#### Community 2 — Frontend (21 nodes, yellow)
React 18 + TypeScript + Vite + Tailwind. Layered architecture: Pages → Components → Hooks → Service Layer → Mock Data.

#### Community 3 — API Design & Documentation (7 nodes, purple)
20 endpoints covering 6 domains: shipments, carriers, rates, pickups, webhooks, address validation.

### 4.3 God Nodes (High-Connectivity Hubs)

| Node | Community | Degree | Type |
|---|---|---|---|
| cargo_service_layer | Frontend | 9 | code |
| status_mapper | Mapping | 6 | code |
| react_frontend | Frontend | 6 | code |
| rest_endpoints | API Design | 6 | document |
| cargo_service_arch | Architecture | 5 | document |
| unified_status | Architecture | 5 | code |
| shared_components | Frontend | 5 | code |

`cargo_service_layer` is the most critical node — every page depends on it.

### 4.4 Edge Analysis

**EXTRACTED (confidence 1.0)**: `depends_on`, `contains`, `implements`, `uses`, `part_of`, `maps_to`

**INFERRED (confidence < 1.0)**: `complements` (status_mapper ↔ carrier_adapter, 0.85), `crosscuts` (i18n → frontend, 0.95), `links_to` (dashboard → shipments, 0.95), `competes_with` (DHL ↔ FedEx, 0.85)

### 4.5 Architectural Insights

1. **Modular architecture** — Adding a 5th carrier = implement interface + add status maps
2. **Status Mapping = key differentiator** — Turkish carrier status names supported via regex
3. **Service Layer = bottleneck** — Consider splitting into domain services (shipmentService, carrierService...)
4. **Frontend 52.5% of codebase** — Ready for real API by swapping `cargoService.ts`
5. **3 documentation files** — Drift risk. Auto-generation recommended

---

## 5. Project Files

### Core Documents
| File | Purpose |
|---|---|
| `CARGO-SERVICE-ARCHITECTURE.md` | Full backend architecture plan |
| `service_cargo.md` | API documentation (FR) |
| `cargo_service.md` | API documentation (EN) |
| `cargo_service_api.md` | Color-coded API reference |

### Frontend Source
| File/Directory | Purpose |
|---|---|
| `frontend/src/types/index.ts` | 14 TypeScript interfaces |
| `frontend/src/data/mockData.ts` | 6 mock stores |
| `frontend/src/services/statusMapper.ts` | Status mapping engine (4 carriers) |
| `frontend/src/services/cargoService.ts` | 25+ mock API functions |
| `frontend/src/hooks/useCargoService.ts` | useApi, useMutation, useLoading |
| `frontend/src/context/AuthContext.tsx` | JWT mock auth |
| `frontend/src/i18n/` | EN/FR/TR (750+ keys) |
| `frontend/src/pages/` | 9 pages |
| `frontend/src/components/` | 10+ shared components |

---

*Report generated by Graphify — knowledge graph pipeline.*
