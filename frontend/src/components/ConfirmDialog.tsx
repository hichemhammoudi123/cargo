import { AlertTriangle, Loader2 } from 'lucide-react'
import { useTranslation } from '../i18n'

interface Props {
  open: boolean; onConfirm: () => void; onCancel: () => void
  title: string; message: string; loading?: boolean
  confirmLabel?: string; variant?: 'danger' | 'warning'
}

export default function ConfirmDialog({ open, onConfirm, onCancel, title, message, loading, confirmLabel, variant = 'danger' }: Props) {
  const { t } = useTranslation()
  if (!open) return null
  const btnClass = variant === 'danger'
    ? 'bg-red-600 hover:bg-red-700 text-white'
    : 'bg-amber-600 hover:bg-amber-700 text-white'
  const label = confirmLabel || t('confirmDialog.delete')

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-black/40 backdrop-blur-sm" onClick={onCancel} />
      <div className="relative w-full max-w-sm bg-white rounded-xl shadow-xl p-6 text-center">
        <div className={`mx-auto w-12 h-12 rounded-full flex items-center justify-center mb-4 ${variant === 'danger' ? 'bg-red-100' : 'bg-amber-100'}`}>
          <AlertTriangle className={`w-6 h-6 ${variant === 'danger' ? 'text-red-600' : 'text-amber-600'}`} />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
        <p className="text-sm text-gray-500 mb-6">{message}</p>
        <div className="flex gap-3">
          <button onClick={onCancel} disabled={loading}
            className="flex-1 px-4 py-2.5 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">{t('confirmDialog.cancel')}</button>
          <button onClick={onConfirm} disabled={loading}
            className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-medium disabled:opacity-50 ${btnClass}`}>
            {loading ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : label}
          </button>
        </div>
      </div>
    </div>
  )
}
