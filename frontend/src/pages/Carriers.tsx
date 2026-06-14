import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Pencil, Trash2, Eye, Loader2 } from 'lucide-react'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'
import CarrierForm from '../components/forms/CarrierForm'
import { useApi, useMutation } from '../hooks/useCargoService'
import * as cargoService from '../services/cargoService'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n'
import type { Carrier } from '../types'

export default function Carriers() {
  const nav = useNavigate()
  const { t } = useTranslation()
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  const { data: carriers, loading, error, refetch } = useApi(() => cargoService.getCarriers())
  const createC = useMutation(cargoService.createCarrier)
  const updateC = useMutation(cargoService.updateCarrier)
  const deleteC = useMutation(cargoService.deleteCarrier)

  const [showCreate, setShowCreate] = useState(false)
  const [editTarget, setEditTarget] = useState<Carrier | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Carrier | null>(null)

  const handleSave = async (data: any) => {
    if (editTarget) { await updateC.execute(editTarget.code, data) }
    else { await createC.execute(data) }
    setEditTarget(null); setShowCreate(false); refetch()
  }

  const handleDelete = async () => {
    if (!deleteTarget) return; await deleteC.execute(deleteTarget.code)
    setDeleteTarget(null); refetch()
  }

  const cols = [
    { key: 'name', header: t('carriers.carrier'), render: (c: Carrier) => (
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center text-xs font-bold text-gray-500">{c.name[0]}</div>
        <div><div className="font-medium text-gray-900">{c.name}</div><div className="text-xs text-gray-400">API: {c.adapterName}</div></div>
      </div>
    )},
    { key: 'code', header: t('carriers.code'), render: (c: Carrier) => <span className="font-mono text-xs text-cargo-600">{c.code}</span> },
    { key: 'country', header: t('carriers.country') },
    { key: 'status', header: t('common.status'), render: (c: Carrier) => (
      <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${c.active ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
        <span className={`w-1.5 h-1.5 rounded-full ${c.active ? 'bg-green-500' : 'bg-gray-400'}`} />
        {c.active ? t('common.active') : t('common.inactive')}
      </span>
    )},
    { key: 'services', header: t('common.services'), render: (c: Carrier) => <span className="text-gray-500">{c.services.length}</span> },
    { key: 'actions', header: '', render: (c: Carrier) => (
      <div className="flex justify-end gap-1">
        <button onClick={() => nav(`/carriers/${c.code}`)} className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400"><Eye className="w-4 h-4" /></button>
        {isAdmin && <>
          <button onClick={(e) => { e.stopPropagation(); setEditTarget(c); setShowCreate(true) }} className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400"><Pencil className="w-4 h-4" /></button>
          <button onClick={(e) => { e.stopPropagation(); setDeleteTarget(c) }} className="p-1.5 rounded-lg hover:bg-red-50 text-gray-400"><Trash2 className="w-4 h-4" /></button>
        </>}
      </div>
    ), className: 'text-right' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('carriers.title')}</h1>
          <p className="text-gray-500 mt-1">{t('carriers.subtitle', { n: carriers?.length || 0 })}</p>
        </div>
        {isAdmin && <button onClick={() => { setEditTarget(null); setShowCreate(true) }}
          className="flex items-center gap-2 px-4 py-2 bg-cargo-600 text-white rounded-lg text-sm font-medium hover:bg-cargo-700">
          <Plus className="w-4 h-4" /> {t('carriers.addCarrier')}
        </button>}
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}

      <div className="card p-0">
        {loading ? (
          <div className="flex items-center justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
        ) : (
          <DataTable columns={cols} data={carriers || []} onRowClick={(c) => nav(`/carriers/${c.code}`)} />
        )}
      </div>

      <Modal open={showCreate} onClose={() => { setShowCreate(false); setEditTarget(null) }}
        title={editTarget ? t('carriers.editCarrier') : t('carriers.addCarrier')} size="lg">
        <CarrierForm initial={editTarget || undefined} onSave={handleSave}
          onCancel={() => { setShowCreate(false); setEditTarget(null) }}
          saving={createC.loading || updateC.loading} />
      </Modal>

      <ConfirmDialog open={!!deleteTarget} onConfirm={handleDelete} onCancel={() => setDeleteTarget(null)}
        title={t('carriers.deleteCarrier')}
        message={t('carriers.deleteConfirm', { name: deleteTarget?.name || '' })}
        loading={deleteC.loading} />
    </div>
  )
}
