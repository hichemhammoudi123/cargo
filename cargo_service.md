# Cargo Service — API Endpoints Documentation

## 1. Pricing — `POST /api/v1/cargo/rates`

**Purpose:** Get shipping rates from all active carriers.

**Request:**
```json
{
  "sender": { "country": "FR", "zipCode": "75001", "city": "Paris", "address": "12 Rue de Rivoli" },
  "recipient": { "country": "DE", "zipCode": "10115", "city": "Berlin", "address": "Friedrichstraße 100" },
  "packages": [
    { "weight": 2.5, "weightUnit": "KG", "length": 30, "width": 20, "height": 15, "dimUnit": "CM" }
  ],
  "options": { "carrierCodes": ["DHL", "FEDEX"], "serviceType": "EXPRESS" }
}
```

**Response 200:**
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

## 2. Create Shipment — `POST /api/v1/cargo/shipments`

**Purpose:** Create a real shipment with a carrier.

**Request:**
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
    "country": "FR",
    "zipCode": "75001",
    "city": "Paris",
    "address": "12 Rue de Rivoli",
    "address2": "Office 301"
  },
  "recipient": {
    "company": "Berlin GmbH",
    "contactName": "Hans Schmidt",
    "email": "hans@berlin.de",
    "phone": "+4930123456",
    "country": "DE",
    "zipCode": "10115",
    "city": "Berlin",
    "address": "Friedrichstraße 100"
  },
  "packages": [
    {
      "reference": "PARCEL-001",
      "description": "Electronic components",
      "weight": 2.5,
      "weightUnit": "KG",
      "length": 30,
      "width": 20,
      "height": 15,
      "dimUnit": "CM",
      "declaredValue": 500.00,
      "declaredCurrency": "EUR",
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

**Response 201:**
```json
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5",
    "status": "CREATED",
    "carrierCode": "DHL",
    "carrierName": "DHL Express",
    "serviceCode": "DHL_EXPRESS_WORLDWIDE",
    "carrierTrackingNumber": "1234567890",
    "carrierShipmentId": "DE-2026-98765",
    "labelUrl": "https://api.dhl.com/labels/1234567890.pdf",
    "labelFormat": "PDF",
    "trackingUrl": "https://www.dhl.com/track/1234567890",
    "reference": "ORD-2026-001234",
    "price": {
      "total": 45.30,
      "currency": "EUR",
      "breakdown": [
        { "type": "BASE", "amount": 38.00 },
        { "type": "FUEL", "amount": 5.30 },
        { "type": "INSURANCE", "amount": 2.00 }
      ]
    },
    "sender": { "company": "TechCorp Inc", "country": "FR", "zipCode": "75001" },
    "recipient": { "company": "Berlin GmbH", "country": "DE", "zipCode": "10115" },
    "packages": [{ "reference": "PARCEL-001", "weight": 2.5, "trackingNumber": "1234567890-001" }],
    "createdAt": "2026-06-11T10:30:00Z",
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z"
  }
}
```

---

## 3. Get Shipment Details — `GET /api/v1/cargo/shipments/{id}`

**Purpose:** View shipment status and history.

**Response:**
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
    "packages": [{ "reference": "PARCEL-001", "weight": 2.5, "trackingNumber": "1234567890-001" }],
    "price": { "total": 45.30, "currency": "EUR" },
    "createdAt": "2026-06-11T10:30:00Z",
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z"
  }
}
```

---

## 4. Detailed Tracking — `GET /api/v1/cargo/shipments/{id}/tracking`

**Purpose:** View all tracking events with location and raw carrier status.

**Response:**
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
        "description": "Parcel picked up by carrier",
        "location": "Paris, France",
        "timestamp": "2026-06-11T14:00:00Z",
        "carrierRawStatus": "Pickup scanned"
      },
      {
        "eventId": "evt_003",
        "code": "IN_TRANSIT",
        "label": "In transit",
        "description": "Parcel in transit to sorting hub",
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

## 5. Cancel Shipment — `POST /api/v1/cargo/shipments/{id}/cancel`

**Purpose:** Cancel a shipment.

**Response:**
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

## 6. Generate Label — `POST /api/v1/cargo/shipments/{id}/label`

**Purpose:** Generate or retrieve the shipping label.

**Request:**
```json
{ "format": "PDF" }
```

**Response:**
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

## 7. Schedule Pickup — `POST /api/v1/cargo/pickups`

**Purpose:** Request a carrier to collect parcels.

**Request:**
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
    "country": "FR",
    "zipCode": "75001",
    "city": "Paris",
    "address": "12 Rue de Rivoli"
  },
  "totalPackages": 1,
  "totalWeight": 2.5,
  "weightUnit": "KG",
  "specialInstructions": "Ring at reception"
}
```

**Response:**
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
    "location": { "company": "TechCorp Inc", "country": "FR", "city": "Paris", "address": "12 Rue de Rivoli" },
    "instructions": "Ring at reception",
    "createdAt": "2026-06-11T11:00:00Z"
  }
}
```

---

## 8. Incoming Webhook — `POST /api/v1/cargo/webhooks/{carrierCode}`

**Purpose:** Receive status updates pushed by the carrier.

**Request (sent by DHL):**
```json
{
  "shipmentId": "1234567890",
  "status": "DELIVERED",
  "statusDescription": "Shipment delivered",
  "timestamp": "2026-06-13T16:30:00Z",
  "location": { "city": "Berlin", "country": "DE", "zipCode": "10115" },
  "signedBy": "Hans Schmidt",
  "signatureData": "base64...",
  "deliveryPhotoUrl": "https://dhl.com/proof/photo.jpg"
}
```

**Response (always 200):**
```json
{ "success": true, "message": "Webhook processed successfully" }
```

---

## 9. Validate Address — `POST /api/v1/cargo/addresses/validate`

**Purpose:** Validate and normalize an address before shipping.

**Request:**
```json
{
  "country": "FR",
  "zipCode": "75001",
  "city": "Paris",
  "address": "12 Rue de Rivoli",
  "carrierCode": "DHL"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "normalizedAddress": {
      "country": "FR",
      "zipCode": "75001",
      "city": "PARIS",
      "address": "12 RUE DE RIVOLI"
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

## 10. Carrier Management (CRUD)

### 10.1 Add Carrier — `POST /api/v1/cargo/carriers`

**Purpose:** Register a new carrier with credentials and settings.

**Request:**
```json
{
  "code": "CHRONOPOST",
  "name": "Chronopost",
  "adapterName": "ChronopostAdapter",
  "active": true,
  "website": "https://www.chronopost.fr",
  "logoUrl": "https://cdn.example.com/carriers/chronopost.svg",
  "contact": {
    "name": "Chronopost Support",
    "email": "support@chronopost.fr",
    "phone": "+33123456789"
  },
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
    },
    {
      "code": "CHRONO_18",
      "name": "Chrono 18h",
      "description": "Delivery before 6pm next day",
      "maxWeight": 30, "maxWeightUnit": "KG",
      "zones": ["FR", "MC"],
      "transitDays": 1,
      "features": ["SIGNATURE"],
      "active": true
    }
  ],
  "capabilities": {
    "labelFormats": ["PDF", "ZPL"],
    "features": ["RATES", "TRACKING", "SIGNATURE", "INSURANCE", "PICKUP"],
    "labelSizes": ["A6", "A5", "10x15"],
    "requiresSignature": true,
    "supportsSaturday": true,
    "supportsInsurance": true,
    "supportsPickup": true
  },
  "credentials": {
    "authType": "API_KEY",
    "apiKey": "chrono_api_key_12345",
    "apiSecret": "chrono_secret_67890",
    "accountNumber": "CHRONO-ACC-001",
    "endpoint": "https://api.chronopost.fr/v1",
    "webhookSecret": "whsec_chrono_abc123"
  },
  "settings": {
    "timeoutMs": 15000,
    "retryMaxAttempts": 3,
    "retryDelayMs": 1000,
    "rateLimitPerMinute": 60,
    "trackingPollingEnabled": false,
    "webhookEnabled": true
  }
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "code": "CHRONOPOST",
    "name": "Chronopost",
    "adapterName": "ChronopostAdapter",
    "active": true,
    "status": "PENDING_TEST",
    "message": "Carrier added. Run a connection test before using."
  }
}
```

### 10.2 List Carriers — `GET /api/v1/cargo/carriers`

**Purpose:** View all carriers. Filters: `?active=true&zone=FR&feature=INSURANCE&page=1&limit=20`

**Response:**
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
      "logoUrl": "https://cdn.example.com/carriers/dhl.svg",
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

### 10.3 Get Carrier Detail — `GET /api/v1/cargo/carriers/{code}`

**Response:**
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
        "description": "International express delivery",
        "maxWeight": 70, "maxWeightUnit": "KG",
        "zones": ["WORLDWIDE"],
        "transitDays": 2,
        "features": ["SIGNATURE", "INSURANCE", "SATURDAY"],
        "active": true
      }
    ],
    "capabilities": {
      "labelFormats": ["PDF", "ZPL", "PNG"],
      "features": ["RATES", "TRACKING", "SIGNATURE", "INSURANCE", "SATURDAY", "PICKUP"],
      "labelSizes": ["A6", "A5", "4x6"],
      "requiresSignature": true,
      "supportsSaturday": true,
      "supportsInsurance": true,
      "supportsPickup": true,
      "supportsCashOnDelivery": false
    },
    "settings": {
      "timeoutMs": 10000,
      "retryMaxAttempts": 3,
      "retryDelayMs": 500,
      "rateLimitPerMinute": 100,
      "trackingPollingEnabled": true,
      "trackingPollingIntervalMin": 30,
      "webhookEnabled": true
    }
  }
}
```

### 10.4 Update Carrier — `PUT /api/v1/cargo/carriers/{code}`

**Request:**
```json
{
  "settings": { "timeoutMs": 15000, "retryMaxAttempts": 3 },
  "active": true
}
```

### 10.5 Toggle Carrier — `PATCH /api/v1/cargo/carriers/{code}/toggle`

**Purpose:** Enable/disable a carrier (e.g., FedEx outage).

**Request:**
```json
{ "active": false, "reason": "API outage - maintenance" }
```

**Response:**
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

### 10.6 Test Connection — `POST /api/v1/cargo/carriers/{code}/test`

**Response (success):**
```json
{
  "success": true,
  "data": {
    "status": "CONNECTED",
    "latencyMs": 245,
    "testedAt": "2026-06-11T15:00:00Z",
    "endpoint": "https://api.chronopost.fr/v1/health",
    "details": { "httpStatus": 200, "message": "API is reachable", "accountValid": true }
  }
}
```

**Response (failure):**
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

### 10.7 Add Service — `POST /api/v1/cargo/carriers/{code}/services`

**Request:**
```json
{
  "code": "DHL_EXPRESS_9",
  "name": "Express 9:00",
  "description": "Delivery before 9am next day",
  "maxWeight": 30, "maxWeightUnit": "KG",
  "zones": ["FR", "DE", "BE", "NL", "LU"],
  "transitDays": 1,
  "features": ["SIGNATURE", "INSURANCE"],
  "active": true
}
```

### 10.8 Update Credentials — `PUT /api/v1/cargo/carriers/{code}/credentials`

**Request:**
```json
{
  "authType": "API_KEY",
  "apiKey": "new_dhl_api_key_67890",
  "apiSecret": "new_dhl_secret_12345",
  "webhookSecret": "whsec_new_abc456"
}
```

**Response:**
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

## Complete Typical Flow

```
1. POST /carriers                        → Add a new carrier (Chronopost)
2. POST /carriers/CHRONOPOST/test        → Test connection
3. GET  /carriers                        → View available carriers
4. POST /rates                           → Compare DHL / FedEx prices
5. POST /addresses/validate              → Validate recipient address
6. POST /shipments                       → Create the shipment
7. POST /pickups                         → Schedule pickup
8. ← DHL Webhook (DELIVERED)             → Automatic status update
9. GET  /shipments/{id}/tracking         → Track in real time
10. POST /shipments/{id}/cancel          → Cancel if needed
```

## Shipment Lifecycle (Statuses)

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

## Data Models

### `shipments` table

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Internal identifier |
| `status` | enum | CREATED, VALIDATED, PICKED_UP, IN_TRANSIT, OUT_FOR_DELIVERY, DELIVERED, FAILED, CANCELLED |
| `carrier_code` | string | DHL, FEDEX, CHRONOPOST |
| `carrier_service_code` | string | DHL_EXPRESS_WORLDWIDE |
| `carrier_tracking_number` | string | Carrier tracking number |
| `carrier_shipment_id` | string | Carrier shipment ID |
| `reference` | string | Business reference |
| `label_url` | string | Label URL |
| `label_format` | string | PDF, ZPL |
| `tracking_url` | string | Carrier tracking URL |
| `sender` | JSON | Sender address |
| `recipient` | JSON | Recipient address |
| `packages` | JSON[] | Parcel list |
| `price_total` | decimal | Total price |
| `price_currency` | string | EUR, USD |
| `insurance_amount` | decimal | Insured amount |
| `signature_required` | boolean | Signature required |
| `saturday_delivery` | boolean | Saturday delivery |
| `estimated_delivery_date` | datetime | Estimated date |
| `actual_delivery_date` | datetime | Actual delivery date |
| `created_at` | datetime | |
| `updated_at` | datetime | |

### `tracking_events` table

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier |
| `shipment_id` | UUID | Reference to shipment |
| `code` | enum | LABEL_CREATED, PICKED_UP, IN_TRANSIT, ARRIVED_AT_HUB, DEPARTED_FROM_HUB, OUT_FOR_DELIVERY, DELIVERED, DELIVERY_ATTEMPTED, FAILED, RETURNED_TO_SENDER, CUSTOMS_HELD, CUSTOMS_CLEARED |
| `label` | string | Human-readable label |
| `description` | string | Detailed description |
| `location` | JSON | City, country |
| `timestamp` | datetime | Event date |
| `carrier_raw_status` | string | Raw carrier status |
| `carrier_raw_data` | JSON | Raw payload |
| `signed_by` | string | Signatory name |
| `delivery_photo_url` | string | Proof of delivery photo |

### `carriers` table

| Field | Type | Description |
|-------|------|-------------|
| `code` | string (PK) | DHL, FEDEX, CHRONOPOST |
| `name` | string | Commercial name |
| `adapter_name` | string | Adapter class (DhlAdapter) |
| `active` | boolean | Enabled or disabled |
| `status` | enum | PENDING_TEST, CONNECTED, DISCONNECTED, ERROR |
| `last_tested_at` | datetime | Last connection test |
| `capabilities` | JSON | Technical capabilities |
| `settings` | JSON | Timeout, retry, rate limit |
| `credentials` | JSON (encrypted) | API keys, secrets |
| `contact` | JSON | Support contact |
| `created_at` | datetime | |
| `updated_at` | datetime | |

### `carrier_services` table

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID (PK) | |
| `carrier_code` | string (FK) | Reference to carrier |
| `code` | string | DHL_EXPRESS_WORLDWIDE |
| `name` | string | Express Worldwide |
| `max_weight` | decimal | Max weight |
| `zones` | JSON[] | FR, DE, BE... |
| `transit_days` | int | Transit days |
| `features` | JSON[] | SIGNATURE, INSURANCE |
| `active` | boolean | Service active |
