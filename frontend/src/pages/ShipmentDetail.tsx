import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, MapPin, Package, Truck, ExternalLink, XCircle, Pencil, Loader2 } from 'lucide-react'
import StatusBadge from '../components/StatusBadge'
import Modal from '../components/Modal'
import ShipmentForm from '../components/forms/ShipmentForm'
import { useApi, useApiById, useMutation } from '../hooks/useCargoService'
import * as cargoService from '../services/cargoService'
import { mapUnifiedToLabel, buildMilestones } from '../services/statusMapper'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n'
import type { TrackingEventCode } from '../types'

export default function ShipmentDetail() {
  const { id } = useParams()
  const nav = useNavigate()
  const { t } = useTranslation()
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  const { data: shipment, loading, error, refetch } = useApiById(cargoService.getShipmentById, id)
  const { data: carriers } = useApi(() => cargoService.getCarriers(), [])
  const cancel = useMutation(cargoService.cancelShipment)
  const updateSh = useMutation(cargoService.updateShipment)
  const [showEdit, setShowEdit] = useState(false)
  const [cancelling, setCancelling] = useState(false)

  const handleCancel = async () => {
    if (!id) return; setCancelling(true); await cancel.execute(id); setCancelling(false); refetch()
  }

  const handleUpdate = async (data: any) => {
    if (!id) return; const res = await updateSh.execute(id, data)
    if (res) { setShowEdit(false); refetch() }
  }

  if (loading) return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-cargo-500" /></div>
  if (error || !shipment) return <div className="text-center py-12 text-gray-400">{error || t('common.notFound')}</div>

  const events = shipment.statusHistory.map(h => ({ code: h.status as TrackingEventCode, timestamp: h.timestamp }))

  return (
    <div className="space-y-6 max-w-4xl">
      <button onClick={() => nav('/shipments')} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft className="w-4 h-4" /> {t('common.back')}
      </button>

      <div className="card">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-bold text-gray-900">{shipment.reference}</h1>
              <StatusBadge status={shipment.status} />
            </div>
            <p className="text-sm text-gray-500 mt-1 font-mono">{shipment.id}</p>
          </div>
          <div className="flex gap-2">
            {isAdmin && (
              <button onClick={() => setShowEdit(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-100">
                <Pencil className="w-3.5 h-3.5" /> {t('common.edit')}
              </button>
            )}
            {shipment.labelUrl && (
              <a href={shipment.labelUrl} target="_blank"
                className="flex items-center gap-1.5 px-3 py-1.5 bg-cargo-50 text-cargo-700 rounded-lg text-sm font-medium hover:bg-cargo-100">
                <ExternalLink className="w-3.5 h-3.5" /> {t('shipments.label')}
              </a>
            )}
            {shipment.status !== 'CANCELLED' && shipment.status !== 'DELIVERED' && (
              <button onClick={handleCancel} disabled={cancelling}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-red-50 text-red-600 rounded-lg text-sm font-medium hover:bg-red-100 disabled:opacity-50">
                {cancelling ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <XCircle className="w-3.5 h-3.5" />} {t('shipments.cancel')}
              </button>
            )}
          </div>
        </div>
        {cancel.data && <div className="mt-3 text-sm text-green-600">{t('shipments.shipmentCancelled')}</div>}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="font-semibold text-gray-900 mb-3 flex items-center gap-2"><MapPin className="w-4 h-4 text-cargo-500" /> {t('shipments.sender')}</h2>
          <div className="text-sm text-gray-600 space-y-1">
            <p className="font-medium text-gray-800">{shipment.sender.company}</p>
            <p>{shipment.sender.zipCode} {shipment.sender.city}</p>
            <p>{shipment.sender.country}</p>
          </div>
        </div>
        <div className="card">
          <h2 className="font-semibold text-gray-900 mb-3 flex items-center gap-2"><MapPin className="w-4 h-4 text-green-500" /> {t('shipments.recipient')}</h2>
          <div className="text-sm text-gray-600 space-y-1">
            <p className="font-medium text-gray-800">{shipment.recipient.company}</p>
            <p>{shipment.recipient.zipCode} {shipment.recipient.city}</p>
            <p>{shipment.recipient.country}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="font-semibold text-gray-900 mb-3 flex items-center gap-2"><Truck className="w-4 h-4 text-cargo-500" /> {t('shipments.carrier')}</h2>
          <div className="text-sm space-y-2">
            <div className="flex justify-between"><span className="text-gray-500">{t('shipments.carrier')}</span><span className="font-medium">{shipment.carrierName}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">{t('shipments.service')}</span><span>{shipment.serviceCode}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">{t('shipments.trackingNo')}</span><span className="font-mono text-cargo-600">{shipment.carrierTrackingNumber}</span></div>
          </div>
        </div>
        <div className="card">
          <h2 className="font-semibold text-gray-900 mb-3 flex items-center gap-2"><Package className="w-4 h-4 text-emerald-500" /> {t('shipments.pricing')}</h2>
          <div className="text-sm space-y-2">
            <div className="flex justify-between"><span className="text-gray-500">{t('shipments.total')}</span><span className="text-lg font-bold text-gray-900">{shipment.price.total.toFixed(2)} {shipment.price.currency}</span></div>
            {shipment.estimatedDeliveryDate && <div className="flex justify-between"><span className="text-gray-500">{t('shipments.estDelivery')}</span><span>{new Date(shipment.estimatedDeliveryDate).toLocaleDateString()}</span></div>}
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="font-semibold text-gray-900 mb-3 flex items-center gap-2"><Package className="w-4 h-4 text-cargo-500" /> {t('common.packages')}</h2>
        {shipment.packages.map((pkg, i) => (
          <div key={i} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
            <div><span className="font-medium">{pkg.reference}</span>{pkg.description && <span className="text-gray-500 ml-2">{pkg.description}</span>}</div>
            <div className="text-sm text-gray-500">{pkg.weight} {pkg.weightUnit}</div>
          </div>
        ))}
      </div>

      <div className="card">
        <h2 className="font-semibold text-gray-900 mb-3">{t('shipments.statusTimeline')}</h2>
        <div className="space-y-0">
          {shipment.statusHistory.map((h, i) => {
            const label = mapUnifiedToLabel(shipment.carrierCode, h.status as TrackingEventCode, 'en')
            const isLast = i === shipment.statusHistory.length - 1
            return (
              <div key={i} className="flex gap-4 pb-3 relative">
                <div className="flex flex-col items-center">
                  <div className={`w-3 h-3 rounded-full mt-1.5 ${isLast ? 'bg-cargo-500 ring-2 ring-cargo-200' : 'bg-gray-300'}`} />
                  {i < shipment.statusHistory.length - 1 && <div className="w-0.5 flex-1 bg-gray-200 mt-1" />}
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-900">{label}</div>
                  <div className="text-xs text-gray-400">{new Date(h.timestamp).toLocaleString()}</div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      <Modal open={showEdit} onClose={() => setShowEdit(false)} title={t('shipments.editShipment')} size="lg">
        <ShipmentForm initial={shipment} carriers={carriers || []} onSave={handleUpdate} onCancel={() => setShowEdit(false)} saving={updateSh.loading} />
      </Modal>
    </div>
  )
}
