import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Plus, Pencil, Trash2, Loader2, CheckCircle2, XCircle } from 'lucide-react'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'
import ServiceForm from '../components/forms/ServiceForm'
import { useApiById, useMutation } from '../hooks/useCargoService'
import * as cargoService from '../services/cargoService'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n'
import type { CarrierService } from '../types'

export default function CarrierDetail() {
  const { code } = useParams()
  const nav = useNavigate()
  const { t } = useTranslation()
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  const { data: carrier, loading, error, refetch } = useApiById(cargoService.getCarrierByCode, code)
  const toggle = useMutation(cargoService.toggleCarrier)
  const testConn = useMutation(cargoService.testCarrierConnection)
  const addSvc = useMutation(cargoService.addService)
  const updateSvc = useMutation(cargoService.updateService)
  const deleteSvc = useMutation(cargoService.deleteService)
  const upCreds = useMutation(cargoService.updateCredentials)

  const [showAddService, setShowAddService] = useState(false)
  const [editSvcTarget, setEditSvcTarget] = useState<CarrierService | null>(null)
  const [deleteSvcTarget, setDeleteSvcTarget] = useState<CarrierService | null>(null)
  const [credsOpen, setCredsOpen] = useState(false)
  const [credsForm, setCredsForm] = useState({ apiKey: '', apiSecret: '', accountNumber: '' })

  const handleToggle = async () => { if (!code) return; await toggle.execute(code); refetch() }
  const handleTest = async () => { if (!code) return; await testConn.execute(code) }

  const handleSaveService = async (data: any) => {
    if (!code) return
    if (editSvcTarget) { await updateSvc.execute(data) }
    else { await addSvc.execute(code, data) }
    setEditSvcTarget(null); setShowAddService(false); refetch()
  }

  const handleDeleteService = async () => {
    if (!deleteSvcTarget) return; await deleteSvc.execute(deleteSvcTarget.code); setDeleteSvcTarget(null); refetch()
  }

  const handleSaveCreds = async () => {
    if (!code) return; await upCreds.execute(code, credsForm); setCredsOpen(false); refetch()
  }

  if (loading) return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-cargo-500" /></div>
  if (error || !carrier) return <div className="text-center py-12 text-gray-400">{error || t('common.notFound')}</div>

  return (
    <div className="space-y-6 max-w-4xl">
      <button onClick={() => nav('/carriers')} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft className="w-4 h-4" /> {t('common.back')}
      </button>

      <div className="card">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-cargo-50 flex items-center justify-center text-lg font-bold text-cargo-600">{carrier.name[0]}</div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">{carrier.name}</h1>
              <p className="text-sm text-gray-500 font-mono">{carrier.code} · {carrier.adapterName}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={handleTest}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-100">
              {testConn.loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />} {t('carriers.test')}
            </button>
            {isAdmin && (
              <button onClick={() => { setCredsForm({ apiKey: '', apiSecret: '', accountNumber: '' }); setCredsOpen(true) }}
                className="px-3 py-1.5 bg-gray-50 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-100">{t('carriers.credentials')}</button>
            )}
            <button onClick={handleToggle}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium ${carrier.active ? 'bg-red-50 text-red-600 hover:bg-red-100' : 'bg-green-50 text-green-600 hover:bg-green-100'}`}>
              {carrier.active ? <XCircle className="w-3.5 h-3.5" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
              {carrier.active ? t('carriers.deactivate') : t('carriers.activate')}
            </button>
          </div>
        </div>
        {testConn.data !== null && testConn.data !== undefined && (
          <div className={`mt-3 text-sm ${testConn.data ? 'text-green-600' : 'text-red-600'}`}>
            {testConn.data ? t('carriers.connectionSuccess') : t('carriers.connectionFailed')}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-2">{t('carriers.connectionInfo')}</h3>
          <div className="text-sm space-y-1.5 text-gray-600">
            <div className="flex justify-between"><span>{t('carriers.baseUrl')}</span><span className="font-mono text-xs">{'-'}</span></div>
            <div className="flex justify-between"><span>{t('carriers.account')}</span><span>{'-'}</span></div>
            <div className="flex justify-between"><span>{t('carriers.trackingUrl')}</span><span className="font-mono text-xs">{'-'}</span></div>
          </div>
        </div>
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-2">{t('carriers.capabilities')}</h3>
          <div className="flex flex-wrap gap-2">{carrier.capabilities.features.map(f => (
            <span key={f} className="px-2 py-0.5 bg-cargo-50 text-cargo-700 rounded text-xs font-medium">{f}</span>
          ))}</div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-900">{t('carriers.servicesCount', { n: carrier.services.length })}</h2>
          {isAdmin && <button onClick={() => { setEditSvcTarget(null); setShowAddService(true) }}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-cargo-50 text-cargo-700 rounded-lg text-sm font-medium hover:bg-cargo-100">
            <Plus className="w-4 h-4" /> {t('carriers.addService')}
          </button>}
        </div>
        <div className="space-y-2">
          {carrier.services.map(svc => (
            <div key={svc.code} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <div className="font-medium text-gray-900">{svc.name}</div>
                <div className="text-xs text-gray-500 font-mono">{svc.code} · {svc.description}</div>
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-500">
                {svc.transitDays && <span className="font-medium">{svc.transitDays} days</span>}
                {isAdmin && <div className="flex gap-1">
                  <button onClick={() => { setEditSvcTarget(svc); setShowAddService(true) }} className="p-1 rounded hover:bg-gray-200"><Pencil className="w-3.5 h-3.5" /></button>
                  <button onClick={() => setDeleteSvcTarget(svc)} className="p-1 rounded hover:bg-red-100 text-red-400"><Trash2 className="w-3.5 h-3.5" /></button>
                </div>}
              </div>
            </div>
          ))}
        </div>
      </div>

      <Modal open={showAddService} onClose={() => { setShowAddService(false); setEditSvcTarget(null) }}
        title={editSvcTarget ? t('carriers.editService') : t('carriers.addService')}>
        <ServiceForm initial={editSvcTarget || undefined} carrierCode={carrier.code}
          onSave={handleSaveService} onCancel={() => { setShowAddService(false); setEditSvcTarget(null) }}
          saving={addSvc.loading || updateSvc.loading} />
      </Modal>

      <ConfirmDialog open={!!deleteSvcTarget} onConfirm={handleDeleteService} onCancel={() => setDeleteSvcTarget(null)}
        title={t('carriers.deleteService')}
        message={t('carriers.deleteServiceConfirm', { name: deleteSvcTarget?.name || '' })}
        loading={deleteSvc.loading} />

      <Modal open={credsOpen} onClose={() => setCredsOpen(false)} title={t('carriers.apiCredentials')}>
        <div className="space-y-4">
          {(['apiKey', 'apiSecret', 'accountNumber'] as const).map(f => (
            <div key={f}>
              <label className="block text-sm font-medium text-gray-700 mb-1 capitalize">
                {t(`carriers.${f}`)}
              </label>
              <input type={f === 'apiSecret' ? 'password' : 'text'} value={credsForm[f]} onChange={e => setCredsForm(p => ({ ...p, [f]: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-cargo-500 focus:border-transparent outline-none" />
            </div>
          ))}
          <div className="flex justify-end gap-2 pt-2">
            <button onClick={() => setCredsOpen(false)} className="btn-secondary text-sm">{t('common.cancel')}</button>
            <button onClick={handleSaveCreds} disabled={upCreds.loading}
              className="btn-primary text-sm flex items-center gap-1.5 disabled:opacity-50">
              {upCreds.loading && <Loader2 className="w-4 h-4 animate-spin" />} {t('common.save')}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
