import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Truck, Loader2, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n'

export default function Login() {
  const [email, setEmail] = useState('admin@cargo.com')
  const [password, setPassword] = useState('admin')
  const [showPw, setShowPw] = useState(false)
  const [error, setError] = useState('')
  const { login, loading, isAuthenticated } = useAuth()
  const { t } = useTranslation()
  const nav = useNavigate()

  if (isAuthenticated) { nav('/', { replace: true }); return null }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); setError('')
    const err = await login(email, password)
    if (err) setError(err)
    else nav('/', { replace: true })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-cargo-50 via-white to-cargo-100">
      <div className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <div className="inline-flex p-3 rounded-2xl bg-cargo-100 mb-4">
            <Truck className="w-10 h-10 text-cargo-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">{t('app.title')}</h1>
          <p className="text-gray-500 mt-1">{t('auth.signInTitle')}</p>
        </div>

        <form onSubmit={handleSubmit} className="card space-y-4">
          {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">{t('auth.email')}</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)}
              className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cargo-500 focus:border-transparent"
              placeholder="admin@cargo.com" required />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">{t('auth.password')}</label>
            <div className="relative">
              <input type={showPw ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)}
                className="w-full px-3 py-2.5 pr-10 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cargo-500 focus:border-transparent"
                placeholder="••••••" required />
              <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button type="submit" disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-2.5 bg-cargo-600 text-white rounded-lg text-sm font-medium hover:bg-cargo-700 disabled:opacity-50 transition-colors">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
            {loading ? t('auth.signingIn') : t('auth.signIn')}
          </button>

          <p className="text-xs text-gray-400 text-center pt-2">{t('auth.demoHint')}</p>
        </form>
      </div>
    </div>
  )
}
