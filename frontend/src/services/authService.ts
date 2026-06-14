export interface User {
  email: string; name: string; role: 'admin' | 'operator' | 'viewer'
}

export interface AuthResponse {
  success: boolean; user?: User; token?: string; error?: string
}

const delay = (ms = 400) => new Promise(r => setTimeout(r, ms))

export async function login(email: string, password: string): Promise<AuthResponse> {
  await delay()
  if (!email || !password) return { success: false, error: 'Email and password required' }
  if (password.length < 3) return { success: false, error: 'Invalid credentials' }
  return {
    success: true, user: { email, name: email.split('@')[0], role: 'admin' }, token: 'mock-jwt-' + Math.random().toString(36).substring(2)
  }
}

export async function logout(): Promise<void> { await delay(100) }
