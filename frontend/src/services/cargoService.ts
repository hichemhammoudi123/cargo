/**
 * ──────────────────────────────────────────────────────────────────────
 *  CARGO SERVICE — Service Layer (Mock)
 * ──────────────────────────────────────────────────────────────────────
 *  Simule tous les appels API du backend. Chaque méthode retourne une
 *  Promise pour reproduire le comportement asynchrone réel.
 *
 *  Pour passer en mode "vrai backend", il suffit de remplacer les appels
 *  mock par des fetch/axios vers les endpoints réels.
 * ──────────────────────────────────────────────────────────────────────
 */

import type {
  Shipment, RateOffer, TrackingData, Carrier,
  Pickup, WebhookLog, DashboardStats,
} from '../types'

import {
  mockStats, mockShipments, mockRates, mockTracking,
  mockCarriers, mockPickups, mockWebhookLogs,
} from '../data/mockData'

import { mapCarrierStatusToUnified } from './statusMapper'

/* ─── Utils ─────────────────────────────────────────────────────────── */

/**
 * Simule un délai réseau aléatoire entre 200ms et 600ms.
 */
const delay = (min = 200, max = 600) =>
  new Promise(resolve => setTimeout(resolve, Math.random() * (max - min) + min))

/**
 * Génère un ID unique préfixé.
 */
const uid = (prefix: string): string =>
  `${prefix}_${Math.random().toString(36).substring(2, 10)}`

/* ─── Types ─────────────────────────────────────────────────────────── */

export interface RateRequest {
  sender: { country: string; zipCode: string; city: string; address?: string }
  recipient: { country: string; zipCode: string; city: string; address?: string }
  packages: Array<{ weight: number; weightUnit: string; length?: number; width?: number; height?: number; dimUnit?: string }>
  options?: { carrierCodes?: string[]; serviceType?: string }
}

export interface CreateShipmentRequest {
  carrierCode: string; serviceCode: string; reference: string
  sender: any; recipient: any; packages: any[]
  options?: { insurance?: any; signatureRequired?: boolean; saturdayDelivery?: boolean }
}

export interface ShipmentFilters {
  status?: string; carrier?: string; page?: number; limit?: number
}

export interface ApiResponse<T> {
  success: boolean; data?: T; error?: { code: string; message: string; details?: any }
}

/* ─── 1. Dashboard ──────────────────────────────────────────────────── */

export async function getDashboardStats(): Promise<ApiResponse<DashboardStats>> {
  await delay()
  return { success: true, data: mockStats }
}

/* ─── 2. Rates ──────────────────────────────────────────────────────── */

export async function getRates(request: RateRequest): Promise<ApiResponse<RateOffer[]>> {
  await delay()
  // Filtre par transporteur si demandé
  const codes = request.options?.carrierCodes
  let result = mockRates
  if (codes && codes.length > 0) {
    result = result.filter(r => codes.includes(r.carrierCode))
  }
  // Trier par prix croissant
  result = [...result].sort((a, b) => a.totalPrice - b.totalPrice)
  return { success: true, data: result }
}

/* ─── 3. Shipments ──────────────────────────────────────────────────── */

export async function getShipments(filters?: ShipmentFilters): Promise<ApiResponse<Shipment[]>> {
  await delay()
  let result = [...mockShipments]
  if (filters?.status) {
    result = result.filter(s => s.status === filters.status)
  }
  if (filters?.carrier) {
    result = result.filter(s => s.carrierCode === filters.carrier)
  }
  // Pagination
  const page = filters?.page || 1
  const limit = filters?.limit || 20
  const start = (page - 1) * limit
  result = result.slice(start, start + limit)
  return { success: true, data: result }
}

export async function getShipmentById(id: string): Promise<ApiResponse<Shipment>> {
  await delay()
  const shipment = mockShipments.find(s => s.id === id)
  if (!shipment) {
    return { success: false, error: { code: 'NOT_FOUND', message: `Shipment ${id} not found` } }
  }
  return { success: true, data: shipment }
}

export async function createShipment(request: CreateShipmentRequest): Promise<ApiResponse<Shipment>> {
  await delay(300, 800)
  const newShipment: Shipment = {
    id: uid('shp'),
    status: 'CREATED',
    statusHistory: [{ status: 'CREATED', timestamp: new Date().toISOString() }],
    carrierCode: request.carrierCode,
    carrierName: mockCarriers.find(c => c.code === request.carrierCode)?.name,
    carrierTrackingNumber: `${request.carrierCode}-${Math.floor(Math.random() * 1000000)}`,
    serviceCode: request.serviceCode,
    reference: request.reference,
    labelUrl: `https://api.${request.carrierCode.toLowerCase()}.com/labels/dummy.pdf`,
    labelFormat: 'PDF',
    trackingUrl: `https://www.${request.carrierCode.toLowerCase()}.com/track/dummy`,
    sender: request.sender,
    recipient: request.recipient,
    packages: request.packages.map((p, i) => ({ ...p, trackingNumber: `TN-${i}` })),
    price: { total: Math.round(Math.random() * 100 * 100) / 100, currency: 'EUR' },
    createdAt: new Date().toISOString(),
    estimatedDeliveryDate: new Date(Date.now() + 2 * 86400000).toISOString(),
  }
  return { success: true, data: newShipment }
}

export async function cancelShipment(id: string): Promise<ApiResponse<Shipment>> {
  await delay()
  const shipment = mockShipments.find(s => s.id === id)
  if (!shipment) {
    return { success: false, error: { code: 'NOT_FOUND', message: `Shipment ${id} not found` } }
  }
  return {
    success: true,
    data: { ...shipment, status: 'CANCELLED' as any, statusHistory: [...shipment.statusHistory, { status: 'CANCELLED', timestamp: new Date().toISOString() }] },
  }
}

/* ─── 4. Tracking ───────────────────────────────────────────────────── */

export async function getTracking(shipmentId: string): Promise<ApiResponse<TrackingData>> {
  await delay()
  const shipment = mockShipments.find(s => s.id === shipmentId)
  if (!shipment) {
    return { success: false, error: { code: 'NOT_FOUND', message: `Tracking not found for ${shipmentId}` } }
  }
  return { success: true, data: { ...mockTracking, shipmentId, carrierTrackingNumber: shipment.carrierTrackingNumber || '' } }
}

/* ─── 5. Carriers ───────────────────────────────────────────────────── */

export async function getCarriers(filters?: { active?: boolean }): Promise<ApiResponse<Carrier[]>> {
  await delay()
  let result = [...mockCarriers]
  if (filters?.active !== undefined) {
    result = result.filter(c => c.active === filters.active)
  }
  return { success: true, data: result }
}

export async function getCarrierByCode(code: string): Promise<ApiResponse<Carrier>> {
  await delay()
  const carrier = mockCarriers.find(c => c.code === code)
  if (!carrier) {
    return { success: false, error: { code: 'NOT_FOUND', message: `Carrier ${code} not found` } }
  }
  return { success: true, data: carrier }
}

export async function testCarrierConnection(code: string): Promise<ApiResponse<{ status: string; latencyMs: number; testedAt: string }>> {
  await delay(500, 1500)
  const carrier = mockCarriers.find(c => c.code === code)
  if (!carrier) {
    return { success: false, error: { code: 'NOT_FOUND', message: `Carrier ${code} not found` } }
  }
  const ok = carrier.status !== 'DISCONNECTED'
  return {
    success: ok,
    data: ok
      ? { status: 'CONNECTED', latencyMs: Math.floor(Math.random() * 400 + 100), testedAt: new Date().toISOString() }
      : undefined,
    error: ok ? undefined : { code: 'CARRIER_CONNECTION_FAILED', message: `Connection failed for ${code}` },
  }
}

export async function toggleCarrier(code: string, active: boolean): Promise<ApiResponse<Carrier>> {
  await delay()
  const carrier = mockCarriers.find(c => c.code === code)
  if (!carrier) {
    return { success: false, error: { code: 'NOT_FOUND', message: `Carrier ${code} not found` } }
  }
  return { success: true, data: { ...carrier, active } }
}

/* ─── 6. Pickups ────────────────────────────────────────────────────── */

export async function getPickups(): Promise<ApiResponse<Pickup[]>> {
  await delay()
  return { success: true, data: mockPickups }
}

/* ─── 7. Webhooks ───────────────────────────────────────────────────── */

export async function getWebhookLogs(filters?: { carrier?: string }): Promise<ApiResponse<WebhookLog[]>> {
  await delay()
  let result = [...mockWebhookLogs]
  if (filters?.carrier) {
    result = result.filter(w => w.carrierCode === filters.carrier)
  }
  return { success: true, data: result }
}

/* ─── 8. Address Validation ────────────────────────────────────────── */

export async function validateAddress(address: {
  country: string; zipCode: string; city: string; address: string
}): Promise<ApiResponse<{ valid: boolean; normalizedAddress: any; suggestions: string[] }>> {
  await delay()
  return {
    success: true,
    data: {
      valid: true,
      normalizedAddress: {
        country: address.country.toUpperCase(),
        zipCode: address.zipCode,
        city: address.city.toUpperCase(),
        address: address.address.toUpperCase(),
      },
      suggestions: [],
    },
  }
}

/* ─── 10. Carrier CRUD ──────────────────────────────────────────────── */

export async function createCarrier(data: any): Promise<ApiResponse<Carrier>> {
  await delay(300, 700)
  const newCarrier: Carrier = {
    code: data.code, name: data.name, adapterName: data.adapterName || `${data.code}Adapter`,
    active: true, status: 'PENDING_TEST', services: [],
    capabilities: { labelFormats: ['PDF', 'ZPL'], features: ['RATES', 'TRACKING'] },
  }
  return { success: true, data: newCarrier }
}

export async function updateCarrier(code: string, data: any): Promise<ApiResponse<Carrier>> {
  await delay()
  const carrier = mockCarriers.find(c => c.code === code)
  if (!carrier) return { success: false, error: { code: 'NOT_FOUND', message: `Carrier ${code} not found` } }
  return { success: true, data: { ...carrier, ...data } }
}

export async function deleteCarrier(code: string): Promise<ApiResponse<{ deleted: boolean }>> {
  await delay()
  return { success: true, data: { deleted: true } }
}

export async function addService(carrierCode: string, data: any): Promise<ApiResponse<Carrier>> {
  await delay()
  const carrier = mockCarriers.find(c => c.code === carrierCode)
  if (!carrier) return { success: false, error: { code: 'NOT_FOUND', message: `Carrier ${carrierCode} not found` } }
  return { success: true, data: { ...carrier, services: [...carrier.services, { ...data, active: true }] } }
}

export async function updateService(carrierCode: string, serviceCode: string, data: any): Promise<ApiResponse<Carrier>> {
  await delay()
  const carrier = mockCarriers.find(c => c.code === carrierCode)
  if (!carrier) return { success: false, error: { code: 'NOT_FOUND', message: `Carrier ${carrierCode} not found` } }
  return { success: true, data: { ...carrier, services: carrier.services.map(s => s.code === serviceCode ? { ...s, ...data } : s) } }
}

export async function deleteService(carrierCode: string, serviceCode: string): Promise<ApiResponse<Carrier>> {
  await delay()
  const carrier = mockCarriers.find(c => c.code === carrierCode)
  if (!carrier) return { success: false, error: { code: 'NOT_FOUND', message: `Carrier ${carrierCode} not found` } }
  return { success: true, data: { ...carrier, services: carrier.services.filter(s => s.code !== serviceCode) } }
}

export async function updateCredentials(carrierCode: string, data: any): Promise<ApiResponse<{ updated: boolean }>> {
  await delay()
  return { success: true, data: { updated: true } }
}

/* ─── 11. Pickup CRUD ────────────────────────────────────────────────── */

export async function createPickup(data: any): Promise<ApiResponse<Pickup>> {
  await delay(300, 700)
  const newPickup: Pickup = {
    id: uid('pck'), carrierCode: data.carrierCode, status: 'SCHEDULED',
    pickupDate: data.pickupDate, readyTime: data.readyTime, closeTime: data.closeTime,
    location: data.location, instructions: data.specialInstructions,
    shipmentIds: data.shipmentIds || [],
    totalPackages: data.totalPackages, totalWeight: data.totalWeight,
    createdAt: new Date().toISOString(),
  }
  return { success: true, data: newPickup }
}

export async function cancelPickup(id: string): Promise<ApiResponse<Pickup>> {
  await delay()
  const pickup = mockPickups.find(p => p.id === id)
  if (!pickup) return { success: false, error: { code: 'NOT_FOUND', message: `Pickup ${id} not found` } }
  return { success: true, data: { ...pickup, status: 'CANCELLED' } }
}

/* ─── 12. Shipment CRUD extensions ──────────────────────────────────── */

export async function updateShipment(id: string, data: any): Promise<ApiResponse<Shipment>> {
  await delay()
  const shipment = mockShipments.find(s => s.id === id)
  if (!shipment) return { success: false, error: { code: 'NOT_FOUND', message: `Shipment ${id} not found` } }
  return { success: true, data: { ...shipment, ...data, statusHistory: [...shipment.statusHistory, { status: 'UPDATED', timestamp: new Date().toISOString() }] } }
}

export async function deleteShipment(id: string): Promise<ApiResponse<{ deleted: boolean }>> {
  await delay()
  return { success: true, data: { deleted: true } }
}

/* ─── 10. Webhook Simulator (émet un webhook de test) ──────────────── */

export async function simulateWebhook(carrierCode: string, event: {
  status: string; shipmentId: string; timestamp?: string
}): Promise<ApiResponse<{ processed: boolean; mappedStatus: string }>> {
  await delay(200, 500)
  const unified = mapCarrierStatusToUnified(carrierCode, event.status)
  return {
    success: true,
    data: { processed: true, mappedStatus: unified },
  }
}

/* ─── Export API object (convenience) ──────────────────────────────── */

export const cargoApi = {
  getDashboardStats, getRates,
  getShipments, getShipmentById, createShipment, updateShipment, deleteShipment, cancelShipment,
  getTracking,
  getCarriers, getCarrierByCode, createCarrier, updateCarrier, deleteCarrier,
  addService, updateService, deleteService, updateCredentials,
  testCarrierConnection, toggleCarrier,
  getPickups, createPickup, cancelPickup,
  getWebhookLogs,
  validateAddress, simulateWebhook,
}
