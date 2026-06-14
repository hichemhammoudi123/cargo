import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Eye, Trash2, Loader2 } from 'lucide-react'
import StatusBadge from '../components/StatusBadge'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'
import ShipmentForm from '../components/forms/ShipmentForm'
import { useApi, useMutation } from '../hooks/useCargoService'
import * as cargoService from '../services/cargoService'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n'
import type { Shipment } from '../types'

export default function Shipments() {
  const nav = useNavigate()
  const { t } = useTranslation()
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  const { data: shipments, loading, error, refetch } = useApi(() => cargoService.getShipments())
  const { data: carriers } = useApi(() => cargoService.getCarriers())
  const createShip = useMutation(cargoService.createShipment)
  const deleteShip = useMutation(cargoService.deleteShipment)

  const [showCreate, setShowCreate] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<Shipment | null>(null)

  const handleCreate = async (data: any) => {
    const res = await createShip.execute(data)
    if (res) { setShowCreate(false); refetch() }
  }

  const handleDelete = async () => {
    if (!deleteTarget) return
    await deleteShip.execute(deleteTarget.id)
    setDeleteTarget(null)
    refetch()
  }

  const cols = [
    { key: 'id', header: t('common.id'), render: (s: Shipment) => <span className="font-mono text-xs text-cargo-600">{s.id}</span> },
    { key: 'reference', header: t('common.reference'), render: (s: Shipment) => <span className="font-medium">{s.reference}</span> },
    { key: 'carrierName', header: t('common.carrier') },
    { key: 'carrierTrackingNumber', header: t('shipments.trackingNo'), render: (s: Shipment) => <span className="font-mono text-xs">{s.carrierTrackingNumber || '-'}</span> },
    { key: 'status', header: t('common.status'), render: (s: Shipment) => <StatusBadge status={s.status} /> },
    { key: 'price', header: t('common.price'), render: (s: Shipment) => `${s.price.total.toFixed(2)} ${s.price.currency}` },
    { key: 'createdAt', header: t('common.date'), render: (s: Shipment) => new Date(s.createdAt).toLocaleDateString() },
    { key: 'actions', header: '', render: (s: Shipment) => (
      <div className="flex items-center gap-1 justify-end">
        <button onClick={(e) => { e.stopPropagation(); nav(`/shipments/${s.id}`) }} className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-cargo-600"><Eye className="w-4 h-4" /></button>
        {isAdmin && <button onClick={(e) => { e.stopPropagation(); setDeleteTarget(s) }} className="p-1.5 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-600"><Trash2 className="w-4 h-4" /></button>}
      </div>
    ), className: 'text-right' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('shipments.title')}</h1>
          <p className="text-gray-500 mt-1">{t('shipments.subtitle', { n: shipments?.length || 0 })}</p>
        </div>
        <button onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-4 py-2 bg-cargo-600 text-white rounded-lg text-sm font-medium hover:bg-cargo-700 transition-colors">
          <Plus className="w-4 h-4" /> {t('shipments.newShipment')}
        </button>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}

      <div className="card p-0">
        {loading ? (
          <div className="flex items-center justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
        ) : (
          <DataTable columns={cols} data={shipments || []} onRowClick={(s) => nav(`/shipments/${s.id}`)} />
        )}
      </div>

      {createShip.error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{createShip.error}</div>}

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title={t('shipments.createShipment')} size="lg">
        <ShipmentForm carriers={carriers || []} onSave={handleCreate} onCancel={() => setShowCreate(false)} saving={createShip.loading} />
      </Modal>

      <ConfirmDialog open={!!deleteTarget} onConfirm={handleDelete} onCancel={() => setDeleteTarget(null)}
        title={t('shipments.deleteShipment')}
        message={t('shipments.deleteConfirm', { ref: deleteTarget?.reference || deleteTarget?.id || '' })}
        loading={deleteShip.loading} />
    </div>
  )
}
