import type { ReactNode } from 'react'
import { useTranslation } from '../i18n'

export interface Column<T> {
  key: string; header: string
  render?: (item: T) => ReactNode
  className?: string
}

interface Props<T> {
  columns: Column<T>[]; data: T[]
  onRowClick?: (item: T) => void
}

export default function DataTable<T extends Record<string, any>>({ columns, data, onRowClick }: Props<T>) {
  const { t } = useTranslation()

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            {columns.map(col => (
              <th key={col.key} className={`text-left px-4 py-3 font-medium text-gray-500 ${col.className || ''}`}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item, i) => (
            <tr
              key={item.id || i}
              onClick={() => onRowClick?.(item)}
              className={`border-b border-gray-50 ${onRowClick ? 'cursor-pointer hover:bg-gray-50' : ''}`}
            >
              {columns.map(col => (
                <td key={col.key} className={`px-4 py-3 ${col.className || ''}`}>
                  {col.render ? col.render(item) : item[col.key]}
                </td>
              ))}
            </tr>
          ))}
          {data.length === 0 && (
            <tr><td colSpan={columns.length} className="px-4 py-8 text-center text-gray-400">{t('common.noData')}</td></tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
