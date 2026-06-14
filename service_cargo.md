# Service Cargo — Documentation des Endpoints

## 1. Tarification — `POST /api/v1/cargo/rates`

**Rôle :** Demander les prix auprès de tous les transporteurs actifs.

**Request :**
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

**Response 200 :**
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
        { "type": "FUEL", "label": "Surcharge carburant", "amount": 5.30 },
        { "type": "INSURANCE", "label": "Assurance", "amount": 2.00 }
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
        { "type": "FUEL", "label": "Surcharge carburant", "amount": 5.50 },
        { "type": "INSURANCE", "label": "Assurance", "amount": 2.00 }
      ]
    }
  ]
}
```

---

## 2. Créer une expédition — `POST /api/v1/cargo/shipments`

**Rôle :** Créer une expédition réelle chez un transporteur.

**Request :**
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
    "address": "12 Rue de Rivoli",
    "address2": "Bureau 301"
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
      "description": "Composants électroniques",
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

**Response 201 :**
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
    "reference": "CMD-2026-001234",
    "price": {
      "total": 45.30,
      "currency": "EUR",
      "breakdown": [
        { "type": "BASE", "amount": 38.00 },
        { "type": "FUEL", "amount": 5.30 },
        { "type": "INSURANCE", "amount": 2.00 }
      ]
    },
    "sender": { "company": "TechCorp SAS", "country": "FR", "zipCode": "75001" },
    "recipient": { "company": "Berlin GmbH", "country": "DE", "zipCode": "10115" },
    "packages": [{ "reference": "COLIS-001", "weight": 2.5, "trackingNumber": "1234567890-001" }],
    "createdAt": "2026-06-11T10:30:00Z",
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z"
  }
}
```

---

## 3. Détail d'une expédition — `GET /api/v1/cargo/shipments/{id}`

**Rôle :** Consulter le statut actuel et l'historique.

**Response :**
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
    "reference": "CMD-2026-001234",
    "sender": { "company": "TechCorp SAS", "country": "FR" },
    "recipient": { "company": "Berlin GmbH", "country": "DE" },
    "packages": [{ "reference": "COLIS-001", "weight": 2.5, "trackingNumber": "1234567890-001" }],
    "price": { "total": 45.30, "currency": "EUR" },
    "createdAt": "2026-06-11T10:30:00Z",
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z"
  }
}
```

---

## 4. Suivi détaillé — `GET /api/v1/cargo/shipments/{id}/tracking`

**Rôle :** Voir tous les événements de suivi avec localisation.

**Response :**
```json
{
  "success": true,
  "data": {
    "shipmentId": "shp_a1b2c3d4e5",
    "carrierCode": "DHL",
    "carrierTrackingNumber": "1234567890",
    "currentStatus": {
      "code": "IN_TRANSIT",
      "label": "En transit",
      "location": "Francfort, Allemagne",
      "timestamp": "2026-06-12T08:15:00Z"
    },
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z",
    "events": [
      {
        "eventId": "evt_001",
        "code": "LABEL_CREATED",
        "label": "Étiquette créée",
        "description": "Étiquette d'expédition générée",
        "location": "Paris, France",
        "timestamp": "2026-06-11T10:30:00Z",
        "carrierRawStatus": "Shipment information received"
      },
      {
        "eventId": "evt_002",
        "code": "PICKED_UP",
        "label": "Colis récupéré",
        "description": "Colis pris en charge par le transporteur",
        "location": "Paris, France",
        "timestamp": "2026-06-11T14:00:00Z",
        "carrierRawStatus": "Pickup scanned"
      },
      {
        "eventId": "evt_003",
        "code": "IN_TRANSIT",
        "label": "En transit",
        "description": "Colis en transit vers le centre de tri",
        "location": "Francfort, Allemagne",
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

## 5. Annuler une expédition — `POST /api/v1/cargo/shipments/{id}/cancel`

**Rôle :** Annuler l'expédition.

**Response :**
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

## 6. Générer l'étiquette — `POST /api/v1/cargo/shipments/{id}/label`

**Rôle :** Générer ou récupérer l'étiquette d'expédition.

**Request :**
```json
{ "format": "PDF" }
```

**Response :**
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

## 7. Planifier un enlèvement — `POST /api/v1/cargo/pickups`

**Rôle :** Demander au transporteur de venir chercher les colis.

**Request :**
```json
{
  "carrierCode": "DHL",
  "shipmentIds": ["shp_a1b2c3d4e5"],
  "pickupDate": "2026-06-12",
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
  "specialInstructions": "Sonner à l'accueil"
}
```

**Response :**
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
    "location": { "company": "TechCorp SAS", "country": "FR", "city": "Paris", "address": "12 Rue de Rivoli" },
    "instructions": "Sonner à l'accueil",
    "createdAt": "2026-06-11T11:00:00Z"
  }
}
```

---

## 8. Webhook entrant — `POST /api/v1/cargo/webhooks/{carrierCode}`

**Rôle :** Recevoir les mises à jour poussées par le transporteur.

**Request (envoyé par DHL) :**
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

**Response (toujours 200) :**
```json
{ "success": true, "message": "Webhook processed successfully" }
```

---

## 9. Valider une adresse — `POST /api/v1/cargo/addresses/validate`

**Rôle :** Vérifier et normaliser une adresse avant expédition.

**Request :**
```json
{
  "country": "FR",
  "zipCode": "75001",
  "city": "Paris",
  "address": "12 Rue de Rivoli",
  "carrierCode": "DHL"
}
```

**Response :**
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

## 10. Gestion des transporteurs (CRUD)

### 10.1 Ajouter — `POST /api/v1/cargo/carriers`

**Rôle :** Enregistrer un nouveau transporteur avec ses credentials.

**Request :**
```json
{
  "code": "CHRONOPOST",
  "name": "Chronopost",
  "adapterName": "ChronopostAdapter",
  "active": true,
  "website": "https://www.chronopost.fr",
  "logoUrl": "https://cdn.example.com/carriers/chronopost.svg",
  "contact": {
    "name": "Support Chronopost",
    "email": "support@chronopost.fr",
    "phone": "+33123456789"
  },
  "services": [
    {
      "code": "CHRONO_13",
      "name": "Chrono 13h",
      "description": "Livraison avant 13h le lendemain",
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
      "description": "Livraison avant 18h le lendemain",
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

**Response 201 :**
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

### 10.2 Lister — `GET /api/v1/cargo/carriers`

**Rôle :** Voir tous les transporteurs. Filtres : `?active=true&zone=FR&feature=INSURANCE&page=1&limit=20`

**Response :**
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

### 10.3 Détail — `GET /api/v1/cargo/carriers/{code}`

**Response :**
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
        "description": "Livraison express internationale",
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

### 10.4 Modifier — `PUT /api/v1/cargo/carriers/{code}`

**Request :**
```json
{
  "settings": { "timeoutMs": 15000, "retryMaxAttempts": 3 },
  "active": true
}
```

### 10.5 Activer/désactiver — `PATCH /api/v1/cargo/carriers/{code}/toggle`

**Request :**
```json
{ "active": false, "reason": "API outage - maintenance" }
```

**Response :**
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

### 10.6 Tester la connexion — `POST /api/v1/cargo/carriers/{code}/test`

**Response (succès) :**
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

**Response (échec) :**
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

### 10.7 Ajouter un service — `POST /api/v1/cargo/carriers/{code}/services`

**Request :**
```json
{
  "code": "DHL_EXPRESS_9",
  "name": "Express 9:00",
  "description": "Livraison avant 9h le lendemain",
  "maxWeight": 30, "maxWeightUnit": "KG",
  "zones": ["FR", "DE", "BE", "NL", "LU"],
  "transitDays": 1,
  "features": ["SIGNATURE", "INSURANCE"],
  "active": true
}
```

### 10.8 Mettre à jour les credentials — `PUT /api/v1/cargo/carriers/{code}/credentials`

**Request :**
```json
{
  "authType": "API_KEY",
  "apiKey": "new_dhl_api_key_67890",
  "apiSecret": "new_dhl_secret_12345",
  "webhookSecret": "whsec_new_abc456"
}
```

**Response :**
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

## Flux typique complet

```
1. POST /carriers                        → Ajouter un transporteur (Chronopost)
2. POST /carriers/CHRONOPOST/test        → Tester la connexion
3. GET  /carriers                        → Voir les transporteurs disponibles
4. POST /rates                           → Comparer les prix DHL / FedEx
5. POST /addresses/validate              → Valider l'adresse du destinataire
6. POST /shipments                       → Créer l'expédition
7. POST /pickups                         → Planifier l'enlèvement
8. ← Webhook DHL (DELIVERED)             → Mise à jour automatique
9. GET  /shipments/{id}/tracking         → Suivre en temps réel
10. POST /shipments/{id}/cancel          → Annuler si besoin
```

## Cycle de vie d'une expédition (statuts)

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

## Modèle de données

### Table `shipments`

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | Identifiant interne |
| `status` | enum | CREATED, VALIDATED, PICKED_UP, IN_TRANSIT, OUT_FOR_DELIVERY, DELIVERED, FAILED, CANCELLED |
| `carrier_code` | string | DHL, FEDEX, CHRONOPOST |
| `carrier_service_code` | string | DHL_EXPRESS_WORLDWIDE |
| `carrier_tracking_number` | string | Numéro de suivi carrier |
| `carrier_shipment_id` | string | ID expédition carrier |
| `reference` | string | Référence métier |
| `label_url` | string | URL de l'étiquette |
| `label_format` | string | PDF, ZPL |
| `tracking_url` | string | URL de tracking carrier |
| `sender` | JSON | Adresse expéditeur |
| `recipient` | JSON | Adresse destinataire |
| `packages` | JSON[] | Liste des colis |
| `price_total` | decimal | Prix total |
| `price_currency` | string | EUR, USD |
| `insurance_amount` | decimal | Montant assuré |
| `signature_required` | boolean | Signature exigée |
| `saturday_delivery` | boolean | Livraison samedi |
| `estimated_delivery_date` | datetime | Date estimée |
| `actual_delivery_date` | datetime | Date réelle |
| `created_at` | datetime | |
| `updated_at` | datetime | |

### Table `tracking_events`

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | Identifiant unique |
| `shipment_id` | UUID | Référence à l'expédition |
| `code` | enum | LABEL_CREATED, PICKED_UP, IN_TRANSIT, ARRIVED_AT_HUB, DEPARTED_FROM_HUB, OUT_FOR_DELIVERY, DELIVERED, DELIVERY_ATTEMPTED, FAILED, RETURNED_TO_SENDER, CUSTOMS_HELD, CUSTOMS_CLEARED |
| `label` | string | Libellé en français |
| `description` | string | Description détaillée |
| `location` | JSON | Ville, pays |
| `timestamp` | datetime | Date de l'événement |
| `carrier_raw_status` | string | Statut brut carrier |
| `carrier_raw_data` | JSON | Payload brut |
| `signed_by` | string | Signataire |
| `delivery_photo_url` | string | Preuve photo |

### Table `carriers`

| Champ | Type | Description |
|-------|------|-------------|
| `code` | string (PK) | DHL, FEDEX, CHRONOPOST |
| `name` | string | Nom commercial |
| `adapter_name` | string | Classe adaptateur (DhlAdapter) |
| `active` | boolean | Actif ou désactivé |
| `status` | enum | PENDING_TEST, CONNECTED, DISCONNECTED, ERROR |
| `last_tested_at` | datetime | Dernier test |
| `capabilities` | JSON | Capacités techniques |
| `settings` | JSON | Timeout, retry, rate limit |
| `credentials` | JSON (chiffré) | API keys, secrets |
| `contact` | JSON | Support |
| `created_at` | datetime | |
| `updated_at` | datetime | |

### Table `carrier_services`

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID (PK) | |
| `carrier_code` | string (FK) | Référence transporteur |
| `code` | string | DHL_EXPRESS_WORLDWIDE |
| `name` | string | Express Worldwide |
| `max_weight` | decimal | Poids max |
| `zones` | JSON[] | FR, DE, BE... |
| `transit_days` | int | Jours de transit |
| `features` | JSON[] | SIGNATURE, INSURANCE |
| `active` | boolean | Service actif |
