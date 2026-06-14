import { useState } from 'react'
import { useTranslation } from '../../i18n'

interface Props {
  carriers: Array<{ code: string; name: string }>
  onSave: (data: any) => Promise<void>; onCancel: () => void; saving?: boolean
}

export default function PickupForm({ carriers, onSave, onCancel, saving }: Props) {
  const { t } = useTranslation()
  const [form, setForm] = useState({
    carrierCode: '', pickupDate: new Date(Date.now() + 86400000).toISOString().split('T')[0],
    readyTime: '09:00', closeTime: '17:00',
    city: '', country: 'FR', address: '', company: '', contactName: '', phone: '',
    totalPackages: 1, totalWeight: 1, instructions: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await onSave({
      carrierCode: form.carrierCode, pickupDate: form.pickupDate,
      readyTime: form.readyTime, closeTime: form.closeTime,
      location: { company: form.company, contactName: form.contactName, phone: form.phone, country: form.country, city: form.city, address: form.address },
      totalPackages: form.totalPackages, totalWeight: form.totalWeight, weightUnit: 'KG',
      specialInstructions: form.instructions,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">{t('pickupForm.carrier')}</label>
          <select value={form.carrierCode} onChange={e => setForm({ ...form, carrierCode: e.target.value })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" required>
            <option value="">{t('pickupForm.selectCarrier')}</option>
            {carriers.map(c => <option key={c.code} value={c.code}>{c.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">{t('pickupForm.pickupDate')}</label>
          <input type="date" value={form.pickupDate} onChange={e => setForm({ ...form, pickupDate: e.target.value })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">{t('pickupForm.readyTime')}</label>
          <input type="time" value={form.readyTime} onChange={e => setForm({ ...form, readyTime: e.target.value })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">{t('pickupForm.closeTime')}</label>
          <input type="time" value={form.closeTime} onChange={e => setForm({ ...form, closeTime: e.target.value })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
      </div>
      <fieldset className="border border-gray-100 rounded-lg p-4">
        <legend className="text-sm font-medium text-gray-600 px-1">{t('pickupForm.location')}</legend>
        <div className="grid grid-cols-2 gap-3">
          <div className="col-span-2"><input value={form.company} onChange={e => setForm({ ...form, company: e.target.value })} placeholder={t('pickupForm.company')} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
          <input value={form.contactName} onChange={e => setForm({ ...form, contactName: e.target.value })} placeholder={t('pickupForm.contactName')} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <input value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} placeholder={t('pickupForm.phone')} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <input value={form.country} onChange={e => setForm({ ...form, country: e.target.value })} placeholder={t('pickupForm.country')} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <input value={form.city} onChange={e => setForm({ ...form, city: e.target.value })} placeholder={t('pickupForm.city')} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <div className="col-span-2"><input value={form.address} onChange={e => setForm({ ...form, address: e.target.value })} placeholder={t('pickupForm.address')} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        </div>
      </fieldset>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">{t('pickupForm.packages')}</label>
          <input type="number" value={form.totalPackages} onChange={e => setForm({ ...form, totalPackages: +e.target.value })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">{t('pickupForm.totalWeight')}</label>
          <input type="number" step="0.1" value={form.totalWeight} onChange={e => setForm({ ...form, totalWeight: +e.target.value })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">{t('pickupForm.instructions')}</label>
        <input value={form.instructions} onChange={e => setForm({ ...form, instructions: e.target.value })}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" placeholder={t('pickupForm.ringReception')} />
      </div>
      <div className="flex gap-3 pt-2">
        <button type="button" onClick={onCancel} className="flex-1 px-4 py-2.5 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">{t('common.cancel')}</button>
        <button type="submit" disabled={saving}
          className="flex-1 px-4 py-2.5 bg-cargo-600 text-white rounded-lg text-sm font-medium hover:bg-cargo-700 disabled:opacity-50">
          {saving ? t('common.saving') : t('pickupForm.schedulePickup')}
        </button>
      </div>
    </form>
  )
}
