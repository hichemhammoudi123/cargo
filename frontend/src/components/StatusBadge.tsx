import { useTranslation } from '../i18n'

const colors: Record<string, string> = {
  CREATED: 'bg-blue-100 text-blue-700',
  VALIDATED: 'bg-indigo-100 text-indigo-700',
  PICKED_UP: 'bg-amber-100 text-amber-700',
  IN_TRANSIT: 'bg-cyan-100 text-cyan-700',
  OUT_FOR_DELIVERY: 'bg-purple-100 text-purple-700',
  DELIVERED: 'bg-green-100 text-green-700',
  FAILED: 'bg-red-100 text-red-700',
  CANCELLED: 'bg-gray-100 text-gray-500',
  CONFIRMED: 'bg-green-100 text-green-700',
  SCHEDULED: 'bg-blue-100 text-blue-700',
  PENDING: 'bg-yellow-100 text-yellow-700',
  COMPLETED: 'bg-green-100 text-green-700',
  CONNECTED: 'bg-green-100 text-green-700',
  DISCONNECTED: 'bg-red-100 text-red-700',
  PENDING_TEST: 'bg-yellow-100 text-yellow-700',
  ERROR: 'bg-red-100 text-red-700',
}

export default function StatusBadge({ status }: { status: string }) {
  const { t } = useTranslation()
  const cls = colors[status] || 'bg-gray-100 text-gray-600'
  const label = t(`status.${status}`, {}) || status.replace(/_/g, ' ')
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${cls}`}>
      {label}
    </span>
  )
}
