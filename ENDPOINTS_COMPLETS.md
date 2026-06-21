# Cargo Service — Endpoints Complets (Request / Response)

> Architecture : Adapter → Mapper (3 niveaux) → Core System  
> Statuts internes : PENDING → PICKED_UP → IN_PROGRESS → DELIVERED | RETURNED | CANCELLED

---

## 1. Shipments

### `POST /api/v1/cargo/shipments` — Créer une expédition

**Request :**
```json
{
  "carrierCode": "DHL",
  "serviceCode": "DHL_EXPRESS_WORLDWIDE",
  "reference": "CMD-2026-001234",
  "sender": {
    "company": "TechCorp SAS", "contactName": "Jean Dupont",
    "email": "jean@techcorp.fr", "phone": "+33123456789",
    "country": "FR", "zipCode": "75001", "city": "Paris", "address": "12 Rue de Rivoli"
  },
  "recipient": {
    "company": "Berlin GmbH", "contactName": "Hans Schmidt",
    "email": "hans@berlin.de", "phone": "+4930123456",
    "country": "DE", "zipCode": "10115", "city": "Berlin", "address": "Friedrichstraße 100"
  },
  "packages": [{
    "reference": "COLIS-001", "description": "Composants électroniques",
    "weight": 2.5, "weightUnit": "KG", "length": 30, "width": 20, "height": 15, "dimUnit": "CM",
    "declaredValue": 500.00, "declaredCurrency": "EUR"
  }],
  "options": {
    "insurance": { "amount": 500.00, "currency": "EUR" },
    "signatureRequired": true,
    "saturdayDelivery": false
  }
}
```

**Pipeline :** Request → `DhlAdapter.createShipment()` → API DHL → **Mapper** → Response

**Response 201 :**
```json
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5",
    "status": "SUBMITTED",
    "internalStatus": "PENDING",
    "carrierCode": "DHL",
    "carrierName": "DHL Express",
    "carrierTrackingNumber": "1234567890",
    "carrierShipmentId": "DE-2026-98765",
    "labelUrl": "https://api.dhl.com/labels/1234567890.pdf",
    "trackingUrl": "https://www.dhl.com/track/1234567890",
    "reference": "CMD-2026-001234",
    "price": { "total": 45.30, "currency": "EUR" },
    "sender": { "company": "TechCorp SAS", "country": "FR", "zipCode": "75001" },
    "recipient": { "company": "Berlin GmbH", "country": "DE", "zipCode": "10115" },
    "packages": [{ "reference": "COLIS-001", "weight": 2.5, "trackingNumber": "1234567890-001" }],
    "createdAt": "2026-06-11T10:30:00Z",
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z"
  }
}
```

---

### `GET /api/v1/cargo/shipments` — Lister les expéditions

**Filtres :** `?status=IN_PROGRESS&carrier=UPS&page=1&limit=20`

**Response 200 :**
```json
{
  "success": true,
  "data": [
    {
      "id": "shp_a1b2c3d4e5",
      "internalStatus": "IN_PROGRESS",
      "carrierCode": "UPS",
      "carrierTrackingNumber": "1Z999AA10123456784",
      "reference": "CMD-2026-001235",
      "recipient": { "company": "ACME GmbH", "country": "DE" },
      "createdAt": "2026-06-11T10:30:00Z"
    }
  ],
  "pagination": { "page": 1, "limit": 20, "total": 42 }
}
```

---

### `GET /api/v1/cargo/shipments/{id}` — Détail d'une expédition

**Response 200 :**
```json
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5",
    "internalStatus": "IN_PROGRESS",
    "carrierStatus": "OnTheWay",
    "statusHistory": [
      { "status": "SUBMITTED",   "internalStatus": "PENDING",    "timestamp": "2026-06-11T10:30:00Z" },
      { "status": "PICKED_UP",   "internalStatus": "PICKED_UP",  "timestamp": "2026-06-11T14:00:00Z" },
      { "status": "OnTheWay",    "internalStatus": "IN_PROGRESS", "timestamp": "2026-06-12T08:15:00Z" }
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

### `PUT /api/v1/cargo/shipments/{id}` — Modifier une expédition

**Request :**
```json
{
  "reference": "CMD-2026-001235-UPDATED",
  "options": { "signatureRequired": false }
}
```

**Response 200 :**
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

### `DELETE /api/v1/cargo/shipments/{id}` — Supprimer une expédition

**Response 200 :**
```json
{ "success": true, "data": { "deleted": true } }
```

---

### `POST /api/v1/cargo/shipments/{id}/cancel` — Annuler une expédition

**Pipeline :** → `UpsAdapter.cancelShipment()` → API UPS → Core

**Response 200 :**
```json
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5",
    "internalStatus": "CANCELLED",
    "carrierStatus": "Cancelled",
    "cancelledAt": "2026-06-11T12:00:00Z"
  }
}
```

---

### `POST /api/v1/cargo/shipments/{id}/label` — Générer l'étiquette

**Pipeline :** → `DhlAdapter.getLabel()` → API DHL

**Request :**
```json
{ "format": "PDF" }
```

**Response 200 :**
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

## 2. Tracking

### `GET /api/v1/cargo/shipments/{id}/tracking` — Suivi détaillé

**Pipeline :** → `DhlAdapter.track()` → API DHL → **StatusMapper** → Core

**Response 200 :**
```json
{
  "success": true,
  "data": {
    "shipmentId": "shp_a1b2c3d4e5",
    "carrierCode": "DHL",
    "carrierTrackingNumber": "1234567890",
    "currentStatus": {
      "internalCode": "IN_PROGRESS",
      "carrierCode": "IN_TRANSIT",
      "label": "En transit",
      "location": "Francfort, Allemagne",
      "timestamp": "2026-06-12T08:15:00Z"
    },
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z",
    "events": [
      {
        "eventId": "evt_001",
        "internalCode": "PENDING",
        "carrierCode": "LABEL_CREATED",
        "carrierRawStatus": "Shipment information received",
        "label": "Étiquette créée",
        "location": "Paris, France",
        "timestamp": "2026-06-11T10:30:00Z"
      },
      {
        "eventId": "evt_002",
        "internalCode": "PICKED_UP",
        "carrierCode": "PICKED_UP",
        "carrierRawStatus": "Pickup scanned",
        "label": "Colis récupéré",
        "location": "Paris, France",
        "timestamp": "2026-06-11T14:00:00Z"
      },
      {
        "eventId": "evt_003",
        "internalCode": "IN_PROGRESS",
        "carrierCode": "IN_TRANSIT",
        "carrierRawStatus": "Departed from transit hub",
        "label": "En transit",
        "location": "Francfort, Allemagne",
        "timestamp": "2026-06-12T08:15:00Z"
      }
    ],
    "milestones": {
      "pending": "2026-06-11T10:30:00Z",
      "pickedUp": "2026-06-11T14:00:00Z",
      "inProgress": "2026-06-12T08:15:00Z",
      "delivered": null
    }
  }
}
```

---

### `POST /api/v1/cargo/webhooks/{carrierCode}` — Webhook entrant

**Pipeline :** Webhook → validation HMAC → `UpsAdapter.parseWebhook()` → **StatusMapper.map("UPS", rawStatus)** → Core

**Request (UPS envoie ceci) :**
```json
{
  "shipment_id": "1Z999AA10123456784",
  "state": "Completed",
  "customer": "Ahmed",
  "timestamp": "2026-06-13T16:30:00Z",
  "signed_by": "Ahmed"
}
```

**Response (toujours 200) :**
```json
{ "success": true, "message": "Webhook processed successfully" }
```

**Ce qui se passe côté serveur :**
```
1. UPS envoie : { "shipment_id": "1Z999...", "state": "Completed", "customer": "Ahmed" }
2. UpsAdapter.parse() → { tracking_no: "1Z999...", carrier_raw_status: "Completed", customer_name: "Ahmed" }
3. StatusMapper.map("UPS", "Completed") → InternalStatus.DELIVERED
4. Core : crée TrackingEvent + update Shipment status = "DELIVERED"
```

---

## 3. Rates

### `POST /api/v1/cargo/rates` — Comparer les prix

**Pipeline :** → `DhlAdapter.getRates()` + `UpsAdapter.getRates()` + `FedExAdapter.getRates()` en parallèle → Agrégation

**Request :**
```json
{
  "sender": { "country": "FR", "zipCode": "75001", "city": "Paris" },
  "recipient": { "country": "DE", "zipCode": "10115", "city": "Berlin" },
  "packages": [{ "weight": 2.5, "weightUnit": "KG", "length": 30, "width": 20, "height": 15, "dimUnit": "CM" }],
  "options": { "carrierCodes": ["DHL", "UPS", "FEDEX"], "serviceType": "EXPRESS" }
}
```

**Response 200 :**
```json
{
  "success": true,
  "data": [
    {
      "carrierCode": "DHL", "carrierName": "DHL Express",
      "serviceCode": "DHL_EXPRESS_WORLDWIDE",
      "totalPrice": 45.30, "currency": "EUR",
      "estimatedTransitDays": 2,
      "breakdown": [
        { "type": "BASE", "label": "Transport", "amount": 38.00 },
        { "type": "FUEL", "label": "Surcharge carburant", "amount": 5.30 },
        { "type": "INSURANCE", "label": "Assurance", "amount": 2.00 }
      ]
    },
    {
      "carrierCode": "UPS", "carrierName": "UPS",
      "serviceCode": "UPS_EXPRESS_SAVER",
      "totalPrice": 42.00, "currency": "EUR",
      "estimatedTransitDays": 3,
      "breakdown": [
        { "type": "BASE", "amount": 36.00 },
        { "type": "FUEL", "amount": 4.50 },
        { "type": "INSURANCE", "amount": 1.50 }
      ]
    },
    {
      "carrierCode": "FEDEX", "carrierName": "FedEx",
      "serviceCode": "FEDEX_PRIORITY",
      "totalPrice": 48.50, "currency": "EUR",
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

---

## 4. Pickups

### `POST /api/v1/cargo/pickups` — Planifier un enlèvement

**Pipeline :** → `DhlAdapter.schedulePickup()` → API DHL

**Request :**
```json
{
  "carrierCode": "DHL",
  "shipmentIds": ["shp_a1b2c3d4e5"],
  "pickupDate": "2026-06-12",
  "readyTime": "09:00",
  "closeTime": "17:00",
  "location": {
    "company": "TechCorp SAS", "contactName": "Jean Dupont",
    "phone": "+33123456789",
    "country": "FR", "zipCode": "75001", "city": "Paris", "address": "12 Rue de Rivoli"
  },
  "totalPackages": 1,
  "totalWeight": 2.5,
  "weightUnit": "KG",
  "specialInstructions": "Sonner à l'accueil"
}
```

**Response 201 :**
```json
{
  "success": true,
  "data": {
    "id": "pck_001a2b3c",
    "carrierCode": "DHL",
    "carrierPickupId": "DHL-PICKUP-98765",
    "status": "CONFIRMED",
    "pickupDate": "2026-06-12",
    "confirmationNumber": "CONF-ABC-123"
  }
}
```

### `POST /api/v1/cargo/pickups/{id}/cancel` — Annuler un enlèvement

**Pipeline :** → `DhlAdapter.cancelPickup()` → API DHL

**Response 200 :**
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

## 5. Carriers (CRUD)

### `POST /api/v1/cargo/carriers` — Ajouter un transporteur

**Request :**
```json
{
  "code": "UPS",
  "name": "UPS",
  "adapterName": "UpsAdapter",
  "active": true,
  "website": "https://www.ups.com",
  "contact": {
    "name": "UPS Support", "email": "support@ups.com", "phone": "+18007425877"
  },
  "services": [{
    "code": "UPS_EXPRESS_SAVER", "name": "UPS Express Saver",
    "zones": ["WORLDWIDE"], "transitDays": 2, "active": true
  }],
  "capabilities": {
    "features": ["RATES", "TRACKING", "SIGNATURE", "PICKUP"]
  },
  "credentials": {
    "authType": "API_KEY",
    "apiKey": "ups_api_key_123",
    "apiSecret": "ups_secret_456",
    "accountNumber": "UPS-ACC-001",
    "endpoint": "https://onlinetools.ups.com/api"
  },
  "settings": {
    "timeoutMs": 10000,
    "retryMaxAttempts": 3,
    "rateLimitPerMinute": 50
  }
}
```

**Response 201 :**
```json
{
  "success": true,
  "data": {
    "code": "UPS",
    "name": "UPS",
    "adapterName": "UpsAdapter",
    "active": true,
    "status": "PENDING_TEST",
    "message": "Carrier added. Run a connection test before using."
  }
}
```

---

### `GET /api/v1/cargo/carriers` — Lister les transporteurs

**Filtres :** `?active=true&feature=TRACKING&page=1&limit=20`

**Response 200 :**
```json
{
  "success": true,
  "data": [
    {
      "code": "DHL", "name": "DHL Express", "adapterName": "DhlAdapter",
      "active": true, "status": "CONNECTED",
      "services": [
        { "code": "DHL_EXPRESS_WORLDWIDE", "name": "Express Worldwide", "active": true }
      ]
    },
    {
      "code": "UPS", "name": "UPS", "adapterName": "UpsAdapter",
      "active": true, "status": "PENDING_TEST",
      "services": [
        { "code": "UPS_EXPRESS_SAVER", "name": "UPS Express Saver", "active": true }
      ]
    }
  ],
  "pagination": { "page": 1, "limit": 20, "total": 3 }
}
```

---

### `GET /api/v1/cargo/carriers/{code}` — Détail d'un transporteur

**Response 200 :**
```json
{
  "success": true,
  "data": {
    "code": "UPS",
    "name": "UPS",
    "adapterName": "UpsAdapter",
    "active": true,
    "status": "CONNECTED",
    "services": [{
      "code": "UPS_EXPRESS_SAVER", "name": "UPS Express Saver",
      "description": "International express shipping",
      "maxWeight": 70, "zones": ["WORLDWIDE"], "transitDays": 2,
      "features": ["SIGNATURE", "INSURANCE"], "active": true
    }],
    "capabilities": {
      "features": ["RATES", "TRACKING", "SIGNATURE", "INSURANCE", "PICKUP"]
    },
    "settings": {
      "timeoutMs": 10000, "retryMaxAttempts": 3, "rateLimitPerMinute": 100
    }
  }
}
```

---

### `PUT /api/v1/cargo/carriers/{code}` — Modifier un transporteur

**Request :**
```json
{
  "settings": { "timeoutMs": 15000, "retryMaxAttempts": 5 },
  "active": true
}
```

---

### `DELETE /api/v1/cargo/carriers/{code}` — Supprimer un transporteur

**Response 200 :**
```json
{ "success": true, "data": { "deleted": true } }
```

---

### `PATCH /api/v1/cargo/carriers/{code}/toggle` — Activer/désactiver

**Request :**
```json
{ "active": false, "reason": "API outage - maintenance" }
```

**Response 200 :**
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

### `POST /api/v1/cargo/carriers/{code}/test` — Tester la connexion

**Pipeline :** → `UpsAdapter.testConnection()` → API UPS health

**Response — Succès :**
```json
{
  "success": true,
  "data": {
    "status": "CONNECTED",
    "latencyMs": 245,
    "endpoint": "https://onlinetools.ups.com/api/health",
    "details": { "httpStatus": 200, "message": "API is reachable", "accountValid": true }
  }
}
```

**Response — Échec :**
```json
{
  "success": false,
  "error": {
    "code": "CARRIER_CONNECTION_FAILED",
    "message": "Failed to connect to UPS API",
    "details": { "httpStatus": 401, "reason": "Invalid API key" }
  }
}
```

---

### `PUT /api/v1/cargo/carriers/{code}/credentials` — Màj credentials

**Request :**
```json
{
  "authType": "API_KEY",
  "apiKey": "new_ups_api_key_67890",
  "apiSecret": "new_ups_secret_12345",
  "webhookSecret": "whsec_new_abc456"
}
```

**Response 200 :**
```json
{
  "success": true,
  "data": {
    "code": "UPS",
    "credentialsUpdatedAt": "2026-06-11T16:00:00Z",
    "message": "Credentials updated. Re-test connection."
  }
}
```

---

### `POST /api/v1/cargo/carriers/{code}/services` — Ajouter un service

**Request :**
```json
{
  "code": "UPS_STANDARD",
  "name": "UPS Standard",
  "description": "Economy international shipping",
  "maxWeight": 30,
  "zones": ["FR", "DE", "BE", "NL"],
  "transitDays": 5,
  "features": ["SIGNATURE"],
  "active": true
}
```

---

## 6. Address

### `POST /api/v1/cargo/addresses/validate` — Valider une adresse

**Pipeline :** → `DhlAdapter.validateAddress()` → API DHL

**Request :**
```json
{
  "country": "TR", "zipCode": "34000", "city": "Istanbul",
  "address": "İstiklal Cad. No:15", "carrierCode": "YURTICI"
}
```

**Response 200 :**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "normalizedAddress": {
      "country": "TR", "zipCode": "34000",
      "city": "İSTANBUL", "address": "İSTİKLAL CAD. NO:15"
    },
    "suggestions": [],
    "carrierValidation": { "code": "VALID", "message": "Address is valid" }
  }
}
```

---

## Flux complet avec le pipeline Adapter → Mapper

```
                          ┌──────────────────────────────────────────────┐
                          │  POST /api/v1/cargo/shipments               │
                          │  { carrierCode: "UPS", ... }                 │
                          └──────────────────┬───────────────────────────┘
                                             │
                          ┌──────────────────▼───────────────────────────┐
                          │  1. UpsAdapter.createShipment(ourFormat)     │
                          │     → transforme en format UPS              │
                          │     → appel API UPS                         │
                          └──────────────────┬───────────────────────────┘
                                             │
                          ┌──────────────────▼───────────────────────────┐
                          │  2. Webhook UPS → "Completed"                │
                          │     → UpsAdapter.parse(rawJSON)              │
                          │     → { carrier_raw_status: "Completed" }    │
                          └──────────────────┬───────────────────────────┘
                                             │
                          ┌──────────────────▼───────────────────────────┐
                          │  3. StatusMapper.map("UPS", "Completed")     │
                          │     → Niveau 1 : exact match?                │
                          │       "Completed" → DELIVERED ✓              │
                          └──────────────────┬───────────────────────────┘
                                             │
                          ┌──────────────────▼───────────────────────────┐
                          │  4. Core System                             │
                          │     → TrackingEvent { internalStatus:        │
                          │       "DELIVERED" }                          │
                          │     → Shipment.status = "DELIVERED"          │
                          │     → EventBus publish                      │
                          └──────────────────────────────────────────────┘
```

**19 endpoints — 0 dépendance directe aux transporteurs. Seuls les Adapters et les Status Maps changent.**
