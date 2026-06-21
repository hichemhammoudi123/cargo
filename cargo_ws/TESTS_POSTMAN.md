# Cargo Delivery Service — Postman Test Scenarios

> Base URL: `http://localhost:8000/api/v1/cargo`

---

## Table of Contents

1. [Carriers — CRUD](#1-carriers--crud)
2. [Shipments — CRUD](#2-shipments--crud)
3. [Tracking](#3-tracking)
4. [Rates](#4-rates)
5. [Pickups](#5-pickups)
6. [Address Validation](#6-address-validation)
7. [Webhooks](#7-webhooks)
8. [Complete Scenario: End-to-End Shipment Lifecycle](#8-complete-scenario-end-to-end-shipment-lifecycle)
9. [Multi-Language Testing](#9-multi-language-testing)
10. [Error Scenarios](#10-error-scenarios)

---

## 1. Carriers — CRUD

### 1.1 Add a New Carrier (DHL)
**POST** `{{base}}/carriers`

```json
{
  "code": "DHL",
  "name": "DHL Express",
  "adapterName": "DhlAdapter",
  "active": true,
  "website": "https://www.dhl.com",
  "contact": {
    "name": "DHL Support",
    "email": "support@dhl.com",
    "phone": "+18002255345"
  },
  "services": [
    {
      "code": "DHL_EXPRESS_WORLDWIDE",
      "name": "Express Worldwide",
      "description": "International express shipping",
      "maxWeight": 70,
      "maxWeightUnit": "KG",
      "zones": ["WORLDWIDE"],
      "transitDays": 2,
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
    "apiKey": "dhl_api_key_test",
    "apiSecret": "dhl_secret_test",
    "accountNumber": "DHL-ACC-001",
    "endpoint": "https://api.dhl.com",
    "webhookSecret": "whsec_dhl_test"
  },
  "settings": {
    "timeoutMs": 10000,
    "retryMaxAttempts": 3,
    "retryDelayMs": 1000,
    "rateLimitPerMinute": 50
  }
}
```
**Expected:** `201 Created` with status `PENDING_TEST`

### 1.2 Add UPS (same structure, code="UPS")
**POST** `{{base}}/carriers`

### 1.3 Add FedEx (same structure, code="FEDEX")
**POST** `{{base}}/carriers`

### 1.4 Add Yurtiçi Kargo
**POST** `{{base}}/carriers`

```json
{
  "code": "YURTICI",
  "name": "Yurtiçi Kargo",
  "adapterName": "YurticiAdapter",
  "active": true,
  "services": [
    {
      "code": "YURTICI_STANDARD",
      "name": "Standart Kargo",
      "zones": ["TR"],
      "transitDays": 3,
      "features": ["SIGNATURE"],
      "active": true
    }
  ],
  "capabilities": {
    "features": ["RATES", "TRACKING", "SIGNATURE"]
  },
  "credentials": {
    "apiKey": "yurtici_api_test",
    "apiSecret": "yurtici_secret_test",
    "endpoint": "https://api.yurticikargo.com"
  }
}
```

### 1.5 List All Carriers
**GET** `{{base}}/carriers`

**Expected:** Array of all carriers with status, services summary

### 1.6 List Active Carriers
**GET** `{{base}}/carriers?active=true`

### 1.7 Get Carrier Detail
**GET** `{{base}}/carriers/DHL`

**Expected:** Full carrier info (services, capabilities, settings — no credentials)

### 1.8 Update Carrier Settings
**PUT** `{{base}}/carriers/DHL`

```json
{
  "active": true,
  "settings": {
    "timeoutMs": 15000,
    "retryMaxAttempts": 5
  }
}
```

### 1.9 Test Carrier Connection
**POST** `{{base}}/carriers/DHL/test`

**Expected:**
```json
{
  "success": true,
  "data": {
    "status": "CONNECTED",
    "latencyMs": 120,
    "endpoint": "https://api.dhl.com/health",
    "details": {
      "httpStatus": 200,
      "message": "API is reachable",
      "accountValid": true
    }
  }
}
```

### 1.10 Toggle Carrier (Disable)
**PATCH** `{{base}}/carriers/DHL/toggle`

```json
{
  "active": false,
  "reason": "API maintenance"
}
```

### 1.11 Update Credentials
**PUT** `{{base}}/carriers/DHL/credentials`

```json
{
  "authType": "API_KEY",
  "apiKey": "new_dhl_key_67890",
  "apiSecret": "new_dhl_secret_12345",
  "webhookSecret": "whsec_new_dhl"
}
```

**Expected:** Status goes back to `PENDING_TEST`

### 1.12 Add a Service
**POST** `{{base}}/carriers/DHL/services`

```json
{
  "code": "DHL_ECONOMY",
  "name": "DHL Economy Select",
  "maxWeight": 30,
  "zones": ["EU"],
  "transitDays": 5,
  "features": ["SIGNATURE"],
  "active": true
}
```

### 1.13 Delete a Carrier
**DELETE** `{{base}}/carriers/DHL`

---

## 2. Shipments — CRUD

### 2.1 Create a Shipment (DHL — France to Germany)
**POST** `{{base}}/shipments`

```json
{
  "carrierCode": "DHL",
  "serviceCode": "DHL_EXPRESS_WORLDWIDE",
  "reference": "CMD-2026-001234",
  "sender": {
    "company": "TechCorp SAS",
    "contactName": "Jean Dupont",
    "email": "jean@techcorp.fr",
    "phone": "+33123456789",
    "country": "FR",
    "zipCode": "75001",
    "city": "Paris",
    "address": "12 Rue de Rivoli"
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
      "reference": "COLIS-001",
      "description": "Electronic components",
      "weight": 2.5,
      "weightUnit": "KG",
      "length": 30,
      "width": 20,
      "height": 15,
      "dimUnit": "CM",
      "declaredValue": 500.00,
      "declaredCurrency": "EUR"
    }
  ],
  "options": {
    "insurance": {
      "amount": 500.00,
      "currency": "EUR"
    },
    "signatureRequired": true,
    "saturdayDelivery": false
  }
}
```
**Expected:** `201 Created`, save the `id` for next tests

### 2.2 Create a Shipment with UPS
**POST** `{{base}}/shipments`

```json
{
  "carrierCode": "UPS",
  "serviceCode": "UPS_EXPRESS_SAVER",
  "reference": "CMD-2026-001235",
  "sender": {
    "company": "TechCorp SAS",
    "contactName": "Jean Dupont",
    "country": "FR",
    "zipCode": "75001",
    "city": "Paris",
    "address": "12 Rue de Rivoli"
  },
  "recipient": {
    "company": "ACME GmbH",
    "contactName": "Klaus Mueller",
    "country": "DE",
    "zipCode": "10115",
    "city": "Berlin",
    "address": "Unter den Linden 50"
  },
  "packages": [
    {
      "reference": "BOX-001",
      "weight": 1.5,
      "weightUnit": "KG"
    }
  ]
}
```

### 2.3 Create a Shipment with Yurtiçi (Turkish domestic)
**POST** `{{base}}/shipments`

```json
{
  "carrierCode": "YURTICI",
  "serviceCode": "YURTICI_STANDARD",
  "reference": "SIP-2026-0500",
  "sender": {
    "company": "Tekno AŞ",
    "contactName": "Ali Yılmaz",
    "country": "TR",
    "zipCode": "34000",
    "city": "İstanbul",
    "address": "İstiklal Cad. No:15"
  },
  "recipient": {
    "company": "Ankara Ltd",
    "contactName": "Ayşe Demir",
    "country": "TR",
    "zipCode": "06000",
    "city": "Ankara",
    "address": "Atatürk Bulvarı No:20"
  },
  "packages": [
    {
      "reference": "KUTU-001",
      "weight": 3.0,
      "weightUnit": "KG"
    }
  ]
}
```

### 2.4 List All Shipments
**GET** `{{base}}/shipments`

### 2.5 Filter by Status
**GET** `{{base}}/shipments?status=IN_PROGRESS`

### 2.6 Filter by Carrier
**GET** `{{base}}/shipments?carrier=UPS`

### 2.7 Filter by Date Range
**GET** `{{base}}/shipments?from=2026-06-01&to=2026-06-30`

### 2.8 Search by Reference
**GET** `{{base}}/shipments?q=CMD-2026`

### 2.9 Get Shipment Detail
**GET** `{{base}}/shipments/shp_XXXXX`
(Replace with the ID from step 2.1)

### 2.10 Update Shipment
**PUT** `{{base}}/shipments/shp_XXXXX`

```json
{
  "reference": "CMD-2026-001234-UPDATED",
  "options": {
    "signatureRequired": false
  }
}
```

### 2.11 Generate Label
**POST** `{{base}}/shipments/shp_XXXXX/label`

```json
{
  "format": "PDF"
}
```

### 2.12 Cancel Shipment
**POST** `{{base}}/shipments/shp_XXXXX/cancel`

**Expected:** Status changes to CANCELLED

### 2.13 Delete Shipment
**DELETE** `{{base}}/shipments/shp_XXXXX`

---

## 3. Tracking

### 3.1 Get Tracking for a Shipment
**GET** `{{base}}/shipments/shp_XXXXX/tracking`

**Expected:** Full tracking timeline with events containing:
- `internalCode` (mapped: PENDING, PICKED_UP, IN_PROGRESS)
- `carrierCode` (carrier-native code)
- `carrierRawStatus` (raw carrier status preserved)
- `label`, `location`, `timestamp`

### 3.2 Verify Status Mapping
Check that the StatusMapper has correctly translated:
- DHL: `"Shipment information received"` → `PENDING`
- DHL: `"Pickup scanned"` → `PICKED_UP`
- DHL: `"Departed from transit hub"` → `IN_PROGRESS`
- UPS: `"OnTheWay"` → `IN_PROGRESS`
- Yurtiçi: `"Yolda"` → `IN_PROGRESS`

---

## 4. Rates

### 4.1 Compare All Carriers
**POST** `{{base}}/rates`

```json
{
  "sender": {
    "country": "FR",
    "zipCode": "75001",
    "city": "Paris"
  },
  "recipient": {
    "country": "DE",
    "zipCode": "10115",
    "city": "Berlin"
  },
  "packages": [
    {
      "weight": 2.5,
      "weightUnit": "KG",
      "length": 30,
      "width": 20,
      "height": 15,
      "dimUnit": "CM"
    }
  ],
  "options": {
    "carrierCodes": ["DHL", "UPS", "FEDEX"],
    "serviceType": "EXPRESS"
  }
}
```

**Expected:** Ordered by price ascending, with breakdown

### 4.2 Compare Turkish Carriers Only
**POST** `{{base}}/rates`

```json
{
  "sender": { "country": "TR", "zipCode": "34000", "city": "İstanbul" },
  "recipient": { "country": "TR", "zipCode": "06000", "city": "Ankara" },
  "packages": [{ "weight": 3.0, "weightUnit": "KG" }],
  "options": {
    "carrierCodes": ["YURTICI", "MNG"]
  }
}
```

---

## 5. Pickups

### 5.1 Schedule a Pickup
**POST** `{{base}}/pickups`

```json
{
  "carrierCode": "DHL",
  "shipmentIds": ["shp_XXXXX"],
  "pickupDate": "2026-06-20",
  "readyTime": "09:00",
  "closeTime": "17:00",
  "location": {
    "company": "TechCorp SAS",
    "contactName": "Jean Dupont",
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

**Expected:** `201 Created` with confirmation number

### 5.2 Cancel Pickup
**POST** `{{base}}/pickups/pck_XXXXX/cancel`

---

## 6. Address Validation

### 6.1 Validate French Address
**POST** `{{base}}/addresses/validate`

```json
{
  "country": "FR",
  "zipCode": "75001",
  "city": "Paris",
  "address": "12 Rue de Rivoli",
  "carrierCode": "DHL"
}
```

### 6.2 Validate Turkish Address
**POST** `{{base}}/addresses/validate`

```json
{
  "country": "TR",
  "zipCode": "34000",
  "city": "Istanbul",
  "address": "İstiklal Cad. No:15",
  "carrierCode": "YURTICI"
}
```

**Expected:** Address normalized to uppercase: `"İSTANBUL"`, `"İSTİKLAL CAD. NO:15"`

---

## 7. Webhooks

### 7.1 UPS Webhook — DELIVERED
**POST** `{{base}}/webhooks/UPS`

```json
{
  "shipment_id": "1Z999AA10123456784",
  "state": "Completed",
  "customer": "Ahmed",
  "signed_by": "Ahmed",
  "timestamp": "2026-06-13T16:30:00Z"
}
```

**Expected:** `200 OK`. Behind the scenes:
- Adapter normalizes: `shipment_id` → `tracking_no`, `state` → `carrier_raw_status`
- StatusMapper maps: `"Completed"` → `DELIVERED`
- Shipment status updated to `DELIVERED`

### 7.2 DHL Webhook — DELIVERED
**POST** `{{base}}/webhooks/DHL`

```json
{
  "trackingNumber": "1234567890",
  "status": "DELIVERED",
  "statusDescription": "Shipment delivered",
  "timestamp": "2026-06-13T16:30:00Z",
  "location": { "city": "Berlin", "country": "DE" },
  "signedBy": "Hans Schmidt"
}
```

**Expected:** Same result as UPS — StatusMapper normalizes to `DELIVERED`

### 7.3 Yurtiçi Webhook — DELIVERED (Turkish)
**POST** `{{base}}/webhooks/YURTICI`

```json
{
  "takipNo": "YT2026001122334",
  "durum": "Teslim Edildi",
  "alici": "Ahmet",
  "tarih": "2026-06-13T16:30:00Z"
}
```

**Expected:** `DELIVERED` — StatusMapper handles Turkish status text

### 7.4 UPS Webhook — In Transit
**POST** `{{base}}/webhooks/UPS`

```json
{
  "shipment_id": "1Z999AA10123456784",
  "state": "Out for delivery",
  "customer": "Ahmed",
  "timestamp": "2026-06-13T10:30:00Z"
}
```

**Expected:** `IN_PROGRESS` — matched via regex `/out for delivery/i`

### 7.5 DHL Webhook — Customs Issue (Regex)
**POST** `{{base}}/webhooks/DHL`

```json
{
  "trackingNumber": "1234567890",
  "status": "Return to sender requested",
  "timestamp": "2026-06-12T08:00:00Z"
}
```

**Expected:** `RETURNED` — matched via regex `/return to sender/i`

---

## 8. Complete Scenario: End-to-End Shipment Lifecycle

### Step 1: Add Carriers (if not already done)
**POST** `{{base}}/carriers` for DHL, UPS, YURTICI, FEDEX, MNG, ARAMEX

### Step 2: Compare Rates
**POST** `{{base}}/rates` with sender=Paris, recipient=Berlin

### Step 3: Create Shipment with chosen carrier
**POST** `{{base}}/shipments`

### Step 4: Verify Shipment Created
**GET** `{{base}}/shipments/shp_XXXXX`
→ Status should be `PENDING`

### Step 5: Get Label
**POST** `{{base}}/shipments/shp_XXXXX/label`

### Step 6: Simulate Webhook — Pickup
**POST** `{{base}}/webhooks/DHL`

```json
{
  "trackingNumber": "1234567890",
  "status": "Pickup scanned",
  "timestamp": "2026-06-11T14:00:00Z"
}
```
→ Status becomes `PICKED_UP`

### Step 7: Verify Tracking
**GET** `{{base}}/shipments/shp_XXXXX/tracking`
→ First event: PICKED_UP

### Step 8: Simulate Webhook — In Transit
**POST** `{{base}}/webhooks/DHL`

```json
{
  "trackingNumber": "1234567890",
  "status": "Departed from transit hub",
  "timestamp": "2026-06-12T08:15:00Z"
}
```
→ Status becomes `IN_PROGRESS`

### Step 9: Simulate Webhook — Delivered
**POST** `{{base}}/webhooks/DHL`

```json
{
  "trackingNumber": "1234567890",
  "status": "Delivered",
  "timestamp": "2026-06-13T16:30:00Z",
  "signedBy": "Hans Schmidt"
}
```
→ Status becomes `DELIVERED`

### Step 10: Verify Final Tracking
**GET** `{{base}}/shipments/shp_XXXXX/tracking`
→ Full timeline: PENDING → PICKED_UP → IN_PROGRESS → DELIVERED

---

## 9. Multi-Language Testing

### 9.1 Test with Accept-Language header
**GET** `{{base}}/shipments` — Set header `Accept-Language: fr`

**Expected:** French-translated field values (carrier names, descriptions)

### 9.2 Test Turkish
**GET** `{{base}}/shipments` — Set header `Accept-Language: tr`

### 9.3 Test Arabic
**GET** `{{base}}/shipments` — Set header `Accept-Language: ar`

### 9.4 Create Yurtiçi Shipment (Turkish fields)
**POST** `{{base}}/shipments` with Turkish sender/recipient data
→ Verify all labels and statuses appear in Turkish

---

## 10. Error Scenarios

### 10.1 Invalid Carrier Code
**POST** `{{base}}/shipments`

```json
{
  "carrierCode": "INVALID_CARRIER",
  ...
}
```
**Expected:** `400 Bad Request` — carrier not found

### 10.2 Cancel Already Delivered Shipment
**POST** `{{base}}/shipments/shp_XXXXX/cancel`
(where shipment is already DELIVERED)
**Expected:** `409 Conflict` — "Cannot cancel a delivered shipment"

### 10.3 Missing Required Fields
**POST** `{{base}}/shipments`

```json
{
  "carrierCode": "DHL"
}
```
**Expected:** `400 Bad Request` — validation error details

### 10.4 Invalid Webhook Signature
**POST** `{{base}}/webhooks/UPS` — with invalid HMAC signature header
**Expected:** `200 OK` (still responds, but logs warning)

### 10.5 Delete Non-Existent Shipment
**DELETE** `{{base}}/shipments/nonexistent`
**Expected:** `404 Not Found`

---

## 11. Postman Collection Setup

### Environment Variables

| Variable | Value |
|---|---|
| `base` | `http://localhost:8000/api/v1/cargo` |
| `shipmentId` | (set from test response) |
| `trackingNumberDHL` | `1234567890` |
| `trackingNumberUPS` | `1Z999AA10123456784` |
| `trackingNumberYT` | `YT2026001122334` |

### Headers
- `Content-Type: application/json`
- `Accept-Language: en` (change to `fr`, `tr`, `ar` for multi-lang)

### Test Script (Postman Pre-request/Test)

```javascript
// Save shipment ID from create response
pm.test("Save shipment ID", function () {
    var jsonData = pm.response.json();
    if (jsonData.data && jsonData.data.id) {
        pm.environment.set("shipmentId", jsonData.data.id);
    }
});
```

---

## 12. Quick Test Sequence (All Endpoints)

Run these in order for a complete smoke test:

```
 1. POST /carriers  (DHL)
 2. POST /carriers  (UPS)
 3. POST /carriers  (YURTICI)
 4. GET  /carriers
 5. GET  /carriers/DHL
 6. POST /carriers/DHL/test
 7. POST /shipments  (DHL)            → save id
 8. GET  /shipments/{id}
 9. POST /shipments/{id}/label
10. GET  /shipments/{id}/tracking
11. POST /webhooks/DHL                → PICKED_UP
12. GET  /shipments/{id}/tracking
13. POST /webhooks/DHL                → IN_TRANSIT
14. GET  /shipments/{id}/tracking
15. POST /webhooks/DHL                → DELIVERED
16. GET  /shipments/{id}/tracking     → verify DELIVERED
17. POST /rates
18. POST /pickups
19. POST /addresses/validate
20. POST /shipments/{id}/cancel       → test cancel
21. PUT  /carriers/DHL/credentials
22. PATCH /carriers/DHL/toggle        → disable
```

---

*Document generated on 2026-06-14 — 22 API endpoints with Postman test scenarios.*
