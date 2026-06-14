import type {
  DashboardStats, Shipment, RateOffer, TrackingData,
  Carrier, Pickup, WebhookLog
} from '../types'

export const mockStats: DashboardStats = {
  totalShipments: 12580,
  activeShipments: 342,
  deliveredToday: 89,
  pendingPickups: 23,
  activeCarriers: 4,
  averageTransitDays: 2.4,
  revenue: { total: 458920, currency: 'EUR' }
}

export const mockShipments: Shipment[] = [
  { id: 'shp_a1b2c3d4e5', status: 'IN_TRANSIT', statusHistory: [
    { status: 'CREATED', timestamp: '2026-06-11T10:30:00Z' },
    { status: 'PICKED_UP', timestamp: '2026-06-11T14:00:00Z' },
    { status: 'IN_TRANSIT', timestamp: '2026-06-12T08:15:00Z' }
  ], carrierCode: 'DHL', carrierName: 'DHL Express',
    carrierTrackingNumber: '1234567890', serviceCode: 'DHL_EXPRESS_WORLDWIDE',
    reference: 'ORD-2026-001234',
    sender: { company: 'TechCorp Inc', country: 'FR', city: 'Paris', zipCode: '75001' },
    recipient: { company: 'Berlin GmbH', country: 'DE', city: 'Berlin', zipCode: '10115' },
    packages: [{ reference: 'PARCEL-001', weight: 2.5, weightUnit: 'KG',
      trackingNumber: '1234567890-001' }],
    price: { total: 45.30, currency: 'EUR' },
    createdAt: '2026-06-11T10:30:00Z',
    estimatedDeliveryDate: '2026-06-13T18:00:00Z'
  },
  { id: 'shp_f6g7h8i9j0', status: 'DELIVERED', statusHistory: [
    { status: 'CREATED', timestamp: '2026-06-10T09:00:00Z' },
    { status: 'PICKED_UP', timestamp: '2026-06-10T14:30:00Z' },
    { status: 'IN_TRANSIT', timestamp: '2026-06-11T07:00:00Z' },
    { status: 'OUT_FOR_DELIVERY', timestamp: '2026-06-11T09:00:00Z' },
    { status: 'DELIVERED', timestamp: '2026-06-11T14:22:00Z' }
  ], carrierCode: 'FEDEX', carrierName: 'FedEx',
    carrierTrackingNumber: 'FEDEX-98765', serviceCode: 'FEDEX_PRIORITY',
    reference: 'ORD-2026-001235',
    sender: { company: 'TechCorp Inc', country: 'FR', city: 'Lyon', zipCode: '69001' },
    recipient: { company: 'Milano Srl', country: 'IT', city: 'Milan', zipCode: '20121' },
    packages: [{ reference: 'PARCEL-002', weight: 5.0, weightUnit: 'KG',
      trackingNumber: 'FEDEX-98765-001' }],
    price: { total: 62.00, currency: 'EUR' },
    createdAt: '2026-06-10T09:00:00Z',
    estimatedDeliveryDate: '2026-06-11T18:00:00Z'
  },
  { id: 'shp_k1l2m3n4o5', status: 'CREATED', statusHistory: [
    { status: 'CREATED', timestamp: '2026-06-12T08:00:00Z' }
  ], carrierCode: 'CHRONOPOST', carrierName: 'Chronopost',
    carrierTrackingNumber: 'CHRONO-554433', serviceCode: 'CHRONO_13',
    reference: 'ORD-2026-001236',
    sender: { company: 'TechCorp Inc', country: 'FR', city: 'Paris', zipCode: '75001' },
    recipient: { company: 'Bruxelles BV', country: 'BE', city: 'Brussels', zipCode: '1000' },
    packages: [{ reference: 'PARCEL-003', weight: 1.2, weightUnit: 'KG',
      trackingNumber: 'CHRONO-554433-001' }],
    price: { total: 18.50, currency: 'EUR' },
    createdAt: '2026-06-12T08:00:00Z',
    estimatedDeliveryDate: '2026-06-13T13:00:00Z'
  },
  { id: 'shp_p6q7r8s9t0', status: 'DELIVERED', statusHistory: [
    { status: 'CREATED', timestamp: '2026-06-09T11:00:00Z' },
    { status: 'PICKED_UP', timestamp: '2026-06-09T16:00:00Z' },
    { status: 'IN_TRANSIT', timestamp: '2026-06-10T06:00:00Z' },
    { status: 'DELIVERED', timestamp: '2026-06-10T12:00:00Z' }
  ], carrierCode: 'UPS', carrierName: 'UPS',
    carrierTrackingNumber: 'UPS-11223344', serviceCode: 'UPS_EXPRESS_SAVER',
    reference: 'ORD-2026-001237',
    sender: { company: 'TechCorp Inc', country: 'FR', city: 'Marseille', zipCode: '13001' },
    recipient: { company: 'Madrid SL', country: 'ES', city: 'Madrid', zipCode: '28001' },
    packages: [{ reference: 'PARCEL-004', weight: 3.8, weightUnit: 'KG',
      trackingNumber: 'UPS-11223344-001' }],
    price: { total: 38.75, currency: 'EUR' },
    createdAt: '2026-06-09T11:00:00Z',
    estimatedDeliveryDate: '2026-06-10T18:00:00Z'
  },
  { id: 'shp_u1v2w3x4y5', status: 'FAILED', statusHistory: [
    { status: 'CREATED', timestamp: '2026-06-10T15:00:00Z' },
    { status: 'PICKED_UP', timestamp: '2026-06-11T09:00:00Z' },
    { status: 'FAILED', timestamp: '2026-06-11T11:30:00Z' }
  ], carrierCode: 'DHL', carrierName: 'DHL Express',
    carrierTrackingNumber: 'DHL-998877', serviceCode: 'DHL_EXPRESS_12',
    reference: 'ORD-2026-001238',
    sender: { company: 'TechCorp Inc', country: 'FR', city: 'Paris', zipCode: '75001' },
    recipient: { company: 'Amsterdam NV', country: 'NL', city: 'Amsterdam', zipCode: '1012' },
    packages: [{ reference: 'PARCEL-005', weight: 10.0, weightUnit: 'KG',
      trackingNumber: 'DHL-998877-001' }],
    price: { total: 72.00, currency: 'EUR' },
    createdAt: '2026-06-10T15:00:00Z'
  }
]

export const mockRates: RateOffer[] = [
  { carrierCode: 'DHL', carrierName: 'DHL Express', serviceCode: 'DHL_EXPRESS_WORLDWIDE',
    serviceName: 'Express Worldwide', totalPrice: 45.30, currency: 'EUR',
    estimatedTransitDays: 2, estimatedDeliveryDate: '2026-06-13', guaranteed: true,
    breakdown: [
      { type: 'BASE', label: 'Transport', amount: 38.00 },
      { type: 'FUEL', label: 'Fuel surcharge', amount: 5.30 },
      { type: 'INSURANCE', label: 'Insurance', amount: 2.00 }
    ]
  },
  { carrierCode: 'DHL', carrierName: 'DHL Express', serviceCode: 'DHL_EXPRESS_12',
    serviceName: 'Express 12:00', totalPrice: 55.00, currency: 'EUR',
    estimatedTransitDays: 1, estimatedDeliveryDate: '2026-06-12', guaranteed: true,
    breakdown: [
      { type: 'BASE', label: 'Transport', amount: 47.00 },
      { type: 'FUEL', label: 'Fuel surcharge', amount: 6.00 },
      { type: 'INSURANCE', label: 'Insurance', amount: 2.00 }
    ]
  },
  { carrierCode: 'FEDEX', carrierName: 'FedEx', serviceCode: 'FEDEX_PRIORITY',
    serviceName: 'FedEx Priority', totalPrice: 48.50, currency: 'EUR',
    estimatedTransitDays: 1, estimatedDeliveryDate: '2026-06-12', guaranteed: true,
    breakdown: [
      { type: 'BASE', label: 'Transport', amount: 41.00 },
      { type: 'FUEL', label: 'Fuel surcharge', amount: 5.50 },
      { type: 'INSURANCE', label: 'Insurance', amount: 2.00 }
    ]
  },
  { carrierCode: 'CHRONOPOST', carrierName: 'Chronopost', serviceCode: 'CHRONO_13',
    serviceName: 'Chrono 13h', totalPrice: 18.50, currency: 'EUR',
    estimatedTransitDays: 1, estimatedDeliveryDate: '2026-06-12', guaranteed: false,
    breakdown: [
      { type: 'BASE', label: 'Transport', amount: 16.00 },
      { type: 'FUEL', label: 'Fuel surcharge', amount: 2.50 }
    ]
  },
  { carrierCode: 'UPS', carrierName: 'UPS', serviceCode: 'UPS_EXPRESS_SAVER',
    serviceName: 'UPS Express Saver', totalPrice: 52.20, currency: 'EUR',
    estimatedTransitDays: 2, estimatedDeliveryDate: '2026-06-13', guaranteed: true,
    breakdown: [
      { type: 'BASE', label: 'Transport', amount: 44.00 },
      { type: 'FUEL', label: 'Fuel surcharge', amount: 5.70 },
      { type: 'INSURANCE', label: 'Insurance', amount: 2.50 }
    ]
  }
]

export const mockTracking: TrackingData = {
  shipmentId: 'shp_a1b2c3d4e5',
  carrierCode: 'DHL',
  carrierTrackingNumber: '1234567890',
  currentStatus: { code: 'IN_TRANSIT', label: 'In transit', location: 'Frankfurt, Germany', timestamp: '2026-06-12T08:15:00Z' },
  estimatedDeliveryDate: '2026-06-13T18:00:00Z',
  events: [
    { eventId: 'evt_001', code: 'LABEL_CREATED', label: 'Label created', description: 'Shipping label generated', location: 'Paris, France', timestamp: '2026-06-11T10:30:00Z', carrierRawStatus: 'Shipment information received' },
    { eventId: 'evt_002', code: 'PICKED_UP', label: 'Parcel collected', description: 'Parcel picked up by carrier', location: 'Paris, France', timestamp: '2026-06-11T14:00:00Z', carrierRawStatus: 'Pickup scanned' },
    { eventId: 'evt_003', code: 'ARRIVED_AT_HUB', label: 'Arrived at hub', description: 'Arrived at Paris sorting center', location: 'Paris, France', timestamp: '2026-06-11T16:30:00Z', carrierRawStatus: 'Arrived at sort facility' },
    { eventId: 'evt_004', code: 'DEPARTED_FROM_HUB', label: 'Departed from hub', description: 'Departed from Paris hub', location: 'Paris, France', timestamp: '2026-06-11T22:00:00Z', carrierRawStatus: 'Departed from sort facility' },
    { eventId: 'evt_005', code: 'IN_TRANSIT', label: 'In transit', description: 'In transit to Frankfurt hub', location: 'Frankfurt, Germany', timestamp: '2026-06-12T08:15:00Z', carrierRawStatus: 'Departed from transit hub' }
  ],
  milestones: { created: '2026-06-11T10:30:00Z', pickedUp: '2026-06-11T14:00:00Z', inTransit: '2026-06-12T08:15:00Z', outForDelivery: null, delivered: null }
}

export const mockCarriers: Carrier[] = [
  { code: 'DHL', name: 'DHL Express', adapterName: 'DhlAdapter', active: true, status: 'CONNECTED', lastTestedAt: '2026-06-10T08:00:00Z', logoUrl: 'https://cdn.example.com/carriers/dhl.svg', services: [
    { code: 'DHL_EXPRESS_WORLDWIDE', name: 'Express Worldwide', description: 'International express delivery', maxWeight: 70, maxWeightUnit: 'KG', zones: ['WORLDWIDE'], transitDays: 2, features: ['SIGNATURE', 'INSURANCE', 'SATURDAY'], active: true },
    { code: 'DHL_EXPRESS_12', name: 'Express 12:00', description: 'Delivery before noon', maxWeight: 30, maxWeightUnit: 'KG', zones: ['EU'], transitDays: 1, features: ['SIGNATURE', 'INSURANCE'], active: true }
  ], capabilities: { labelFormats: ['PDF', 'ZPL', 'PNG'], features: ['RATES', 'TRACKING', 'SIGNATURE', 'INSURANCE', 'SATURDAY', 'PICKUP'], labelSizes: ['A6', 'A5', '4x6'], requiresSignature: true, supportsSaturday: true, supportsInsurance: true, supportsPickup: true } },
  { code: 'FEDEX', name: 'FedEx', adapterName: 'FedExAdapter', active: true, status: 'CONNECTED', lastTestedAt: '2026-06-09T14:00:00Z', logoUrl: 'https://cdn.example.com/carriers/fedex.svg', services: [
    { code: 'FEDEX_PRIORITY', name: 'FedEx Priority', description: 'Time-definite delivery', maxWeight: 68, maxWeightUnit: 'KG', zones: ['WORLDWIDE'], transitDays: 1, features: ['SIGNATURE', 'INSURANCE', 'SATURDAY'], active: true },
    { code: 'FEDEX_ECONOMY', name: 'FedEx Economy', description: 'Cost-effective delivery', maxWeight: 68, maxWeightUnit: 'KG', zones: ['WORLDWIDE'], transitDays: 3, features: ['TRACKING'], active: true }
  ], capabilities: { labelFormats: ['PDF', 'ZPL'], features: ['RATES', 'TRACKING', 'SIGNATURE', 'INSURANCE', 'SATURDAY'], requiresSignature: true, supportsSaturday: true, supportsInsurance: true, supportsPickup: false } },
  { code: 'CHRONOPOST', name: 'Chronopost', adapterName: 'ChronopostAdapter', active: true, status: 'PENDING_TEST', services: [
    { code: 'CHRONO_13', name: 'Chrono 13h', description: 'Delivery before 1pm next day', maxWeight: 30, maxWeightUnit: 'KG', zones: ['FR', 'MC', 'AD'], transitDays: 1, features: ['SIGNATURE', 'INSURANCE'], active: true },
    { code: 'CHRONO_18', name: 'Chrono 18h', description: 'Delivery before 6pm next day', maxWeight: 30, maxWeightUnit: 'KG', zones: ['FR', 'MC'], transitDays: 1, features: ['SIGNATURE'], active: true }
  ], capabilities: { labelFormats: ['PDF', 'ZPL'], features: ['RATES', 'TRACKING', 'SIGNATURE', 'INSURANCE', 'PICKUP'], labelSizes: ['A6', 'A5'], requiresSignature: true, supportsSaturday: true, supportsInsurance: true, supportsPickup: true } },
  { code: 'UPS', name: 'UPS', adapterName: 'UpsAdapter', active: false, status: 'DISCONNECTED', services: [
    { code: 'UPS_EXPRESS_SAVER', name: 'UPS Express Saver', description: 'Express delivery by end of day', maxWeight: 70, maxWeightUnit: 'KG', zones: ['WORLDWIDE'], transitDays: 2, features: ['SIGNATURE', 'INSURANCE'], active: true }
  ], capabilities: { labelFormats: ['PDF', 'ZPL', 'PNG'], features: ['RATES', 'TRACKING', 'SIGNATURE', 'INSURANCE'], requiresSignature: true, supportsSaturday: false, supportsInsurance: true, supportsPickup: false } }
]

export const mockPickups: Pickup[] = [
  { id: 'pck_001a2b3c', carrierCode: 'DHL', carrierPickupId: 'DHL-PICKUP-98765', status: 'CONFIRMED', pickupDate: '2026-06-12', readyTime: '09:00', closeTime: '17:00', confirmationNumber: 'CONF-ABC-123', location: { company: 'TechCorp Inc', country: 'FR', city: 'Paris', address: '12 Rue de Rivoli' }, instructions: 'Ring at reception', shipmentIds: ['shp_a1b2c3d4e5'], totalPackages: 1, totalWeight: 2.5, createdAt: '2026-06-11T11:00:00Z' },
  { id: 'pck_002d3e4f', carrierCode: 'FEDEX', carrierPickupId: 'FEDEX-PICKUP-44332', status: 'SCHEDULED', pickupDate: '2026-06-13', readyTime: '14:00', closeTime: '18:00', location: { company: 'TechCorp Inc', country: 'FR', city: 'Lyon', address: '45 Rue de la République' }, shipmentIds: ['shp_f6g7h8i9j0'], totalPackages: 2, totalWeight: 8.0, createdAt: '2026-06-11T14:30:00Z' },
  { id: 'pck_003g5h6i7', carrierCode: 'CHRONOPOST', status: 'PENDING', pickupDate: '2026-06-14', readyTime: '08:00', closeTime: '12:00', location: { company: 'TechCorp Inc', country: 'FR', city: 'Paris', address: '12 Rue de Rivoli' }, shipmentIds: ['shp_k1l2m3n4o5'], totalPackages: 1, totalWeight: 1.2, createdAt: '2026-06-12T08:30:00Z' }
]

export const mockWebhookLogs: WebhookLog[] = [
  { id: 'wh_001', carrierCode: 'DHL', eventType: 'DELIVERED', receivedAt: '2026-06-11T14:22:05Z', shipmentId: 'shp_f6g7h8i9j0', processed: true },
  { id: 'wh_002', carrierCode: 'DHL', eventType: 'IN_TRANSIT', receivedAt: '2026-06-12T08:15:10Z', shipmentId: 'shp_a1b2c3d4e5', processed: true },
  { id: 'wh_003', carrierCode: 'FEDEX', eventType: 'PICKED_UP', receivedAt: '2026-06-11T09:30:00Z', shipmentId: 'shp_u1v2w3x4y5', processed: true },
  { id: 'wh_004', carrierCode: 'FEDEX', eventType: 'FAILED', receivedAt: '2026-06-11T11:30:00Z', shipmentId: 'shp_u1v2w3x4y5', processed: true },
  { id: 'wh_005', carrierCode: 'UPS', eventType: 'DELIVERED', receivedAt: '2026-06-10T12:00:00Z', shipmentId: 'shp_p6q7r8s9t0', processed: true }
]


