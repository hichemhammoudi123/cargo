export type ShipmentStatus =
  | 'CREATED' | 'VALIDATED' | 'PICKED_UP' | 'IN_TRANSIT'
  | 'OUT_FOR_DELIVERY' | 'DELIVERED' | 'FAILED' | 'CANCELLED'

export type TrackingEventCode =
  | 'LABEL_CREATED' | 'PICKED_UP' | 'IN_TRANSIT' | 'ARRIVED_AT_HUB'
  | 'DEPARTED_FROM_HUB' | 'OUT_FOR_DELIVERY' | 'DELIVERED'
  | 'DELIVERY_ATTEMPTED' | 'FAILED' | 'RETURNED_TO_SENDER'
  | 'CUSTOMS_HELD' | 'CUSTOMS_CLEARED'

export type CarrierStatus = 'PENDING_TEST' | 'CONNECTED' | 'DISCONNECTED' | 'ERROR'

export interface Address {
  company?: string; contactName?: string; email?: string; phone?: string
  country: string; zipCode: string; city: string; address: string; address2?: string
}

export interface Package {
  reference: string; description?: string; weight: number; weightUnit: string
  length?: number; width?: number; height?: number; dimUnit?: string
  declaredValue?: number; declaredCurrency?: string
  containsDangerousGoods?: boolean; trackingNumber?: string
}

export interface PriceBreakdown {
  type: string; label: string; amount: number
}

export interface Shipment {
  id: string; status: ShipmentStatus; statusHistory: { status: string; timestamp: string }[]
  carrierCode: string; carrierName?: string; carrierTrackingNumber?: string
  carrierShipmentId?: string; serviceCode?: string
  reference: string; labelUrl?: string; labelFormat?: string; trackingUrl?: string
  sender: Partial<Address>; recipient: Partial<Address>; packages: Package[]
  price: { total: number; currency: string; breakdown?: PriceBreakdown[] }
  insurance?: { amount: number; currency: string }
  signatureRequired?: boolean; estimatedDeliveryDate?: string
  createdAt: string; updatedAt?: string
}

export interface RateOffer {
  carrierCode: string; carrierName: string; serviceCode: string; serviceName: string
  totalPrice: number; currency: string; estimatedTransitDays: number
  estimatedDeliveryDate: string; guaranteed: boolean
  breakdown: PriceBreakdown[]
}

export interface TrackingEvent {
  eventId: string; code: TrackingEventCode; label: string; description?: string
  location: string; timestamp: string; carrierRawStatus?: string
  signedBy?: string; deliveryPhotoUrl?: string
}

export interface TrackingData {
  shipmentId: string; carrierCode: string; carrierTrackingNumber: string
  currentStatus: { code: string; label: string; location: string; timestamp: string }
  estimatedDeliveryDate?: string; events: TrackingEvent[]
  milestones: Record<string, string | null>
}

export interface CarrierService {
  code: string; name: string; description?: string
  maxWeight?: number; maxWeightUnit?: string
  zones?: string[]; transitDays?: number; features?: string[]
  active: boolean
}

export interface CarrierCapabilities {
  labelFormats: string[]; features: string[]; labelSizes?: string[]
  requiresSignature?: boolean; supportsSaturday?: boolean
  supportsInsurance?: boolean; supportsPickup?: boolean
}

export interface Carrier {
  code: string; name: string; adapterName: string; active: boolean
  status: CarrierStatus; lastTestedAt?: string
  website?: string; logoUrl?: string
  services: CarrierService[]; capabilities: CarrierCapabilities
  settings?: Record<string, any>
}

export interface Pickup {
  id: string; carrierCode: string; carrierPickupId?: string
  status: string; pickupDate: string; readyTime: string; closeTime: string
  confirmationNumber?: string; location: Partial<Address>
  instructions?: string; shipmentIds: string[]
  totalPackages?: number; totalWeight?: number
  createdAt: string
}

export interface WebhookLog {
  id: string; carrierCode: string; eventType: string
  receivedAt: string; shipmentId: string; processed: boolean
}

export interface DashboardStats {
  totalShipments: number; activeShipments: number; deliveredToday: number
  pendingPickups: number; activeCarriers: number; averageTransitDays: number
  revenue: { total: number; currency: string }
}


