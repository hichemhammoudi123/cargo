# Architecture Adaptateur + Mapper Multi-Transporteur

> **Principe :** Le système ne dépend d'aucun transporteur. Chaque transporteur est un plugin.

---

## 1. Le Problème Concret

Chaque transporteur a son propre format JSON et ses propres statuts :

```
DHL API →
{
  "trackingNumber": "12345",
  "status": "IN_TRANSIT",
  "recipientName": "Ahmed"
}

UPS API →
{
  "shipment_id": "12345",
  "state": "OnTheWay",
  "customer": "Ahmed"
}

FedEx API →
{
  "tracking_number": "12345",
  "current_status": "EN_ROUTE",
  "recipient": { "name": "Ahmed" }
}

Yurtiçi Kargo API →
{
  "takipNo": "12345",
  "durum": "Yolda",
  "alici": "Ahmed"
}

Aramex API →
{
  "awb": "12345",
  "event": "IN TRANSIT",
  "consignee": "Ahmed"
}
```

On veut un format interne unique :

```json
{
  "tracking_no": "12345",
  "status": "IN_PROGRESS",
  "customer_name": "Ahmed"
}
```

---

## 2. La Solution : Pipeline à 3 Étages

```
                    ┌─────────────────────┐
                    │   Transporteur API   │
                    │  (format brut)       │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Adapter           │
                    │  ─ Normalise le JSON │
                    │  ─ Gère l'auth       │
                    │  ─ Gère les erreurs  │
                    │  ─ Timeout / retry   │
                    └──────────┬──────────┘
                               │ (format normalisé)
                    ┌──────────▼──────────┐
                    │    Status Mapper     │
                    │  ─ Traduit les       │
                    │    statuts           │
                    │  ─ 3 niveaux de      │
                    │    matching          │
                    └──────────┬──────────┘
                               │ (format interne)
                    ┌──────────▼──────────┐
                    │  Cargo Core System   │
                    │  ─ Shipment          │
                    │  ─ TrackingEvent     │
                    │  ─ Workflow          │
                    │  ─ Base de données   │
                    └─────────────────────┘
```

---

## 3. Étape 1 : L'Adapter

L'adapter transforme le JSON propre à chaque transporteur en un format normalisé commun.

### Interface

```typescript
interface CarrierAdapter {
  // Chaque transporteur implémente ces méthodes
  createShipment(input: NormalizedShipment): Promise<NormalizedShipmentResponse>
  track(trackingNumber: string): Promise<NormalizedTrackingData>
  getRates(request: RateRequest): Promise<NormalizedRateOffer[]>
  cancelShipment(trackingNumber: string): Promise<void>
  schedulePickup(request: PickupRequest): Promise<NormalizedPickupResponse>
  testConnection(): Promise<boolean>
}
```

### Exemple Concret : Adapter UPS

```typescript
class UpsAdapter implements CarrierAdapter {
  // UPS format : { "shipment_id": "12345", "state": "OnTheWay", "customer": "Ahmed" }
  // Notre format : { "tracking_no": "12345", "status": "IN_PROGRESS", "customer_name": "Ahmed" }

  async track(trackingNumber: string): Promise<NormalizedTrackingData> {
    // 1. Appeler l'API UPS
    const upsResponse = await this.httpClient.get(`/api/track/${trackingNumber}`)
    // upsResponse = { "shipment_id": "12345", "state": "OnTheWay", "customer": "Ahmed" }

    // 2. Normaliser le JSON
    return {
      tracking_no: upsResponse.shipment_id,
      carrier_raw_status: upsResponse.state,   // "OnTheWay" → sera mappé après
      customer_name: upsResponse.customer,
    }
  }

  async createShipment(input: NormalizedShipment): Promise<NormalizedShipmentResponse> {
    // Transformer notre format → format UPS
    const upsPayload = {
      shipment_id: input.tracking_no,
      customer: input.customer_name,
    }
    // Appeler UPS API...
  }
}
```

### Exemple Concret : Adapter Yurtiçi Kargo

```typescript
class YurticiKargoAdapter implements CarrierAdapter {
  // Yurtiçi format : { "takipNo": "12345", "durum": "Yolda", "alici": "Ahmed" }

  async track(trackingNumber: string): Promise<NormalizedTrackingData> {
    const response = await this.httpClient.get(`/track/${trackingNumber}`)
    // response = { "takipNo": "12345", "durum": "Yolda", "alici": "Ahmed" }

    return {
      tracking_no: response.takipNo,
      carrier_raw_status: response.durum,   // "Yolda" → sera mappé après
      customer_name: response.alici,
    }
  }
}
```

---

## 4. Étape 2 : Le Status Mapper

Le mapper traduit les statuts bruts (français, anglais, turc...) en statuts internes.

### La Table de Mapping

```
┌─────────────────────┬──────────────────────┬──────────────────┐
│ Transporteur        │ Statut Brut          │ Statut Interne   │
├─────────────────────┼──────────────────────┼──────────────────┤
│ DHL                 │ IN_TRANSIT           │ IN_PROGRESS      │
│ UPS                 │ OnTheWay             │ IN_PROGRESS      │
│ FedEx               │ EN_ROUTE             │ IN_PROGRESS      │
│ Yurtiçi Kargo       │ Yolda                │ IN_PROGRESS      │
│ MNG Kargo           │ Yolda                │ IN_PROGRESS      │
│ Aramex              │ IN TRANSIT           │ IN_PROGRESS      │
├─────────────────────┼──────────────────────┼──────────────────┤
│ DHL                 │ DELIVERED            │ DELIVERED        │
│ UPS                 │ Completed            │ DELIVERED        │
│ FedEx               │ DELIVERED            │ DELIVERED        │
│ Yurtiçi Kargo       │ Teslim Edildi        │ DELIVERED        │
│ MNG Kargo           │ Teslim Edildi        │ DELIVERED        │
│ Aramex              │ DELIVERED            │ DELIVERED        │
├─────────────────────┼──────────────────────┼──────────────────┤
│ DHL                 │ RETURNED             │ RETURNED         │
│ UPS                 │ BackToSender         │ RETURNED         │
│ FedEx               │ RETURNED             │ RETURNED         │
│ Yurtiçi Kargo       │ İade Edildi          │ RETURNED         │
│ MNG Kargo           │ İade                 │ RETURNED         │
│ Aramex              │ RETURNED             │ RETURNED         │
├─────────────────────┼──────────────────────┼──────────────────┤
│ DHL                 │ PICKED_UP            │ PICKED_UP        │
│ UPS                 │ Collected            │ PICKED_UP        │
│ FedEx               │ PICKED UP            │ PICKED_UP        │
│ Yurtiçi Kargo       │ Teslim Alındı        │ PICKED_UP        │
├─────────────────────┼──────────────────────┼──────────────────┤
│ DHL                 │ CANCELLED            │ CANCELLED        │
│ UPS                 │ Cancelled            │ CANCELLED        │
│ FedEx               │ CANCELLED            │ CANCELLED        │
│ Yurtiçi Kargo       │ İptal Edildi         │ CANCELLED        │
└─────────────────────┴──────────────────────┴──────────────────┘
```

### Les Statuts Internes (6 seulement)

```typescript
enum InternalStatus {
  PENDING      = 'PENDING',       // En attente de prise en charge
  PICKED_UP    = 'PICKED_UP',     // Pris en charge par le transporteur
  IN_PROGRESS  = 'IN_PROGRESS',   // En transit / en cours
  DELIVERED    = 'DELIVERED',     // Livré ✓
  RETURNED     = 'RETURNED',      // Retourné à l'expéditeur
  CANCELLED    = 'CANCELLED',     // Annulé
}
```

### Code du Status Mapper

```typescript
class StatusMapperEngine {
  // 1. Mapping exact (table de correspondance directe)
  private exactMaps: Map<string, Map<string, InternalStatus>> = new Map([
    ['DHL', new Map([
      ['IN_TRANSIT', InternalStatus.IN_PROGRESS],
      ['DELIVERED',  InternalStatus.DELIVERED],
      ['RETURNED',   InternalStatus.RETURNED],
      ['PICKED_UP',  InternalStatus.PICKED_UP],
      ['CANCELLED',  InternalStatus.CANCELLED],
    ])],
    ['UPS', new Map([
      ['OnTheWay',    InternalStatus.IN_PROGRESS],
      ['Completed',   InternalStatus.DELIVERED],
      ['BackToSender', InternalStatus.RETURNED],
      ['Collected',   InternalStatus.PICKED_UP],
      ['Cancelled',   InternalStatus.CANCELLED],
    ])],
    ['YURTICI', new Map([
      ['Yolda',          InternalStatus.IN_PROGRESS],
      ['Teslim Edildi',  InternalStatus.DELIVERED],
      ['İade Edildi',    InternalStatus.RETURNED],
      ['Teslim Alındı',  InternalStatus.PICKED_UP],
      ['İptal Edildi',   InternalStatus.CANCELLED],
    ])],
  ])

  // 2. Regex patterns (pour les variations)
  private regexMaps: Map<string, Array<{ pattern: RegExp; status: InternalStatus }>> = new Map([
    ['DHL', [
      { pattern: /out for delivery/i,         status: InternalStatus.IN_PROGRESS },
      { pattern: /delivery attempted/i,       status: InternalStatus.IN_PROGRESS },
    ]],
    ['FEDEX', [
      { pattern: /en route/i,                 status: InternalStatus.IN_PROGRESS },
      { pattern: /out for delivery/i,          status: InternalStatus.IN_PROGRESS },
    ]],
    ['ARAMEX', [
      { pattern: /in transit/i,               status: InternalStatus.IN_PROGRESS },
      { pattern: /out for delivery/i,          status: InternalStatus.IN_PROGRESS },
    ]],
  ])

  map(carrierCode: string, rawStatus: string): InternalStatus {
    // Niveau 1 : Recherche exacte
    const exactMap = this.exactMaps.get(carrierCode)
    if (exactMap?.has(rawStatus)) {
      return exactMap.get(rawStatus)!
    }

    // Niveau 2 : Regex patterns
    const patterns = this.regexMaps.get(carrierCode) || []
    for (const { pattern, status } of patterns) {
      if (pattern.test(rawStatus)) {
        return status
      }
    }

    // Niveau 3 : Fuzzy match (similarité)
    const fuzzy = this.fuzzyMatch(carrierCode, rawStatus)
    if (fuzzy) return fuzzy

    // Fallback : statut par défaut sûr
    return InternalStatus.IN_PROGRESS
  }

  private fuzzyMatch(carrierCode: string, rawStatus: string): InternalStatus | null {
    // Levenshtein distance ou similarité de Jaccard
    // entre rawStatus et chaque clé de la exactMap
    // Retourne le match avec la meilleure similarité (> 0.8)
  }
}
```

---

## 5. Le Pipeline Complet

```
                    ┌──────────────────────────────────────────────┐
                    │        1. APPEL API TRANSPORTEUR             │
                    │                                              │
                    │  DHL:   GET /dhl/track/12345                 │
                    │  UPS:   GET /ups/track/12345                 │
                    │  FedEx: GET /fedex/track/12345               │
                    └──────────────────┬───────────────────────────┘
                                       │
                    ┌──────────────────▼───────────────────────────┐
                    │        2. ADAPTER (Normalisation JSON)       │
                    │                                              │
                    │  upsResponse = {                             │
                    │    shipment_id: "12345",          ───┐        │
                    │    state: "OnTheWay",              ───┼──►   │
                    │    customer: "Ahmed"               ───┘        │
                    │  }                                             │
                    │  ↓                                             │
                    │  normalized = {                                │
                    │    tracking_no: "12345",                       │
                    │    carrier_raw_status: "OnTheWay",             │
                    │    customer_name: "Ahmed"                      │
                    │  }                                             │
                    └──────────────────┬───────────────────────────┘
                                       │
                    ┌──────────────────▼───────────────────────────┐
                    │        3. STATUS MAPPER                      │
                    │                                              │
                    │  Entrée : "OnTheWay" (UPS)                   │
                    │  ↓                                           │
                    │  Exact match ? → UPS map → OnTheWay =        │
                    │                     IN_PROGRESS              │
                    │  ↓                                           │
                    │  Sortie : InternalStatus.IN_PROGRESS         │
                    └──────────────────┬───────────────────────────┘
                                       │
                    ┌──────────────────▼───────────────────────────┐
                    │        4. CORE SYSTEM                        │
                    │                                              │
                    │  tracking_no: "12345"                        │
                    │  status: "IN_PROGRESS"                       │
                    │  customer_name: "Ahmed"                      │
                    │                                              │
                    │  ┌────────────────┐                          │
                    │  │  Base de       │                          │
                    │  │  données       │                          │
                    │  └────────────────┘                          │
                    └──────────────────────────────────────────────┘
```

---

## 6. Exemple Complet avec du Code

```typescript
// ====== 1. Un appel API arrive ======

// Webhook UPS ou polling tracker
const upsRawData = {
  shipment_id: "12345",
  state: "OnTheWay",
  customer: "Ahmed"
}

// ====== 2. L'Adapter normalise ======

const adapter = new UpsAdapter()
const normalized = await adapter.track(upsRawData.shipment_id)
// normalized = { tracking_no: "12345", carrier_raw_status: "OnTheWay", customer_name: "Ahmed" }

// ====== 3. Le Mapper traduit le statut ======

const mapper = new StatusMapperEngine()
const internalStatus = mapper.map('UPS', normalized.carrier_raw_status)
// internalStatus = InternalStatus.IN_PROGRESS

// ====== 4. Le Core System enregistre ======

const event = new TrackingEvent({
  shipmentId: normalized.tracking_no,
  status: internalStatus,              // "IN_PROGRESS"
  carrierRawStatus: normalized.carrier_raw_status,  // "OnTheWay" (conservé pour debug)
  customerName: normalized.customer_name,
  timestamp: new Date()
})

await trackingEventRepository.save(event)
await shipmentService.updateStatus(normalized.tracking_no, internalStatus)
await eventBus.publish(TRACKING_EVENT_RECEIVED, event)
```

---

## 7. Résumé Visuel

```
                    DHL                  UPS           Yurtiçi Kargo
                 ┌────────┐         ┌────────┐        ┌────────────┐
                 │JSON A  │         │JSON B  │        │JSON C       │
                 └───┬────┘         └───┬────┘        └──────┬─────┘
                     │                  │                     │
              ┌──────▼──────┐   ┌──────▼──────┐   ┌──────────▼──────────┐
              │ DhlAdapter  │   │ UpsAdapter  │   │ YurticiAdapter      │
              │             │   │             │   │                     │
              │ shipment_id │   │ shipment_id │   │ takipNo →           │
              │ →           │   │ →           │   │ tracking_no         │
              │ tracking_no │   │ tracking_no │   │ durum →             │
              │ status →    │   │ state →     │   │ carrier_raw_status  │
              │ carrier_    │   │ carrier_    │   │ alici →             │
              │ raw_status  │   │ raw_status  │   │ customer_name       │
              └──────┬──────┘   └──────┬──────┘   └──────────┬──────────┘
                     │                  │                     │
                     └──────────────────┼─────────────────────┘
                                        │
                               ┌────────▼────────┐
                               │ StatusMapper    │
                               │                 │
                               │ IN_TRANSIT ──┐  │
                               │ OnTheWay   ──┤  │
                               │ EN_ROUTE   ──┤  │
                               │ Yolda      ──┤  │
                               │ IN TRANSIT ──┘  │
                               │         ↓       │
                               │   IN_PROGRESS   │
                               └────────┬────────┘
                                        │
                               ┌────────▼────────┐
                               │   Core System    │
                               │   ───────────    │
                               │   tracking_no    │
                               │   status:        │
                               │   IN_PROGRESS    │
                               │   customer_name  │
                               └─────────────────┘
```

---

## 8. Ce Que Ça Apporte

| Principe | Bénéfice |
|---|---|
| **Adapter** normalise le JSON | Le Core System ne voit jamais le format brut |
| **Mapper** traduit les statuts | 6 statuts internes seulement, quelque soit le transporteur |
| **Registry** enregistre les adapters | Ajouter un transporteur = 1 classe + 1 status map |
| **3 niveaux de matching** | Gère les variations, les fautes, le multilangue |
| **Statut brut conservé** | Debug possible, traçabilité complète |

Ajouter **MNG Kargo** demain :
```
1. Créer MngKargoAdapter     → normalise le JSON
2. Ajouter la table de mapping → "Yolda" → IN_PROGRESS
3. Enregistrer dans le Registry
4. ✅ Fini — zéro changement dans le Core System
```
