import { useState } from 'react'
import { useTranslation } from '../../i18n'
import type { Shipment } from '../../types'

interface Props {
  initial?: Partial<Shipment>
  carriers: Array<{ code: string; name: string; services: Array<{ code: string; name: string }> }>
  onSave: (data: any) => Promise<void>; onCancel: () => void; saving?: boolean
}

export default function ShipmentForm({ initial, carriers, onSave, onCancel, saving }: Props) {
  const { t } = useTranslation()
  const [form, setForm] = useState({
    carrierCode: initial?.carrierCode || '', serviceCode: initial?.serviceCode || '',
    reference: initial?.reference || '',
    senderCompany: (initial?.sender as any)?.company || '', senderCountry: (initial?.sender as any)?.country || 'FR',
    senderCity: (initial?.sender as any)?.city || '', senderZip: (initial?.sender as any)?.zipCode || '',
    recipientCompany: (initial?.recipient as any)?.company || '', recipientCountry: (initial?.recipient as any)?.country || '',
    recipientCity: (initial?.recipient as any)?.city || '', recipientZip: (initial?.recipient as any)?.zipCode || '',
    weight: 2.5, signatureRequired: false,
  })

  const selectedCarrier = carriers.find(c => c.code === form.carrierCode)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await onSave({
      carrierCode: form.carrierCode, serviceCode: form.serviceCode, reference: form.reference,
      sender: { company: form.senderCompany, country: form.senderCountry, city: form.senderCity, zipCode: form.senderZip },
      recipient: { company: form.recipientCompany, country: form.recipientCountry, city: form.recipientCity, zipCode: form.recipientZip },
      packages: [{ reference: 'PARCEL-001', weight: form.weight, weightUnit: 'KG' }],
      options: { signatureRequired: form.signatureRequired },
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">{t('shipmentForm.carrier')}</label>
          <select value={form.carrierCode} onChange={e => { setForm({ ...form, carrierCode: e.target.value, serviceCode: '' }) }}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cargo-500" required>
            <option value="">{t('shipmentForm.selectCarrier')}</option>
            {carriers.map(c => <option key={c.code} value={c.code}>{c.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">{t('shipmentForm.service')}</label>
          <select value={form.serviceCode} onChange={e => setForm({ ...form, serviceCode: e.target.value })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cargo-500" required>
            <option value="">{t('shipmentForm.selectService')}</option>
            {selectedCarrier?.services.filter(s => s.code).map(s => <option key={s.code} value={s.code}>{s.name}</option>)}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">{t('shipmentForm.reference')}</label>
        <input value={form.reference} onChange={e => setForm({ ...form, reference: e.target.value })}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cargo-500" placeholder="ORD-2026-..." />
      </div>

      <fieldset className="border border-gray-100 rounded-lg p-4">
        <legend className="text-sm font-medium text-gray-600 px-1">{t('shipmentForm.sender')}</legend>
        <div className="grid grid-cols-2 gap-3">
          <div className="col-span-2"><input value={form.senderCompany} onChange={e => setForm({ ...form, senderCompany: e.target.value })} placeholder={t('shipmentForm.company')} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cargo-500" /></div>
          <input value={form.senderCountry} onChange={e => setForm({ ...form, senderCountry: e.target.value })} placeholder={t('shipmentForm.country')} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <input value={form.senderZip} onChange={e => setForm({ ...form, senderZip: e.target.value })} placeholder={t('shipmentForm.zip')} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <div className="col-span-2"><input value={form.senderCity} onChange={e => setForm({ ...form, senderCity: e.target.value })} placeholder={t('shipmentForm.city')} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        </div>
      </fieldset>

      <fieldset className="border border-gray-100 rounded-lg p-4">
        <legend className="text-sm font-medium text-gray-600 px-1">{t('shipmentForm.recipient')}</legend>
        <div className="grid grid-cols-2 gap-3">
          <div className="col-span-2"><input value={form.recipientCompany} onChange={e => setForm({ ...form, recipientCompany: e.target.value })} placeholder={t('shipmentForm.company')} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
          <input value={form.recipientCountry} onChange={e => setForm({ ...form, recipientCountry: e.target.value })} placeholder={t('shipmentForm.country')} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <input value={form.recipientZip} onChange={e => setForm({ ...form, recipientZip: e.target.value })} placeholder={t('shipmentForm.zip')} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <div className="col-span-2"><input value={form.recipientCity} onChange={e => setForm({ ...form, recipientCity: e.target.value })} placeholder={t('shipmentForm.city')} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
        </div>
      </fieldset>

      <div className="grid grid-cols-2 gap-4 items-end">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">{t('shipmentForm.weight')}</label>
          <input type="number" step="0.1" value={form.weight} onChange={e => setForm({ ...form, weight: +e.target.value })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
        <label className="flex items-center gap-2 py-2 text-sm text-gray-600">
          <input type="checkbox" checked={form.signatureRequired} onChange={e => setForm({ ...form, signatureRequired: e.target.checked })} className="rounded border-gray-300" />
          {t('shipmentForm.signatureRequired')}
        </label>
      </div>

      <div className="flex gap-3 pt-2">
        <button type="button" onClick={onCancel} className="flex-1 px-4 py-2.5 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">{t('common.cancel')}</button>
        <button type="submit" disabled={saving}
          className="flex-1 px-4 py-2.5 bg-cargo-600 text-white rounded-lg text-sm font-medium hover:bg-cargo-700 disabled:opacity-50">
          {saving ? t('common.saving') : initial ? t('shipmentForm.updateShipment') : t('shipmentForm.createShipment')}
        </button>
      </div>
    </form>
  )
}
