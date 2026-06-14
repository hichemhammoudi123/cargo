import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Truck, DollarSign, Package,
  Building2, CalendarClock, Webhook,
  LogOut, User
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useTranslation } from '../i18n'
import LanguageSwitcher from './LanguageSwitcher'

const links = [
  { to: '/', labelKey: 'nav.dashboard', icon: LayoutDashboard },
  { to: '/rates', labelKey: 'nav.rates', icon: DollarSign },
  { to: '/shipments', labelKey: 'nav.shipments', icon: Package },
  { to: '/carriers', labelKey: 'nav.carriers', icon: Building2 },
  { to: '/pickups', labelKey: 'nav.pickups', icon: CalendarClock },
  { to: '/webhooks', labelKey: 'nav.webhooks', icon: Webhook },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const { t } = useTranslation()
  const nav = useNavigate()

  const handleLogout = async () => {
    await logout()
    nav('/login')
  }

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col shrink-0">
      <div className="h-16 flex items-center gap-2 px-6 border-b border-gray-100">
        <Truck className="w-6 h-6 text-cargo-600" />
        <span className="font-bold text-lg text-gray-900">{t('app.title')}</span>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {links.map(({ to, labelKey, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive ? 'bg-cargo-50 text-cargo-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <Icon className="w-5 h-5" />
            {t(labelKey)}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-100 space-y-2">
        <LanguageSwitcher />
        {user && (
          <div className="flex items-center gap-2 px-3 py-2 text-sm text-gray-500">
            <User className="w-4 h-4" />
            <span className="truncate">{user.name}</span>
            <span className="text-xs text-gray-400 ml-auto capitalize">{user.role}</span>
          </div>
        )}
        <button onClick={handleLogout}
          className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
          <LogOut className="w-4 h-4" />
          {t('nav.signOut')}
        </button>
      </div>
    </aside>
  )
}
