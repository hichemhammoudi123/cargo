# Cargo Delivery Service — Architecture Backend

> **Focus : logique métier, workflow, extensibilité transporteurs**
> Générique, évolutif, indépendant de l'UI

---

## 1. Domain Model (Cœur Métier)

### 1.1 Entités Principales

```
┌─────────────┐     ┌──────────────────┐     ┌────────────────┐
│   Shipment  │────>│  TrackingEvent   │     │   Carrier      │
├─────────────┤     ├──────────────────┤     ├────────────────┤
│ id          │     │ id               │     │ code (PK)      │
│ status      │     │ shipment_id      │     │ name           │
│ carrier_code│     │ code             │     │ adapter_name   │
│ reference   │     │ description      │     │ active         │
│ sender      │     │ location         │     │ status         │
│ recipient   │     │ timestamp        │     │ capabilities   │
│ packages[]  │     │ carrier_raw_data │     │ credentials    │
│ price       │     │ signed_by        │     │ settings       │
│ labels[]    │     │ photo_url        │     │ services[]     │
│ carrier_ids │     └──────────────────┘     └────────────────┘
└─────────────┘
```

### 1.2 Value Objects

```typescript
// Adresse normalisée
interface Address {
  company?: string; contactName?: string; email?: string; phone?: string
  country: string; zipCode: string; city: string; address: string; address2?: string
}

// Colis
interface Parcel {
  reference: string; description?: string
  weight: number; weightUnit: 'KG' | 'LB'
  length?: number; width?: number; height?: number; dimUnit?: 'CM' | 'IN'
  declaredValue?: number; declaredCurrency?: string
  containsDangerousGoods?: boolean
  trackingNumber?: string
}

// Prix
interface Price {
  total: number; currency: 'EUR' | 'USD' | 'GBP'
  breakdown: Array<{ type: string; label: string; amount: number }>
}

// Étiquette
interface Label {
  url: string; format: 'PDF' | 'ZPL' | 'PNG'; size: string; generatedAt: DateTime
}
```

---

## 2. Unified Status Model

### 2.1 Shipment Status (Machine à États)

```typescript
enum ShipmentStatus {
  DRAFT         = 'DRAFT',          // Création en cours
  VALIDATED     = 'VALIDATED',      // Données validées, pas encore envoyé
  SUBMITTED     = 'SUBMITTED',      // Envoyé au transporteur
  PICKED_UP     = 'PICKED_UP',      // Pris en charge par le transporteur
  IN_TRANSIT    = 'IN_TRANSIT',     // En transit
  CUSTOMS_HELD  = 'CUSTOMS_HELD',   // Bloqué en douane
  OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY', // En cours de livraison
  DELIVERED     = 'DELIVERED',      // Livré ✓ (terminal)
  DELIVERY_ATTEMPTED = 'DELIVERY_ATTEMPTED', // Tentative échouée
  FAILED        = 'FAILED',         // Échec définitif (terminal)
  RETURNED      = 'RETURNED',       // Retour à l'expéditeur (terminal)
  CANCELLED     = 'CANCELLED'       // Annulé (terminal)
}
```

### 2.2 Diagramme de Transition

```
                    ┌──────────┐
                    │  DRAFT   │
                    └────┬─────┘
                         │ validate
                    ┌────▼─────┐
                    │VALIDATED │
                    └────┬─────┘
                         │ submit (→ carrier API)
                    ┌────▼─────┐
                    │SUBMITTED │
                    └────┬─────┘
                         │ pickup scan
                    ┌────▼─────┐
                    │PICKED_UP │
                    └────┬─────┘
                         │
                    ┌────▼────────┐
                    │ IN_TRANSIT  │◄──── CUSTOMS_CLEARED
                    └────┬────────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
         ┌────▼─────┐ ┌──▼─────┐ ┌─▼──────────┐
         │CUSTOMS   │ │ OUT_FOR│ │ DELIVERY    │
         │HELD      │ │DELIVERY│ │ ATTEMPTED   │
         └────┬─────┘ └──┬─────┘ └──────┬──────┘
              │          │              │
              └──────────┼──────────────┘
                         │
                    ┌────▼─────┐
                    │DELIVERED │ (terminal)
                    └──────────┘

       Chemins terminaux : DELIVERED ─ FAILED ─ RETURNED ─ CANCELLED
```

### 2.3 Règles de Transition

```typescript
const TRANSITIONS: Record<ShipmentStatus, ShipmentStatus[]> = {
  DRAFT:              ['VALIDATED', 'CANCELLED'],
  VALIDATED:          ['SUBMITTED', 'CANCELLED'],
  SUBMITTED:          ['PICKED_UP', 'FAILED', 'CANCELLED'],
  PICKED_UP:          ['IN_TRANSIT', 'FAILED'],
  IN_TRANSIT:         ['CUSTOMS_HELD', 'OUT_FOR_DELIVERY', 'FAILED', 'RETURNED'],
  CUSTOMS_HELD:       ['IN_TRANSIT', 'RETURNED'],
  OUT_FOR_DELIVERY:   ['DELIVERED', 'DELIVERY_ATTEMPTED', 'FAILED'],
  DELIVERY_ATTEMPTED: ['OUT_FOR_DELIVERY', 'FAILED', 'RETURNED'],
  DELIVERED:          [],  // terminal
  FAILED:             [],  // terminal
  RETURNED:           [],  // terminal
  CANCELLED:          []   // terminal
}
```

### 2.4 Tracking Event Codes (12 codes)

```typescript
enum TrackingEventCode {
  LABEL_CREATED       = 'LABEL_CREATED',
  PICKED_UP           = 'PICKED_UP',
  ARRIVED_AT_HUB      = 'ARRIVED_AT_HUB',
  DEPARTED_FROM_HUB   = 'DEPARTED_FROM_HUB',
  IN_TRANSIT          = 'IN_TRANSIT',
  CUSTOMS_HELD        = 'CUSTOMS_HELD',
  CUSTOMS_CLEARED     = 'CUSTOMS_CLEARED',
  OUT_FOR_DELIVERY    = 'OUT_FOR_DELIVERY',
  DELIVERY_ATTEMPTED  = 'DELIVERY_ATTEMPTED',
  DELIVERED           = 'DELIVERED',
  FAILED              = 'FAILED',
  RETURNED_TO_SENDER  = 'RETURNED_TO_SENDER'
}
```

---

## 3. Carrier Adapter Interface (Pluggable)

### 3.1 Interface Générique

```typescript
interface CarrierAdapter {
  // Métadonnées
  readonly code: string
  readonly name: string

  // Cycle de vie expédition
  createShipment(shipment: ShipmentInput): Promise<CarrierShipmentResponse>
  cancelShipment(trackingNumber: string): Promise<CarrierCancelResponse>
  getLabel(trackingNumber: string, format: LabelFormat): Promise<Label>

  // Tarification
  getRates(request: RateRequest): Promise<RateOffer[]>

  // Suivi
  track(trackingNumber: string): Promise<CarrierTrackingData>
  trackBatch(trackingNumbers: string[]): Promise<Map<string, CarrierTrackingData>>

  // Enlèvement
  schedulePickup(request: PickupRequest): Promise<CarrierPickupResponse>
  cancelPickup(pickupId: string): Promise<void>

  // Adresse
  validateAddress(address: Address): Promise<AddressValidationResult>

  // Connexion
  testConnection(): Promise<ConnectionTestResult>

  // Webhook (validation signature entrante)
  validateWebhookSignature(payload: string, signature: string): boolean
}
```

### 3.2 Contrat Standardisé des Réponses

Tous les adaptateurs normalisent leurs réponses dans un format interne :

```typescript
interface CarrierShipmentResponse {
  carrierTrackingNumber: string
  carrierShipmentId: string
  labelUrl?: string
  labelFormat?: LabelFormat
  trackingUrl?: string
  price: Price
  estimatedDeliveryDate?: DateTime
  rawResponse: unknown          // payload brut conservé pour debug
}

interface CarrierTrackingData {
  trackingNumber: string
  currentStatus: UnifiedTrackingCode
  events: Array<{
    code: UnifiedTrackingCode
    description: string
    location?: string
    timestamp: DateTime
    rawStatus: string           // statut brut du transporteur
  }>
  estimatedDeliveryDate?: DateTime
  rawResponse: unknown
}
```

### 3.3 Implémentations

```
CarrierAdapter (interface)
  ├── DhlAdapter          → API DHL (Express, Parcel)
  ├── FedExAdapter        → API FedEx (Priority, Economy)
  ├── UpsAdapter          → API UPS (Standard, Express Saver)
  ├── ChronopostAdapter   → API Chronopost (Chrono 13, 18)
  └── CustomAdapter       → Template pour transporteur custom
```

### 3.4 Registry (Injection Dynamique)

```typescript
class CarrierRegistry {
  private adapters: Map<string, CarrierAdapter> = new Map()

  register(code: string, adapter: CarrierAdapter): void {
    this.adapters.set(code, adapter)
  }

  get(code: string): CarrierAdapter {
    const adapter = this.adapters.get(code)
    if (!adapter) throw new CarrierNotFoundException(code)
    return adapter
  }

  getAll(): CarrierAdapter[] {
    return Array.from(this.adapters.values())
  }

  getActive(): CarrierAdapter[] {
    return this.getAll().filter(a => a.isActive())
  }
}
```

---

## 4. Status Mapping Engine

### 4.1 Architecture à 3 Niveaux

```
Statut brut transporteur (string)
         │
         ▼
┌─ Niveau 1 : Correspondance Exacte ─┐
│  "Delivered" → DELIVERED            │
│  "Shipment delivered" → DELIVERED   │
│  "In transit" → IN_TRANSIT          │
└─────────────────────────────────────┘
         │ si aucun match
         ▼
┌─ Niveau 2 : Regex Patterns ────────┐
│  /delivered/i → DELIVERED           │
│  /out for delivery/i → OUT_FOR_DEL  │
│  /customs.*held/i → CUSTOMS_HELD    │
│  /attempt.*fail/i → DELIVERY_ATTEMPT│
└─────────────────────────────────────┘
         │ si aucun match
         ▼
┌─ Niveau 3 : Fuzzy Match ───────────┐
│  Similarité > 0.8 → meilleur match  │
│  (distance de Levenshtein)          │
└─────────────────────────────────────┘
         │ si aucun match
         ▼
┌─ Fallback ─────────────────────────┐
│  log warning, marquer IN_TRANSIT   │
│  (statut par défaut sûr)           │
└─────────────────────────────────────┘
```

### 4.2 Per-Carrier Strategy

Chaque transporteur a sa propre map avec pondérations :

```typescript
interface CarrierStatusMap {
  carrierCode: string
  exactMatches: Map<string, UnifiedTrackingCode>     // Niveau 1
  regexPatterns: Array<{ pattern: RegExp; target: UnifiedTrackingCode }>  // Niveau 2
  fuzzyThreshold: number                              // Niveau 3 (défaut: 0.8)
  defaultStatus: UnifiedTrackingCode                  // Fallback
  terminalStatuses: Set<UnifiedTrackingCode>           // Statuts finaux
}
```

Exemple DHL :
```typescript
const dhlMap: CarrierStatusMap = {
  carrierCode: 'DHL',
  exactMatches: new Map([
    ['Shipment information received', 'LABEL_CREATED'],
    ['Pickup scanned', 'PICKED_UP'],
    ['Delivered', 'DELIVERED'],
    ['Shipment has been delivered', 'DELIVERED'],
    ['Shipment is on hold', 'CUSTOMS_HELD'],
  ]),
  regexPatterns: [
    { pattern: /departed from (transit|origin|destination)/i, target: 'IN_TRANSIT' },
    { pattern: /arrived at (transit|sort|destination)/i, target: 'ARRIVED_AT_HUB' },
    { pattern: /out for delivery/i, target: 'OUT_FOR_DELIVERY' },
    { pattern: /delivery attempted/i, target: 'DELIVERY_ATTEMPTED' },
    { pattern: /return to sender/i, target: 'RETURNED_TO_SENDER' },
  ],
  fuzzyThreshold: 0.8,
  defaultStatus: 'IN_TRANSIT',
  terminalStatuses: new Set(['DELIVERED', 'FAILED', 'RETURNED_TO_SENDER', 'CANCELLED']),
}
```

### 4.3 Lifecycle Validator

Vérifie qu'un événement respecte l'ordre logique du cycle de vie :

```typescript
function validateTransition(
  currentStatus: ShipmentStatus,
  newEventCode: UnifiedTrackingCode
): boolean {
  // Un événement DELIVERED est impossible avant OUT_FOR_DELIVERY
  // Un CUSTOMS_HELD n'a de sens qu'en IN_TRANSIT
  // etc.
  return TRANSITION_RULES[currentStatus]?.includes(newEventCode) ?? false
}
```

---

## 5. Workflow Engine

### 5.1 ShipmentOrchestrator

```typescript
class ShipmentOrchestrator {
  constructor(
    private carrierRegistry: CarrierRegistry,
    private shipmentRepo: ShipmentRepository,
    private eventBus: EventBus
  )

  async createShipment(input: CreateShipmentInput): Promise<Shipment> {
    // 1. Valider les données
    // 2. Choisir le transporteur via CarrierRegistry
    // 3. Appeler carrier.createShipment()
    // 4. Sauvegarder la Shipment (status = SUBMITTED)
    // 5. Publier un événement ShipmentCreated
    // 6. Retourner le résultat
  }

  async processTrackingEvent(
    trackingNumber: string,
    carrierCode: string,
    rawStatus: string
  ): Promise<TrackingResult> {
    // 1. Récupérer le mapping via StatusMappingEngine
    // 2. Valider la transition via LifecycleValidator
    // 3. Créer un TrackingEvent
    // 4. Mettre à jour le status Shipment
    // 5. Si terminal → déclencher actions post-livraison
    // 6. Publier événement (pour notifications)
  }

  async cancelShipment(id: string): Promise<Shipment> {
    // 1. Vérifier que l'annulation est autorisée (pas DELIVERED)
    // 2. Appeler carrier.cancelShipment()
    // 3. Mettre à jour status = CANCELLED
    // 4. Publier événement
  }
}
```

### 5.2 RateOrchestrator

```typescript
class RateOrchestrator {
  async getRates(request: RateRequest): Promise<RateComparison> {
    // 1. Récupérer les transporteurs actifs compatibles
    // 2. Paralléliser les appaux carrier.getRates() (Promise.all)
    // 3. Agréger + trier par prix
    // 4. Retourner le comparatif
  }
}
```

### 5.3 PickupOrchestrator

```typescript
class PickupOrchestrator {
  async schedulePickup(request: PickupRequest): Promise<Pickup> {
    // 1. Vérifier que les expéditions sont en status SUBMITTED
    // 2. Appeler carrier.schedulePickup()
    // 3. Créer et retourner le Pickup
  }
}
```

---

## 6. Event System

### 6.1 Événements Métier

```typescript
enum DomainEvent {
  SHIPMENT_CREATED        = 'shipment.created',
  SHIPMENT_SUBMITTED      = 'shipment.submitted',
  SHIPMENT_STATUS_CHANGED = 'shipment.status_changed',
  SHIPMENT_DELIVERED      = 'shipment.delivered',
  SHIPMENT_FAILED         = 'shipment.failed',
  SHIPMENT_CANCELLED      = 'shipment.cancelled',
  TRACKING_EVENT_RECEIVED = 'tracking.event_received',
  CARRIER_CONNECTED       = 'carrier.connected',
  CARRIER_DISCONNECTED    = 'carrier.disconnected',
  PICKUP_SCHEDULED        = 'pickup.scheduled',
  PICKUP_CANCELLED        = 'pickup.cancelled',
  WEBHOOK_RECEIVED        = 'webhook.received',
  RATE_REQUESTED          = 'rate.requested',
}
```

### 6.2 Event Bus

```typescript
interface EventBus {
  publish(event: DomainEvent, payload: unknown): Promise<void>
  subscribe(event: DomainEvent, handler: EventHandler): void
  unsubscribe(event: DomainEvent, handler: EventHandler): void
}

// Implémentations possibles :
// - InMemoryEventBus (développement / tests)
// - RabbitMQEventBus (production)
// - KafkaEventBus (haute volumétrie)
```

### 6.3 Handlers (Effets de Bord)

```typescript
// Notification au client (email / SMS)
eventBus.subscribe(SHIPMENT_STATUS_CHANGED, async (payload) => {
  await notificationService.notifyClient(payload.shipment, payload.newStatus)
})

// Webhook sortant vers le système client
eventBus.subscribe(SHIPMENT_DELIVERED, async (payload) => {
  await webhookService.sendWebhook(payload.clientWebhookUrl, payload)
})

// Audit log
eventBus.subscribe('*', async (payload) => {
  await auditService.log(payload)
})
```

---

## 7. Error Handling & Resilience

### 7.1 Erreurs Métier

```typescript
class CargoError extends Error {
  constructor(
    public code: string,
    message: string,
    public httpStatus: number = 500,
    public details?: unknown
  ) { super(message) }
}

class CarrierConnectionError extends CargoError {
  constructor(carrierCode: string, cause: Error) {
    super('CARRIER_CONNECTION_FAILED',
      `Failed to connect to ${carrierCode}: ${cause.message}`,
      502, { carrierCode, cause: cause.message })
  }
}

class InvalidTransitionError extends CargoError {
  constructor(shipmentId: string, from: string, to: string) {
    super('INVALID_TRANSITION',
      `Cannot transition ${shipmentId} from ${from} to ${to}`,
      409, { shipmentId, from, to })
  }
}

class CarrierNotFoundException extends CargoError {
  constructor(code: string) {
    super('CARRIER_NOT_FOUND', `Carrier ${code} not found`, 404, { carrierCode: code })
  }
}
```

### 7.2 Retry Policy (Appels Transporteurs)

```typescript
interface RetryPolicy {
  maxAttempts: number
  initialDelayMs: number
  backoffMultiplier: number       // exponentiel
  maxDelayMs: number
  retryableErrors: string[]       // ex: TIMEOUT, RATE_LIMIT, NETWORK_ERROR
  onRetry?: (attempt: number, error: Error) => void
}

const DEFAULT_RETRY_POLICY: RetryPolicy = {
  maxAttempts: 3,
  initialDelayMs: 500,
  backoffMultiplier: 2,
  maxDelayMs: 10000,
  retryableErrors: ['TIMEOUT', 'RATE_LIMIT', 'NETWORK_ERROR', 'SERVICE_UNAVAILABLE'],
}
```

### 7.3 Circuit Breaker

```typescript
class CarrierCircuitBreaker {
  // Si un transporteur échoue 5 fois en 60 secondes → OPEN
  // Pendant OPEN : les requêtes sont rejetées immédiatement (fail fast)
  // Après 30 secondes → HALF_OPEN (test)
  // Si le test réussit → CLOSED, sinon → OPEN

  state: 'CLOSED' | 'OPEN' | 'HALF_OPEN'
  failureCount: number
  lastFailureTime: DateTime
  threshold: number        // 5
  timeoutMs: number        // 30000
}
```

### 7.4 Dead Letter Queue (Événements Non Traités)

```typescript
interface DeadLetterRecord {
  originalEvent: DomainEvent
  payload: unknown
  errorMessage: string
  failedAt: DateTime
  retryCount: number
}
```

---

## 8. Service Layer (Orchestration)

```
┌─────────────────────────────────────────────────────────┐
│                      API Layer                           │
│  (REST endpoints — controllers / handlers)               │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                 Service Layer                            │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Shipment    │  │    Rate      │  │   Pickup     │  │
│  │  Orchestrator│  │  Orchestrator│  │  Orchestrator│  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │          │
└─────────┼─────────────────┼─────────────────┼──────────┘
          │                 │                 │
┌─────────▼─────────────────▼─────────────────▼──────────┐
│               Infrastructure Layer                      │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │CarrierRegistry│  │StatusMapper │  │  EventBus    │  │
│  │ + Adapters   │  │ Engine      │  │  + Handlers  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Repositories │  │ Circuit     │  │  Dead Letter │  │
│  │ (DB)         │  │ Breaker     │  │  Queue       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 9. API REST (Résumé)

| Method | Path | Service | Description |
|---|---|---|---|
| POST | `/api/v1/cargo/rates` | RateOrchestrator | Comparer les prix |
| POST | `/api/v1/cargo/shipments` | ShipmentOrchestrator | Créer expédition |
| GET | `/api/v1/cargo/shipments` | ShipmentOrchestrator | Lister |
| GET | `/api/v1/cargo/shipments/{id}` | ShipmentOrchestrator | Détail |
| GET | `/api/v1/cargo/shipments/{id}/tracking` | ShipmentOrchestrator | Suivi |
| POST | `/api/v1/cargo/shipments/{id}/cancel` | ShipmentOrchestrator | Annuler |
| POST | `/api/v1/cargo/shipments/{id}/label` | ShipmentOrchestrator | Étiquette |
| POST | `/api/v1/cargo/pickups` | PickupOrchestrator | Enlèvement |
| POST | `/api/v1/cargo/webhooks/{carrierCode}` | ShipmentOrchestrator | Webhook entrant |
| POST | `/api/v1/cargo/addresses/validate` | CarrierRegistry | Valider adresse |
| POST | `/api/v1/cargo/carriers` | CarrierRegistry | Ajouter transporteur |
| GET | `/api/v1/cargo/carriers` | CarrierRegistry | Lister |
| GET | `/api/v1/cargo/carriers/{code}` | CarrierRegistry | Détail |
| PUT | `/api/v1/cargo/carriers/{code}` | CarrierRegistry | Modifier |
| PATCH | `/api/v1/cargo/carriers/{code}/toggle` | CarrierRegistry | Activer/désactiver |
| POST | `/api/v1/cargo/carriers/{code}/test` | CarrierRegistry | Tester connexion |
| PUT | `/api/v1/cargo/carriers/{code}/credentials` | CarrierRegistry | Màj credentials |

---

## 10. Guide d'Intégration : Nouveau Transporteur

Ajouter un 5e transporteur (ex: La Poste) en 5 étapes :

### Étape 1 : Implémenter l'Adapter

```typescript
class LaPosteAdapter implements CarrierAdapter {
  code = 'LAPOSTE'
  name = 'La Poste'

  async createShipment(input: ShipmentInput): Promise<CarrierShipmentResponse> {
    // 1. Mapper ShipmentInput → format La Poste API
    // 2. Appeler l'API POST /laposte/v1/colis
    // 3. Normaliser la réponse en CarrierShipmentResponse
    // 4. Gérer les erreurs (timeout, validation, auth)
  }

  async getRates(request: RateRequest): Promise<RateOffer[]> { /* ... */ }
  async track(trackingNumber: string): Promise<CarrierTrackingData> { /* ... */ }
  // ... autres méthodes
}
```

### Étape 2 : Ajouter la Status Map

```typescript
const laPosteStatusMap: CarrierStatusMap = {
  carrierCode: 'LAPOSTE',
  exactMatches: new Map([
    ['Déposé', 'LABEL_CREATED'],
    ['Pris en charge', 'PICKED_UP'],
    ['Distribué', 'DELIVERED'],
  ]),
  regexPatterns: [
    { pattern: /en cours d'acheminement/i, target: 'IN_TRANSIT' },
    { pattern: /en livraison/i, target: 'OUT_FOR_DELIVERY' },
  ],
  fuzzyThreshold: 0.8,
  defaultStatus: 'IN_TRANSIT',
  terminalStatuses: new Set(['DELIVERED', 'FAILED', 'CANCELLED']),
}
```

### Étape 3 : Enregistrer dans le Registry

```typescript
carrierRegistry.register('LAPOSTE', new LaPosteAdapter())
statusMapper.registerMap('LAPOSTE', laPosteStatusMap)
```

### Étape 4 : Ajouter la Config & Credentials

```json
{
  "code": "LAPOSTE",
  "name": "La Poste",
  "adapterName": "LaPosteAdapter",
  "active": true,
  "credentials": {
    "authType": "API_KEY",
    "apiKey": "...",
    "endpoint": "https://api.laposte.fr/v1"
  },
  "settings": { "timeoutMs": 10000, "retryMaxAttempts": 3 }
}
```

### Étape 5 : Tester

```
POST /api/v1/cargo/carriers/LAPOSTE/test → CONNECTED
POST /api/v1/cargo/rates?carrierCodes=LAPOSTE → rates
POST /api/v1/cargo/shipments → shipment with La Poste
GET  /api/v1/cargo/shipments/{id}/tracking → events
```

---

## 11. Sécurité

### 11.1 Authentification

- JWT avec refresh token
- Rôles : `admin` (full CRUD), `operator` (expéditions + suivi), `viewer` (lecture seule)
- Rate limiting par token : 100 req/min (admin), 30 req/min (viewer)

### 11.2 Credentials Transporteurs

- Chiffrement AES-256-GCM au repos
- Déchiffré en mémoire uniquement au moment de l'appel API
- Rotation des clés via `PUT /carriers/{code}/credentials`

### 11.3 Webhooks (Sécurité)

- Signature HMAC-SHA256 validée sur chaque webhook entrant
- `validateWebhookSignature()` implémenté dans chaque adapter
- Timeout de validité : 5 minutes (anti-replay)

---

## 12. Monitoring & Observabilité

### 12.1 Métriques Clés

```
cargo_shipments_created_total      → Compteur
cargo_shipments_delivered_total    → Compteur
cargo_carrier_requests_duration_ms → Histogramme (par transporteur)
cargo_carrier_errors_total         → Compteur (par code d'erreur)
cargo_webhook_received_total       → Compteur
cargo_retry_attempts_total         → Compteur
cargo_circuit_breaker_state        → Gauge (0=CLOSED, 1=OPEN, 2=HALF_OPEN)
```

### 12.2 Logs Structurés

```typescript
// Tous les logs au format JSON structuré
{
  "timestamp": "2026-06-14T10:30:00Z",
  "level": "info" | "warn" | "error",
  "service": "cargo-service",
  "traceId": "abc-123-def",
  "action": "createShipment",
  "carrier": "DHL",
  "durationMs": 245,
  "shipmentId": "shp_xxx",
  "error": { "code": "CARRIER_CONNECTION_FAILED", "message": "..." }
}
```

---

## 13. Tests

### 13.1 Test de l'Adapter (Mock)

```typescript
// Chaque adapter a des tests unitaires avec des réponses mock
describe('DhlAdapter', () => {
  it('maps raw status "Delivered" to DELIVERED', async () => {
    const adapter = new DhlAdapter()
    const result = await adapter.track('1234567890')
    expect(result.currentStatus).toBe('DELIVERED')
  })

  it('throws CarrierConnectionError on timeout', async () => {
    const adapter = new DhlAdapter()
    await expect(adapter.createShipment(invalidInput))
      .rejects.toThrow(CarrierConnectionError)
  })
})
```

### 13.2 Test du Workflow (Intégration)

```typescript
describe('ShipmentOrchestrator', () => {
  it('rejects cancel after delivery', async () => {
    const shipment = await orchestrator.createShipment(validInput)
    await orchestrator.processTrackingEvent(shipment.id, 'DELIVERED')
    await expect(orchestrator.cancelShipment(shipment.id))
      .rejects.toThrow(InvalidTransitionError)
  })
})
```

### 13.3 Test du Status Mapping (Tous les cas)

```typescript
describe('StatusMapperEngine', () => {
  // Test pour chaque transporteur, chaque statut, chaque niveau
  it.each([
    ['DHL', 'Delivered',          'DELIVERED'],       // exact
    ['DHL', 'delivered',          'DELIVERED'],       // case-insensitive
    ['DHL', 'Out for delivery',   'OUT_FOR_DELIVERY'], // regex
    ['DHL', 'Shipped with delay', 'IN_TRANSIT'],       // fuzzy fallback
    ['FEDEX', 'At destination',   'ARRIVED_AT_HUB'],   // exact
    ['UPS', 'Customs clearance',  'CUSTOMS_CLEARED'],  // regex
  ])('maps %s status "%s" to %s', (carrier, raw, expected) => {
    expect(mapper.map(carrier, raw)).toBe(expected)
  })
})
```

---

*Document généré le 2026-06-14 — Architecture Backend Cargo Delivery Service*
