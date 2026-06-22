# Cargo Delivery Service — Tous les Endpoints CRUD

## Shipments

### `GET /api/v1/cargo/shipments`
Lister les expéditions.

```json
// Response 200
{
  "success": true,
  "data": [
    {
      "id": "shp_a1b2c3d4e5",
      "internalStatus": "IN_PROGRESS",
      "carrierStatus": "OnTheWay",
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

### `POST /api/v1/cargo/shipments`
Créer une expédition.

```json
// Request
{
  "carrierCode": "DHL",
  "serviceCode": "DHL_EXP",
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
      "description": "Composants électroniques",
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
    "insurance": { "amount": 500.00, "currency": "EUR" },
    "signatureRequired": true,
    "saturdayDelivery": false
  }
}

// Response 201
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5",
    "internalStatus": "PENDING",
    "carrierStatus": "Shipment information received",
    "carrierCode": "DHL",
    "carrierName": "DHL Express",
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
        { "type": "BASE", "label": "Transport", "amount": 38.00 },
        { "type": "FUEL", "label": "Surcharge carburant", "amount": 5.30 },
        { "type": "INSURANCE", "label": "Assurance", "amount": 2.00 }
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

### `GET /api/v1/cargo/shipments/{id}`
Détail d'une expédition.

```json
// Response 200
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5",
    "internalStatus": "IN_PROGRESS",
    "carrierStatus": "OnTheWay",
    "statusHistory": [
      { "status": "PICKED_UP", "internalStatus": "PICKED_UP", "timestamp": "2026-06-11T10:00:00Z" }
    ],
    "carrierCode": "UPS",
    "carrierName": "UPS United Parcel Service",
    "carrierTrackingNumber": "1Z999AA10123456784",
    "carrierShipmentId": "UPS-SHIP-12345",
    "labelUrl": "https://www.ups.com/labels/label.pdf",
    "labelFormat": "PDF",
    "trackingUrl": "https://www.ups.com/track/1Z999AA10123456784",
    "reference": "CMD-2026-001235",
    "price": { "total": 42.50, "currency": "EUR", "breakdown": [] },
    "sender": { "company": "TechCorp", "country": "FR", "zipCode": "75001" },
    "recipient": { "company": "ACME GmbH", "country": "DE", "zipCode": "10115" },
    "packages": [{ "reference": "COLIS-001", "weight": 2.5, "trackingNumber": "1234567890-001" }],
    "createdAt": "2026-06-11T10:30:00Z",
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z"
  }
}
```

### `PUT /api/v1/cargo/shipments/{id}`
Modifier une expédition (statut SUBMITTED uniquement).

```json
// Request
{
  "reference": "CMD-2026-MODIFIED",
  "options": { "signatureRequired": false }
}

// Response 200
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5",
    "reference": "CMD-2026-MODIFIED",
    "updatedAt": "2026-06-11T11:00:00Z"
  }
}
```

### `DELETE /api/v1/cargo/shipments/{id}`
Supprimer une expédition (statut DRAFT ou SUBMITTED uniquement).

```json
// Response 200
{ "success": true, "data": { "deleted": true } }
```

### `POST /api/v1/cargo/shipments/{id}/cancel`
Annuler une expédition.

```json
// Response 200
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5",
    "internalStatus": "CANCELLED",
    "carrierStatus": "Cancelled",
    "cancelledAt": "2026-06-11T11:00:00Z"
  }
}
```

### `POST /api/v1/cargo/shipments/{id}/label`
Générer l'étiquette.

```json
// Request
{ "format": "PDF" }

// Response 200
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

## Tracking

### `GET /api/v1/cargo/shipments/{id}/tracking`
Suivi détaillé d'une expédition.

```json
// Response 200
{
  "success": true,
  "data": {
    "shipmentId": "shp_a1b2c3d4e5",
    "carrierCode": "DHL",
    "carrierTrackingNumber": "1234567890",
    "currentStatus": {
      "internalCode": "DELIVERED",
      "carrierCode": "DHL",
      "carrierRawStatus": "DELIVERED",
      "label": "Delivered",
      "timestamp": "2026-06-13T16:30:00Z"
    },
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z",
    "events": [
      {
        "eventId": "evt_001a2b3c",
        "internalCode": "PICKED_UP",
        "carrierCode": "DHL",
        "carrierRawStatus": "PICKED_UP",
        "label": "Picked Up",
        "location": "Paris, FR",
        "timestamp": "2026-06-11T10:00:00Z"
      },
      {
        "eventId": "evt_004d5e6f",
        "internalCode": "DELIVERED",
        "carrierCode": "DHL",
        "carrierRawStatus": "DELIVERED",
        "label": "Delivered",
        "location": "Berlin, DE",
        "timestamp": "2026-06-13T16:30:00Z"
      }
    ]
  }
}
```

### `POST /api/v1/cargo/webhooks/{carrierCode}`
Webhook entrant — le transporteur nous notifie d'un changement de statut.

```json
// UPS envoie :
{ "shipment_id": "1Z999AA10123456784", "state": "Completed", "timestamp": "2026-06-13T16:30:00Z" }

// DHL envoie :
{ "trackingNumber": "1234567890", "status": "DELIVERED", "timestamp": "2026-06-13T16:30:00Z" }

// Yurtiçi envoie :
{ "takipNo": "YT2026001122334", "durum": "Teslim Edildi", "tarih": "2026-06-13T16:30:00Z" }

// Response (toujours 200)
{ "success": true, "message": "Webhook processed successfully" }
```

---

## Rates

### `POST /api/v1/cargo/rates`
Comparer les prix de tous les transporteurs.

```json
// Request
{
  "sender": { "country": "FR", "zipCode": "75001", "city": "Paris", "address": "12 Rue de Rivoli" },
  "recipient": { "country": "DE", "zipCode": "10115", "city": "Berlin", "address": "Friedrichstraße 100" },
  "packages": [
    { "weight": 2.5, "weightUnit": "KG", "length": 30, "width": 20, "height": 15, "dimUnit": "CM" }
  ],
  "options": {
    "carrierCodes": ["DHL", "UPS"],
    "serviceType": "EXPRESS"
  }
}

// Response 200
{
  "success": true,
  "data": [
    {
      "carrierCode": "DHL",
      "carrierName": "DHL Express",
      "serviceCode": "DHL_EXP",
      "serviceName": "DHL Express Worldwide",
      "totalPrice": 45.30,
      "currency": "EUR",
      "estimatedTransitDays": 2,
      "estimatedDeliveryDate": "2026-06-13",
      "guaranteed": true,
      "breakdown": [
        { "type": "BASE", "label": "Transport", "amount": 38.00 },
        { "type": "FUEL", "label": "Fuel", "amount": 5.30 },
        { "type": "INSURANCE", "label": "Insurance", "amount": 2.00 }
      ]
    },
    {
      "carrierCode": "UPS",
      "carrierName": "UPS United Parcel Service",
      "serviceCode": "UPS_EXP",
      "serviceName": "UPS Express Plus",
      "totalPrice": 48.00,
      "currency": "EUR",
      "estimatedTransitDays": 2,
      "estimatedDeliveryDate": "2026-06-13",
      "guaranteed": false,
      "breakdown": [
        { "type": "BASE", "label": "Transport", "amount": 42.00 },
        { "type": "FUEL", "label": "Fuel", "amount": 6.00 }
      ]
    }
  ],
  "errors": null
}
```

---

## Pickups

### `GET /api/v1/cargo/pickups`
Lister les enlèvements.

```json
// Response 200
{
  "success": true,
  "data": [
    {
      "id": "pck_001a2b3c",
      "carrierCode": "DHL",
      "status": "CONFIRMED",
      "pickupDate": "2026-06-12",
      "confirmationNumber": "CONF-ABC-123",
      "createdAt": "2026-06-11T10:00:00Z"
    }
  ],
  "pagination": { "page": 1, "limit": 20, "total": 5 }
}
```

### `POST /api/v1/cargo/pickups`
Planifier un enlèvement.

```json
// Request
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

// Response 201
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

### `GET /api/v1/cargo/pickups/{id}`
Détail d'un enlèvement.

```json
// Response 200
{
  "success": true,
  "data": {
    "id": "pck_001a2b3c",
    "carrierCode": "DHL",
    "carrierPickupId": "DHL-PICKUP-98765",
    "status": "CONFIRMED",
    "pickupDate": "2026-06-12",
    "readyTime": "09:00:00",
    "closeTime": "17:00:00",
    "totalPackages": 1,
    "totalWeight": 2.5,
    "weightUnit": "KG",
    "confirmationNumber": "CONF-ABC-123",
    "createdAt": "2026-06-11T10:00:00Z",
    "cancelledAt": null
  }
}
```

### `PUT /api/v1/cargo/pickups/{id}`
Modifier un enlèvement.

```json
// Request
{
  "pickupDate": "2026-06-14",
  "readyTime": "10:00",
  "closeTime": "16:00",
  "specialInstructions": "Entrepôt B, quai 3"
}

// Response 200
{ "success": true, "data": { "mêmes champs que GET detail" } }
```

### `DELETE /api/v1/cargo/pickups/{id}`
Supprimer (annuler) un enlèvement.

```json
// Response 200
{ "success": true, "data": { "id": "pck_001a2b3c", "status": "CANCELLED", "cancelledAt": "2026-06-11T14:00:00Z" } }
```

### `POST /api/v1/cargo/pickups/{id}/cancel`
Annuler un enlèvement.

```json
// Response 200
{ "success": true, "data": { "id": "pck_001a2b3c", "status": "CANCELLED", "cancelledAt": "2026-06-11T14:00:00Z" } }
```

---

## Carriers

### `GET /api/v1/cargo/carriers`
Lister les transporteurs.

```json
// Response 200
{
  "success": true,
  "data": [
    {
      "code": "DHL",
      "name": "DHL Express",
      "adapterName": "Dhl",
      "active": true,
      "status": "CONNECTED",
      "services": [
        { "code": "DHL_EXP", "name": "DHL Express Worldwide", "description": "Express", "active": true }
      ]
    }
  ],
  "pagination": { "page": 1, "limit": 20, "total": 6 }
}
```

### `POST /api/v1/cargo/carriers`
Ajouter un transporteur.

```json
// Request
{
  "code": "NEWCARRIER",
  "name": "New Carrier Ltd",
  "adapterName": "Newcarrier",
  "active": true,
  "website": "https://newcarrier.com",
  "contact": { "email": "support@newcarrier.com", "phone": "+44123456789" },
  "services": [{"code":"NC_EXP","name":"Express"}],
  "capabilities": {"labelFormats":["PDF","ZPL"],"features":["insurance"]},
  "credentials": {"apiKey":"","apiSecret":""},
  "settings": {"timeoutMs":30000,"retryMaxAttempts":3}
}

// Response 201
{ "success": true, "data": { "code": "NEWCARRIER", "name": "New Carrier Ltd", "active": true } }
```

### `GET /api/v1/cargo/carriers/{code}`
Détail d'un transporteur.

```json
// Response 200
{
  "success": true,
  "data": {
    "code": "DHL",
    "name": "DHL Express",
    "adapterName": "Dhl",
    "active": true,
    "status": "CONNECTED",
    "lastTestedAt": "2026-06-11T10:00:00Z",
    "services": [
      { "code": "DHL_EXP", "name": "DHL Express Worldwide", "description": "Express", "maxWeight": 70.0, "transitDays": 2, "active": true }
    ],
    "capabilities": { "labelFormats": ["PDF", "ZPL", "PNG"], "features": ["insurance", "signature"] },
    "settings": { "timeoutMs": 30000, "retryMaxAttempts": 3, "retryDelayMs": 1000, "rateLimitPerMin": 50 },
    "credentialsUpdatedAt": "2026-06-11T10:00:00Z"
  }
}
```

### `PUT /api/v1/cargo/carriers/{code}`
Modifier un transporteur.

```json
// Request
{ "active": true, "settings": { "timeoutMs": 15000, "retryMaxAttempts": 5 } }

// Response 200
{ "success": true, "data": { "code": "DHL", "active": true } }
```

### `DELETE /api/v1/cargo/carriers/{code}`
Supprimer un transporteur.

```json
// Response 200
{ "success": true, "data": { "deleted": true } }
```

### `PATCH /api/v1/cargo/carriers/{code}/toggle`
Activer/désactiver un transporteur.

```json
// Request
{ "active": false, "reason": "API down for maintenance" }

// Response 200
{ "success": true, "data": { "code": "DHL", "active": false, "deactivatedAt": "2026-06-11T10:00:00Z" } }
```

### `POST /api/v1/cargo/carriers/{code}/test`
Tester la connexion au transporteur.

```json
// Response 200
{
  "success": true,
  "data": {
    "status": "CONNECTED",
    "latencyMs": 145,
    "testedAt": "2026-06-11T10:30:00Z",
    "endpoint": "https://api.dhl.com/test",
    "details": {
      "httpStatus": 200,
      "message": "Connection successful",
      "accountValid": true
    }
  }
}
```

### `PUT /api/v1/cargo/carriers/{code}/credentials`
Mettre à jour les identifiants.

```json
// Request
{
  "authType": "API_KEY",
  "apiKey": "new-api-key-123",
  "apiSecret": "new-api-secret-456",
  "webhookSecret": "whsec_new_secret"
}

// Response 200
{ "success": true, "data": { "code": "DHL", "credentialsUpdatedAt": "2026-06-11T10:30:00Z" } }
```

### `POST /api/v1/cargo/carriers/{code}/services`
Ajouter un service au transporteur.

```json
// Request
{
  "code": "DHL_ECO",
  "name": "DHL Economy Select",
  "description": "Economy international shipping",
  "maxWeight": 70,
  "maxWeightUnit": "KG",
  "zones": ["EU", "US"],
  "transitDays": 5,
  "features": ["tracking"],
  "active": true
}

// Response 201
{ "success": true, "data": { "code": "DHL_ECO", "name": "DHL Economy Select", "active": true } }
```

---

## Address

### `POST /api/v1/cargo/addresses/validate`
Valider une adresse.

```json
// Request
{
  "country": "US",
  "zipCode": "10001",
  "city": "New York",
  "address": "123 Main St",
  "carrierCode": "DHL"
}

// Response 200
{
  "success": true,
  "data": {
    "valid": true,
    "normalizedAddress": {
      "country": "US",
      "zipCode": "10001",
      "city": "NEW YORK",
      "address": "123 MAIN ST"
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

## Résumé des 26 endpoints

| # | Méthode | Endpoint | Description |
|---|---------|----------|-------------|
| 1 | POST | `/shipments` | Créer expédition |
| 2 | GET | `/shipments` | Lister expéditions |
| 3 | GET | `/shipments/{id}` | Détail expédition |
| 4 | PUT | `/shipments/{id}` | Modifier expédition |
| 5 | DELETE | `/shipments/{id}` | Supprimer expédition |
| 6 | POST | `/shipments/{id}/cancel` | Annuler expédition |
| 7 | POST | `/shipments/{id}/label` | Générer étiquette |
| 8 | GET | `/shipments/{id}/tracking` | Suivi détaillé |
| 9 | POST | `/webhooks/{carrierCode}` | Webhook entrant |
| 10 | POST | `/rates` | Comparer prix |
| 11 | GET | `/pickups` | Lister enlèvements |
| 12 | POST | `/pickups` | Planifier enlèvement |
| 13 | GET | `/pickups/{id}` | Détail enlèvement |
| 14 | PUT | `/pickups/{id}` | Modifier enlèvement |
| 15 | DELETE | `/pickups/{id}` | Supprimer enlèvement |
| 16 | POST | `/pickups/{id}/cancel` | Annuler enlèvement |
| 17 | GET | `/carriers` | Lister transporteurs |
| 18 | POST | `/carriers` | Ajouter transporteur |
| 19 | GET | `/carriers/{code}` | Détail transporteur |
| 20 | PUT | `/carriers/{code}` | Modifier transporteur |
| 21 | DELETE | `/carriers/{code}` | Supprimer transporteur |
| 22 | PATCH | `/carriers/{code}/toggle` | Activer/désactiver |
| 23 | POST | `/carriers/{code}/test` | Tester connexion |
| 24 | PUT | `/carriers/{code}/credentials` | Màj credentials |
| 25 | POST | `/carriers/{code}/services` | Ajouter service |
| 26 | POST | `/addresses/validate` | Valider adresse |
