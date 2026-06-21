# Cargo Service — Documentation Complète des Endpoints

> Chaque champ JSON est commenté avec son rôle.  
> En fin de document : schéma du pipeline complet avec le mapping.

---

## 1. Créer une expédition

### `POST /api/v1/cargo/shipments`

## Request

```json
{
  "carrierCode": "DHL",                    // Code du transporteur choisi (DHL, UPS, FEDEX, YURTICI, ARAMEX, MNG)
  "serviceCode": "DHL_EXPRESS_WORLDWIDE",  // Service choisi (récupéré depuis GET /rates)
  "reference": "CMD-2026-001234",          // Référence métier (numéro de commande, facture...)
  "sender": {
    "company": "TechCorp SAS",             // Nom de l'entreprise expéditrice
    "contactName": "Jean Dupont",          // Personne à contacter chez l'expéditeur
    "email": "jean@techcorp.fr",           // Email pour les notifications
    "phone": "+33123456789",               // Téléphone pour le transporteur
    "country": "FR",                       // Code pays ISO 3166-1 alpha-2
    "zipCode": "75001",                    // Code postal
    "city": "Paris",                       // Ville
    "address": "12 Rue de Rivoli"          // Adresse (numéro + rue)
  },
  "recipient": {
    "company": "Berlin GmbH",              // Nom de l'entreprise destinataire
    "contactName": "Hans Schmidt",         // Personne à contacter chez le destinataire
    "email": "hans@berlin.de",             // Email du destinataire
    "phone": "+4930123456",                // Téléphone du destinataire
    "country": "DE",                       // Code pays ISO
    "zipCode": "10115",                    // Code postal
    "city": "Berlin",                      // Ville
    "address": "Friedrichstraße 100"       // Adresse
  },
  "packages": [
    {
      "reference": "COLIS-001",            // Référence interne du colis
      "description": "Composants électroniques", // Description du contenu
      "weight": 2.5,                       // Poids
      "weightUnit": "KG",                  // Unité de poids (KG ou LB)
      "length": 30,                        // Longueur en cm
      "width": 20,                         // Largeur en cm
      "height": 15,                        // Hauteur en cm
      "dimUnit": "CM",                     // Unité des dimensions (CM ou IN)
      "declaredValue": 500.00,             // Valeur déclarée pour l'assurance
      "declaredCurrency": "EUR"            // Devise de la valeur déclarée
    }
  ],
  "options": {
    "insurance": {
      "amount": 500.00,                    // Montant assuré
      "currency": "EUR"                    // Devise
    },
    "signatureRequired": true,             // Signature exigée à la livraison
    "saturdayDelivery": false              // Livraison le samedi
  }
}
```

## Response 201

```json
{
  "success": true,                                 // Statut de la requête
  "data": {
    "id": "shp_a1b2c3d4e5",                       // ID interne de l'expédition (UUID préfixé)
    "internalStatus": "PENDING",                   // Statut interne (PENDING | PICKED_UP | IN_PROGRESS | DELIVERED | RETURNED | CANCELLED)
    "carrierStatus": "Shipment information received", // Statut brut chez le transporteur (conservé pour debug)
    "carrierCode": "DHL",                          // Code du transporteur utilisé
    "carrierName": "DHL Express",                  // Nom du transporteur
    "carrierTrackingNumber": "1234567890",         // Numéro de suivi chez le transporteur
    "carrierShipmentId": "DE-2026-98765",          // ID de l'expédition chez le transporteur
    "labelUrl": "https://api.dhl.com/labels/1234567890.pdf", // URL de l'étiquette (PDF)
    "labelFormat": "PDF",                          // Format de l'étiquette
    "trackingUrl": "https://www.dhl.com/track/1234567890", // URL de tracking chez le transporteur
    "reference": "CMD-2026-001234",                // Référence métier (recopiée de la requête)
    "price": {
      "total": 45.30,                              // Prix total en EUR
      "currency": "EUR",
      "breakdown": [                               // Détail du prix
        { "type": "BASE", "label": "Transport", "amount": 38.00 },
        { "type": "FUEL", "label": "Surcharge carburant", "amount": 5.30 },
        { "type": "INSURANCE", "label": "Assurance", "amount": 2.00 }
      ]
    },
    "sender": { "company": "TechCorp SAS", "country": "FR", "zipCode": "75001" },
    "recipient": { "company": "Berlin GmbH", "country": "DE", "zipCode": "10115" },
    "packages": [{
      "reference": "COLIS-001",
      "weight": 2.5,
      "trackingNumber": "1234567890-001"           // Numéro de suivi par colis
    }],
    "createdAt": "2026-06-11T10:30:00Z",           // Date de création (ISO 8601)
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z" // Date estimée de livraison
  }
}
```

> **Mapping ici :** `DhlAdapter.createShipment()` transforme notre JSON → format DHL, appelle l'API DHL, puis normalise la réponse DHL → notre format.

---

## 2. Lister les expéditions

### `GET /api/v1/cargo/shipments`

## Query params

```
?status=IN_PROGRESS     // Filtrer par statut interne
&carrier=UPS            // Filtrer par transporteur
&from=2026-06-01        // Date de création min
&to=2026-06-14          // Date de création max
&q=CMD-2026             // Recherche texte (référence, nom)
&page=1                 // Numéro de page
&limit=20               // Nombre d'éléments par page
```

## Response 200

```json
{
  "success": true,
  "data": [
    {
      "id": "shp_a1b2c3d4e5",                     // ID interne
      "internalStatus": "IN_PROGRESS",             // Statut interne (6 valeurs)
      "carrierStatus": "OnTheWay",                 // Statut brut chez le transporteur
      "carrierCode": "UPS",                        // Code transporteur
      "carrierTrackingNumber": "1Z999AA10123456784", // N° suivi transporteur
      "reference": "CMD-2026-001235",              // Référence métier
      "recipient": { "company": "ACME GmbH", "country": "DE" }, // Destinataire (résumé)
      "createdAt": "2026-06-11T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,                                     // Page actuelle
    "limit": 20,                                   // Limite par page
    "total": 42                                    // Total d'éléments
  }
}
```

---

## 3. Détail d'une expédition

### `GET /api/v1/cargo/shipments/{id}`

## Response 200

```json
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5",
    "internalStatus": "IN_PROGRESS",               // Statut interne (mappé par le StatusMapper)
    "carrierStatus": "OnTheWay",                   // Statut brut retourné par le transporteur (conservé pour traçabilité)
    "statusHistory": [                             // Historique complet des changements de statut
      {
        "status": "SUBMITTED",                     // Statut au moment de l'événement
        "internalStatus": "PENDING",               // Statut interne correspondant
        "timestamp": "2026-06-11T10:30:00Z"
      },
      {
        "status": "PICKED_UP",
        "internalStatus": "PICKED_UP",
        "timestamp": "2026-06-11T14:00:00Z"
      },
      {
        "status": "OnTheWay",                      // Statut brut UPS : "OnTheWay"
        "internalStatus": "IN_PROGRESS",            // Mappé par StatusMapper → "IN_PROGRESS"
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

## 4. Modifier une expédition

### `PUT /api/v1/cargo/shipments/{id}`

## Request

```json
{
  "reference": "CMD-2026-001235-UPDATED",          // Nouvelle référence
  "options": {
    "signatureRequired": false                      // Désactiver la signature
  }
}
```

## Response 200

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

## 5. Supprimer une expédition

### `DELETE /api/v1/cargo/shipments/{id}`

## Response 200

```json
{
  "success": true,
  "data": { "deleted": true }                      // Confirmation de suppression
}
```

---

## 6. Annuler une expédition

### `POST /api/v1/cargo/shipments/{id}/cancel`

## Response 200

```json
{
  "success": true,
  "data": {
    "id": "shp_a1b2c3d4e5",
    "internalStatus": "CANCELLED",                 // Statut interne mis à jour
    "carrierStatus": "Cancelled",                  // Statut chez le transporteur
    "cancelledAt": "2026-06-11T12:00:00Z"          // Date d'annulation
  }
}
```

> **Mapping ici :** `UpsAdapter.cancelShipment()` transforme notre requête → format UPS, appelle API UPS.

---

## 7. Générer l'étiquette

### `POST /api/v1/cargo/shipments/{id}/label`

## Request

```json
{
  "format": "PDF"                                   // Format demandé (PDF, ZPL, PNG)
}
```

## Response 200

```json
{
  "success": true,
  "data": {
    "labelUrl": "https://api.dhl.com/labels/1234567890.pdf", // URL de l'étiquette
    "format": "PDF",                                 // Format retourné
    "size": "A6",                                    // Taille du papier (A6, A5, 10x15)
    "generatedAt": "2026-06-11T10:30:00Z"             // Date de génération
  }
}
```

---

## 8. Suivi détaillé

### `GET /api/v1/cargo/shipments/{id}/tracking`

## Response 200

```json
{
  "success": true,
  "data": {
    "shipmentId": "shp_a1b2c3d4e5",                 // ID interne
    "carrierCode": "DHL",                            // Code transporteur
    "carrierTrackingNumber": "1234567890",           // N° suivi transporteur
    "currentStatus": {                               // Dernier statut connu
      "internalCode": "IN_PROGRESS",                 // Statut interne (mappé par StatusMapper)
      "carrierCode": "IN_TRANSIT",                   // Code statut chez le transporteur
      "label": "En transit",                         // Libellé lisible
      "location": "Francfort, Allemagne",             // Localisation
      "timestamp": "2026-06-12T08:15:00Z"
    },
    "estimatedDeliveryDate": "2026-06-13T18:00:00Z",
    "events": [                                      // Tous les événements de suivi
      {
        "eventId": "evt_001",
        "internalCode": "PENDING",                   // Statut interne (mappé)
        "carrierCode": "LABEL_CREATED",              // Code chez le transporteur
        "carrierRawStatus": "Shipment information received", // Statut BRUT du transporteur (gardé pour debug)
        "label": "Étiquette créée",
        "location": "Paris, France",
        "timestamp": "2026-06-11T10:30:00Z"
      },
      {
        "eventId": "evt_002",
        "internalCode": "PICKED_UP",                 // Mappé : "Pickup scanned" → PICKED_UP
        "carrierCode": "PICKED_UP",
        "carrierRawStatus": "Pickup scanned",
        "label": "Colis récupéré",
        "location": "Paris, France",
        "timestamp": "2026-06-11T14:00:00Z"
      },
      {
        "eventId": "evt_003",
        "internalCode": "IN_PROGRESS",               // Mappé : "Departed from transit hub" → IN_PROGRESS
        "carrierCode": "IN_TRANSIT",
        "carrierRawStatus": "Departed from transit hub",
        "label": "En transit",
        "location": "Francfort, Allemagne",
        "timestamp": "2026-06-12T08:15:00Z"
      }
    ],
    "milestones": {                                  // Étapes clés du cycle de vie
      "pending": "2026-06-11T10:30:00Z",             // Création
      "pickedUp": "2026-06-11T14:00:00Z",           // Prise en charge
      "inProgress": "2026-06-12T08:15:00Z",         // En transit
      "delivered": null                               // Pas encore livré
    }
  }
}
```

> **MAPPING CRITIQUE ici :** Chaque `carrierRawStatus` est passé dans `StatusMapper.map("DHL", rawStatus)` pour produire `internalCode`.

---

## 9. Webhook entrant (push transporteur)

### `POST /api/v1/cargo/webhooks/{carrierCode}`

## Request — UPS envoie ceci

```json
{
  "shipment_id": "1Z999AA10123456784",               // N° suivi UPS (champ différent selon transporteur)
  "state": "Completed",                              // Statut UPS : "Completed" (≠ DHL "DELIVERED")
  "customer": "Ahmed",                               // Nom du destinataire (UPS utilise "customer")
  "signed_by": "Ahmed",                              // Signataire
  "timestamp": "2026-06-13T16:30:00Z"                // Horodatage
}
```

**Ce que voit le Core System après mapping :**

```json
{
  "tracking_no": "1Z999AA10123456784",               // Normalisé par UpsAdapter (shipment_id → tracking_no)
  "carrier_raw_status": "Completed",                 // Statut brut conservé
  "internalStatus": "DELIVERED",                     // Mappé par StatusMapper : "Completed" → "DELIVERED"
  "customer_name": "Ahmed",                          // Normalisé (customer → customer_name)
  "timestamp": "2026-06-13T16:30:00Z"
}
```

## Request — DHL envoie ceci

```json
{
  "trackingNumber": "1234567890",                    // DHL utilise "trackingNumber" (≠ UPS "shipment_id")
  "status": "DELIVERED",                             // DHL utilise "DELIVERED" (≠ UPS "Completed")
  "statusDescription": "Shipment delivered",
  "timestamp": "2026-06-13T16:30:00Z",
  "location": { "city": "Berlin", "country": "DE" },
  "signedBy": "Hans Schmidt"                         // DHL utilise "signedBy" (≠ UPS "signed_by")
}
```

**Ce que voit le Core System après mapping :**

```json
{
  "tracking_no": "1234567890",                       // Normalisé (trackingNumber → tracking_no)
  "carrier_raw_status": "DELIVERED",                 // Statut brut conservé
  "internalStatus": "DELIVERED",                     // Mappé : "DELIVERED" → "DELIVERED"
  "customer_name": "Hans Schmidt",                   // Normalisé (signedBy → customer_name)
  "timestamp": "2026-06-13T16:30:00Z"
}
```

## Request — Yurtiçi Kargo envoie ceci

```json
{
  "takipNo": "YT2026001122334",                       // Yurtiçi utilise "takipNo" (turc)
  "durum": "Teslim Edildi",                           // Statut en turc : "Teslim Edildi" (≠ "DELIVERED")
  "alici": "Ahmet",                                   // Destinataire : "alici" (≠ "customer")
  "tarih": "2026-06-13T16:30:00Z"                     // Date : "tarih" (≠ "timestamp")
}
```

**Ce que voit le Core System après mapping :**

```json
{
  "tracking_no": "YT2026001122334",                   // Normalisé (takipNo → tracking_no)
  "carrier_raw_status": "Teslim Edildi",              // Statut brut en turc conservé
  "internalStatus": "DELIVERED",                      // Mappé par StatusMapper : "Teslim Edildi" → "DELIVERED"
  "customer_name": "Ahmet",                           // Normalisé (alici → customer_name)
  "timestamp": "2026-06-13T16:30:00Z"
}
```

## Response (toujours 200)

```json
{
  "success": true,
  "message": "Webhook processed successfully"         // Le transporteur saura que le webhook est bien reçu
}
```

> **MAPPING CRITIQUE ici :** L'Adapter parse le payload JSON (normalisation des champs), puis le StatusMapper traduit le statut (normalisation des valeurs). C'est le point d'entrée unique de tous les transporteurs.

---

## 10. Comparer les prix

### `POST /api/v1/cargo/rates`

## Request

```json
{
  "sender": {                                        // Adresse de l'expéditeur
    "country": "FR",
    "zipCode": "75001",
    "city": "Paris"
  },
  "recipient": {                                     // Adresse du destinataire
    "country": "DE",
    "zipCode": "10115",
    "city": "Berlin"
  },
  "packages": [{                                     // Colis à expédier
    "weight": 2.5,
    "weightUnit": "KG",
    "length": 30, "width": 20, "height": 15,
    "dimUnit": "CM"
  }],
  "options": {
    "carrierCodes": ["DHL", "UPS", "FEDEX"],          // Transporteurs à comparer (vide = tous)
    "serviceType": "EXPRESS"                           // Type de service
  }
}
```

## Response 200

```json
{
  "success": true,
  "data": [
    {
      "carrierCode": "DHL",
      "carrierName": "DHL Express",
      "serviceCode": "DHL_EXPRESS_WORLDWIDE",
      "serviceName": "Express Worldwide",
      "totalPrice": 45.30,                             // Prix total
      "currency": "EUR",
      "estimatedTransitDays": 2,                       // Jours de transit estimés
      "estimatedDeliveryDate": "2026-06-13",
      "guaranteed": true,                              // Date garantie ?
      "breakdown": [
        { "type": "BASE", "label": "Transport", "amount": 38.00 },
        { "type": "FUEL", "label": "Surcharge carburant", "amount": 5.30 },
        { "type": "INSURANCE", "label": "Assurance", "amount": 2.00 }
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

> **Mapping ici :** Chaque Adapter (`DhlAdapter`, `UpsAdapter`, `FedExAdapter`) transforme la requête dans le format de son transporteur, appelle son API, et normalise la réponse.

---

## 11. Planifier un enlèvement

### `POST /api/v1/cargo/pickups`

## Request

```json
{
  "carrierCode": "DHL",                               // Transporteur
  "shipmentIds": ["shp_a1b2c3d4e5"],                  // Expéditions concernées
  "pickupDate": "2026-06-12",                          // Date souhaitée
  "readyTime": "09:00",                                // Heure de disponibilité
  "closeTime": "17:00",                                // Heure de fermeture
  "location": {                                        // Adresse de l'enlèvement
    "company": "TechCorp SAS",
    "contactName": "Jean Dupont",
    "phone": "+33123456789",
    "country": "FR", "zipCode": "75001",
    "city": "Paris", "address": "12 Rue de Rivoli"
  },
  "totalPackages": 1,                                  // Nombre total de colis
  "totalWeight": 2.5,                                  // Poids total
  "weightUnit": "KG",
  "specialInstructions": "Sonner à l'accueil"           // Instructions spéciales
}
```

## Response 201

```json
{
  "success": true,
  "data": {
    "id": "pck_001a2b3c",                              // ID interne de l'enlèvement
    "carrierCode": "DHL",
    "carrierPickupId": "DHL-PICKUP-98765",              // ID chez le transporteur
    "status": "CONFIRMED",                              // Statut (CONFIRMED, CANCELLED)
    "pickupDate": "2026-06-12",
    "confirmationNumber": "CONF-ABC-123"                // Numéro de confirmation
  }
}
```

---

## 12. Annuler un enlèvement

### `POST /api/v1/cargo/pickups/{id}/cancel`

## Response 200

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

## 13. Ajouter un transporteur

### `POST /api/v1/cargo/carriers`

## Request

```json
{
  "code": "UPS",                                       // Code unique du transporteur
  "name": "UPS",                                       // Nom commercial
  "adapterName": "UpsAdapter",                         // Nom de la classe Adapter (pour le Registry)
  "active": true,                                      // Actif dès l'ajout ?
  "website": "https://www.ups.com",
  "contact": {
    "name": "UPS Support",
    "email": "support@ups.com",
    "phone": "+18007425877"
  },
  "services": [{                                       // Services proposés
    "code": "UPS_EXPRESS_SAVER",
    "name": "UPS Express Saver",
    "description": "International express shipping",
    "maxWeight": 70, "maxWeightUnit": "KG",
    "zones": ["WORLDWIDE"],
    "transitDays": 2,
    "features": ["SIGNATURE", "INSURANCE"],
    "active": true
  }],
  "capabilities": {                                    // Capacités techniques
    "labelFormats": ["PDF", "ZPL"],
    "features": ["RATES", "TRACKING", "SIGNATURE", "INSURANCE", "PICKUP"]
  },
  "credentials": {                                     // Clés API (chiffrées en base)
    "authType": "API_KEY",
    "apiKey": "ups_api_key_123",
    "apiSecret": "ups_secret_456",
    "accountNumber": "UPS-ACC-001",
    "endpoint": "https://onlinetools.ups.com/api",
    "webhookSecret": "whsec_ups_abc123"
  },
  "settings": {                                        // Paramètres techniques
    "timeoutMs": 10000,                                // Timeout des appels API
    "retryMaxAttempts": 3,                             // Nombre de tentatives en cas d'échec
    "retryDelayMs": 1000,
    "rateLimitPerMinute": 50                           // Limite de requêtes par minute
  }
}
```

## Response 201

```json
{
  "success": true,
  "data": {
    "code": "UPS",
    "name": "UPS",
    "adapterName": "UpsAdapter",
    "active": true,
    "status": "PENDING_TEST",                          // En attente de test (pas encore utilisable)
    "message": "Carrier added. Run a connection test before using."
  }
}
```

---

## 14. Lister les transporteurs

### `GET /api/v1/cargo/carriers`

## Query params

```
?active=true           // Uniquement les transporteurs actifs
&feature=TRACKING      // Uniquement ceux qui supportent le tracking
&zone=TR               // Uniquement ceux qui livrent en Turquie
```

## Response 200

```json
{
  "success": true,
  "data": [
    {
      "code": "DHL", "name": "DHL Express",
      "adapterName": "DhlAdapter",
      "active": true,
      "status": "CONNECTED",                           // CONNECTED, PENDING_TEST, DISCONNECTED, ERROR
      "services": [                                    // Résumé des services
        { "code": "DHL_EXPRESS_WORLDWIDE", "name": "Express Worldwide", "active": true }
      ]
    }
  ],
  "pagination": { "page": 1, "limit": 20, "total": 3 }
}
```

---

## 15. Détail d'un transporteur

### `GET /api/v1/cargo/carriers/{code}`

## Response 200

```json
{
  "success": true,
  "data": {
    "code": "UPS",
    "name": "UPS",
    "adapterName": "UpsAdapter",
    "active": true,
    "status": "CONNECTED",
    "lastTestedAt": "2026-06-10T08:00:00Z",            // Dernier test de connexion
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
    "credentialsUpdatedAt": "2026-06-01T12:00:00Z"    // Date de dernière màj des credentials (jamais les clés elles-mêmes)
  }
}
```

---

## 16. Modifier un transporteur

### `PUT /api/v1/cargo/carriers/{code}`

## Request

```json
{
  "active": true,                                      // Activer/désactiver
  "settings": {                                        // Modifier les paramètres
    "timeoutMs": 15000,
    "retryMaxAttempts": 5
  }
}
```

---

## 17. Supprimer un transporteur

### `DELETE /api/v1/cargo/carriers/{code}`

## Response 200

```json
{ "success": true, "data": { "deleted": true } }
```

---

## 18. Activer/désactiver un transporteur

### `PATCH /api/v1/cargo/carriers/{code}/toggle`

## Request

```json
{
  "active": false,                                     // false = désactivé (ex: panne API)
  "reason": "API outage - maintenance"                 // Raison de la désactivation
}
```

## Response 200

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

## 19. Tester la connexion

### `POST /api/v1/cargo/carriers/{code}/test`

## Response — Succès

```json
{
  "success": true,
  "data": {
    "status": "CONNECTED",                             // Statut après test
    "latencyMs": 245,                                  // Temps de réponse en ms
    "testedAt": "2026-06-11T15:00:00Z",
    "endpoint": "https://onlinetools.ups.com/api/health", // Endpoint testé
    "details": {                                       // Détails de la réponse
      "httpStatus": 200,
      "message": "API is reachable",
      "accountValid": true                             // Credentials valides ?
    }
  }
}
```

## Response — Échec

```json
{
  "success": false,
  "error": {
    "code": "CARRIER_CONNECTION_FAILED",
    "message": "Failed to connect to UPS API",
    "details": {
      "httpStatus": 401,
      "reason": "Invalid API key"                      // Clé API invalide
    }
  }
}
```

---

## 20. Mettre à jour les credentials

### `PUT /api/v1/cargo/carriers/{code}/credentials`

## Request

```json
{
  "authType": "API_KEY",
  "apiKey": "new_ups_api_key_67890",                   // Nouvelle clé API
  "apiSecret": "new_ups_secret_12345",                 // Nouveau secret
  "webhookSecret": "whsec_new_abc456"                  // Nouveau secret webhook
}
```

## Response 200

```json
{
  "success": true,
  "data": {
    "code": "UPS",
    "credentialsUpdatedAt": "2026-06-11T16:00:00Z",
    "message": "Credentials updated. Re-test connection."  // Recommande un test
  }
}
```

---

## 21. Ajouter un service

### `POST /api/v1/cargo/carriers/{code}/services`

## Request

```json
{
  "code": "UPS_STANDARD",                              // Code du nouveau service
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

## 22. Valider une adresse

### `POST /api/v1/cargo/addresses/validate`

## Request

```json
{
  "country": "TR",                                     // Code pays ISO
  "zipCode": "34000",                                  // Code postal
  "city": "Istanbul",                                  // Ville
  "address": "İstiklal Cad. No:15",                    // Adresse
  "carrierCode": "YURTICI"                             // Transporteur pour la validation
}
```

## Response 200

```json
{
  "success": true,
  "data": {
    "valid": true,                                      // Adresse valide ?
    "normalizedAddress": {                               // Adresse normalisée par le transporteur
      "country": "TR",
      "zipCode": "34000",
      "city": "İSTANBUL",
      "address": "İSTİKLAL CAD. NO:15"
    },
    "suggestions": [],                                  // Suggestions si adresse invalide
    "carrierValidation": {
      "code": "VALID",
      "message": "Address is valid"
    }
  }
}
```

---

# Annexe : Schéma du Pipeline Complet avec Mapping

```
                                 NOTRE SYSTÈME
                            ┌─────────────────────────────────────┐
                            │                                     │
                            │  6 STATUTS INTERNES UNIFIÉS         │
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
                    ┌─────────────────┼─────────────────┐
                    │                 │                  │
                    ▼                 ▼                  ▼
           ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
           │   UPS          │ │   DHL          │ │   Yurtiçi      │
           │   Adapter      │ │   Adapter      │ │   Adapter      │
           └───────┬────────┘ └───────┬────────┘ └───────┬────────┘
                   │                  │                  │
          ┌────────▼────────┐ ┌───────▼────────┐ ┌───────▼────────┐
          │  UpsAdapter     │ │  DhlAdapter    │ │  YurticiAdapter│
          │  .parseWebhook()│ │  .parseWebhook()│ │  .parseWebhook│
          │                 │ │                 │ │  ()            │
          │  Normalise le   │ │  Normalise le   │ │  Normalise le  │
          │  JSON UPS :     │ │  JSON DHL :     │ │  JSON Yurtiçi: │
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
          │   NIVEAU 1 : Correspondance exacte                  │
          │   ──────────────────────────────                    │
          │   UPS: "Completed"       → DELIVERED                │
          │   DHL: "DELIVERED"       → DELIVERED                │
          │   UPS: "OnTheWay"        → IN_PROGRESS              │
          │   DHL: "IN_TRANSIT"      → IN_PROGRESS              │
          │   Yurtiçi: "Yolda"       → IN_PROGRESS              │
          │   UPS: "Cancelled"       → CANCELLED                │
          │   Yurtiçi: "İptal Edildi"→ CANCELLED                │
          │                                                     │
          │   NIVEAU 2 : Regex (variations)                     │
          │   ───────────────────────                           │
          │   /out for delivery/i     → IN_PROGRESS             │
          │   /delivery attempted/i   → IN_PROGRESS             │
          │   /return to sender/i     → RETURNED                │
          │                                                     │
          │   NIVEAU 3 : Fuzzy (similarité > 0.8)               │
          │   ────────────────────────                          │
          │   "Customs clearence" (faute) → CUSTOMS_CLEARED     │
          │   "Shipped" (ambigu)        → IN_PROGRESS           │
          │                                                     │
          │   FALLBACK :                                        │
          │   Aucun match → IN_PROGRESS (sûr par défaut)        │
          └────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
          ┌─────────────────────────────────────────────────────┐
          │                   CORE SYSTEM                       │
          │                                                     │
          │   {                                                 │
          │     "tracking_no": "12345",                         │
          │     "internalStatus": "DELIVERED",   ← Mappé !     │
          │     "carrierRawStatus": "Completed", ← Conservé     │
          │     "customer_name": "Ahmed"                        │
          │   }                                                 │
          │                                                     │
          │   ┌─────────────────────────────────────────────┐   │
          │   │  Base de données                            │   │
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

    Exemple complet : UPS envoie un webhook "Completed"

    HEURE 1 : UPS envoie
    ─────────────────────
    { "shipment_id": "1Z999...", "state": "Completed", "customer": "Ahmed" }

    HEURE 2 : UpsAdapter.parseWebhook()
    ───────────────────────────────────
    { "tracking_no": "1Z999...", "carrier_raw_status": "Completed", "customer_name": "Ahmed" }
          ↑ Normalisation du JSON : les champs UPS sont traduits en champs standards

    HEURE 3 : StatusMapper.map("UPS", "Completed")
    ──────────────────────────────────────────────
    Recherche dans la table UPS :
      "Completed" ? Table exacte → oui ! → InternalStatus.DELIVERED
          ↑ Traduction du statut : le mot "Completed" devient "DELIVERED"

    HEURE 4 : Core System
    ─────────────────────
    trackingEventRepo.create({
      shipmentId: "1Z999...",
      internalStatus: "DELIVERED",            ← Résultat du mapping
      carrierRawStatus: "Completed",          ← Statut brut conservé (debug)
      customerName: "Ahmed"
    })

    shipmentRepo.updateStatus("1Z999...", "DELIVERED")
    EventBus.publish(SHIPMENT_DELIVERED, { shipmentId: "1Z999..." })
    → Notification client : "Votre colis est livré !"

    ───────────────────────────────────────────────────────────────────

    Si c'était DHL qui envoyait :

    Etape 1 : DHL envoie
    { "trackingNumber": "12345", "status": "DELIVERED", "signedBy": "Hans" }

    Etape 2 : DhlAdapter.parseWebhook()
    { "tracking_no": "12345", "carrier_raw_status": "DELIVERED", "customer_name": "Hans" }

    Etape 3 : StatusMapper.map("DHL", "DELIVERED") → "DELIVERED"

    Etape 4 : Core System → pareil ! Le Core System ne voit jamais la différence
              entre UPS, DHL, Yurtiçi, FedEx, MNG Kargo ou Aramex.

    ───────────────────────────────────────────────────────────────────

    RÉSUMÉ : 2 niveaux de mapping, 2 fichiers à créer par transporteur

    ┌─────────────────────────────────────────────────────────────────┐
    │ NIVEAU 1 : L'ADAPTER (1 classe par transporteur)                │
    │ ───────────────────────────────────────────────                 │
    │ Rôle : Normaliser le JSON (champs, structure)                  │
    │ Fichier : src/adapters/UpsAdapter.ts                           │
    │           src/adapters/DhlAdapter.ts                           │
    │           src/adapters/YurticiAdapter.ts                       │
    │                                                                 │
    │   UPS: "shipment_id" → "tracking_no"     DHL: "trackingNumber" │
    │        "state"       → "carrierStatus"        "status"         │
    │        "customer"    → "customerName"         "signedBy"       │
    │                                                                 │
    │ NIVEAU 2 : LE STATUS MAPPER (1 table par transporteur)         │
    │ ───────────────────────────────────────────────                 │
    │ Rôle : Traduire les valeurs de statut                          │
    │ Fichier : src/mapper/statusMaps.ts                             │
    │                                                                 │
    │   UPS: "Completed"   → DELIVERED    DHL: "DELIVERED" → DELIVERED│
    │        "OnTheWay"    → IN_PROGRESS       "IN_TRANSIT" → PROGRESS│
    │        "BackToSender"→ RETURNED          "RETURNED"   → RETURNED│
    │        "Collected"   → PICKED_UP         "PICKED_UP"  → PICKED_UP│
    │        "Cancelled"   → CANCELLED         "CANCELLED"  → CANCELLED│
    │                                                                 │
    │ +3 niveaux de matching : exact → regex → fuzzy                 │
    └─────────────────────────────────────────────────────────────────┘
```

---

*Document généré le 2026-06-14 — 22 endpoints documentés avec mapping.*
