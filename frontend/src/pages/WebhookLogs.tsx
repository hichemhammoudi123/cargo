import { CheckCircle2, XCircle, Loader2 } from 'lucide-react'
import StatusBadge from '../components/StatusBadge'
import DataTable from '../components/DataTable'
import { useApi } from '../hooks/useCargoService'
import * as cargoService from '../services/cargoService'
import { useTranslation } from '../i18n'
import type { WebhookLog } from '../types'

export default function WebhookLogs() {
  const { t } = useTranslation()
  const { data: logs, loading, error } = useApi(() => cargoService.getWebhookLogs())

  const cols = [
    { key: 'id', header: t('common.id'), render: (w: WebhookLog) => <span className="font-mono text-xs text-cargo-600">{w.id}</span> },
    { key: 'carrierCode', header: t('common.carrier'), render: (w: WebhookLog) => <StatusBadge status={w.carrierCode} /> },
    { key: 'eventType', header: t('webhooks.event'), render: (w: WebhookLog) => <span className="font-medium">{w.eventType}</span> },
    { key: 'shipmentId', header: t('webhooks.shipment'), render: (w: WebhookLog) => <span className="font-mono text-xs">{w.shipmentId}</span> },
    { key: 'receivedAt', header: t('webhooks.received'), render: (w: WebhookLog) => new Date(w.receivedAt).toLocaleString() },
    { key: 'processed', header: t('webhooks.processed'), render: (w: WebhookLog) => w.processed
      ? <CheckCircle2 className="w-4 h-4 text-green-500" />
      : <XCircle className="w-4 h-4 text-red-500" />
    },
  ]

  if (loading) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-cargo-500" /></div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('webhooks.title')}</h1>
        <p className="text-gray-500 mt-1">{t('webhooks.subtitle')}</p>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}

      <div className="card p-0">
        <DataTable columns={cols} data={logs || []} />
      </div>
    </div>
  )
}
