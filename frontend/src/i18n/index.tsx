import { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import en from './locales/en'
import fr from './locales/fr'
import tr from './locales/tr'

export type Lang = 'en' | 'fr' | 'tr'

const messages: Record<Lang, any> = { en, fr, tr }

interface I18nCtx {
  lang: Lang
  setLang: (l: Lang) => void
  t: (path: string, vars?: Record<string, string | number>) => string
}

const I18nContext = createContext<I18nCtx>(null!)

function resolve(obj: any, path: string): any {
  return path.split('.').reduce((acc, key) => acc?.[key], obj)
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>('en')

  const t = useCallback((path: string, vars?: Record<string, string | number>) => {
    let val = resolve(messages[lang], path)
    if (val === undefined) val = resolve(messages.en, path)
    if (val === undefined) return path
    if (vars) {
      Object.entries(vars).forEach(([k, v]) => { val = String(val).replace(`{${k}}`, String(v)) })
    }
    return val
  }, [lang])

  return (
    <I18nContext.Provider value={{ lang, setLang, t }}>
      {children}
    </I18nContext.Provider>
  )
}

export function useTranslation() {
  return useContext(I18nContext)
}
