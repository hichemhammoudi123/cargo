import { useState } from 'react'
import { Plus, XCircle, Loader2 } from 'lucide-react'
import StatusBadge from '../components/StatusBadge'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'
import PickupForm from '../components/forms/PickupForm'
import { useApi, useMutation } from '../hooks/useCargoService'
import * as cargoService from '../services/cargoService'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n'
import type { Pickup } from '../types'

export default function Pickups() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  const { data: pickups, loading, error, refetch } = useApi(() => cargoService.getPickups())
  const { data: carriers } = useApi(() => cargoService.getCarriers())
  const create = useMutation(cargoService.createPickup)
  const cancel = useMutation(cargoService.cancelPickup)
  const [showCreate, setShowCreate] = useState(false)
  const [cancelTarget, setCancelTarget] = useState<Pickup | null>(null)

  const handleCreate = async (data: any) => {
    const res = await create.execute(data)
    if (res) { setShowCreate(false); refetch() }
  }

  const handleCancel = async () => {
    if (!cancelTarget) return
    await cancel.execute(cancelTarget.id)
    setCancelTarget(null); refetch()
  }

  const cols = [
    { key: 'id', header: t('common.id'), render: (p: Pickup) => <span className="font-mono text-xs text-cargo-600">{p.id}</span> },
    { key: 'pickupDate', header: t('common.date'), render: (p: Pickup) => new Date(p.pickupDate).toLocaleDateString() },
    { key: 'address', header: t('common.address'), render: (p: Pickup) => <span className="text-sm">{p.location.address}, {p.location.zipCode} {p.location.city}</span> },
    { key: 'carrierName', header: t('common.carrier') },
    { key: 'packageCount', header: t('common.packages'), render: (p: Pickup) => p.totalWeight ? `${p.totalWeight} kg` : '-' },
    { key: 'status', header: t('common.status'), render: (p: Pickup) => <StatusBadge status={p.status as any} /> },
    { key: 'actions', header: '', render: (p: Pickup) => (
      <div className="flex justify-end gap-1">
        {p.status !== 'CANCELLED' && p.status !== 'COMPLETED' && isAdmin && (
          <button onClick={(e) => { e.stopPropagation(); setCancelTarget(p) }}
            className="p-1.5 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-600">
            <XCircle className="w-4 h-4" />
          </button>
        )}
      </div>
    ), className: 'text-right' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('pickups.title')}</h1>
          <p className="text-gray-500 mt-1">{t('pickups.subtitle', { n: pickups?.length || 0 })}</p>
        </div>
        {isAdmin && <button onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-4 py-2 bg-cargo-600 text-white rounded-lg text-sm font-medium hover:bg-cargo-700">
          <Plus className="w-4 h-4" /> {t('pickups.requestPickup')}
        </button>}
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}

      <div className="card p-0">
        {loading ? (
          <div className="flex items-center justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
        ) : (
          <DataTable columns={cols} data={pickups || []} />
        )}
      </div>

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title={t('pickups.requestPickup')}>
        <PickupForm carriers={carriers || []} onSave={handleCreate} onCancel={() => setShowCreate(false)} saving={create.loading} />
      </Modal>

      <ConfirmDialog open={!!cancelTarget} onConfirm={handleCancel} onCancel={() => setCancelTarget(null)}
        title={t('pickups.cancelPickup')}
        message={t('pickups.cancelConfirm', { date: cancelTarget?.pickupDate ? new Date(cancelTarget.pickupDate).toLocaleDateString() : '' })}
        loading={cancel.loading} />
    </div>
  )
}
