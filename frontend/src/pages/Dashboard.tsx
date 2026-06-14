import { useNavigate } from 'react-router-dom'
import { Package, Truck, CheckCircle2, CalendarClock, Building2, Euro, Loader2 } from 'lucide-react'
import StatCard from '../components/StatCard'
import StatusBadge from '../components/StatusBadge'
import DataTable from '../components/DataTable'
import { useApi } from '../hooks/useCargoService'
import * as cargoService from '../services/cargoService'
import { useTranslation } from '../i18n'
import type { Shipment } from '../types'

export default function Dashboard() {
  const nav = useNavigate()
  const { t } = useTranslation()
  const stats = useApi(() => cargoService.getDashboardStats())
  const shipments = useApi(() => cargoService.getShipments({ limit: 5 }))

  const cols = [
    { key: 'id', header: t('common.id'), render: (s: Shipment) => <span className="font-mono text-xs">{s.id}</span> },
    { key: 'reference', header: t('common.reference') },
    { key: 'carrierName', header: t('common.carrier') },
    { key: 'status', header: t('common.status'), render: (s: Shipment) => <StatusBadge status={s.status} /> },
    { key: 'createdAt', header: t('common.date'), render: (s: Shipment) => new Date(s.createdAt).toLocaleDateString() },
    { key: 'price', header: t('common.price'), render: (s: Shipment) => `${s.price.total} ${s.price.currency}` },
  ]

  if (stats.loading) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-cargo-500" /></div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('dashboard.title')}</h1>
        <p className="text-gray-500 mt-1">{t('dashboard.subtitle')}</p>
      </div>

      {stats.error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{stats.error}</div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label={t('dashboard.totalShipments')} value={stats.data?.totalShipments || 0} icon={Package} color="text-cargo-600" sub={t('dashboard.allTime')} />
        <StatCard label={t('dashboard.activeShipments')} value={stats.data?.activeShipments || 0} icon={Truck} color="text-amber-600" sub={t('dashboard.inTransit')} />
        <StatCard label={t('dashboard.deliveredToday')} value={stats.data?.deliveredToday || 0} icon={CheckCircle2} color="text-green-600" sub={t('dashboard.avgDays', { n: stats.data?.averageTransitDays || '-' })} />
        <StatCard label={t('dashboard.revenue')} value={`${(stats.data?.revenue.total || 0).toLocaleString()} ${stats.data?.revenue.currency || ''}`} icon={Euro} color="text-emerald-600" />
        <StatCard label={t('dashboard.activeCarriers')} value={stats.data?.activeCarriers || 0} icon={Building2} color="text-purple-600" sub={t('status.CONNECTED')} />
        <StatCard label={t('dashboard.pendingPickups')} value={stats.data?.pendingPickups || 0} icon={CalendarClock} color="text-rose-600" sub={t('dashboard.awaitingCollection')} />
      </div>

      <div className="card">
        <div className="card-header">{t('dashboard.recentShipments')}</div>
        {shipments.loading ? (
          <div className="flex items-center justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
        ) : (
          <DataTable columns={cols} data={shipments.data || []} onRowClick={(s) => nav(`/shipments/${s.id}`)} />
        )}
      </div>
    </div>
  )
}
