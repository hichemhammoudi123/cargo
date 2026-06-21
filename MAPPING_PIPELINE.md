# Où et comment le mapping est fait

> **Le mapping a 2 niveaux :**
> 1. **L'Adapter** normalise le JSON (champs, structure)
> 2. **Le StatusMapper** traduit les statuts (valeurs, nomenclature)

---

## Endpoint 1 : `POST /api/v1/cargo/shipments` — Créer une expédition

### Étape par étape

```
Toi (Frontend/API)                    Adapter (normalise le JSON)          API Transporteur
─────────────────                    ───────────────────────────          ────────────────

{                                     {
  "carrierCode": "DHL",                 "product": "EXPRESS_WORLDWIDE",
  "serviceCode":                        "sender": { "addressStreet": "12 Rue de Rivoli",
    "DHL_EXPRESS_WORLDWIDE",               "postalCode": "75001" },
  "sender": {                          →  "recipient": { "addressStreet": "Friedrichstraße 100",
    "country": "FR",        ────────       "postalCode": "10115" },
    "zipCode": "75001",    DhlAdapter    "pieces": [{ "weight": 2.5, "weightUnit": "KG" }]
    "city": "Paris",                    }
    "address": "12 Rue de Rivoli"         ↓
  },                                      ↓
  "recipient": {                       POST https://api.dhl.com/v1/shipments
    "country": "DE",
    "zipCode": "10115",
    "city": "Berlin",
    "address": "Friedrichstraße 100"
  },
  "packages": [{ "weight": 2.5 }]
}
```

**Où est le mapping ici ?** → Dans `DhlAdapter.createShipment()`

Le Adapter transforme NOTRE format en format DHL :
```typescript
class DhlAdapter implements CarrierAdapter {
  async createShipment(input: NormalizedShipment): Promise<NormalizedShipmentResponse> {
    // NOTRE FORMAT → FORMAT DHL
    const dhlPayload = {
      product: input.serviceCode,                               // serviceCode → product
      sender: {
        addressStreet: input.sender.address,                     // address → addressStreet
        postalCode: input.sender.zipCode,                        // zipCode → postalCode
      },
      recipient: {
        addressStreet: input.recipient.address,
        postalCode: input.recipient.zipCode,
      },
      pieces: input.packages.map(p => ({                         // packages[] → pieces[]
        weight: p.weight,
        weightUnit: p.weightUnit,
      })),
    }

    // APPEL API DHL
    const dhlResponse = await this.httpClient.post(
      'https://api.dhl.com/v1/shipments',
      dhlPayload,
      { headers: { Authorization: `Bearer ${this.apiKey}` } }
    )

    // FORMAT DHL → NOTRE FORMAT
    return {
      id: dhlResponse.shipmentId,                                // shipmentId → id
      trackingNumber: dhlResponse.trackingNumber,                // trackingNumber (déjà ok)
      labelUrl: dhlResponse.label.url,                          // label.url → labelUrl
      price: {
        total: dhlResponse.totalPrice,
        currency: dhlResponse.currencyCode,
      },
    }
  }
}
```

---

## Endpoint 2 : `POST /api/v1/cargo/webhooks/{carrierCode}` — Webhook entrant

### C'est ICI que le mapping statut est le plus visible

```
Transporteur envoie :                 Adapter parse +                   Core System
                                      StatusMapper traduit
                                      
UPS envoie :                          
{                                     {
  "shipment_id": "1Z999...",            "tracking_no": "1Z999...",
  "state": "Completed",       ──────►   "carrier_raw_status": "Completed",
  "customer": "Ahmed"                   "customer_name": "Ahmed"
}                                     }
                                        ↓
                                      StatusMapper.map("UPS", "Completed")
                                        ↓
                                      "DELIVERED"  ← statut interne
                                        ↓
                                      {
                                        "tracking_no": "1Z999...",
                                        "status": "DELIVERED",         ← mappé !
                                        "customer_name": "Ahmed"
                                      }
```

### Le code exact :

```typescript
// 1. Webhook reçu : POST /api/v1/cargo/webhooks/UPS
//    Body brut UPS : { "shipment_id": "1Z999...", "state": "Completed", "customer": "Ahmed" }

// 2. L'Adapter parse (normalisation du JSON)
const adapter = carrierRegistry.get('UPS')  // → UpsAdapter
const parsed = adapter.parseWebhook(rawBody)
// parsed = { tracking_no: "1Z999...", carrier_raw_status: "Completed", customer_name: "Ahmed" }

// 3. Le StatusMapper traduit le statut (3 niveaux)
const mapper = new StatusMapperEngine()
const internalStatus = mapper.map('UPS', parsed.carrier_raw_status)
//                    ↑              ↑       ↑
//                    |              |       "Completed"
//                    |              code transporteur
//                    InternalStatus.DELIVERED

// 4. Core System : mise à jour
await trackingEventRepo.create({
  shipmentId: parsed.tracking_no,
  internalStatus: internalStatus,               // "DELIVERED"
  carrierRawStatus: parsed.carrier_raw_status,  // "Completed" (conservé pour debug)
  customerName: parsed.customer_name,           // "Ahmed"
  timestamp: new Date()
})

await shipmentService.updateStatus(parsed.tracking_no, internalStatus)
// Shipment.status passe de "IN_PROGRESS" à "DELIVERED"
```

### La table de mapping (exacte) :

```typescript
// StatusMapperEngine.ts
class StatusMapperEngine {
  private exactMaps = new Map([
    ['DHL', new Map([
      ['IN_TRANSIT',  InternalStatus.IN_PROGRESS],    // DHL "IN_TRANSIT" → "IN_PROGRESS"
      ['DELIVERED',   InternalStatus.DELIVERED],      // DHL "DELIVERED"  → "DELIVERED"
      ['RETURNED',    InternalStatus.RETURNED],       // DHL "RETURNED"   → "RETURNED"
    ])],
    ['UPS', new Map([
      ['OnTheWay',    InternalStatus.IN_PROGRESS],    // UPS "OnTheWay"   → "IN_PROGRESS"
      ['Completed',   InternalStatus.DELIVERED],      // UPS "Completed"  → "DELIVERED"
      ['BackToSender', InternalStatus.RETURNED],      // UPS "BackToSender" → "RETURNED"
    ])],
    ['YURTICI', new Map([
      ['Yolda',          InternalStatus.IN_PROGRESS], // Yurtiçi "Yolda"  → "IN_PROGRESS"
      ['Teslim Edildi',  InternalStatus.DELIVERED],   // Yurtiçi "Teslim Edildi" → "DELIVERED"
      ['İade Edildi',    InternalStatus.RETURNED],    // Yurtiçi "İade Edildi" → "RETURNED"
    ])],
    ['FEDEX', new Map([
      ['EN_ROUTE',     InternalStatus.IN_PROGRESS],
      ['DELIVERED',    InternalStatus.DELIVERED],
      ['RETURNED',     InternalStatus.RETURNED],
    ])],
    ['MNG', new Map([
      ['Yolda',          InternalStatus.IN_PROGRESS],
      ['Teslim Edildi',  InternalStatus.DELIVERED],
      ['İade',           InternalStatus.RETURNED],
    ])],
    ['ARAMEX', new Map([
      ['IN TRANSIT',   InternalStatus.IN_PROGRESS],
      ['DELIVERED',    InternalStatus.DELIVERED],
      ['RETURNED',     InternalStatus.RETURNED],
    ])],
  ])

  map(carrierCode: string, rawStatus: string): InternalStatus {
    // Niveau 1 : correspondance exacte
    const carrierMap = this.exactMaps.get(carrierCode)
    if (carrierMap?.has(rawStatus)) {
      return carrierMap.get(rawStatus)!    // ← LE MAPPING A LIEU ICI
    }

    // Niveau 2 : regex (variations orthographiques)
    const regexMatch = this.tryRegex(carrierCode, rawStatus)
    if (regexMatch) return regexMatch

    // Niveau 3 : fuzzy (similarité)
    const fuzzyMatch = this.tryFuzzy(carrierCode, rawStatus)
    if (fuzzyMatch) return fuzzyMatch

    // Fallback : statut par défaut
    return InternalStatus.IN_PROGRESS
  }
}
```

---

## Endpoint 3 : `GET /api/v1/cargo/shipments/{id}/tracking` — Suivi

### Le même mapping, mais pour chaque événement

```
API DHL retourne :                     StatusMapper (traduit chaque statut)    Core retourne à l'utilisateur :

{                                      {                                       {
  "trackingNumber": "12345",             "tracking_no": "12345",                  "shipmentId": "shp_...",
  "events": [                            "events": [{                             "events": [{
    {                                      "code": "PICKED_UP",                      "internalCode": "PICKED_UP",
      "status": "Pickup scanned",           "carrierRawStatus":                       "carrierRawStatus":
      "location": "Paris"                    "Pickup scanned"                          "Pickup scanned",
    },                                     },                                         "label": "Colis récupéré"
    {                                      {                                         },
      "status": "Customs cleared",   →     "code": "IN_TRANSIT",         →         {
      "location": "Frankfurt"               "carrierRawStatus":                       "internalCode": "IN_PROGRESS",
    },                                       "Customs cleared"                        "label": "En transit",
    {                                      },                                         "carrierRawStatus":
    {                                      {                                           "Customs cleared"
      "status": "Departed from              "code": "IN_TRANSIT",                    },
      transit hub"                           "carrierRawStatus":                     {
      "location": "Cologne"                  "Departed from transit hub"              "internalCode": "IN_PROGRESS",
    }                                      },                                         "label": "En transit",
  ]                                      }]                                           "carrierRawStatus":
}                                      }                                              "Departed from transit hub"
                                                                                   }]
                                                                                 }
```

**Pour chaque événement**, le code fait :
```typescript
const internalCode = statusMapper.map('DHL', event.rawStatus)
// "Pickup scanned"             → PICKED_UP
// "Customs cleared"            → IN_PROGRESS
// "Departed from transit hub"  → IN_PROGRESS
```

---

## Récapitulatif : Où est le mapping ?

| Endpoint | Qui mappe ? | Quoi ? | Comment ? |
|---|---|---|---|
| `POST /shipments` | **Adapter** | Format JSON → Format transporteur | `DhlAdapter.createShipment()` |
| `POST /shipments` (réponse) | **Adapter** | Format transporteur → Format interne | `return { id, trackingNumber, ... }` |
| **`POST /webhooks/{code}`** | **Adapter + StatusMapper** | JSON brut → Format interne + Statut traduit | `parseWebhook()` + `mapper.map(carrier, status)` |
| **`GET /tracking`** | **Adapter + StatusMapper** | Événements bruts → Événements mappés | `track()` + `mapper.map()` pour chaque event |
| `POST /rates` | **Adapter** | Requête → Format transporteur | chaque adapter fait son mapping |
| `POST /addresses` | **Adapter** | Adresse → Format transporteur | `adapter.validateAddress()` |

### Les 2 seuls endroits où le code touche au statut sont :

```
1. POST /webhooks/{carrierCode}
   → statusMapper.map("UPS", "Completed")     → "DELIVERED"

2. GET /shipments/{id}/tracking
   → statusMapper.map("DHL", "Pickup scanned") → "PICKED_UP"
   → statusMapper.map("DHL", "Customs cleared") → "IN_PROGRESS"
```

**Partout ailleurs, le statut est déjà en format interne.** Le Core System ne voit jamais "OnTheWay", "Yolda" ou "Completed" — seulement PENDING, PICKED_UP, IN_PROGRESS, DELIVERED, RETURNED, CANCELLED.
