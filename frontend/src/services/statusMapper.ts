/**
 * ──────────────────────────────────────────────────────────────────────
 *  STATUS MAPPER — Carrier Status → Unified Status Engine
 * ──────────────────────────────────────────────────────────────────────
 *  Chaque transporteur a son propre vocabulaire de statuts (ex: DHL dit
 *  "Shipment information received", UPS dit "Order Processed", Chronopost
 *  dit "Prise en charge"). Ce moteur normalise tout vers notre référentiel
 *  interne commun, et permet la conversion inverse.
 * ──────────────────────────────────────────────────────────────────────
 */

/* ─── 1. Référentiel Interne Unifié ────────────────────────────────── */

/** Statuts agrégés d'une expédition (Shipment.status) */
export type UnifiedShipmentStatus =
  | 'CREATED'
  | 'VALIDATED'
  | 'PICKED_UP'
  | 'IN_TRANSIT'
  | 'OUT_FOR_DELIVERY'
  | 'DELIVERED'
  | 'FAILED'
  | 'CANCELLED'

/** Codes d'événements de tracking (TrackingEvent.code) */
export type UnifiedTrackingCode =
  | 'LABEL_CREATED'
  | 'PICKED_UP'
  | 'IN_TRANSIT'
  | 'ARRIVED_AT_HUB'
  | 'DEPARTED_FROM_HUB'
  | 'OUT_FOR_DELIVERY'
  | 'DELIVERED'
  | 'DELIVERY_ATTEMPTED'
  | 'FAILED'
  | 'RETURNED_TO_SENDER'
  | 'CUSTOMS_HELD'
  | 'CUSTOMS_CLEARED'

/* ─── 2. Définition d'une map de statuts par transporteur ──────────── */

/**
 * Chaque transporteur fournit une map qui associe ses statuts bruts
 * (exacts ou par pattern regex) à nos codes internes.
 */
export interface CarrierStatusDefinition {
  /** Code du transporteur */
  carrierCode: string
  /** Map: statut brut du transporteur → code interne unifié */
  map: Record<string, UnifiedTrackingCode>
  /** Map inverse: code interne → libellé lisible (pour l'affichage) */
  labels: Partial<Record<UnifiedTrackingCode, string>>
  /** Règles de correspondance "fuzzy" (regex) pour les statuts imprévisibles */
  patterns?: Array<{ regex: RegExp; mapTo: UnifiedTrackingCode }>
}

/* ─── 3. Chronologie / lifecycle ────────────────────────────────────── */

/**
 * Ordre de progression dans le cycle de vie d'une expédition.
 * Permet de savoir si un événement est une avancée, un recul, ou une
 * anomalie.
 */
export const SHIPMENT_LIFECYCLE_ORDER: UnifiedTrackingCode[] = [
  'LABEL_CREATED',
  'PICKED_UP',
  'IN_TRANSIT',
  'ARRIVED_AT_HUB',
  'DEPARTED_FROM_HUB',
  'OUT_FOR_DELIVERY',
  'DELIVERY_ATTEMPTED',   // boucle de rattrapage
  'OUT_FOR_DELIVERY',      // retour possible après échec
  'DELIVERED',
]

/** Codes terminaux : une fois atteints, l'expédition ne progresse plus */
export const TERMINAL_STATUSES: UnifiedTrackingCode[] = [
  'DELIVERED',
  'FAILED',
  'RETURNED_TO_SENDER',
  'CANCELLED',
]

/** Statuts "en souffrance" qui nécessitent une action humaine */
export const BLOCKING_STATUSES: UnifiedTrackingCode[] = [
  'CUSTOMS_HELD',
  'DELIVERY_ATTEMPTED',
  'FAILED',
  'RETURNED_TO_SENDER',
]

/* ─── 4. Maps par transporteur ──────────────────────────────────────── */

export const DHL_STATUS_MAP: CarrierStatusDefinition = {
  carrierCode: 'DHL',
  map: {
    'Shipment information received':       'LABEL_CREATED',
    'Shipment information received online':'LABEL_CREATED',
    'Pickup scanned':                      'PICKED_UP',
    'Parcel collected':                    'PICKED_UP',
    'Departed from sort facility':         'DEPARTED_FROM_HUB',
    'Departed from transit hub':           'IN_TRANSIT',
    'Arrived at sort facility':            'ARRIVED_AT_HUB',
    'Arrived at delivery location':        'OUT_FOR_DELIVERY',
    'With delivery courier':               'OUT_FOR_DELIVERY',
    'Delivery attempted':                  'DELIVERY_ATTEMPTED',
    'Delivered':                           'DELIVERED',
    'Shipment on hold':                    'FAILED',
    'Shipment returned':                   'RETURNED_TO_SENDER',
    'Returned to sender':                  'RETURNED_TO_SENDER',
    'Customs clearance delay':             'CUSTOMS_HELD',
    'Clearance processing complete':       'CUSTOMS_CLEARED',
  },
  labels: {
    LABEL_CREATED:      'Label created',
    PICKED_UP:          'Collected',
    IN_TRANSIT:         'In transit',
    ARRIVED_AT_HUB:     'Arrived at facility',
    DEPARTED_FROM_HUB:  'Departed from facility',
    OUT_FOR_DELIVERY:   'Out for delivery',
    DELIVERED:          'Delivered',
    DELIVERY_ATTEMPTED: 'Delivery attempted',
    FAILED:             'On hold — contact DHL',
    RETURNED_TO_SENDER: 'Returned to sender',
    CUSTOMS_HELD:       'Customs delay',
    CUSTOMS_CLEARED:    'Customs cleared',
  },
  patterns: [
    { regex: /customs|custom|douane|gümrük/i, mapTo: 'CUSTOMS_HELD' },
    { regex: /return|iade/i, mapTo: 'RETURNED_TO_SENDER' },
    { regex: /attempt|deneme/i, mapTo: 'DELIVERY_ATTEMPTED' },
    { regex: /hold|bekleme/i, mapTo: 'FAILED' },
  ],
}

export const FEDEX_STATUS_MAP: CarrierStatusDefinition = {
  carrierCode: 'FEDEX',
  map: {
    'Package information transmitted':     'LABEL_CREATED',
    'Shipment information sent':           'LABEL_CREATED',
    'Picked up':                           'PICKED_UP',
    'Package received at FedEx location':  'ARRIVED_AT_HUB',
    'Departed from FedEx location':        'DEPARTED_FROM_HUB',
    'In transit':                          'IN_TRANSIT',
    'At local FedEx facility':             'ARRIVED_AT_HUB',
    'On FedEx vehicle for delivery':       'OUT_FOR_DELIVERY',
    'Delivery attempted':                  'DELIVERY_ATTEMPTED',
    'Delivered':                           'DELIVERED',
    'Package not delivered':               'FAILED',
    'Returned to sender':                  'RETURNED_TO_SENDER',
    'International shipment release':      'CUSTOMS_CLEARED',
    'Clearance delay':                     'CUSTOMS_HELD',
    'Customer refused':                    'FAILED',
  },
  labels: {
    LABEL_CREATED:      'Information transmitted',
    PICKED_UP:          'Picked up',
    IN_TRANSIT:         'In transit',
    ARRIVED_AT_HUB:     'Arrived at FedEx facility',
    DEPARTED_FROM_HUB:  'Departed facility',
    OUT_FOR_DELIVERY:   'On vehicle for delivery',
    DELIVERED:          'Delivered',
    DELIVERY_ATTEMPTED: 'Delivery attempted',
    FAILED:             'Delivery exception',
    RETURNED_TO_SENDER: 'Returned',
    CUSTOMS_HELD:       'Customs delay',
    CUSTOMS_CLEARED:    'Customs released',
  },
  patterns: [
    { regex: /clearance|customs|gümrük/i, mapTo: 'CUSTOMS_HELD' },
    { regex: /vehicle|delivery.*out/i, mapTo: 'OUT_FOR_DELIVERY' },
    { regex: /exception|error|hata/i, mapTo: 'FAILED' },
  ],
}

export const UPS_STATUS_MAP: CarrierStatusDefinition = {
  carrierCode: 'UPS',
  map: {
    'Order Processed':                     'LABEL_CREATED',
    'Shipper created a label':             'LABEL_CREATED',
    'Pickup Scan':                         'PICKED_UP',
    'Origin Scan':                         'PICKED_UP',
    'Departed from Facility':              'DEPARTED_FROM_HUB',
    'Arrived at Facility':                 'ARRIVED_AT_HUB',
    'Warehouse Scan':                      'ARRIVED_AT_HUB',
    'Destination Scan':                    'IN_TRANSIT',
    'Out for Delivery':                    'OUT_FOR_DELIVERY',
    'Out for Delivery Today':              'OUT_FOR_DELIVERY',
    'Delivery Attempted':                  'DELIVERY_ATTEMPTED',
    'Delivered':                           'DELIVERED',
    'Return to Sender':                    'RETURNED_TO_SENDER',
    'Customer refused shipment':           'FAILED',
    'Damaged':                             'FAILED',
    'Lost':                                'FAILED',
    'Clearance in Progress':               'CUSTOMS_HELD',
    'Clearance Completed':                 'CUSTOMS_CLEARED',
    'Hold for clearance':                  'CUSTOMS_HELD',
  },
  labels: {
    LABEL_CREATED:      'Order processed',
    PICKED_UP:          'Origin scan',
    IN_TRANSIT:         'Destination scan',
    ARRIVED_AT_HUB:     'Arrived at facility',
    DEPARTED_FROM_HUB:  'Departed facility',
    OUT_FOR_DELIVERY:   'Out for delivery',
    DELIVERED:          'Delivered',
    DELIVERY_ATTEMPTED: 'Delivery attempted',
    FAILED:             'Exception',
    RETURNED_TO_SENDER: 'Returned to sender',
    CUSTOMS_HELD:       'Customs in progress',
    CUSTOMS_CLEARED:    'Customs completed',
  },
  patterns: [
    { regex: /scan|tarama/i, mapTo: 'ARRIVED_AT_HUB' },
    { regex: /clearance|gümrük/i, mapTo: 'CUSTOMS_HELD' },
    { regex: /delivery.*attempt|teslimat.*deneme/i, mapTo: 'DELIVERY_ATTEMPTED' },
  ],
}

export const CHRONOPOST_STATUS_MAP: CarrierStatusDefinition = {
  carrierCode: 'CHRONOPOST',
  map: {
    'Prise en charge':                     'PICKED_UP',
    'Prise en charge du colis':            'PICKED_UP',
    'Colis pris en charge':                'PICKED_UP',
    'Tri en cours':                        'ARRIVED_AT_HUB',
    'Tri effectué':                        'DEPARTED_FROM_HUB',
    'En cours d\'acheminement':             'IN_TRANSIT',
    'En livraison':                        'OUT_FOR_DELIVERY',
    'En cours de livraison':               'OUT_FOR_DELIVERY',
    'Livraison échouée':                   'DELIVERY_ATTEMPTED',
    'Livré':                                'DELIVERED',
    'Colis livré':                          'DELIVERED',
    'Retour à l\'expéditeur':               'RETURNED_TO_SENDER',
    'Retour expéditeur':                    'RETURNED_TO_SENDER',
    'Expéditeur refusé':                    'FAILED',
    'Colis refusé':                         'FAILED',
    'Douane':                               'CUSTOMS_HELD',
    'Dédouanement en cours':               'CUSTOMS_HELD',
    'Dédouané':                             'CUSTOMS_CLEARED',
  },
  labels: {
    LABEL_CREATED:      'Étiquette créée',
    PICKED_UP:          'Prise en charge',
    IN_TRANSIT:         'En acheminement',
    ARRIVED_AT_HUB:     'Tri en cours',
    DEPARTED_FROM_HUB:  'Tri effectué',
    OUT_FOR_DELIVERY:   'En livraison',
    DELIVERED:          'Livré',
    DELIVERY_ATTEMPTED: 'Livraison échouée',
    FAILED:             'Échec',
    RETURNED_TO_SENDER: 'Retour expéditeur',
    CUSTOMS_HELD:       'Douane',
    CUSTOMS_CLEARED:    'Dédouané',
  },
  patterns: [
    { regex: /douane|gümrük|customs/i, mapTo: 'CUSTOMS_HELD' },
    { regex: /échec|echec|refus|başarısız/i, mapTo: 'FAILED' },
    { regex: /retour|iade/i, mapTo: 'RETURNED_TO_SENDER' },
    { regex: /livraison.*échou|teslimat.*başarısız/i, mapTo: 'DELIVERY_ATTEMPTED' },
  ],
}

/* ─── 5. Registry global de tous les transporteurs ──────────────────── */

export const ALL_CARRIER_STATUS_MAPS: Record<string, CarrierStatusDefinition> = {
  DHL: DHL_STATUS_MAP,
  FEDEX: FEDEX_STATUS_MAP,
  UPS: UPS_STATUS_MAP,
  CHRONOPOST: CHRONOPOST_STATUS_MAP,
}

/* ─── 6. Fonctions de mapping ──────────────────────────────────────── */

/**
 * Convertit un statut brut d'un transporteur en code interne unifié.
 *
 * @param carrierCode - "DHL", "FEDEX", "UPS", "CHRONOPOST"
 * @param rawStatus   - Statut brut tel que reçu du transporteur
 * @returns Code interne unifié, ou 'IN_TRANSIT' par défaut si inconnu
 */
export function mapCarrierStatusToUnified(
  carrierCode: string,
  rawStatus: string
): UnifiedTrackingCode {
  const def = ALL_CARRIER_STATUS_MAPS[carrierCode?.toUpperCase()]
  if (!def) return 'IN_TRANSIT'

  // 1. Exact match
  const exact = def.map[rawStatus]
  if (exact) return exact

  // 2. Pattern (regex) match
  if (def.patterns) {
    for (const p of def.patterns) {
      if (p.regex.test(rawStatus)) return p.mapTo
    }
  }

  // 3. Fuzzy match (case-insensitive partial)
  const lower = rawStatus.toLowerCase()
  for (const [key, mapped] of Object.entries(def.map)) {
    if (lower.includes(key.toLowerCase())) return mapped
  }

  return 'IN_TRANSIT'
}

/**
 * Convertit un code interne unifié en libellé lisible pour un transporteur donné.
 *
 * @param carrierCode - "DHL", "FEDEX", ...
 * @param unifiedCode - Code interne (ex: 'PICKED_UP')
 * @param fallbackLang - Langue de secours si le transporteur n'a pas de libellé
 */
export function mapUnifiedToLabel(
  carrierCode: string,
  unifiedCode: UnifiedTrackingCode,
  fallbackLang: 'en' | 'fr' = 'en'
): string {
  const def = ALL_CARRIER_STATUS_MAPS[carrierCode?.toUpperCase()]
  if (def?.labels?.[unifiedCode]) return def.labels[unifiedCode]!

  // Fallback générique
  const fallback: Record<string, Record<string, string>> = {
    en: {
      LABEL_CREATED: 'Label created', PICKED_UP: 'Picked up',
      IN_TRANSIT: 'In transit', ARRIVED_AT_HUB: 'Arrived at hub',
      DEPARTED_FROM_HUB: 'Departed from hub', OUT_FOR_DELIVERY: 'Out for delivery',
      DELIVERED: 'Delivered', DELIVERY_ATTEMPTED: 'Delivery attempted',
      FAILED: 'Failed', RETURNED_TO_SENDER: 'Returned to sender',
      CUSTOMS_HELD: 'Customs held', CUSTOMS_CLEARED: 'Customs cleared',
      CANCELLED: 'Cancelled', CREATED: 'Created', VALIDATED: 'Validated',
    },
    fr: {
      LABEL_CREATED: 'Étiquette créée', PICKED_UP: 'Récupéré',
      IN_TRANSIT: 'En transit', ARRIVED_AT_HUB: 'Arrivé au hub',
      DEPARTED_FROM_HUB: 'Parti du hub', OUT_FOR_DELIVERY: 'En livraison',
      DELIVERED: 'Livré', DELIVERY_ATTEMPTED: 'Livraison échouée',
      FAILED: 'Échec', RETURNED_TO_SENDER: 'Retour expéditeur',
      CUSTOMS_HELD: 'Retenu en douane', CUSTOMS_CLEARED: 'Dédouané',
      CANCELLED: 'Annulé', CREATED: 'Créé', VALIDATED: 'Validé',
    },
  }
  return fallback[fallbackLang]?.[unifiedCode] || unifiedCode.replace(/_/g, ' ')
}

/**
 * Convertit un l'historique brut d'un transporteur en événements internes.
 *
 * @param carrierCode - Code du transporteur
 * @param rawEvents   - Tableau d'événements bruts [{status, timestamp, location}]
 * @returns Tableau d'événements normalisés
 */
export function normalizeTrackingEvents(
  carrierCode: string,
  rawEvents: Array<{ status: string; timestamp: string; location?: string }>
): Array<{
  eventId: string; code: UnifiedTrackingCode; label: string
  description?: string; location: string; timestamp: string
  carrierRawStatus: string
}> {
  return rawEvents.map((evt, i) => {
    const code = mapCarrierStatusToUnified(carrierCode, evt.status)
    const label = mapUnifiedToLabel(carrierCode, code, 'en')
    return {
      eventId: `evt_${i.toString().padStart(3, '0')}`,
      code,
      label,
      location: evt.location || 'Unknown',
      timestamp: evt.timestamp,
      carrierRawStatus: evt.status,
    }
  })
}

/**
 * Détermine le statut agrégé d'une expédition à partir de ses événements.
 * Remonte le long du lifecycle pour trouver le statut le plus avancé.
 */
export function aggregateShipmentStatus(
  events: UnifiedTrackingCode[]
): UnifiedShipmentStatus {
  if (events.length === 0) return 'CREATED'

  // Dernier événement = statut actuel
  const last = events[events.length - 1]

  // Mapping code tracking → statut agrégé
  const map: Record<UnifiedTrackingCode, UnifiedShipmentStatus> = {
    LABEL_CREATED: 'VALIDATED',
    PICKED_UP: 'PICKED_UP',
    IN_TRANSIT: 'IN_TRANSIT',
    ARRIVED_AT_HUB: 'IN_TRANSIT',
    DEPARTED_FROM_HUB: 'IN_TRANSIT',
    OUT_FOR_DELIVERY: 'OUT_FOR_DELIVERY',
    DELIVERED: 'DELIVERED',
    DELIVERY_ATTEMPTED: 'OUT_FOR_DELIVERY',
    FAILED: 'FAILED',
    RETURNED_TO_SENDER: 'FAILED',
    CUSTOMS_HELD: 'IN_TRANSIT',
    CUSTOMS_CLEARED: 'IN_TRANSIT',
    CANCELLED: 'CANCELLED',
  }

  return map[last] || 'IN_TRANSIT'
}

/**
 * Vérifie si un statut est terminal (plus d'évolution possible).
 */
export function isTerminal(status: UnifiedTrackingCode | UnifiedShipmentStatus): boolean {
  return TERMINAL_STATUSES.includes(status as UnifiedTrackingCode) ||
    ['DELIVERED', 'FAILED', 'CANCELLED'].includes(status)
}

/**
 * Vérifie si un événement est "bloquant" (nécessite une action).
 */
export function isBlocking(code: UnifiedTrackingCode): boolean {
  return BLOCKING_STATUSES.includes(code)
}

/**
 * Calcule les milestones à partir d'événements normalisés.
 */
export function buildMilestones(
  events: Array<{ code: UnifiedTrackingCode; timestamp: string }>
): Record<string, string | null> {
  const milestones: Record<string, string | null> = {
    created: null, pickedUp: null, inTransit: null,
    outForDelivery: null, delivered: null, failed: null,
  }

  for (const evt of events) {
    switch (evt.code) {
      case 'LABEL_CREATED': milestones.created ??= evt.timestamp; break
      case 'PICKED_UP': milestones.pickedUp ??= evt.timestamp; break
      case 'IN_TRANSIT': case 'ARRIVED_AT_HUB': case 'DEPARTED_FROM_HUB':
        milestones.inTransit ??= evt.timestamp; break
      case 'OUT_FOR_DELIVERY': milestones.outForDelivery ??= evt.timestamp; break
      case 'DELIVERED': milestones.delivered ??= evt.timestamp; break
      case 'FAILED': case 'RETURNED_TO_SENDER': milestones.failed ??= evt.timestamp; break
    }
  }

  return milestones
}
