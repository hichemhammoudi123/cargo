# Cargo Delivery Service — All Endpoints

> **Single document** : every endpoint with request, response, field-by-field comments, pipeline explanation, and final mapping schema.

---

## Table of Contents

1. [Create a Shipment](#1-create-a-shipment) — `POST /api/v1/cargo/shipments`
2. [List Shipments](#2-list-shipments) — `GET /api/v1/cargo/shipments`
3. [Shipment Detail](#3-shipment-detail) — `GET /api/v1/cargo/shipments/{id}`
4. [Update a Shipment](#4-update-a-shipment) — `PUT /api/v1/cargo/shipments/{id}`
5. [Delete a Shipment](#5-delete-a-shipment) — `DELETE /api/v1/cargo/shipments/{id}`
6. [Cancel a Shipment](#6-cancel-a-shipment) — `POST /api/v1/cargo/shipments/{id}/cancel`
7. [Generate Label](#7-generate-label) — `POST /api/v1/cargo/shipments/{id}/label`
8. [Detailed Tracking](#8-detailed-tracking) — `GET /api/v1/cargo/shipments/{id}/tracking`
9. [Inbound Webhook](#9-inbound-webhook) — `POST /api/v1/cargo/webhooks/{carrierCode}`
10. [Compare Rates](#10-compare-rates) — `POST /api/v1/cargo/rates`
11. [Schedule a Pickup](#11-schedule-a-pickup) — `POST /api/v1/cargo/pickups`
12. [Cancel a Pickup](#12-cancel-a-pickup) — `POST /api/v1/cargo/pickups/{id}/cancel`
13. [Add a Carrier](#13-add-a-carrier) — `POST /api/v1/cargo/carriers`
14. [List Carriers](#14-list-carriers) — `GET /api/v1/cargo/carriers`
15. [Carrier Detail](#15-carrier-detail) — `GET /api/v1/cargo/carriers/{code}`
16. [Update a Carrier](#16-update-a-carrier) — `PUT /api/v1/cargo/carriers/{code}`
17. [Delete a Carrier](#17-delete-a-carrier) — `DELETE /api/v1/cargo/carriers/{code}`
18. [Toggle a Carrier](#18-toggle-a-carrier) — `PATCH /api/v1/cargo/carriers/{code}/toggle`
19. [Test Connection](#19-test-connection) — `POST /api/v1/cargo/carriers/{code}/test`
20. [Update Credentials](#20-update-credentials) — `PUT /api/v1/cargo/carriers/{code}/credentials`
21. [Add a Service](#21-add-a-service) — `POST /api/v1/cargo/carriers/{code}/services`
22. [Validate Address](#22-validate-address) — `POST /api/v1/cargo/addresses/validate`
23. [Full Pipeline Schema with Mapping](#23-full-pipeline-schema-with-mapping)
24. [Endpoints Summary](#24-endpoints-summary)

---

## 1. Create a Shipment

### `POST /api/v1/cargo/shipments`

**When?** The user has chosen a carrier (DHL/UPS/...) via the Rates page and wants to ship a parcel.

**Pipeline:** Request → `DhlAdapter.createShipment()` → DHL API → **Mapper** → Response

**Request:**
```json
{
  "carrierCode": "DHL",                    // Selected carrier code (DHL, UPS, FEDEX, YURTICI, ARAMEX, MNG)
  "serviceCode": "DHL_EXPRESS_WORLDWIDE",  // Chosen service (fetched from GET /rates)
  "reference": "CMD-2026-001234",          // Business reference (order number, invoice...)
  "sender": {
    "company": "TechCorp SAS",             // Sender company name
    "contactName": "Jean Dupont",          // Sender contact person
    "email": "jean@techcorp.fr",           // Email for notifications
    "phone": "+33123456789",               // Phone for the carrier
    "country": "FR",                       // ISO 3166-1 alpha-2 country code
    "zipCode": "75001",                    // Zip code
    "city": "Paris",                       // City
    "address": "12 Rue de Rivoli"          // Address (street + number)
  },
  "recipient": {
    "company": "Berlin GmbH",              // Recipient company name
    "contactName": "Hans Schmidt",         // Recipient contact person
    "email": "hans@berlin.de",             // Recipient email
    "phone": "+4930123456",                // Recipient phone
    "country": "DE",                       // ISO country code
    "zipCode": "10115",                    // Zip code
    "city": "Berlin",                      // City
    "address": "Friedrichstraße 100"       // Address
  },
  "packages": [
    {
      "reference": "COLIS-001",            // Internal package reference
      "description": "Composants électroniques", // Content description
      "weight": 2.5,                       // Weight
      "weightUnit": "KG",                  // Weight unit (KG or LB)
      "length": 30,                        // Length in cm
      "width": 20,                         // Width in cm
      "height": 15,                        // Height in cm
      "dimUnit": "CM",                     // Dimension unit (CM or IN)
      "declaredValue": 500.00,             // Declared value for insurance
      "declaredCurrency": "EUR"            // Declared value currency
    }
  ],
  "options": {
    "insurance": {
      "amount": 500.00,                    // Insured amount
      "currency": "EUR"                    // Currency
    },
    "signatureRequired": true,             // Signature required on delivery
    "saturdayDelivery": false              // Saturday delivery
  }
}
```

**What happens:**
1. The data is sent (recipient, packages, insurance...)
2. The chosen carrier's Adapter transforms the data into the JSON format expected by the carrier's API
   - Ex: `"country":"FR"` → DHL expects `"countryCode":"FR"`, UPS expects `"country":"FR"`
3. The Adapter calls the carrier's API (POST /shipments)
4. The carrier responds with a tracking number, label, and price
5. The Adapter normalizes the response into our common format
6. The Core System saves the shipment with status = "SUBMITTED"
7. The user receives the internal ID, tracking number, and label URL

**Business rules:**
- The carrier must be active and connected (verified via CarrierRegistry)
- The address should be validated (optional but recommended)
- If the carrier API is unreachable → 502 error + automatic retry

**Response 201:**
```json
{
  "success": true,                                 // Request status
  "data": {
    "id": "shp_a1b2c3d4e5",                       // Internal shipment ID (prefixed UUID)
    "internalStatus": "PENDING",                   // Internal status (PENDING | PICKED_UP | IN_PROGRESS | DELIVERED | RETURNED | CANCELLED)
    "carrierStatus": "Shipment information received", // Raw carrier status (kept for debugging)
    "carrierCode": "DHL",                          // Carrier code used
    "carrierName": "DHL Express",                  // Carrier name
    "carrierTrackingNumber": "1234567890",         // Carrier tracking number
    "carrierShipmentId": "DE-2026-98765",          // Carrier shipment ID
    "labelUrl": "https://api.dhl.com/labels/1234567890.pdf", // Label URL (PDF)
    "labelFormat": "PDF",                          // Label format
    "trackingUrl": "https://www.dhl.com/track/1234567890", // Carrier tracking URL
    "reference": "CMD-2026-001234",                // Business reference (copied from request)
    "price": {
      "total": 45.30,                              // Total price in EUR
      "currency": "EUR",
      "breakdown": [                               // Price breakdown
        { "type": "BASE", "label": "Transport", "amount": 38.00 },
        { "type": "FUEL", "label": "Fuel surcharge", "amount": 5.30 },
        { "type": "INSURANCE", "label": "Insurance", "amount": 2.00 }
      ]
    },
    "sender": { "company": "TechCorp SAS", "country": "FR", "zipCode": "75001" },
    "recipient": { "company": "Berlin GmbH", "country": "DE", "zipCode": "10115" },
    "packages": [{
      "reference": "COLIS-001",
      "weight": 2.5,
      "trackingNumber": "1234567890-001"           // Per-package tracking number
    }],
    "createdAt": "2026-06-11T10:30:00Z",           // Creation date (ISO 8601)
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z" // Estimated delivery date
  }
}
```

> **Mapping here:** `DhlAdapter.createShipment()` transforms our JSON → DHL format, calls the DHL API, then normalizes the DHL response → our format.

---

## 2. List Shipments

### `GET /api/v1/cargo/shipments`

**When?** Home page, dashboard, search.

**Pipeline:** Database only (no carrier API call)

**Query params:**
```
?status=IN_PROGRESS     // Filter by internal status (PENDING, PICKED_UP, IN_PROGRESS, DELIVERED...)
&carrier=UPS            // Filter by carrier
&from=2026-06-01        // Min creation date
&to=2026-06-14          // Max creation date
&q=CMD-2026             // Text search (reference, recipient name)
&page=1                 // Page number
&limit=20               // Items per page
```

**What happens:**
1. Paginated query with optional filters (status, carrier, date)
2. The Core System queries the database
3. Returns the list with pagination

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "shp_a1b2c3d4e5",                     // Internal ID
      "internalStatus": "IN_PROGRESS",             // Internal status (6 values)
      "carrierStatus": "OnTheWay",                 // Raw carrier status
      "carrierCode": "UPS",                        // Carrier code
      "carrierTrackingNumber": "1Z999AA10123456784", // Carrier tracking number
      "reference": "CMD-2026-001235",              // Business reference
      "recipient": { "company": "ACME GmbH", "country": "DE" }, // Recipient (summary)
      "createdAt": "2026-06-11T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,                                     // Current page
    "limit": 20,                                   // Limit per page
    "total": 42                                    // Total items
  }
}
```

---

## 3. Shipment Detail

### `GET /api/v1/cargo/shipments/{id}`

**When?** The user clicks on a shipment to see all its details.

**Pipeline:** Database only (no carrier API call)

**What happens:**
1. Fetches the shipment by its ID
2. Returns all info: status, history, price, packages, addresses
3. The displayed status is the INTERNAL status (PENDING, IN_PROGRESS, DELIVERED...)
4. The raw carrier status is kept alongside (OnTheWay, Yolda...)

**Response 200:**
```json
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5",
    "internalStatus": "IN_PROGRESS",               // Internal status (mapped by StatusMapper)
    "carrierStatus": "OnTheWay",                   // Raw carrier status (kept for traceability)
    "statusHistory": [                             // Complete status change history
      {
        "status": "SUBMITTED",                     // Status at event time
        "internalStatus": "PENDING",               // Corresponding internal status
        "timestamp": "2026-06-11T10:30:00Z"
      },
      {
        "status": "PICKED_UP",
        "internalStatus": "PICKED_UP",
        "timestamp": "2026-06-11T14:00:00Z"
      },
      {
        "status": "OnTheWay",                      // Raw UPS status: "OnTheWay"
        "internalStatus": "IN_PROGRESS",            // Mapped by StatusMapper → "IN_PROGRESS"
        "timestamp": "2026-06-12T08:15:00Z"
      }
    ],
    "carrierCode": "UPS",
    "carrierTrackingNumber": "1Z999AA10123456784",
    "reference": "CMD-2026-001235",
    "sender": { "company": "TechCorp SAS", "country": "FR" },
    "recipient": { "company": "ACME GmbH", "country": "DE" },
    "packages": [{ "reference": "COLIS-001", "weight": 2.5 }],
    "price": { "total": 48.50, "currency": "EUR" },
    "createdAt": "2026-06-11T10:30:00Z",
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z"
  }
}
```

---

## 4. Update a Shipment

### `PUT /api/v1/cargo/shipments/{id}`

**When?** The user wants to change the reference or options (signature, insurance) before the parcel is picked up.

**Business rules:**
- Modification only possible if status = `SUBMITTED` (not yet picked up)
- Cannot change carrier or recipient after creation
- Modifications are not synced with the carrier (unless their API allows it)

**Request:**
```json
{
  "reference": "CMD-2026-001235-UPDATED",          // New reference
  "options": {
    "signatureRequired": false                      // Disable signature
  }
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5",
    "reference": "CMD-2026-001235-UPDATED",
    "updatedAt": "2026-06-11T11:00:00Z"
  }
}
```

---

## 5. Delete a Shipment

### `DELETE /api/v1/cargo/shipments/{id}`

**When?** The user wants to permanently delete a shipment (draft, test, error).

**Business rules:**
- Deletion only possible if status = `SUBMITTED` or `PENDING`
- If the parcel is already in transit → use `POST /cancel` instead

**Response 200:**
```json
{
  "success": true,
  "data": { "deleted": true }                      // Deletion confirmation
}
```

---

## 6. Cancel a Shipment

### `POST /api/v1/cargo/shipments/{id}/cancel`

**When?** The parcel is already picked up but needs cancellation (client cancels order, shipping error).

**Pipeline:** → `UpsAdapter.cancelShipment()` → UPS API → Core

**What happens:**
1. Checks that the shipment is not already delivered or cancelled
2. Calls the Adapter → carrier API to cancel
3. The carrier confirms cancellation (or refuses if already delivered)
4. The status changes to "CANCELLED" in Core
5. A "shipment.cancelled" event is published → client notification

**Business rules:**
- Impossible if status = `DELIVERED` (already delivered)
- Impossible if status = `CANCELLED` (already cancelled)
- The carrier may refuse cancellation (e.g., parcel already in final delivery)

**Response 200:**
```json
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5",
    "internalStatus": "CANCELLED",                 // Updated internal status
    "carrierStatus": "Cancelled",                  // Carrier status
    "cancelledAt": "2026-06-11T12:00:00Z"          // Cancellation date
  }
}
```

> **Mapping here:** `UpsAdapter.cancelShipment()` transforms our request → UPS format, calls UPS API.

---

## 7. Generate Label

### `POST /api/v1/cargo/shipments/{id}/label`

**When?** The user wants to download or reprint the label.

**Pipeline:** → `DhlAdapter.getLabel()` → DHL API

**What happens:**
1. Calls the Adapter → carrier API to fetch the label
2. Returns the label URL in the requested format (PDF, ZPL, PNG)
3. The URL can be a direct URL or a signed temporary link

**Request:**
```json
{
  "format": "PDF"                                   // Requested format (PDF, ZPL, PNG)
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "labelUrl": "https://api.dhl.com/labels/1234567890.pdf", // Label URL
    "format": "PDF",                                 // Returned format
    "size": "A6",                                    // Paper size (A6, A5, 10x15)
    "generatedAt": "2026-06-11T10:30:00Z"             // Generation date
  }
}
```

---

## 8. Detailed Tracking

### `GET /api/v1/cargo/shipments/{id}/tracking`

**When?** The user clicks "Track" or the Tracking page refreshes.

**Pipeline:** → `DhlAdapter.track()` → DHL API → **StatusMapper** → Core

**What happens:**
1. Calls the Adapter → carrier API to fetch recent events
2. For each event, the **StatusMapper** translates the raw status → internal status
   - Ex: "OnTheWay" (UPS) → "IN_PROGRESS"
   - Ex: "Yolda" (Yurtiçi) → "IN_PROGRESS"
3. Events are grouped into milestones (key lifecycle stages)
4. Returns the complete timeline with location and timestamps

**Response 200:**
```json
{
  "success": true,
  "data": {
    "shipmentId": "shp_a1b2c3d4e5",                 // Internal ID
    "carrierCode": "DHL",                            // Carrier code
    "carrierTrackingNumber": "1234567890",           // Carrier tracking number
    "currentStatus": {                               // Latest known status
      "internalCode": "IN_PROGRESS",                 // Internal status (mapped by StatusMapper)
      "carrierCode": "IN_TRANSIT",                   // Carrier status code
      "label": "In transit",                         // Human-readable label
      "location": "Frankfurt, Germany",              // Location
      "timestamp": "2026-06-12T08:15:00Z"
    },
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z",
    "events": [                                      // All tracking events
      {
        "eventId": "evt_001",
        "internalCode": "PENDING",                   // Internal status (mapped)
        "carrierCode": "LABEL_CREATED",              // Carrier code
        "carrierRawStatus": "Shipment information received", // RAW carrier status (kept for debugging)
        "label": "Label created",
        "location": "Paris, France",
        "timestamp": "2026-06-11T10:30:00Z"
      },
      {
        "eventId": "evt_002",
        "internalCode": "PICKED_UP",                 // Mapped: "Pickup scanned" → PICKED_UP
        "carrierCode": "PICKED_UP",
        "carrierRawStatus": "Pickup scanned",
        "label": "Package picked up",
        "location": "Paris, France",
        "timestamp": "2026-06-11T14:00:00Z"
      },
      {
        "eventId": "evt_003",
        "internalCode": "IN_PROGRESS",               // Mapped: "Departed from transit hub" → IN_PROGRESS
        "carrierCode": "IN_TRANSIT",
        "carrierRawStatus": "Departed from transit hub",
        "label": "In transit",
        "location": "Frankfurt, Germany",
        "timestamp": "2026-06-12T08:15:00Z"
      }
    ],
    "milestones": {                                  // Key lifecycle milestones
      "pending": "2026-06-11T10:30:00Z",             // Creation
      "pickedUp": "2026-06-11T14:00:00Z",           // Pickup
      "inProgress": "2026-06-12T08:15:00Z",         // In transit
      "delivered": null                               // Not yet delivered
    }
  }
}
```

> **CRITICAL MAPPING here:** Every `carrierRawStatus` is passed through `StatusMapper.map("DHL", rawStatus)` to produce `internalCode`.

---

## 9. Inbound Webhook

### `POST /api/v1/cargo/webhooks/{carrierCode}`

**When?** The carrier automatically notifies the system when an event occurs (parcel picked up, delivered, etc.).

**Pipeline:** Webhook → HMAC validation → `UpsAdapter.parseWebhook()` → **StatusMapper.map("UPS", rawStatus)** → Core

**What happens:**
1. The carrier sends an HTTP POST request with its raw JSON format
   - UPS → `{ "shipment_id": "...", "state": "Completed" }`
   - DHL → `{ "trackingNumber": "...", "status": "DELIVERED" }`
   - Yurtiçi → `{ "takipNo": "...", "durum": "Teslim Edildi" }`
2. HMAC signature validation (security)
3. The Adapter parses the payload → normalized format `{ tracking_no, carrier_raw_status, ... }`
4. The **StatusMapper** translates the raw status → internal status
5. Core: creates a TrackingEvent, updates Shipment.status
6. If the status is terminal → publishes an event (client notification, audit...)
7. Returns 200 to the carrier (acknowledgment)

**Why always 200?** The carrier considers a non-200 webhook as a failure and retries. Even if server-side processing fails, we respond 200 and log the error.

**Security:** Each carrier has a `webhookSecret` stored in their credentials. The HMAC-SHA256 signature of the payload is validated before any processing.

### UPS sends this:

```json
{
  "shipment_id": "1Z999AA10123456784",               // UPS tracking number (field differs per carrier)
  "state": "Completed",                              // UPS status: "Completed" (≠ DHL "DELIVERED")
  "customer": "Ahmed",                               // Recipient name (UPS uses "customer")
  "signed_by": "Ahmed",                              // Signatory
  "timestamp": "2026-06-13T16:30:00Z"                // Timestamp
}
```

**What the Core System sees after mapping:**
```json
{
  "tracking_no": "1Z999AA10123456784",               // Normalized by UpsAdapter (shipment_id → tracking_no)
  "carrier_raw_status": "Completed",                 // Raw status preserved
  "internalStatus": "DELIVERED",                     // Mapped by StatusMapper: "Completed" → "DELIVERED"
  "customer_name": "Ahmed",                          // Normalized (customer → customer_name)
  "timestamp": "2026-06-13T16:30:00Z"
}
```

### DHL sends this:

```json
{
  "trackingNumber": "1234567890",                    // DHL uses "trackingNumber" (≠ UPS "shipment_id")
  "status": "DELIVERED",                             // DHL uses "DELIVERED" (≠ UPS "Completed")
  "statusDescription": "Shipment delivered",
  "timestamp": "2026-06-13T16:30:00Z",
  "location": { "city": "Berlin", "country": "DE" },
  "signedBy": "Hans Schmidt"                         // DHL uses "signedBy" (≠ UPS "signed_by")
}
```

**What the Core System sees after mapping:**
```json
{
  "tracking_no": "1234567890",                       // Normalized (trackingNumber → tracking_no)
  "carrier_raw_status": "DELIVERED",                 // Raw status preserved
  "internalStatus": "DELIVERED",                     // Mapped: "DELIVERED" → "DELIVERED"
  "customer_name": "Hans Schmidt",                   // Normalized (signedBy → customer_name)
  "timestamp": "2026-06-13T16:30:00Z"
}
```

### Yurtiçi Kargo sends this:

```json
{
  "takipNo": "YT2026001122334",                       // Yurtiçi uses "takipNo" (Turkish)
  "durum": "Teslim Edildi",                           // Status in Turkish: "Teslim Edildi" (≠ "DELIVERED")
  "alici": "Ahmet",                                   // Recipient: "alici" (≠ "customer")
  "tarih": "2026-06-13T16:30:00Z"                     // Date: "tarih" (≠ "timestamp")
}
```

**What the Core System sees after mapping:**
```json
{
  "tracking_no": "YT2026001122334",                   // Normalized (takipNo → tracking_no)
  "carrier_raw_status": "Teslim Edildi",              // Raw Turkish status preserved
  "internalStatus": "DELIVERED",                      // Mapped by StatusMapper: "Teslim Edildi" → "DELIVERED"
  "customer_name": "Ahmet",                           // Normalized (alici → customer_name)
  "timestamp": "2026-06-13T16:30:00Z"
}
```

### Response (always 200)

```json
{
  "success": true,
  "message": "Webhook processed successfully"         // The carrier knows the webhook was received
}
```

> **CRITICAL MAPPING here:** The Adapter parses the JSON payload (field normalization), then the StatusMapper translates the status (value normalization). This is the single entry point for all carriers.

---

## 10. Compare Rates

### `POST /api/v1/cargo/rates`

**When?** The user fills in the form (sender, recipient, packages) and clicks "Get rates".

**Pipeline:** → `DhlAdapter.getRates()` + `UpsAdapter.getRates()` + `FedExAdapter.getRates()` in parallel → Aggregation

**What happens:**
1. Fetches all active carriers (or those requested in carrierCodes[])
2. For each carrier, calls its Adapter: adapter.getRates(rateRequest)
3. All calls are parallelized (Promise.all) for performance
4. Results are aggregated and sorted by ascending price
5. Returns the comparison table

**Case when a carrier doesn't respond:**
- If a carrier is unreachable → it is excluded from results with an error in errors[]
- Other carriers are still returned

**Request:**
```json
{
  "sender": {                                        // Sender address
    "country": "FR",
    "zipCode": "75001",
    "city": "Paris"
  },
  "recipient": {                                     // Recipient address
    "country": "DE",
    "zipCode": "10115",
    "city": "Berlin"
  },
  "packages": [{                                     // Packages to ship
    "weight": 2.5,
    "weightUnit": "KG",
    "length": 30, "width": 20, "height": 15,
    "dimUnit": "CM"
  }],
  "options": {
    "carrierCodes": ["DHL", "UPS", "FEDEX"],          // Carriers to compare (empty = all)
    "serviceType": "EXPRESS"                           // Service type
  }
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
      "totalPrice": 45.30,                             // Total price
      "currency": "EUR",
      "estimatedTransitDays": 2,                       // Estimated transit days
      "estimatedDeliveryDate": "2026-06-13",
      "guaranteed": true,                              // Guaranteed date?
      "breakdown": [
        { "type": "BASE", "label": "Transport", "amount": 38.00 },
        { "type": "FUEL", "label": "Fuel surcharge", "amount": 5.30 },
        { "type": "INSURANCE", "label": "Insurance", "amount": 2.00 }
      ]
    },
    {
      "carrierCode": "UPS",
      "carrierName": "UPS",
      "serviceCode": "UPS_EXPRESS_SAVER",
      "serviceName": "UPS Express Saver",
      "totalPrice": 42.00,
      "currency": "EUR",
      "estimatedTransitDays": 3,
      "breakdown": [
        { "type": "BASE", "amount": 36.00 },
        { "type": "FUEL", "amount": 4.50 },
        { "type": "INSURANCE", "amount": 1.50 }
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
      "breakdown": [
        { "type": "BASE", "amount": 41.00 },
        { "type": "FUEL", "amount": 5.50 },
        { "type": "INSURANCE", "amount": 2.00 }
      ]
    }
  ]
}
```

> **Mapping here:** Each Adapter (`DhlAdapter`, `UpsAdapter`, `FedExAdapter`) transforms the request into its carrier's format, calls its API, and normalizes the response.

---

## 11. Schedule a Pickup

### `POST /api/v1/cargo/pickups`

**When?** The user has created shipments and wants the carrier to collect parcels from their warehouse.

**Pipeline:** → `DhlAdapter.schedulePickup()` → DHL API

**What happens:**
1. Checks that the referenced shipments (shipmentIds) exist and are in SUBMITTED status
2. Calls the Adapter → carrier API to schedule the pickup
3. The carrier confirms with a confirmation number
4. The Pickup is created in DB with status = "CONFIRMED"

**Business rules:**
- Shipments must belong to the same carrier
- pickupDate cannot be in the past
- readyTime must be before closeTime
- The carrier may refuse if the timeslot is unavailable

**Request:**
```json
{
  "carrierCode": "DHL",                               // Carrier
  "shipmentIds": ["shp_a1b2c3d4e5"],                  // Affected shipments
  "pickupDate": "2026-06-12",                          // Requested date
  "readyTime": "09:00",                                // Availability time
  "closeTime": "17:00",                                // Closing time
  "location": {                                        // Pickup address
    "company": "TechCorp SAS",
    "contactName": "Jean Dupont",
    "phone": "+33123456789",
    "country": "FR", "zipCode": "75001",
    "city": "Paris", "address": "12 Rue de Rivoli"
  },
  "totalPackages": 1,                                  // Total number of packages
  "totalWeight": 2.5,                                  // Total weight
  "weightUnit": "KG",
  "specialInstructions": "Ring at reception"           // Special instructions
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "id": "pck_001a2b3c",                              // Internal pickup ID
    "carrierCode": "DHL",
    "carrierPickupId": "DHL-PICKUP-98765",              // Carrier pickup ID
    "status": "CONFIRMED",                              // Status (CONFIRMED, CANCELLED)
    "pickupDate": "2026-06-12",
    "confirmationNumber": "CONF-ABC-123"                // Confirmation number
  }
}
```

---

## 12. Cancel a Pickup

### `POST /api/v1/cargo/pickups/{id}/cancel`

**When?** The user wants to cancel the carrier's visit.

**Pipeline:** → `DhlAdapter.cancelPickup()` → DHL API

**Business rules:**
- Cancellation only possible if the pickup hasn't happened yet (pickupDate >= today)
- Calls the Adapter → carrier API to cancel
- Changes status to "CANCELLED"

**Response 200:**
```json
{
  "success": true,
  "data": {
    "id": "pck_001a2b3c",
    "status": "CANCELLED",
    "cancelledAt": "2026-06-11T14:00:00Z"
  }
}
```

---

## 13. Add a Carrier

### `POST /api/v1/cargo/carriers`

**When?** The administrator wants to integrate a new carrier (e.g., MNG Kargo, Aramex, etc.).

**What happens:**
1. Receives carrier info (name, API endpoint, keys, services...)
2. Saves to DB with status = "PENDING_TEST" (not yet tested)
3. The corresponding Adapter must be coded and deployed before using this carrier
4. Returns a message: "Run a connection test before using"

**Request:**
```json
{
  "code": "UPS",                                       // Unique carrier code
  "name": "UPS",                                       // Commercial name
  "adapterName": "UpsAdapter",                         // Adapter class name (for Registry)
  "active": true,                                      // Active on add?
  "website": "https://www.ups.com",
  "contact": {
    "name": "UPS Support",
    "email": "support@ups.com",
    "phone": "+18007425877"
  },
  "services": [{                                       // Offered services
    "code": "UPS_EXPRESS_SAVER",
    "name": "UPS Express Saver",
    "description": "International express shipping",
    "maxWeight": 70, "maxWeightUnit": "KG",
    "zones": ["WORLDWIDE"],
    "transitDays": 2,
    "features": ["SIGNATURE", "INSURANCE"],
    "active": true
  }],
  "capabilities": {                                    // Technical capabilities
    "labelFormats": ["PDF", "ZPL"],
    "features": ["RATES", "TRACKING", "SIGNATURE", "INSURANCE", "PICKUP"]
  },
  "credentials": {                                     // API keys (encrypted at rest)
    "authType": "API_KEY",
    "apiKey": "ups_api_key_123",
    "apiSecret": "ups_secret_456",
    "accountNumber": "UPS-ACC-001",
    "endpoint": "https://onlinetools.ups.com/api",
    "webhookSecret": "whsec_ups_abc123"
  },
  "settings": {                                        // Technical settings
    "timeoutMs": 10000,                                // API call timeout
    "retryMaxAttempts": 3,                             // Retry attempts on failure
    "retryDelayMs": 1000,
    "rateLimitPerMinute": 50                           // Request limit per minute
  }
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "code": "UPS",
    "name": "UPS",
    "adapterName": "UpsAdapter",
    "active": true,
    "status": "PENDING_TEST",                          // Awaiting test (not yet usable)
    "message": "Carrier added. Run a connection test before using."
  }
}
```

---

## 14. List Carriers

### `GET /api/v1/cargo/carriers`

**When?** Carrier management page.

**Filters:**
```
?active=true           // Active carriers only
&feature=TRACKING      // Only those that support tracking
&zone=TR               // Only those that deliver to Turkey
```

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "code": "DHL", "name": "DHL Express",
      "adapterName": "DhlAdapter",
      "active": true,
      "status": "CONNECTED",                           // CONNECTED, PENDING_TEST, DISCONNECTED, ERROR
      "services": [                                    // Services summary
        { "code": "DHL_EXPRESS_WORLDWIDE", "name": "Express Worldwide", "active": true }
      ]
    }
  ],
  "pagination": { "page": 1, "limit": 20, "total": 3 }
}
```

---

## 15. Carrier Detail

### `GET /api/v1/cargo/carriers/{code}`

**When?** The administrator clicks on a carrier to view/configure its settings.

**Note:** Credentials are never returned — only the last update date.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "code": "UPS",
    "name": "UPS",
    "adapterName": "UpsAdapter",
    "active": true,
    "status": "CONNECTED",
    "lastTestedAt": "2026-06-10T08:00:00Z",            // Last connection test
    "services": [{
      "code": "UPS_EXPRESS_SAVER",
      "name": "UPS Express Saver",
      "maxWeight": 70,
      "zones": ["WORLDWIDE"],
      "transitDays": 2,
      "features": ["SIGNATURE", "INSURANCE"],
      "active": true
    }],
    "capabilities": {
      "features": ["RATES", "TRACKING", "SIGNATURE", "INSURANCE", "PICKUP"]
    },
    "settings": {
      "timeoutMs": 10000,
      "retryMaxAttempts": 3,
      "rateLimitPerMinute": 100
    },
    "credentialsUpdatedAt": "2026-06-01T12:00:00Z"    // Last credentials update (never the keys themselves)
  }
}
```

---

## 16. Update a Carrier

### `PUT /api/v1/cargo/carriers/{code}`

**When?** The administrator wants to change the timeout, retry count, or enable/disable polling.

**Request:**
```json
{
  "active": true,                                      // Enable/disable
  "settings": {                                        // Modify settings
    "timeoutMs": 15000,
    "retryMaxAttempts": 5
  }
}
```

---

## 17. Delete a Carrier

### `DELETE /api/v1/cargo/carriers/{code}`

**When?** The administrator wants to permanently remove a carrier.

**Business rules:**
- Does not delete existing shipments (they remain read-only)
- The carrier is no longer available for new shipments
- Credentials are permanently deleted

**Response 200:**
```json
{ "success": true, "data": { "deleted": true } }
```

---

## 18. Toggle a Carrier

### `PATCH /api/v1/cargo/carriers/{code}/toggle`

**When?** The carrier has an API outage (e.g., FedEx API down) → temporarily disable it. When the API recovers → re-enable it.

**What happens:**
- When active = false: carrier is no longer called for rates, no new shipments possible, a "carrier.disconnected" event is published
- When active = true: the carrier becomes available again, a "carrier.connected" event is published

**Request:**
```json
{
  "active": false,                                     // false = disabled (e.g., API outage)
  "reason": "API outage - maintenance"                 // Reason for disabling
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "code": "UPS",
    "active": false,
    "deactivatedAt": "2026-06-11T14:00:00Z"
  }
}
```

---

## 19. Test Connection

### `POST /api/v1/cargo/carriers/{code}/test`

**When?** Right after adding a carrier, or after updating credentials, or periodically.

**Pipeline:** → `UpsAdapter.testConnection()` → UPS health API

**What happens:**
1. Calls the Adapter → adapter.testConnection()
2. The Adapter makes a lightweight call to the carrier API (e.g., GET /health)
3. Measures latency
4. Verifies credentials are valid
5. Updates carrier status: Success → "CONNECTED", Failure → "ERROR"

**Response — Success:**
```json
{
  "success": true,
  "data": {
    "status": "CONNECTED",                             // Status after test
    "latencyMs": 245,                                  // Response time in ms
    "testedAt": "2026-06-11T15:00:00Z",
    "endpoint": "https://onlinetools.ups.com/api/health", // Tested endpoint
    "details": {                                       // Response details
      "httpStatus": 200,
      "message": "API is reachable",
      "accountValid": true                             // Credentials valid?
    }
  }
}
```

**Response — Failure:**
```json
{
  "success": false,
  "error": {
    "code": "CARRIER_CONNECTION_FAILED",
    "message": "Failed to connect to UPS API",
    "details": {
      "httpStatus": 401,
      "reason": "Invalid API key"                      // Invalid API key
    }
  }
}
```

---

## 20. Update Credentials

### `PUT /api/v1/cargo/carriers/{code}/credentials`

**When?** The API key has expired, been compromised, or the administrator is rotating keys.

**What happens:**
1. New keys are encrypted and stored
2. The update date is recorded
3. Status goes back to "PENDING_TEST" (old keys are no longer valid)
4. It is recommended to test the connection after updating

**Request:**
```json
{
  "authType": "API_KEY",
  "apiKey": "new_ups_api_key_67890",                   // New API key
  "apiSecret": "new_ups_secret_12345",                 // New secret
  "webhookSecret": "whsec_new_abc456"                  // New webhook secret
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "code": "UPS",
    "credentialsUpdatedAt": "2026-06-11T16:00:00Z",
    "message": "Credentials updated. Re-test connection."  // Recommends a test
  }
}
```

---

## 21. Add a Service

### `POST /api/v1/cargo/carriers/{code}/services`

**When?** The carrier has launched a new service (e.g., "UPS Standard" in addition to "UPS Express Saver").

**Request:**
```json
{
  "code": "UPS_STANDARD",                              // New service code
  "name": "UPS Standard",
  "description": "Economy international shipping",
  "maxWeight": 30, "maxWeightUnit": "KG",
  "zones": ["FR", "DE", "BE", "NL"],
  "transitDays": 5,
  "features": ["SIGNATURE"],
  "active": true
}
```

---

## 22. Validate Address

### `POST /api/v1/cargo/addresses/validate`

**When?** Before creating a shipment, the user can verify that the recipient's address is correct.

**Pipeline:** → `DhlAdapter.validateAddress()` → DHL API

**What happens:**
1. Calls the carrier's Adapter → carrier API to validate the address
2. The carrier can normalize the address (fix case, complete zip code)
3. It can also suggest alternative addresses if the address is ambiguous

**Why go through the carrier?**
- DHL validates German addresses better
- Yurtiçi validates Turkish addresses better (İstanbul, İzmir...)
- The carrier has the latest postal coding data

**Request:**
```json
{
  "country": "TR",                                     // ISO country code
  "zipCode": "34000",                                  // Zip code
  "city": "Istanbul",                                  // City
  "address": "İstiklal Cad. No:15",                    // Address
  "carrierCode": "YURTICI"                             // Carrier for validation
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "valid": true,                                      // Address valid?
    "normalizedAddress": {                               // Address normalized by carrier
      "country": "TR",
      "zipCode": "34000",
      "city": "İSTANBUL",
      "address": "İSTİKLAL CAD. NO:15"
    },
    "suggestions": [],                                  // Suggestions if address invalid
    "carrierValidation": {
      "code": "VALID",
      "message": "Address is valid"
    }
  }
}
```

---

## 23. Full Pipeline Schema with Mapping

```
                                 OUR SYSTEM
                            ┌─────────────────────────────────────┐
                            │                                     │
                            │  6 UNIFIED INTERNAL STATUSES        │
                            │  ─────────────────────────          │
                            │  PENDING                            │
                            │  PICKED_UP                          │
                            │  IN_PROGRESS                        │
                            │  DELIVERED                          │
                            │  RETURNED                           │
                            │  CANCELLED                          │
                            │                                     │
                            └─────────────────────────────────────┘
                                      │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
           ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
           │   UPS          │ │   DHL          │ │   Yurtiçi      │
           │   Adapter      │ │   Adapter      │ │   Adapter      │
           └───────┬────────┘ └───────┬────────┘ └───────┬────────┘
                   │                  │                  │
          ┌────────▼────────┐ ┌───────▼────────┐ ┌───────▼────────┐
          │  UpsAdapter     │ │  DhlAdapter    │ │  YurticiAdapter│
          │  .parseWebhook()│ │  .parseWebhook()│ │  .parseWebhook │
          │                 │ │                 │ │  ()            │
          │  Normalizes     │ │  Normalizes     │ │  Normalizes    │
          │  UPS JSON:      │ │  DHL JSON:      │ │  Yurtiçi JSON: │
          │                 │ │                 │ │                │
          │  shipment_id →  │ │  trackingNumber │ │  takipNo →     │
          │  tracking_no    │ │  → tracking_no  │ │  tracking_no   │
          │  state →        │ │  status →       │ │  durum →       │
          │  carrier_raw_   │ │  carrier_raw_   │ │  carrier_raw_  │
          │  status         │ │  status         │ │  status        │
          │  customer →     │ │  signedBy →     │ │  alici →       │
          │  customer_name  │ │  customer_name  │ │  customer_name │
          └────────┬────────┘ └───────┬────────┘ └───────┬────────┘
                   │                  │                  │
                   ▼                  ▼                  ▼
          ┌─────────────────────────────────────────────────────┐
          │                 STATUS MAPPER ENGINE                │
          │                                                     │
          │   LEVEL 1 : Exact match                             │
          │   ──────────────────────                            │
          │   UPS: "Completed"       → DELIVERED                │
          │   DHL: "DELIVERED"       → DELIVERED                │
          │   UPS: "OnTheWay"        → IN_PROGRESS              │
          │   DHL: "IN_TRANSIT"      → IN_PROGRESS              │
          │   Yurtiçi: "Yolda"       → IN_PROGRESS              │
          │   UPS: "Cancelled"       → CANCELLED                │
          │   Yurtiçi: "İptal Edildi"→ CANCELLED                │
          │                                                     │
          │   LEVEL 2 : Regex (variations)                      │
          │   ──────────────────────                            │
          │   /out for delivery/i     → IN_PROGRESS             │
          │   /delivery attempted/i   → IN_PROGRESS             │
          │   /return to sender/i     → RETURNED                │
          │                                                     │
          │   LEVEL 3 : Fuzzy (similarity > 0.8)                │
          │   ──────────────────────                            │
          │   "Customs clearence" (typo) → CUSTOMS_CLEARED      │
          │   "Shipped" (ambiguous)     → IN_PROGRESS           │
          │                                                     │
          │   FALLBACK :                                        │
          │   No match → IN_PROGRESS (safe default)             │
          └────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
          ┌─────────────────────────────────────────────────────┐
          │                   CORE SYSTEM                       │
          │                                                     │
          │   {                                                 │
          │     "tracking_no": "12345",                         │
          │     "internalStatus": "DELIVERED",   ← Mapped!     │
          │     "carrierRawStatus": "Completed", ← Preserved    │
          │     "customer_name": "Ahmed"                        │
          │   }                                                 │
          │                                                     │
          │   ┌─────────────────────────────────────────────┐   │
          │   │  Database                                  │   │
          │   │  ─────────────────────                     │   │
          │   │  shipments:                                 │   │
          │   │    internalStatus = "DELIVERED"             │   │
          │   │    carrierRawStatus = "Completed"           │   │
          │   │                                             │   │
          │   │  tracking_events:                           │   │
          │   │    internalCode = "DELIVERED"               │   │
          │   │    carrierRawStatus = "Completed"           │   │
          │   └─────────────────────────────────────────────┘   │
          └─────────────────────────────────────────────────────┘

    ───────────────────────────────────────────────────────────────────

    Complete example: UPS sends a webhook "Completed"

    STEP 1 : UPS sends
    ───────────────────
    { "shipment_id": "1Z999...", "state": "Completed", "customer": "Ahmed" }

    STEP 2 : UpsAdapter.parseWebhook()
    ───────────────────────────────────
    { "tracking_no": "1Z999...", "carrier_raw_status": "Completed", "customer_name": "Ahmed" }
          ↑ JSON normalization: UPS fields are translated into standard fields

    STEP 3 : StatusMapper.map("UPS", "Completed")
    ──────────────────────────────────────────────
    Searching the UPS table:
      "Completed" ? Exact table → yes! → InternalStatus.DELIVERED
          ↑ Status translation: the word "Completed" becomes "DELIVERED"

    STEP 4 : Core System
    ─────────────────────
    trackingEventRepo.create({
      shipmentId: "1Z999...",
      internalStatus: "DELIVERED",            ← Mapping result
      carrierRawStatus: "Completed",          ← Raw status preserved (debug)
      customerName: "Ahmed"
    })

    shipmentRepo.updateStatus("1Z999...", "DELIVERED")
    EventBus.publish(SHIPMENT_DELIVERED, { shipmentId: "1Z999..." })
    → Client notification: "Your package has been delivered!"

    ───────────────────────────────────────────────────────────────────

    If DHL were sending:

    Step 1 : DHL sends
    { "trackingNumber": "12345", "status": "DELIVERED", "signedBy": "Hans" }

    Step 2 : DhlAdapter.parseWebhook()
    { "tracking_no": "12345", "carrier_raw_status": "DELIVERED", "customer_name": "Hans" }

    Step 3 : StatusMapper.map("DHL", "DELIVERED") → "DELIVERED"

    Step 4 : Core System → same! The Core System never sees the difference
              between UPS, DHL, Yurtiçi, FedEx, MNG Kargo or Aramex.

    ───────────────────────────────────────────────────────────────────

    SUMMARY: 2 mapping levels, 2 files to create per carrier

    ┌─────────────────────────────────────────────────────────────────┐
    │ LEVEL 1: THE ADAPTER (1 class per carrier)                      │
    │ ───────────────────────────────────────────────                 │
    │ Role: Normalize JSON (fields, structure)                        │
    │ File: src/adapters/UpsAdapter.ts                               │
    │        src/adapters/DhlAdapter.ts                              │
    │        src/adapters/YurticiAdapter.ts                          │
    │                                                                 │
    │   UPS: "shipment_id" → "tracking_no"   DHL: "trackingNumber"   │
    │        "state"       → "carrierStatus"       "status"          │
    │        "customer"    → "customerName"        "signedBy"        │
    │                                                                 │
    │ LEVEL 2: THE STATUS MAPPER (1 table per carrier)               │
    │ ───────────────────────────────────────────────                 │
    │ Role: Translate status values                                   │
    │ File: src/mapper/statusMaps.ts                                  │
    │                                                                 │
    │   UPS: "Completed"   → DELIVERED   DHL: "DELIVERED" → DELIVERED│
    │        "OnTheWay"    → IN_PROGRESS      "IN_TRANSIT" → PROGRESS│
    │        "BackToSender"→ RETURNED         "RETURNED"   → RETURNED│
    │        "Collected"   → PICKED_UP        "PICKED_UP"  → PICKED_UP│
    │        "Cancelled"   → CANCELLED        "CANCELLED"  → CANCELLED│
    │                                                                 │
    │ +3 matching levels: exact → regex → fuzzy                      │
    └─────────────────────────────────────────────────────────────────┘
```

---

## 24. Endpoints Summary

| # | Method | Endpoint | Description | External API call? | Uses Mapper? | Updates Status? |
|---|---|---|---|---|---|---|
| 1 | POST | `/api/v1/cargo/shipments` | Create a shipment | ✅ → carrier | ❌ | ✅ SUBMITTED |
| 2 | GET | `/api/v1/cargo/shipments` | List shipments | ❌ | ❌ | ❌ |
| 3 | GET | `/api/v1/cargo/shipments/{id}` | Shipment detail | ❌ | ❌ | ❌ |
| 4 | PUT | `/api/v1/cargo/shipments/{id}` | Update a shipment | ❌ | ❌ | ❌ |
| 5 | DELETE | `/api/v1/cargo/shipments/{id}` | Delete a shipment | ❌ | ❌ | ❌ |
| 6 | POST | `/api/v1/cargo/shipments/{id}/cancel` | Cancel a shipment | ✅ → carrier | ❌ | ✅ CANCELLED |
| 7 | POST | `/api/v1/cargo/shipments/{id}/label` | Generate label | ✅ → carrier | ❌ | ❌ |
| 8 | GET | `/api/v1/cargo/shipments/{id}/tracking` | Detailed tracking | ✅ → carrier | ✅ **Mapper** | ❌ (read-only) |
| 9 | POST | `/api/v1/cargo/webhooks/{carrierCode}` | Inbound webhook | ❌ (carrier calls us) | ✅ **Mapper** | ✅ (updates) |
| 10 | POST | `/api/v1/cargo/rates` | Compare rates | ✅ → all carriers | ❌ | ❌ |
| 11 | POST | `/api/v1/cargo/pickups` | Schedule a pickup | ✅ → carrier | ❌ | ❌ |
| 12 | POST | `/api/v1/cargo/pickups/{id}/cancel` | Cancel a pickup | ✅ → carrier | ❌ | ✅ |
| 13 | POST | `/api/v1/cargo/carriers` | Add a carrier | ❌ | ❌ | ❌ |
| 14 | GET | `/api/v1/cargo/carriers` | List carriers | ❌ | ❌ | ❌ |
| 15 | GET | `/api/v1/cargo/carriers/{code}` | Carrier detail | ❌ | ❌ | ❌ |
| 16 | PUT | `/api/v1/cargo/carriers/{code}` | Update a carrier | ❌ | ❌ | ❌ |
| 17 | DELETE | `/api/v1/cargo/carriers/{code}` | Delete a carrier | ❌ | ❌ | ❌ |
| 18 | PATCH | `/api/v1/cargo/carriers/{code}/toggle` | Toggle a carrier | ❌ | ❌ | ❌ |
| 19 | POST | `/api/v1/cargo/carriers/{code}/test` | Test connection | ✅ → carrier | ❌ | ✅ (CONNECTED/ERROR) |
| 20 | PUT | `/api/v1/cargo/carriers/{code}/credentials` | Update credentials | ❌ | ❌ | ❌ |
| 21 | POST | `/api/v1/cargo/carriers/{code}/services` | Add a service | ❌ | ❌ | ❌ |
| 22 | POST | `/api/v1/cargo/addresses/validate` | Validate address | ✅ → carrier | ❌ | ❌ |

**Reminder:** The only 2 endpoints that use the StatusMapper are:

1. **`GET /shipments/{id}/tracking`** → to translate each tracking event
2. **`POST /webhooks/{carrierCode}`** → to translate the received carrier status

Everywhere else, the status is already in internal format (PENDING, PICKED_UP, IN_PROGRESS, DELIVERED, RETURNED, CANCELLED).

---

*Document generated on 2026-06-14 — 22 endpoints documented with request, response, comments, pipeline, and mapping schema.*
