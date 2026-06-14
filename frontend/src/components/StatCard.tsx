import type { LucideIcon } from 'lucide-react'

interface Props {
  label: string; value: string | number; icon: LucideIcon
  sub?: string; color?: string
}

export default function StatCard({ label, value, icon: Icon, sub, color = 'text-cargo-600' }: Props) {
  return (
    <div className="card flex items-start gap-4">
      <div className={`p-3 rounded-lg bg-gray-50 ${color}`}>
        <Icon className="w-6 h-6" />
      </div>
      <div>
        <div className="stat-value">{typeof value === 'number' ? value.toLocaleString() : value}</div>
        <div className="stat-label">{label}</div>
        {sub && <div className="text-xs text-gray-400 mt-0.5">{sub}</div>}
      </div>
    </div>
  )
}
