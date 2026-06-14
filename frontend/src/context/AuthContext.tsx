import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import * as authService from '../services/authService'

interface AuthState {
  user: authService.User | null; token: string | null; loading: boolean
  login: (email: string, password: string) => Promise<string | null>
  logout: () => Promise<void>; isAuthenticated: boolean
}

const AuthContext = createContext<AuthState>(null!)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<authService.User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const login = useCallback(async (email: string, password: string): Promise<string | null> => {
    setLoading(true)
    try {
      const res = await authService.login(email, password)
      if (res.success && res.user && res.token) {
        setUser(res.user); setToken(res.token); return null
      }
      return res.error || 'auth.loginFailed'
    } catch { return 'auth.networkError' }
    finally { setLoading(false) }
  }, [])

  const logout = useCallback(async () => {
    await authService.logout(); setUser(null); setToken(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
