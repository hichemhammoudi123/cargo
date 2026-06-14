import { useState } from 'react'
import { useTranslation } from '../../i18n'
import type { Carrier } from '../../types'

interface Props {
  initial?: Partial<Carrier>; onSave: (data: any) => Promise<void>; onCancel: () => void; saving?: boolean
}

export default function CarrierForm({ initial, onSave, onCancel, saving }: Props) {
  const { t } = useTranslation()
  const [form, setForm] = useState({
    code: initial?.code || '', name: initial?.name || '',
    adapterName: initial?.adapterName || '',
    apiKey: '', apiSecret: '', endpoint: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await onSave({
      code: form.code.toUpperCase(), name: form.name, adapterName: form.adapterName || `${form.code}Adapter`,
      credentials: { authType: 'API_KEY', apiKey: form.apiKey, apiSecret: form.apiSecret, endpoint: form.endpoint },
      active: true,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">{t('carrierForm.code')}</label>
          <input value={form.code} onChange={e => setForm({ ...form, code: e.target.value.toUpperCase() })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-cargo-500" placeholder="DHL" required />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">{t('carrierForm.name')}</label>
          <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cargo-500" placeholder="DHL Express" required />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">{t('carrierForm.adapterName')}</label>
        <input value={form.adapterName} onChange={e => setForm({ ...form, adapterName: e.target.value })}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono" placeholder="DhlAdapter" />
      </div>

      <fieldset className="border border-gray-100 rounded-lg p-4">
        <legend className="text-sm font-medium text-gray-600 px-1">{t('carrierForm.apiCredentials')}</legend>
        <div className="grid grid-cols-2 gap-3">
          <div className="col-span-2">
            <input value={form.endpoint} onChange={e => setForm({ ...form, endpoint: e.target.value })}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" placeholder={t('carrierForm.baseUrl')} />
          </div>
          <input value={form.apiKey} onChange={e => setForm({ ...form, apiKey: e.target.value })} placeholder={t('carrierForm.apiKey')}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono" />
          <input value={form.apiSecret} onChange={e => setForm({ ...form, apiSecret: e.target.value })} placeholder={t('carrierForm.apiSecret')}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono" />
        </div>
      </fieldset>

      <div className="flex gap-3 pt-2">
        <button type="button" onClick={onCancel} className="flex-1 px-4 py-2.5 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">{t('common.cancel')}</button>
        <button type="submit" disabled={saving}
          className="flex-1 px-4 py-2.5 bg-cargo-600 text-white rounded-lg text-sm font-medium hover:bg-cargo-700 disabled:opacity-50">
          {saving ? t('common.saving') : initial ? t('carriers.editCarrier') : t('carriers.addCarrier')}
        </button>
      </div>
    </form>
  )
}
