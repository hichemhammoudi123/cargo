# 📦 Cargo Service — API Reference

> **Centralized shipping service** — Unified interface for DHL, FedEx, UPS, Chronopost, and more.

---

## 📌 Endpoints Overview

| # | Method | Path | Role |
|---|--------|------|------|
| 1 | 🟢 `POST` | `/api/v1/cargo/rates` | 💰 Get shipping prices from all carriers |
| 2 | 🟢 `POST` | `/api/v1/cargo/shipments` | 📤 Create a new shipment |
| 3 | 🔵 `GET` | `/api/v1/cargo/shipments/{id}` | 📋 Get shipment details |
| 4 | 🔵 `GET` | `/api/v1/cargo/shipments/{id}/tracking` | 📍 Get real-time tracking |
| 5 | 🟢 `POST` | `/api/v1/cargo/shipments/{id}/cancel` | ❌ Cancel a shipment |
| 6 | 🟢 `POST` | `/api/v1/cargo/shipments/{id}/label` | 🏷️ Generate shipping label |
| 7 | 🟢 `POST` | `/api/v1/cargo/pickups` | 🚚 Schedule a pickup |
| 8 | 🟢 `POST` | `/api/v1/cargo/webhooks/{carrierCode}` | 🔔 Receive carrier status updates |
| 9 | 🟢 `POST` | `/api/v1/cargo/addresses/validate` | ✅ Validate and normalize addresses |
| 10 | 🔵 `GET` | `/api/v1/cargo/carriers` | 📋 List all carriers |
| 11 | 🟢 `POST` | `/api/v1/cargo/carriers` | ➕ Add a new carrier |
| 12 | 🔵 `GET` | `/api/v1/cargo/carriers/{code}` | 🔍 Get carrier details |
| 13 | 🟠 `PUT` | `/api/v1/cargo/carriers/{code}` | ✏️ Update carrier configuration |
| 14 | 🟣 `PATCH` | `/api/v1/cargo/carriers/{code}/toggle` | ⏻ Enable / disable a carrier |
| 15 | 🟢 `POST` | `/api/v1/cargo/carriers/{code}/test` | 🔌 Test carrier API connection |
| 16 | 🟢 `POST` | `/api/v1/cargo/carriers/{code}/services` | 📦 Add a carrier service |
| 17 | 🟠 `PUT` | `/api/v1/cargo/carriers/{code}/services/{serviceCode}` | ✏️ Update a service |
| 18 | 🔴 `DELETE` | `/api/v1/cargo/carriers/{code}/services/{serviceCode}` | 🗑️ Remove a service |
| 19 | 🟠 `PUT` | `/api/v1/cargo/carriers/{code}/credentials` | 🔑 Update API credentials |

---

## 1️⃣ 💰 Get Shipping Rates

> **Compare prices across multiple carriers in one call.**

`POST /api/v1/cargo/rates`

### What it does
Send sender/recipient addresses + parcel details → the service queries all active carriers in parallel → normalizes responses → returns a sorted price list.

### Request
```json
{
  "sender": {
    "country": "FR", "zipCode": "75001",
    "city": "Paris", "address": "12 Rue de Rivoli"
  },
  "recipient": {
    "country": "DE", "zipCode": "10115",
    "city": "Berlin", "address": "Friedrichstraße 100"
  },
  "packages": [
    {
      "weight": 2.5, "weightUnit": "KG",
      "length": 30, "width": 20, "height": 15, "dimUnit": "CM"
    }
  ],
  "options": {
    "carrierCodes": ["DHL", "FEDEX"],
    "serviceType": "EXPRESS"
  }
}
```

### Response `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "carrierCode": "DHL",
      "carrierName": "DHL Express",
      "serviceCode": "DHL_EXPRESS_WORLDWIDE",
      "serviceName": "Express Worldwide",
      "totalPrice": 45.30,
      "currency": "EUR",
      "estimatedTransitDays": 2,
      "estimatedDeliveryDate": "2026-06-13",
      "guaranteed": true,
      "breakdown": [
        { "type": "BASE", "label": "Transport", "amount": 38.00 },
        { "type": "FUEL", "label": "Fuel surcharge", "amount": 5.30 },
        { "type": "INSURANCE", "label": "Insurance", "amount": 2.00 }
      ]
    },
    {
      "carrierCode": "FEDEX",
      "carrierName": "FedEx",
      "serviceCode": "FEDEX_PRIORITY",
      "serviceName": "FedEx Priority",
      "totalPrice": 48.50,
      "currency": "EUR",
      "estimatedTransitDays": 1,
      "estimatedDeliveryDate": "2026-06-12",
      "guaranteed": true,
      "breakdown": [
        { "type": "BASE", "label": "Transport", "amount": 41.00 },
        { "type": "FUEL", "label": "Fuel surcharge", "amount": 5.50 },
        { "type": "INSURANCE", "label": "Insurance", "amount": 2.00 }
      ]
    }
  ]
}
```

---

## 2️⃣ 📤 Create Shipment

> **Book a real shipment with your chosen carrier.**

`POST /api/v1/cargo/shipments`

### What it does
Creates a shipment in our DB → calls the carrier API via adapter → returns tracking number + label URL.

### Request
```json
{
  "carrierCode": "DHL",
  "serviceCode": "DHL_EXPRESS_WORLDWIDE",
  "reference": "ORD-2026-001234",
  "sender": {
    "company": "TechCorp Inc",
    "contactName": "John Doe",
    "email": "john@techcorp.com",
    "phone": "+33123456789",
    "country": "FR", "zipCode": "75001",
    "city": "Paris", "address": "12 Rue de Rivoli"
  },
  "recipient": {
    "company": "Berlin GmbH",
    "contactName": "Hans Schmidt",
    "email": "hans@berlin.de",
    "phone": "+4930123456",
    "country": "DE", "zipCode": "10115",
    "city": "Berlin", "address": "Friedrichstraße 100"
  },
  "packages": [
    {
      "reference": "PARCEL-001",
      "description": "Electronic components",
      "weight": 2.5, "weightUnit": "KG",
      "length": 30, "width": 20, "height": 15, "dimUnit": "CM",
      "declaredValue": 500.00, "declaredCurrency": "EUR",
      "containsDangerousGoods": false
    }
  ],
  "options": {
    "insurance": { "amount": 500.00, "currency": "EUR" },
    "signatureRequired": true,
    "saturdayDelivery": false
  }
}
```

### Response `201 Created`
```json
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5",
    "status": "CREATED",
    "carrierCode": "DHL",
    "carrierName": "DHL Express",
    "carrierTrackingNumber": "1234567890",
    "labelUrl": "https://api.dhl.com/labels/1234567890.pdf",
    "trackingUrl": "https://www.dhl.com/track/1234567890",
    "reference": "ORD-2026-001234",
    "price": { "total": 45.30, "currency": "EUR" },
    "createdAt": "2026-06-11T10:30:00Z",
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z"
  }
}
```

---

## 3️⃣ 📋 Get Shipment Details

> **View full shipment information and status history.**

`GET /api/v1/cargo/shipments/{id}`

### What it does
Returns current status, status history timeline, carrier info, addresses, parcels, and pricing.

### Response `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5",
    "status": "IN_TRANSIT",
    "statusHistory": [
      { "status": "CREATED", "timestamp": "2026-06-11T10:30:00Z" },
      { "status": "PICKED_UP", "timestamp": "2026-06-11T14:00:00Z" },
      { "status": "IN_TRANSIT", "timestamp": "2026-06-12T08:15:00Z" }
    ],
    "carrierCode": "DHL",
    "carrierTrackingNumber": "1234567890",
    "reference": "ORD-2026-001234",
    "sender": { "company": "TechCorp Inc", "country": "FR" },
    "recipient": { "company": "Berlin GmbH", "country": "DE" },
    "packages": [
      { "reference": "PARCEL-001", "weight": 2.5, "trackingNumber": "1234567890-001" }
    ],
    "price": { "total": 45.30, "currency": "EUR" },
    "createdAt": "2026-06-11T10:30:00Z",
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z"
  }
}
```

---

## 4️⃣ 📍 Real-Time Tracking

> **Get detailed tracking events with carrier raw data.**

`GET /api/v1/cargo/shipments/{id}/tracking`

### What it does
Returns all tracking events, current status with location, milestones, and the raw carrier status for debugging.

### Response `200 OK`
```json
{
  "success": true,
  "data": {
    "shipmentId": "shp_a1b2c3d4e5",
    "carrierCode": "DHL",
    "carrierTrackingNumber": "1234567890",
    "currentStatus": {
      "code": "IN_TRANSIT",
      "label": "In transit",
      "location": "Frankfurt, Germany",
      "timestamp": "2026-06-12T08:15:00Z"
    },
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z",
    "events": [
      {
        "eventId": "evt_001",
        "code": "LABEL_CREATED",
        "label": "Label created",
        "description": "Shipping label generated",
        "location": "Paris, France",
        "timestamp": "2026-06-11T10:30:00Z",
        "carrierRawStatus": "Shipment information received"
      },
      {
        "eventId": "evt_002",
        "code": "PICKED_UP",
        "label": "Parcel collected",
        "location": "Paris, France",
        "timestamp": "2026-06-11T14:00:00Z",
        "carrierRawStatus": "Pickup scanned"
      },
      {
        "eventId": "evt_003",
        "code": "IN_TRANSIT",
        "label": "In transit",
        "location": "Frankfurt, Germany",
        "timestamp": "2026-06-12T08:15:00Z",
        "carrierRawStatus": "Departed from transit hub"
      }
    ],
    "milestones": {
      "created": "2026-06-11T10:30:00Z",
      "pickedUp": "2026-06-11T14:00:00Z",
      "inTransit": "2026-06-12T08:15:00Z",
      "outForDelivery": null,
      "delivered": null
    }
  }
}
```

---

## 5️⃣ ❌ Cancel Shipment

> **Cancel a shipment before it's too late.**

`POST /api/v1/cargo/shipments/{id}/cancel`

### What it does
Contacts the carrier to cancel the shipment. Updates status to `CANCELLED`. May fail if already in transit.

### Response `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5",
    "status": "CANCELLED",
    "cancelledAt": "2026-06-11T12:00:00Z"
  }
}
```

---

## 6️⃣ 🏷️ Generate Shipping Label

> **Print your shipping label in PDF or ZPL format.**

`POST /api/v1/cargo/shipments/{id}/label`

### What it does
Generates or retrieves the shipping label from the carrier in your chosen format.

### Request
```json
{
  "format": "PDF"
}
```

### Response `200 OK`
```json
{
  "success": true,
  "data": {
    "labelUrl": "https://api.dhl.com/labels/1234567890.pdf",
    "format": "PDF",
    "size": "A6",
    "generatedAt": "2026-06-11T10:30:00Z"
  }
}
```

---

## 7️⃣ 🚚 Schedule Pickup

> **Book a carrier pickup at your location.**

`POST /api/v1/cargo/pickups`

### What it does
Schedules a carrier to collect parcels from your address within a time window.

### Request
```json
{
  "carrierCode": "DHL",
  "shipmentIds": ["shp_a1b2c3d4e5"],
  "pickupDate": "2026-06-12",
  "readyTime": "09:00",
  "closeTime": "17:00",
  "location": {
    "company": "TechCorp Inc",
    "contactName": "John Doe",
    "phone": "+33123456789",
    "country": "FR", "zipCode": "75001",
    "city": "Paris", "address": "12 Rue de Rivoli"
  },
  "totalPackages": 1,
  "totalWeight": 2.5,
  "weightUnit": "KG",
  "specialInstructions": "Ring at reception"
}
```

### Response `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "pck_001a2b3c",
    "carrierCode": "DHL",
    "carrierPickupId": "DHL-PICKUP-98765",
    "status": "CONFIRMED",
    "pickupDate": "2026-06-12",
    "readyTime": "09:00",
    "closeTime": "17:00",
    "confirmationNumber": "CONF-ABC-123",
    "location": {
      "company": "TechCorp Inc",
      "country": "FR", "city": "Paris", "address": "12 Rue de Rivoli"
    },
    "instructions": "Ring at reception",
    "createdAt": "2026-06-11T11:00:00Z"
  }
}
```

---

## 8️⃣ 🔔 Incoming Webhook

> **Receive real-time status updates pushed by carriers.**

`POST /api/v1/cargo/webhooks/{carrierCode}`

### What it does
Carrier pushes status updates (DELIVERED, FAILED, etc.) → `WebhookDispatcher` identifies the carrier → adapter parses the raw payload → shipment status is updated → event is published internally.

### Request (sent by DHL)
```json
{
  "shipmentId": "1234567890",
  "status": "DELIVERED",
  "statusDescription": "Shipment delivered",
  "timestamp": "2026-06-13T16:30:00Z",
  "location": { "city": "Berlin", "country": "DE", "zipCode": "10115" },
  "signedBy": "Hans Schmidt",
  "deliveryPhotoUrl": "https://dhl.com/proof/photo.jpg"
}
```

### Response `200 OK` (always acknowledge)
```json
{
  "success": true,
  "message": "Webhook processed successfully"
}
```

---

## 9️⃣ ✅ Validate Address

> **Check and normalize an address before shipping.**

`POST /api/v1/cargo/addresses/validate`

### What it does
Calls the carrier's address validation API. Returns normalized address + suggestions if invalid.

### Request
```json
{
  "country": "FR",
  "zipCode": "75001",
  "city": "Paris",
  "address": "12 Rue de Rivoli",
  "carrierCode": "DHL"
}
```

### Response `200 OK`
```json
{
  "success": true,
  "data": {
    "valid": true,
    "normalizedAddress": {
      "country": "FR", "zipCode": "75001",
      "city": "PARIS", "address": "12 RUE DE RIVOLI"
    },
    "suggestions": [],
    "carrierValidation": {
      "code": "VALID",
      "message": "Address is valid"
    }
  }
}
```

---

## 🔟 📋 List Carriers

> **View all registered carriers and their capabilities.**

`GET /api/v1/cargo/carriers`

### Query Parameters
| Param | Type | Example |
|-------|------|---------|
| `active` | boolean | `true` |
| `zone` | string | `FR` |
| `feature` | string | `INSURANCE` |
| `page` | int | `1` |
| `limit` | int | `20` |

### Response `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "code": "DHL",
      "name": "DHL Express",
      "adapterName": "DhlAdapter",
      "active": true,
      "status": "CONNECTED",
      "lastTestedAt": "2026-06-10T08:00:00Z",
      "services": [
        { "code": "DHL_EXPRESS_WORLDWIDE", "name": "Express Worldwide", "active": true },
        { "code": "DHL_EXPRESS_12", "name": "Express 12:00", "active": true }
      ],
      "capabilities": {
        "labelFormats": ["PDF", "ZPL", "PNG"],
        "features": ["RATES", "TRACKING", "SIGNATURE", "INSURANCE", "SATURDAY"]
      }
    }
  ],
  "pagination": { "page": 1, "limit": 20, "total": 3 }
}
```

---

## 1️⃣1️⃣ ➕ Add Carrier

> **Register a new carrier with its API credentials and services.**

`POST /api/v1/cargo/carriers`

### Request
```json
{
  "code": "CHRONOPOST",
  "name": "Chronopost",
  "adapterName": "ChronopostAdapter",
  "active": true,
  "website": "https://www.chronopost.fr",
  "logoUrl": "https://cdn.example.com/carriers/chronopost.svg",
  "services": [
    {
      "code": "CHRONO_13",
      "name": "Chrono 13h",
      "description": "Delivery before 1pm next day",
      "maxWeight": 30, "maxWeightUnit": "KG",
      "maxLength": 150, "dimUnit": "CM",
      "zones": ["FR", "MC", "AD"],
      "transitDays": 1,
      "features": ["SIGNATURE", "INSURANCE"],
      "active": true
    }
  ],
  "capabilities": {
    "labelFormats": ["PDF", "ZPL"],
    "features": ["RATES", "TRACKING", "SIGNATURE", "INSURANCE", "PICKUP"]
  },
  "credentials": {
    "authType": "API_KEY",
    "apiKey": "chrono_api_key_12345",
    "apiSecret": "chrono_secret_67890",
    "endpoint": "https://api.chronopost.fr/v1",
    "webhookSecret": "whsec_chrono_abc123"
  },
  "settings": {
    "timeoutMs": 15000,
    "retryMaxAttempts": 3,
    "rateLimitPerMinute": 60
  }
}
```

### Response `201 Created`
```json
{
  "success": true,
  "data": {
    "code": "CHRONOPOST",
    "name": "Chronopost",
    "active": true,
    "status": "PENDING_TEST",
    "message": "Carrier added. Run a connection test before using."
  }
}
```

---

## 1️⃣2️⃣ 🔍 Get Carrier Detail

> **View full carrier configuration (credentials are masked).**

`GET /api/v1/cargo/carriers/{code}`

### Response `200 OK`
```json
{
  "success": true,
  "data": {
    "code": "DHL",
    "name": "DHL Express",
    "adapterName": "DhlAdapter",
    "active": true,
    "status": "CONNECTED",
    "lastTestedAt": "2026-06-10T08:00:00Z",
    "services": [
      {
        "code": "DHL_EXPRESS_WORLDWIDE",
        "name": "Express Worldwide",
        "maxWeight": 70, "zones": ["WORLDWIDE"],
        "transitDays": 2,
        "features": ["SIGNATURE", "INSURANCE"],
        "active": true
      }
    ],
    "capabilities": {
      "labelFormats": ["PDF", "ZPL"],
      "features": ["RATES", "TRACKING", "SIGNATURE", "INSURANCE", "PICKUP"]
    },
    "settings": {
      "timeoutMs": 10000,
      "retryMaxAttempts": 3,
      "rateLimitPerMinute": 100,
      "webhookEnabled": true
    }
  }
}
```

---

## 1️⃣3️⃣ ✏️ Update Carrier

> **Modify carrier settings or configuration.**

`PUT /api/v1/cargo/carriers/{code}`

### Request
```json
{
  "settings": { "timeoutMs": 15000, "retryMaxAttempts": 3 },
  "active": true
}
```

---

## 1️⃣4️⃣ ⏻ Toggle Carrier

> **Enable or disable a carrier instantly (e.g., during an outage).**

`PATCH /api/v1/cargo/carriers/{code}/toggle`

### Request
```json
{ "active": false, "reason": "API outage - maintenance" }
```

### Response `200 OK`
```json
{
  "success": true,
  "data": {
    "code": "FEDEX",
    "active": false,
    "deactivatedAt": "2026-06-11T14:00:00Z"
  }
}
```

---

## 1️⃣5️⃣ 🔌 Test Connection

> **Verify that the carrier API is reachable with current credentials.**

`POST /api/v1/cargo/carriers/{code}/test`

### Success Response `200 OK`
```json
{
  "success": true,
  "data": {
    "status": "CONNECTED",
    "latencyMs": 245,
    "testedAt": "2026-06-11T15:00:00Z",
    "details": { "httpStatus": 200, "message": "API is reachable" }
  }
}
```

### Failure Response `200 OK`
```json
{
  "success": false,
  "error": {
    "code": "CARRIER_CONNECTION_FAILED",
    "message": "Failed to connect to Chronopost API",
    "details": { "httpStatus": 401, "reason": "Invalid API key" }
  }
}
```

---

## 1️⃣6️⃣ ~ 1️⃣8️⃣ 📦 Service Management

### Add a service
```http
POST /api/v1/cargo/carriers/{code}/services
```
```json
{
  "code": "DHL_EXPRESS_9",
  "name": "Express 9:00",
  "description": "Delivery before 9am next day",
  "maxWeight": 30, "maxWeightUnit": "KG",
  "zones": ["FR", "DE", "BE"],
  "transitDays": 1,
  "features": ["SIGNATURE", "INSURANCE"],
  "active": true
}
```

### Update a service
```http
PUT /api/v1/cargo/carriers/{code}/services/{serviceCode}
```

### Delete a service
```http
DELETE /api/v1/cargo/carriers/{code}/services/{serviceCode}
```

---

## 1️⃣9️⃣ 🔑 Update Credentials

> **Renew API keys without restarting the service.**

`PUT /api/v1/cargo/carriers/{code}/credentials`

### Request
```json
{
  "authType": "API_KEY",
  "apiKey": "new_dhl_api_key_67890",
  "apiSecret": "new_dhl_secret_12345",
  "webhookSecret": "whsec_new_abc456"
}
```

### Response `200 OK`
```json
{
  "success": true,
  "data": {
    "code": "DHL",
    "credentialsUpdatedAt": "2026-06-11T16:00:00Z",
    "message": "Credentials updated. Re-test connection."
  }
}
```

---

## 🧭 Complete Flow Example

```
 1. POST /carriers                        ➕  Add Chronopost carrier
 2. POST /carriers/CHRONOPOST/test        🔌  Test connection
 3. GET  /carriers                        📋  View available carriers
 4. POST /rates                           💰  Compare prices (DHL vs FedEx)
 5. POST /addresses/validate              ✅  Validate recipient address
 6. POST /shipments                       📤  Create the shipment
 7. POST /pickups                         🚚  Schedule pickup
 8. ← Webhook from DHL (DELIVERED)        🔔  Auto status update
 9. GET  /shipments/{id}/tracking         📍  Real-time tracking
10. POST /shipments/{id}/cancel           ❌  Cancel if needed
```

---

## 🔄 Shipment Status Lifecycle

```
                ┌──────────────────────────────────────────────────────┐
                │                     CREATED                          │
                └──────────────────────┬───────────────────────────────┘
                                       │
                ┌──────────────────────▼───────────────────────────────┐
                │                    VALIDATED                         │
                └──────────────────────┬───────────────────────────────┘
                                       │
                ┌──────────────────────▼───────────────────────────────┐
                │                    PICKED_UP                         │
                └──────┬───────────────────────┬───────────────────────┘
                       │                       │
                ┌──────▼───────┐       ┌───────▼──────────────────────┐
                │   IN_TRANSIT │       │          FAILED               │
                └──────┬───────┘       └──────────────────────────────┘
                       │
          ┌────────────┼────────────────┐
          │            │                │
   ┌──────▼──────┐ ┌──▼───┐   ┌───────▼────────────┐
   │OUT_FOR_     │ │CUSTOMS   │  DELIVERY_ATTEMPTED  │
   │DELIVERY     │ │HELD     │  └───────────┬────────┘
   └──────┬──────┘ └──┬───┘               │
          │           │                   │
   ┌──────▼──────┐ ┌──▼────────┐          │
   │  DELIVERED  │ │ CUSTOMS   │          │
   │             │ │ CLEARED   │──────────┘
   └─────────────┘ └───────────┘
                                       ┌───────────────────────────────┐
                                       │          CANCELLED             │
                                       └───────────────────────────────┘
```

---

## 📊 Data Models

### `shipments`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Internal identifier |
| `status` | `enum` | `CREATED` → `VALIDATED` → `PICKED_UP` → `IN_TRANSIT` → `OUT_FOR_DELIVERY` → `DELIVERED` / `FAILED` / `CANCELLED` |
| `carrier_code` | `string` | `DHL`, `FEDEX`, `CHRONOPOST` |
| `carrier_tracking_number` | `string` | Tracking number from carrier |
| `reference` | `string` | Business order reference |
| `label_url` | `string` | Shipping label URL |
| `sender` | `JSON` | Sender address object |
| `recipient` | `JSON` | Recipient address object |
| `packages` | `JSON[]` | List of parcels |
| `price_total` | `decimal` | Total shipping cost |

### `tracking_events`

| Field | Type | Description |
|-------|------|-------------|
| `code` | `enum` | `LABEL_CREATED`, `PICKED_UP`, `IN_TRANSIT`, `DELIVERED`, `FAILED`, ... |
| `location` | `JSON` | Event location (city, country) |
| `timestamp` | `datetime` | When the event occurred |
| `carrier_raw_status` | `string` | Raw status text from carrier |
| `signed_by` | `string` | Name of person who signed |

### `carriers`

| Field | Type | Description |
|-------|------|-------------|
| `code` | `string PK` | Unique carrier code |
| `name` | `string` | Commercial name |
| `adapter_name` | `string` | Adapter class to use |
| `active` | `boolean` | Enabled or disabled |
| `status` | `enum` | `PENDING_TEST`, `CONNECTED`, `DISCONNECTED`, `ERROR` |
| `credentials` | `JSON encrypted` | API keys and secrets (encrypted at rest) |
| `settings` | `JSON` | Timeout, retry, rate limit config |

### `carrier_services`

| Field | Type | Description |
|-------|------|-------------|
| `carrier_code` | `string FK` | Reference to carrier |
| `code` | `string` | Service code (e.g. `DHL_EXPRESS_WORLDWIDE`) |
| `max_weight` | `decimal` | Maximum weight allowed |
| `zones` | `JSON[]` | Coverage zones (`["FR", "DE"]`) |
| `transit_days` | `int` | Estimated transit days |
| `active` | `boolean` | Service currently active |
