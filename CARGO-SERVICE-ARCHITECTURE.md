# Cargo Delivery Service — Architecture & Plan

## 1. Objectif

Service centralisé et générique de livraison de colis. Il doit :
- Unifier l'intégration de multiples transporteurs (DHL, FedEx, UPS, Colissimo, etc.)
- Normaliser les données brutes de chaque transporteur vers un format interne commun
- Être extensible : un nouvel adaptateur carrier = une classe, pas une réécriture

---

## 2. Architecture Globale

```
┌─────────────────────────────────────────────────────────────────┐
│                     Cargo Service (API Layer)                    │
│  POST /rates  POST /shipments  GET /tracking  POST /webhooks    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      Core Engine (Centralisé)                    │
│  - ShipmentManager        - RateOrchestrator                    │
│  - TrackingService        - PickupScheduler                     │
│  - WebhookDispatcher      - LabelGenerator                     │
└───────────┬──────────────────────────────┬──────────────────────┘
            │                              │
┌───────────▼──────────┐   ┌──────────────▼──────────────────────┐
│   Internal Models     │   │         Data Mapper                 │
│   (Normalized)        │   │  CarrierDTO → InternalDTO          │
│   - Shipment          │   │  InternalDTO → CarrierDTO          │
│   - TrackingEvent     │   └──────────────┬──────────────────────┘
│   - Rate              │                  │
│   - Address           │                  │
│   - Package           │                  │
└───────────────────────┘                  │
                                           │
┌──────────────────────────────────────────▼──────────────────────┐
│                  Carrier Adapter Layer                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ DHL      │ │ FedEx    │ │ UPS      │ │ Colissimo│  ...      │
│  │ Adapter  │ │ Adapter  │ │ Adapter  │ │ Adapter  │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  Chaque adaptateur implémente: CarrierAdapterInterface          │
│    - getRates(request) → CarrierRate[]                         │
│    - createShipment(request) → CarrierShipment                 │
│    - trackShipment(trackingNumber) → CarrierTrackingEvent[]    │
│    - cancelShipment(trackingNumber) → boolean                  │
│    - schedulePickup(request) → CarrierPickup                   │
│    - generateLabel(trackingNumber) → LabelData                 │
│    - validateAddress(address) → ValidatedAddress               │
└────────────────────────────────────────────────────────────────┘
```

---

## 3. Endpoints REST Complets

### 3.1 Tarification (Rates)

| Méthode | Path | Description |
|---------|------|-------------|
| `POST` | `/api/v1/cargo/rates` | Obtenir les tarifs de tous les transporteurs disponibles |

**Request:**
```json
{
  "sender": {
    "country": "FR",
    "zipCode": "75001",
    "city": "Paris",
    "address": "12 Rue de Rivoli"
  },
  "recipient": {
    "country": "DE",
    "zipCode": "10115",
    "city": "Berlin",
    "address": "Friedrichstraße 100"
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
    "carrierCodes": ["DHL", "FEDEX"],
    "serviceType": "EXPRESS"
  }
}
```

**Response:**
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

### 3.2 Expédition (Shipments)

| Méthode | Path | Description |
|---------|------|-------------|
| `POST` | `/api/v1/cargo/shipments` | Créer une expédition |
| `GET` | `/api/v1/cargo/shipments/{id}` | Détails d'une expédition |
| `GET` | `/api/v1/cargo/shipments?status=...&page=...` | Lister les expéditions |
| `PUT` | `/api/v1/cargo/shipments/{id}` | Modifier une expédition (avant prise en charge) |
| `POST` | `/api/v1/cargo/shipments/{id}/cancel` | Annuler une expédition |

#### POST /api/v1/cargo/shipments

**Request:**
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

**Response (201 Created):**
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
    "packages": [
      {
        "reference": "COLIS-001",
        "weight": 2.5,
        "trackingNumber": "1234567890-001"
      }
    ],
    "createdAt": "2026-06-11T10:30:00Z",
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z"
  }
}
```

#### GET /api/v1/cargo/shipments/{id}

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
    "reference": "CMD-2026-001234",
    "sender": { "company": "TechCorp SAS", "country": "FR" },
    "recipient": { "company": "Berlin GmbH", "country": "DE" },
    "packages": [
      { "reference": "COLIS-001", "weight": 2.5, "trackingNumber": "1234567890-001" }
    ],
    "price": { "total": 45.30, "currency": "EUR" },
    "createdAt": "2026-06-11T10:30:00Z",
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z"
  }
}
```

---

### 3.3 Suivi (Tracking)

| Méthode | Path | Description |
|---------|------|-------------|
| `GET` | `/api/v1/cargo/shipments/{id}/tracking` | Suivi d'une expédition (par ID interne) |
| `GET` | `/api/v1/cargo/tracking/{carrierCode}/{trackingNumber}` | Suivi par transporteur + numéro |

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

### 3.4 Enlèvement (Pickup)

| Méthode | Path | Description |
|---------|------|-------------|
| `POST` | `/api/v1/cargo/pickups` | Planifier un enlèvement |
| `GET` | `/api/v1/cargo/pickups/{id}` | Détails d'un enlèvement |
| `POST` | `/api/v1/cargo/pickups/{id}/cancel` | Annuler un enlèvement |

**Request:**
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
    "location": {
      "company": "TechCorp SAS",
      "country": "FR",
      "city": "Paris",
      "address": "12 Rue de Rivoli"
    },
    "instructions": "Sonner à l'accueil",
    "createdAt": "2026-06-11T11:00:00Z"
  }
}
```

---

### 3.5 Webhooks (Réception des mises à jour des transporteurs)

| Méthode | Path | Description |
|---------|------|-------------|
| `POST` | `/api/v1/cargo/webhooks/{carrierCode}` | Réception webhook (ex: DHL, FEDEX) |
| `GET` | `/api/v1/cargo/webhooks/logs?carrier=...` | Logs des webhooks reçus |

#### POST /api/v1/cargo/webhooks/dhl

Le webhook raw du transporteur arrive ici, le `WebhookDispatcher` identifie le transporteur, l'adapter parse et convertit en `TrackingEvent` interne.

**Request (exemple DHL):**
```json
{
  "shipmentId": "1234567890",
  "status": "DELIVERED",
  "statusDescription": "Shipment delivered",
  "timestamp": "2026-06-13T16:30:00Z",
  "location": {
    "city": "Berlin",
    "country": "DE",
    "zipCode": "10115"
  },
  "signedBy": "Hans Schmidt",
  "signatureData": "base64...",
  "deliveryPhotoUrl": "https://dhl.com/proof/photo.jpg"
}
```

**Response (toujours 200 OK pour accuser réception):**
```json
{
  "success": true,
  "message": "Webhook processed successfully"
}
```

**Logs des webhooks — GET /api/v1/cargo/webhooks/logs**
```json
{
  "success": true,
  "data": [
    {
      "id": "whlog_001",
      "carrierCode": "DHL",
      "eventType": "DELIVERED",
      "receivedAt": "2026-06-13T16:30:05Z",
      "shipmentId": "shp_a1b2c3d4e5",
      "processed": true,
      "rawPayload": "{...}"
    }
  ]
}
```

---

### 3.6 Validation d'adresse

| Méthode | Path | Description |
|---------|------|-------------|
| `POST` | `/api/v1/cargo/addresses/validate` | Valider et normaliser une adresse |

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

### 3.7 Gestion des transporteurs (CRUD complet)

| Méthode | Path | Description |
|---------|------|-------------|
| `GET` | `/api/v1/cargo/carriers` | Lister tous les transporteurs |
| `POST` | `/api/v1/cargo/carriers` | Ajouter un nouveau transporteur |
| `GET` | `/api/v1/cargo/carriers/{code}` | Détails d'un transporteur (avec credentials masqués) |
| `PUT` | `/api/v1/cargo/carriers/{code}` | Modifier la config d'un transporteur |
| `PATCH` | `/api/v1/cargo/carriers/{code}/toggle` | Activer/désactiver un transporteur |
| `DELETE` | `/api/v1/cargo/carriers/{code}` | Supprimer (désactiver) un transporteur |
| `POST` | `/api/v1/cargo/carriers/{code}/test` | Tester la connexion à l'API du transporteur |
| `GET` | `/api/v1/cargo/carriers/{code}/services` | Services disponibles |
| `POST` | `/api/v1/cargo/carriers/{code}/services` | Ajouter un service |
| `PUT` | `/api/v1/cargo/carriers/{code}/services/{serviceCode}` | Modifier un service |
| `DELETE` | `/api/v1/cargo/carriers/{code}/services/{serviceCode}` | Supprimer un service |
| `GET` | `/api/v1/cargo/carriers/{code}/credentials` | Voir les credentials (masqués) |
| `PUT` | `/api/v1/cargo/carriers/{code}/credentials` | Mettre à jour les credentials |

---

#### POST /api/v1/cargo/carriers — Ajouter un transporteur

**Exemple concret :** Tu signes un contrat avec **Chronopost**. Tu ajoutes le transporteur dans le système avec ses infos de connexion. L'adaptateur correspondant doit déjà exister dans le code (ou être créé). Une fois ajouté, le service pourra l'utiliser pour les rates, shipments, etc.

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
      "maxWeight": 30,
      "maxWeightUnit": "KG",
      "maxLength": 150,
      "dimUnit": "CM",
      "features": ["SIGNATURE", "INSURANCE"],
      "zones": ["FR", "MC", "AD"],
      "transitDays": 1,
      "active": true
    },
    {
      "code": "CHRONO_18",
      "name": "Chrono 18h",
      "description": "Livraison avant 18h le lendemain",
      "maxWeight": 30,
      "maxWeightUnit": "KG",
      "features": ["SIGNATURE"],
      "zones": ["FR", "MC"],
      "transitDays": 1,
      "active": true
    }
  ],
  "capabilities": {
    "labelFormats": ["PDF", "ZPL"],
    "features": ["RATES", "TRACKING", "SIGNATURE", "INSURANCE", "SATURDAY"],
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

**Response (201) :**
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

---

#### GET /api/v1/cargo/carriers — Lister avec filtres

**Exemple concret :** Tableau de bord admin. Tu filtres les transporteurs actifs ou inactifs, ou par zone géographique.

**Request params :** `?active=true&zone=FR&feature=INSURANCE&page=1&limit=20`

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

---

#### GET /api/v1/cargo/carriers/{code} — Détail complet

**Exemple concret :** Voir toute la config de DHL (services, credentials masqués, settings).

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

> Note : Les `credentials` ne sont jamais retournés dans les GET. Un endpoint dédié `GET /carriers/{code}/credentials` les retourne masqués (`"apiKey": "dhl***345"`).

---

#### PUT /api/v1/cargo/carriers/{code} — Modifier la configuration

**Exemple concret :** DHL a changé son endpoint API ou tu veux ajuster le timeout.

```json
{
  "settings": {
    "timeoutMs": 15000,
    "retryMaxAttempts": 3
  },
  "active": true
}
```

---

#### PATCH /api/v1/cargo/carriers/{code}/toggle — Activer/désactiver

**Exemple concret :** Tu as des problèmes avec FedEx, tu le désactives temporairement. Tous les appels `POST /rates` l'excluront automatiquement.

```json
// Request
{ "active": false, "reason": "API outage - maintenance" }

// Response
{ "success": true, "data": { "code": "FEDEX", "active": false, "deactivatedAt": "2026-06-11T14:00:00Z" } }
```

---

#### POST /api/v1/cargo/carriers/{code}/test — Tester la connexion

**Exemple concret :** Après avoir configuré Chronopost, tu testes la connexion. Le service appelle l'API santé du transporteur avec les credentials fournis.

```json
// Response
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

En cas d'échec :
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

#### POST /api/v1/cargo/carriers/{code}/services — Ajouter un service

**Exemple concret :** DHL a lancé un nouveau service "DHL_EXPRESS_9" (livraison avant 9h). Tu l'ajoutes sans redéploiement.

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

---

#### POST /api/v1/cargo/carriers/{code}/credentials — Mettre à jour les credentials

**Exemple concret :** La clé API DHL a expiré, tu la renouvelles.

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
{ "success": true, "data": { "code": "DHL", "credentialsUpdatedAt": "2026-06-11T16:00:00Z", "message": "Credentials updated. Re-test connection." } }
```

---

#### Modèle de données — Table `carriers`

| Champ | Type | Description |
|-------|------|-------------|
| `code` | string (PK) | Identifiant unique du transporteur (ex: "DHL") |
| `name` | string | Nom commercial |
| `adapter_name` | string | Classe adaptateur à utiliser (ex: "DhlAdapter") |
| `active` | boolean | Actif ou désactivé |
| `status` | enum | `PENDING_TEST`, `CONNECTED`, `DISCONNECTED`, `ERROR` |
| `last_tested_at` | datetime | Dernier test de connexion |
| `website` | string | Site web du transporteur |
| `logo_url` | string | URL du logo |
| `capabilities` | JSON | Capacités techniques |
| `settings` | JSON | Configuration technique (timeout, retry, etc.) |
| `credentials` | JSON (chiffré) | API keys, secrets, endpoints (chiffré en base) |
| `contact` | JSON | Contact support |
| `created_at` | datetime | Date de création |
| `updated_at` | datetime | Date de mise à jour |

#### Modèle de données — Table `carrier_services`

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID (PK) | Identifiant unique |
| `carrier_code` | string (FK) | Référence au transporteur |
| `code` | string | Code du service (ex: "DHL_EXPRESS_WORLDWIDE") |
| `name` | string | Nom du service |
| `description` | text | Description |
| `max_weight` | decimal | Poids max |
| `max_weight_unit` | string | KG / LB |
| `max_length` | decimal | Longueur max |
| `dim_unit` | string | CM / IN |
| `zones` | JSON[] | Zones de couverture (["FR", "DE", ...]) |
| `transit_days` | int | Jours de transit estimés |
| `features` | JSON[] | Fonctionnalités (SIGNATURE, INSURANCE, ...) |
| `active` | boolean | Service actif |
| `created_at` | datetime | |
| `updated_at` | datetime | |

---

### 3.8 Étiquette (Label)

| Méthode | Path | Description |
|---------|------|-------------|
| `POST` | `/api/v1/cargo/shipments/{id}/label` | Générer / régénérer l'étiquette |

**Request:**
```json
{
  "format": "PDF"
}
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

## 4. Modèle de Données Interne (Internal Models)

```
┌──────────────────────────────────────┐
│  ShipmentStatus (enum)               │
├──────────────────────────────────────┤
│  CREATED → VALIDATED → PICKED_UP →   │
│  IN_TRANSIT → OUT_FOR_DELIVERY →     │
│  DELIVERED | FAILED | CANCELLED      │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  TrackingEventCode (enum)            │
├──────────────────────────────────────┤
│  LABEL_CREATED, PICKED_UP,           │
│  IN_TRANSIT, ARRIVED_AT_HUB,         │
│  DEPARTED_FROM_HUB,                  │
│  OUT_FOR_DELIVERY, DELIVERED,        │
│  DELIVERY_ATTEMPTED, FAILED,         │
│  RETURNED_TO_SENDER,                 │
│  CUSTOMS_HELD, CUSTOMS_CLEARED       │
└──────────────────────────────────────┘
```

**Table Shipment :**

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID (string) | Identifiant interne unique |
| `status` | enum ShipmentStatus | Statut actuel |
| `carrier_code` | string | Code du transporteur choisi |
| `carrier_service_code` | string | Code du service chez le transporteur |
| `carrier_tracking_number` | string | Numéro de suivi chez le transporteur |
| `carrier_shipment_id` | string | ID de l'expédition chez le transporteur |
| `reference` | string | Référence métier (commande, etc.) |
| `label_url` | string | URL de l'étiquette |
| `label_format` | string | Format de l'étiquette (PDF, ZPL) |
| `tracking_url` | string | URL de tracking du transporteur |
| `sender` | JSON | Adresse de l'expéditeur |
| `recipient` | JSON | Adresse du destinataire |
| `packages` | JSON[] | Liste des colis |
| `price_total` | decimal | Prix total |
| `price_currency` | string | Devise |
| `price_breakdown` | JSON | Détail du prix |
| `insurance_amount` | decimal | Montant assuré |
| `insurance_currency` | string | Devise de l'assurance |
| `signature_required` | boolean | Signature exigée |
| `saturday_delivery` | boolean | Livraison samedi |
| `estimated_delivery_date` | datetime | Date estimée |
| `actual_delivery_date` | datetime | Date réelle de livraison |
| `created_at` | datetime | Date de création |
| `updated_at` | datetime | Date de mise à jour |

**Table TrackingEvent :**

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID (string) | Identifiant unique |
| `shipment_id` | UUID (string) | Référence à l'expédition |
| `code` | enum TrackingEventCode | Code normalisé |
| `label` | string | Libellé en français |
| `description` | string | Description détaillée |
| `location` | JSON | Ville, pays, code postal |
| `timestamp` | datetime | Date de l'événement |
| `carrier_raw_status` | string | Statut brut reçu du transporteur |
| `carrier_raw_data` | JSON | Payload brut reçu |
| `signed_by` | string | Signataire (si livré) |
| `signature_data` | string | Signature en base64 |
| `delivery_photo_url` | string | Preuve photo |

---

## 5. Scénarios Métier Complets

### Scénario A : Création d'une expédition complète

```
[Client]                  [Cargo Service]              [Carrier Adapter]         [Transporteur API]
    │                            │                            │                        │
    │  POST /rates               │                            │                        │
    │──────────────────────────► │                            │                        │
    │                            │  broadcast à tous les      │                        │
    │                            │  adaptateurs actifs         │                        │
    │                            │──────────────────────►     │                        │
    │                            │                            │  GET /rates            │
    │                            │                            │──────────────────────► │
    │                            │                            │◄────────────────────── │
    │                            │◄──────────────────────     │                        │
    │                            │  normalize toutes les      │                        │
    │                            │  réponses → InternalRate   │                        │
    │◄────────────────────────── │                            │                        │
    │  [Liste des tarifs]        │                            │                        │
    │                            │                            │                        │
    │  POST /shipments           │                            │                        │
    │──────────────────────────► │                            │                        │
    │                            │  créer Shipment en DB      │                        │
    │                            │  (status=CREATED)          │                        │
    │                            │                            │                        │
    │                            │  appel adapter             │                        │
    │                            │  createShipment()          │                        │
    │                            │──────────────────────►     │                        │
    │                            │                            │  POST /shipments       │
    │                            │                            │──────────────────────► │
    │                            │                            │◄────────────────────── │
    │                            │◄──────────────────────     │                        │
    │                            │  update DB avec TN, URL    │                        │
    │                            │  (status=VALIDATED)        │                        │
    │◄────────────────────────── │                            │                        │
    │  [Shipment created +       │                            │                        │
    │   label URL]               │                            │                        │
```

### Scénario B : Suivi de colis (tracking)

```
[Client]                  [Cargo Service]              [Carrier Adapter]         [Transporteur API]
    │                            │                            │                        │
    │  GET /shipments/{id}       │                            │                        │
    │  /tracking                 │                            │                        │
    │──────────────────────────► │                            │                        │
    │                            │  lookup DB pour            │                        │
    │                            │  carrier + TN              │                        │
    │                            │                            │                        │
    │                            │  trackShipment(TN)         │                        │
    │                            │──────────────────────►     │                        │
    │                            │                            │  GET /tracking/{TN}    │
    │                            │                            │──────────────────────► │
    │                            │                            │◄────────────────────── │
    │                            │◄──────────────────────     │                        │
    │                            │  map → InternalEvent[]     │                        │
    │                            │  merge avec DB existant    │                        │
    │                            │  update si nouveaux events │                        │
    │◄────────────────────────── │                            │                        │
    │  [Tracking events +        │                            │                        │
    │   milestones]              │                            │                        │
```

### Scénario C : Mise à jour via webhook (push carrier → nous)

```
[Transporteur API]         [Cargo Service]              [Adapter]         [Système Interne]
    │                            │                            │                    │
    │  POST /webhooks/{carrier}  │                            │                    │
    │──────────────────────────► │                            │                    │
    │                            │  WebhookDispatcher         │                    │
    │                            │  identifie carrier          │                    │
    │                            │                            │                    │
    │                            │  adapter.parseWebhook()    │                    │
    │                            │──────────────────────►     │                    │
    │                            │◄──────────────────────     │                    │
    │                            │  raw → InternalTracking     │                    │
    │                            │                            │                    │
    │                            │  trouver shipment par TN   │                    │
    │                            │  ajouter TrackingEvent     │                    │
    │                            │  update Shipment.status    │                    │
    │                            │                            │                    │
    │                            │  publier événement         │                    │
    │                            │  (RabbitMQ/Kafka/...)      │                    │
    │                            │──────────────────────────────────────────────►  │
    │                            │                            │                    │
    │◄────────────────────────── │                            │                    │
    │  200 OK                    │                            │                    │
```

### Scénario D : Cycle de vie complet d'une expédition

```
    CREATED ──→ VALIDATED ──→ PICKED_UP ──→ IN_TRANSIT ──→ OUT_FOR_DELIVERY ──→ DELIVERED
        │           │              │               │               │
        │           │              │               │               ├── DELIVERY_ATTEMPTED ──→ OUT_FOR_DELIVERY
        │           │              │               │               │
        │           │              │               ├── CUSTOMS_HELD ──→ CUSTOMS_CLEARED ──→ IN_TRANSIT
        │           │              │               │
        │           │              ├── FAILED ──────┘
        │           │              │
        │           ├── CANCELLED ─┘
        │           │
        └───────────┘
```

### Scénario E : Erreur / Fallback

| Problème | Comportement |
|----------|-------------|
| API transporteur indisponible | Rate : exclure ce transporteur + flag `"error": "carrier_unavailable"` |
| | Shipment : retry 3x, puis status=FAILED + événement d'erreur |
| Timeout (10s) | Considéré comme indisponible |
| Invalid address | Retour d'erreur avec suggestions |
| Poids/dimensions invalides | Validation avant envoi au carrier |

---

## 6. Pattern Adaptateur — Interface & Cycle de Vie

### 6.1 Interface contractuelle

```typescript
interface CarrierAdapter {
  readonly code: string;               // "DHL", "FEDEX", "CHRONOPOST"
  readonly name: string;               // "DHL Express"
  readonly active: boolean;
  readonly services: CarrierService[];
  readonly capabilities: CarrierCapabilities;

  // Initialisation avec la config stockée en DB
  initialize(config: CarrierConfig): Promise<void>;

  // Rates
  getRates(request: RateRequest): Promise<CarrierRate[]>;

  // Shipment
  createShipment(request: CreateShipmentRequest): Promise<CarrierShipmentResponse>;
  cancelShipment(trackingNumber: string): Promise<CancelResult>;

  // Tracking
  trackShipment(trackingNumber: string): Promise<CarrierTrackingEvent[]>;

  // Pickup
  schedulePickup(request: PickupRequest): Promise<CarrierPickupResponse>;
  cancelPickup(pickupId: string): Promise<CancelResult>;

  // Label
  generateLabel(trackingNumber: string, format: string): Promise<LabelData>;

  // Address
  validateAddress(address: Address): Promise<ValidatedAddress>;

  // Webhook
  parseWebhook(rawPayload: any): InternalTrackingEvent;
  verifyWebhookSignature(headers: any, body: any): boolean;
}
```

### 6.2 Cycle de vie : de la config DB → à l'adapter actif

Voici comment la configuration du transporteur (stockée en base) est injectée dans l'adaptateur au moment de l'initialisation :

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CARRIER LIFECYCLE                                     │
│                                                                             │
│  1. Admin ajoute un transporteur via POST /carriers                          │
│     → Enregistrement en base (credentials chiffrés, settings, services)      │
│                                                                             │
│  2. Au démarrage du service :                                                │
│     CarrierRegistry.start()                                                 │
│       ├── Charger tous les carriers actifs depuis la DB                      │
│       ├── Pour chaque carrier :                                              │
│       │   ├── Instancier l'adapter par réflexion (adapter_name)              │
│       │   ├── Appeler adapter.initialize(config)                              │
│       │   │   → config.credentials (déchiffrés)                              │
│       │   │   → config.settings (timeout, retry...)                          │
│       │   │   → config.services (services disponibles)                       │
│       │   └── Enregistrer dans le registry actif                             │
│       └── Prêt à servir les requêtes                                         │
│                                                                             │
│  3. Pendant le fonctionnement :                                              │
│     Core Service → CarrierRegistry.getAdapter("DHL")                         │
│                   → adapter.getRates(request)                                │
│                                                                             │
│  4. Mise à jour en runtime (sans redémarrage) :                              │
│     PUT /carriers/DHL/credentials                                            │
│       → CarrierRegistry.reloadAdapter("DHL")                                 │
│       → Réinitialiser avec les nouveaux credentials                          │
│                                                                             │
│  5. Désactivation :                                                          │
│     PATCH /carriers/DHL/toggle { active: false }                             │
│       → CarrierRegistry.deactivateAdapter("DHL")                             │
│       → Exclu de tous les appels (rates, shipments, etc.)                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 Exemple concret : DhlAdapter.initialize()

```typescript
class DhlAdapter implements CarrierAdapter {
  private client: HttpClient;
  private config: CarrierConfig;

  async initialize(config: CarrierConfig): Promise<void> {
    this.config = config;
    this.client = new HttpClient({
      baseUrl: config.credentials.endpoint,       // "https://api.dhl.com/v1"
      authType: config.credentials.authType,       // "API_KEY"
      apiKey: config.credentials.apiKey,           // "dhl_live_xxxx"
      apiSecret: config.credentials.apiSecret,
      timeout: config.settings.timeoutMs,          // 10000
      retry: config.settings.retryMaxAttempts,     // 3
    });
  }

  async getRates(request: RateRequest): Promise<CarrierRate[]> {
    // 1. Convertir Internal → DTO DHL (via DhlMapper)
    const dhlRequest = DhlMapper.toRateRequest(request);
    // 2. Appeler l'API DHL
    const dhlResponse = await this.client.post('/rates', dhlRequest);
    // 3. Convertir DTO DHL → Internal (via DhlMapper)
    return DhlMapper.toInternalRates(dhlResponse);
  }
}
```

### 6.4 CarrierRegistry — Le registre central

```typescript
class CarrierRegistry {
  private adapters: Map<string, CarrierAdapter> = new Map();
  private configs: Map<string, CarrierConfig> = new Map();

  // Au démarrage
  async start(): Promise<void> {
    const carriers = await carrierRepository.findAllActive();
    for (const carrier of carriers) {
      await this.register(carrier);
    }
  }

  async register(carrier: CarrierEntity): Promise<void> {
    // Instanciation dynamique par le nom de la classe
    const AdapterClass = await import(`../adapters/${carrier.adapterName}`);
    const adapter: CarrierAdapter = new AdapterClass();
    
    await adapter.initialize({
      credentials: decrypt(carrier.credentials),
      settings: carrier.settings,
      services: carrier.services,
    });
    
    this.adapters.set(carrier.code, adapter);
    this.configs.set(carrier.code, carrier);
  }

  getAdapter(code: string): CarrierAdapter {
    const adapter = this.adapters.get(code);
    if (!adapter || !adapter.active) {
      throw new CarrierNotAvailableError(code);
    }
    return adapter;
  }

  getAllActive(): CarrierAdapter[] {
    return Array.from(this.adapters.values()).filter(a => a.active);
  }

  async reloadAdapter(code: string): Promise<void> {
    const carrier = await carrierRepository.findByCode(code);
    this.adapters.delete(code);
    await this.register(carrier);
  }

  async deactivateAdapter(code: string): Promise<void> {
    const adapter = this.adapters.get(code);
    if (adapter) adapter.active = false;
  }
}
```

### 6.5 Exemple de flux complet avec DhlMapper

Le mapper est le seul endroit où la logique de conversion vit. Exemple :

```typescript
// DhlMapper.ts — Conversion bidirectionnelle
class DhlMapper {

  // Internal → DHL (avant d'envoyer la requête à DHL)
  static toRateRequest(internal: RateRequest): DhlRateRequest {
    return {
      origin: {
        countryCode: internal.sender.country,
        postalCode: internal.sender.zipCode,
        cityName: internal.sender.city,
      },
      destination: {
        countryCode: internal.recipient.country,
        postalCode: internal.recipient.zipCode,
        cityName: internal.recipient.city,
      },
      packages: internal.packages.map(p => ({
        weight: p.weight,
        weightUnit: p.weightUnit,
        dimensions: { length: p.length, width: p.width, height: p.height, unit: p.dimUnit },
      })),
      products: this.mapServiceCode(internal.options?.serviceType),
    };
  }

  // DHL → Internal (après réception de la réponse)
  static toInternalRates(dhlResponse: DhlRateResponse): CarrierRate[] {
    return dhlResponse.products.map(product => ({
      carrierCode: "DHL",
      carrierName: "DHL Express",
      serviceCode: product.productCode,
      serviceName: product.productName,
      totalPrice: product.totalPrice.amount,
      currency: product.totalPrice.currency,
      estimatedTransitDays: product.deliveryCapabilities.estimatedTransitDays,
      guaranteed: product.deliveryCapabilities.deliveryType === "DOOR_TO_DOOR",
      breakdown: product.charges.map(c => ({
        type: this.mapChargeType(c.chargeCode),
        label: c.chargeName,
        amount: c.amount,
      })),
    }));
  }

  private static mapChargeType(code: string): string {
    const map = { "BASE": "BASE", "FUEL": "FUEL", "INSURANCE": "INSURANCE" };
    return map[code] || "OTHER";
  }
}
```

### 6.6 Ajouter un nouveau transporteur : la checklist

Pour intégrer **Chronopost** par exemple :

| Étape | Action | Fichier |
|-------|--------|---------|
| 1 | Créer le dossier `adapters/chronopost/` | |
| 2 | Implémenter `ChronopostAdapter.ts` (implements CarrierAdapter) | `adapters/chronopost/ChronopostAdapter.ts` |
| 3 | Créer `ChronopostMapper.ts` (conversion bidirectionnelle) | `adapters/chronopost/ChronopostMapper.ts` |
| 4 | Définir les DTO spécifiques `ChronopostModels.ts` | `adapters/chronopost/ChronopostModels.ts` |
| 5 | Créer le client HTTP `ChronopostClient.ts` | `adapters/chronopost/ChronopostClient.ts` |
| 6 | Enregistrer l'adapter dans le code (le registry le découvre automatiquement si convention de nommage) | |
| 7 | **Sans code** : `POST /carriers` avec les credentials, services et settings | Base de données |
| 8 | `POST /carriers/CHRONOPOST/test` pour valider la connexion | |
| 9 | Actif et prêt ! | |

---

## 7. Structure de Dossiers Recommandée

```
src/
├── api/
│   ├── controllers/
│   │   ├── ShipmentController.java/.ts
│   │   ├── RateController.java/.ts
│   │   ├── TrackingController.java/.ts
│   │   ├── PickupController.java/.ts
│   │   ├── WebhookController.java/.ts
│   │   └── CarrierController.java/.ts
│   └── middlewares/
│       └── errorHandler.ts
│
├── core/
│   ├── models/
│   │   ├── Shipment.ts
│   │   ├── TrackingEvent.ts
│   │   ├── Rate.ts
│   │   ├── Address.ts
│   │   ├── Package.ts
│   │   └── enums/
│   │       ├── ShipmentStatus.ts
│   │       └── TrackingEventCode.ts
│   ├── services/
│   │   ├── ShipmentService.ts
│   │   ├── RateOrchestrator.ts
│   │   ├── TrackingService.ts
│   │   ├── PickupService.ts
│   │   ├── WebhookDispatcher.ts
│   │   └── AddressService.ts
│   └── repository/
│       └── interfaces/
│           └── IShipmentRepository.ts
│
├── adapters/
│   ├── contracts/
│   │   └── CarrierAdapter.ts          (interface)
│   ├── registry/
│   │   └── CarrierRegistry.ts         (enregistre et fournit les adapteurs)
│   ├── dhl/
│   │   ├── DhlAdapter.ts
│   │   ├── DhlMapper.ts              (convertit DTO DHL ↔ Internal)
│   │   ├── DhlModels.ts              (DTO spécifiques DHL)
│   │   └── DhlClient.ts              (client HTTP vers l'API DHL)
│   ├── fedex/
│   │   ├── FedExAdapter.ts
│   │   ├── FedExMapper.ts
│   │   ├── FedExModels.ts
│   │   └── FedExClient.ts
│   └── ups/
│       ├── UpsAdapter.ts
│       ├── UpsMapper.ts
│       ├── UpsModels.ts
│       └── UpsClient.ts
│
├── infrastructure/
│   ├── persistence/
│   │   ├── entities/
│   │   └── repositories/
│   ├── http/
│   │   └── HttpClientFactory.ts
│   ├── cache/
│   │   └── RateCacheService.ts
│   └── messaging/
│       └── EventPublisher.ts
│
└── config/
    ├── carriers.config.ts
    └── app.config.ts
```

---

## 8. Principes Clés

1. **Centralisé mais extensible** — Le core engine ne change jamais. Pour ajouter un transporteur : créer un dossier `adapters/{carrier}/`, implémenter `CarrierAdapter`, l'enregistrer dans `CarrierRegistry`.

2. **Mapper dédié** — Chaque adaptateur contient son propre mapper (`XxxMapper.ts`). Il est le seul responsable de la conversion entre le format carrier et le format interne. Pas de mapping spaghetti dans le core.

3. **Statut unifié** — Tous les événements carrier sont normalisés vers `TrackingEventCode` (enum commun). Le carrier raw status est conservé dans `carrier_raw_status` pour debug.

4. **Résilience** — Timeout, retry, circuit breaker sur chaque appel carrier. Un carrier qui échoue n'impacte pas les autres.

5. **Webhook d'abord** — Le webhook est la source de vérité pour les mises à jour. Le polling tracking est un fallback.

---

## 9. Prochaines Étapes Techniques

1. Choisir le langage/framework (Spring Boot / NestJS / FastAPI)
2. Définir le schéma de base de données (PostgreSQL recommandé)
3. Implémenter le **core** (models, service interfaces, repository)
4. Implémenter le **premier adaptateur** (ex: DHL ou un carrier mock pour tests)
5. Ajouter la couche API (contrôleurs)
6. Ajouter le webhook dispatcher
7. Ajouter cache et résilience
8. Tests d'intégration avec carriers mockés

---

> **Prêt à implémenter.** Dis-moi sur quel langage/framework on part, je génère le code.
