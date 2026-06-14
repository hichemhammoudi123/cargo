import { Globe } from 'lucide-react'
import { useTranslation } from '../i18n'
import type { Lang } from '../i18n'

const labels: Record<Lang, string> = { en: 'EN', fr: 'FR', tr: 'TR' }
const order: Lang[] = ['en', 'fr', 'tr']

export default function LanguageSwitcher() {
  const { lang, setLang } = useTranslation()
  const idx = order.indexOf(lang)
  const next = order[(idx + 1) % order.length]

  return (
    <button onClick={() => setLang(next)}
      className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-500 hover:text-cargo-600 hover:bg-cargo-50 rounded-lg transition-colors w-full">
      <Globe className="w-4 h-4" />
      <span className="font-medium">{labels[next]}</span>
    </button>
  )
}
