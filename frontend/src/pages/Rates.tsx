import { useState } from 'react'
import { Search, ArrowRightLeft, Package, Loader2 } from 'lucide-react'
import { useApi } from '../hooks/useCargoService'
import * as cargoService from '../services/cargoService'
import { useTranslation } from '../i18n'

export default function Rates() {
  const { t } = useTranslation()
  const [from, setFrom] = useState('Paris, FR')
  const [to, setTo] = useState('Berlin, DE')
  const [weight, setWeight] = useState('2.5')
  const [searched, setSearched] = useState(false)

  const { data: rates, loading, error } = useApi(
    () => searched ? cargoService.getRates({
      sender: { country: 'FR', zipCode: '75001', city: from },
      recipient: { country: 'DE', zipCode: '10115', city: to },
      packages: [{ weight: parseFloat(weight) || 2.5, weightUnit: 'KG' }],
    }) : Promise.resolve({ success: true, data: [] }),
    [searched]
  )

  const handleSearch = () => setSearched(true)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('rates.title')}</h1>
        <p className="text-gray-500 mt-1">{t('rates.subtitle')}</p>
      </div>

      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-end">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-600 mb-1">{t('rates.from')}</label>
            <input value={from} onChange={e => setFrom(e.target.value)} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cargo-500" />
          </div>
          <div className="flex justify-center pb-2"><ArrowRightLeft className="w-5 h-5 text-gray-400" /></div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-600 mb-1">{t('rates.to')}</label>
            <input value={to} onChange={e => setTo(e.target.value)} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cargo-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">{t('rates.weight')}</label>
            <input type="number" value={weight} onChange={e => setWeight(e.target.value)} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cargo-500" />
          </div>
        </div>
        <button onClick={handleSearch} disabled={loading} className="mt-4 flex items-center gap-2 px-4 py-2 bg-cargo-600 text-white rounded-lg text-sm font-medium hover:bg-cargo-700 disabled:opacity-50 transition-colors">
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
          {loading ? t('rates.searching') : t('rates.getRates')}
        </button>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}

      {rates && rates.length > 0 && (
        <div className="space-y-3">
          {rates.map((rate, i) => (
            <div key={i} className="card flex items-center justify-between hover:shadow-md transition-shadow">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-gray-50"><Package className="w-5 h-5 text-cargo-600" /></div>
                <div>
                  <div className="font-semibold text-gray-900">{rate.carrierName}</div>
                  <div className="text-sm text-gray-500">{rate.serviceName}</div>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <div className="text-sm text-gray-500">{t('rates.days', { n: rate.estimatedTransitDays })}</div>
                  <div className="text-xs text-gray-400">{rate.estimatedDeliveryDate}</div>
                </div>
                <div className="text-right min-w-[80px]">
                  <div className="text-xl font-bold text-gray-900">{rate.totalPrice.toFixed(2)}</div>
                  <div className="text-xs text-gray-400">{rate.currency}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {rates && rates.length === 0 && searched && !loading && (
        <div className="text-center py-8 text-gray-400">{t('rates.noRates')}</div>
      )}
    </div>
  )
}
