import { useParams } from 'react-router-dom'
import { MapPin, Clock, Truck, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import { useApiById } from '../hooks/useCargoService'
import * as cargoService from '../services/cargoService'
import { mapUnifiedToLabel, isTerminal, isBlocking } from '../services/statusMapper'
import { useTranslation } from '../i18n'
import type { TrackingEventCode } from '../types'

export default function Tracking() {
  const { id } = useParams()
  const { t } = useTranslation()
  const { data: tracking, loading, error } = useApiById(cargoService.getTracking, id)

  const stepIcons: Record<string, any> = {
    LABEL_CREATED: Clock, PICKED_UP: Truck, IN_TRANSIT: Truck,
    ARRIVED_AT_HUB: MapPin, DEPARTED_FROM_HUB: Truck,
    OUT_FOR_DELIVERY: Truck, DELIVERED: CheckCircle2,
    DELIVERY_ATTEMPTED: AlertCircle, FAILED: AlertCircle,
    CUSTOMS_HELD: AlertCircle, CUSTOMS_CLEARED: CheckCircle2,
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-cargo-500" /></div>
  }

  if (error || !tracking) {
    return <div className="text-center py-12 text-gray-400">{error || t('common.notFound')}</div>
  }

  const events = tracking.events
  const isCurrentTerminal = isTerminal(tracking.currentStatus.code as TrackingEventCode)
  const isCurrentBlocking = isBlocking(tracking.currentStatus.code as TrackingEventCode)

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('tracking.title')}</h1>
        <p className="text-gray-500 mt-1">{tracking.carrierCode} · {tracking.carrierTrackingNumber}</p>
      </div>

      <div className={`card bg-gradient-to-r ${isCurrentTerminal
        ? tracking.currentStatus.code === 'DELIVERED'
          ? 'from-green-500 to-green-700'
          : 'from-red-500 to-red-700'
        : isCurrentBlocking
          ? 'from-amber-500 to-amber-700'
          : 'from-cargo-500 to-cargo-700'
      } text-white`}>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm opacity-80">{t('tracking.currentStatus')}</div>
            <div className="text-2xl font-bold mt-1">{tracking.currentStatus.label}</div>
            <div className="flex items-center gap-2 mt-2 text-sm opacity-80">
              <MapPin className="w-3.5 h-3.5" /> {tracking.currentStatus.location}
            </div>
            {isCurrentBlocking && (
              <div className="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 bg-white/20 rounded text-xs font-medium">
                {t('tracking.actionRequired')}
              </div>
            )}
          </div>
          <div className="text-right">
            <div className="text-sm opacity-80">{t('tracking.lastUpdated')}</div>
            <div className="text-lg font-semibold mt-1">{new Date(tracking.currentStatus.timestamp).toLocaleString()}</div>
            {tracking.estimatedDeliveryDate && (
              <div className="text-sm opacity-80 mt-1">{t('tracking.est')} {new Date(tracking.estimatedDeliveryDate).toLocaleDateString()}</div>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-3">
        {Object.entries(tracking.milestones).map(([key, val]) => (
          <div key={key} className={`card text-center ${val ? 'border-cargo-200 bg-cargo-50/30' : ''}`}>
            <div className={`text-xs font-medium uppercase ${val ? 'text-cargo-600' : 'text-gray-400'}`}>
              {key.replace(/([A-Z])/g, ' $1').trim()}
            </div>
            {val ? <div className="text-xs text-gray-500 mt-1">{new Date(val).toLocaleDateString()}</div> : <div className="text-xs text-gray-300 mt-1">—</div>}
          </div>
        ))}
      </div>

      <div className="card">
        <div className="card-header">{t('tracking.trackingEvents')}</div>
        <div className="space-y-0">
          {events.map((evt, i) => {
            const Icon = stepIcons[evt.code] || Clock
            const unifiedCode = evt.code as TrackingEventCode
            const displayLabel = mapUnifiedToLabel(tracking.carrierCode, unifiedCode, 'en')
            const isLast = i === events.length - 1

            return (
              <div key={evt.eventId} className="flex gap-4 pb-4 relative">
                <div className="flex flex-col items-center">
                  <div className={`p-1.5 rounded-full ${isLast ? 'bg-cargo-100 text-cargo-600 ring-2 ring-cargo-200' : 'bg-gray-100 text-gray-400'}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  {i < events.length - 1 && <div className="w-0.5 flex-1 bg-gray-100 mt-1" />}
                </div>
                <div className="flex-1 pb-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-medium text-gray-900">{displayLabel}</span>
                      {evt.description && <span className="text-sm text-gray-500 ml-2">— {evt.description}</span>}
                    </div>
                    <span className="text-xs text-gray-400">{new Date(evt.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <MapPin className="w-3 h-3 text-gray-400" />
                    <span className="text-xs text-gray-400">{evt.location || t('tracking.unknown')}</span>
                    {evt.carrierRawStatus && (
                      <span className="text-xs text-gray-300">
                         · {t('tracking.raw')} <span className="italic">"{evt.carrierRawStatus}"</span>
                      </span>
                    )}
                  </div>
                  {evt.carrierRawStatus && (
                    <div className="mt-1">
                      <span className="text-[10px] text-gray-300 bg-gray-50 px-1.5 py-0.5 rounded">
                        {t('tracking.mapped')} {unifiedCode}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
