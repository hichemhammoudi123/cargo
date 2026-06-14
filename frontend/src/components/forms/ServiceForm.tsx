import { useState } from 'react'
import { useTranslation } from '../../i18n'
import type { CarrierService } from '../../types'

interface Props {
  carrierCode: string; initial?: Partial<CarrierService>
  onSave: (data: any) => Promise<void>; onCancel: () => void; saving?: boolean
}

export default function ServiceForm({ carrierCode, initial, onSave, onCancel, saving }: Props) {
  const { t } = useTranslation()
  const [form, setForm] = useState({
    code: initial?.code || '', name: initial?.name || '',
    description: initial?.description || '',
    maxWeight: initial?.maxWeight || 30, transitDays: initial?.transitDays || 2,
    zones: (initial?.zones || []).join(', '), features: (initial?.features || []).join(', '),
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await onSave({
      code: form.code, name: form.name, description: form.description,
      maxWeight: form.maxWeight, maxWeightUnit: 'KG', transitDays: form.transitDays,
      zones: form.zones.split(',').map(z => z.trim()).filter(Boolean),
      features: form.features.split(',').map(f => f.trim()).filter(Boolean),
      active: true,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input type="hidden" value={carrierCode} />
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">{t('serviceForm.name')} *</label>
          <input value={form.code} onChange={e => setForm({ ...form, code: e.target.value })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-cargo-500" placeholder="EXPRESS_24" required />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">{t('serviceForm.name')} *</label>
          <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" placeholder="Express 24h" required />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">{t('serviceForm.description')}</label>
        <input value={form.description} onChange={e => setForm({ ...form, description: e.target.value })}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" placeholder="Delivery within 24 hours" />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">{t('serviceForm.maxWeight')}</label>
          <input type="number" value={form.maxWeight} onChange={e => setForm({ ...form, maxWeight: +e.target.value })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">{t('serviceForm.transitDays')}</label>
          <input type="number" value={form.transitDays} onChange={e => setForm({ ...form, transitDays: +e.target.value })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">{t('serviceForm.zones')}</label>
        <input value={form.zones} onChange={e => setForm({ ...form, zones: e.target.value })}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono" placeholder="FR, DE, BE, NL" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">{t('serviceForm.features')}</label>
        <input value={form.features} onChange={e => setForm({ ...form, features: e.target.value })}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono" placeholder="SIGNATURE, INSURANCE" />
      </div>
      <div className="flex gap-3 pt-2">
        <button type="button" onClick={onCancel} className="flex-1 px-4 py-2.5 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">{t('common.cancel')}</button>
        <button type="submit" disabled={saving}
          className="flex-1 px-4 py-2.5 bg-cargo-600 text-white rounded-lg text-sm font-medium hover:bg-cargo-700 disabled:opacity-50">
          {saving ? t('common.saving') : initial ? t('serviceForm.editService') : t('serviceForm.addService')}
        </button>
      </div>
    </form>
  )
}
