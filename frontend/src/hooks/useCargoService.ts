/**
 * ──────────────────────────────────────────────────────────────────────
 *  CARGO HOOKS — React Hooks for Cargo Service
 * ──────────────────────────────────────────────────────────────────────
 *  Chaque hook gère : loading, data, error, refetch.
 *  Pattern standard qui peut être remplacé par React Query / SWR plus tard.
 * ──────────────────────────────────────────────────────────────────────
 */

import { useState, useEffect, useCallback } from 'react'
import type { ApiResponse } from '../services/cargoService'

interface HookState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

type AsyncFn<T> = (...args: any[]) => Promise<ApiResponse<T>>

/**
 * Hook générique pour un appel API unique (au montage).
 */
export function useApi<T>(fetcher: () => Promise<ApiResponse<T>>, deps: any[] = []) {
  const [state, setState] = useState<HookState<T>>({ data: null, loading: true, error: null })

  const fetch = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }))
    try {
      const res = await fetcher()
      if (res.success) {
        setState({ data: res.data || null, loading: false, error: null })
      } else {
        setState({ data: null, loading: false, error: res.error?.message || 'Unknown error' })
      }
    } catch (err: any) {
      setState({ data: null, loading: false, error: err.message || 'Network error' })
    }
  }, deps)

  useEffect(() => { fetch() }, [fetch])

  return { ...state, refetch: fetch }
}

/**
 * Hook pour un appel API avec paramètre (ex: getShipmentById(id)).
 */
export function useApiById<T>(
  fetcher: (id: string) => Promise<ApiResponse<T>>,
  id: string | undefined
) {
  const [state, setState] = useState<HookState<T>>({ data: null, loading: !!id, error: null })

  const fetch = useCallback(async () => {
    if (!id) { setState({ data: null, loading: false, error: null }); return }
    setState(prev => ({ ...prev, loading: true, error: null }))
    try {
      const res = await fetcher(id)
      if (res.success) {
        setState({ data: res.data || null, loading: false, error: null })
      } else {
        setState({ data: null, loading: false, error: res.error?.message || 'Not found' })
      }
    } catch (err: any) {
      setState({ data: null, loading: false, error: err.message || 'Network error' })
    }
  }, [id])

  useEffect(() => { fetch() }, [fetch])

  return { ...state, refetch: fetch }
}

/**
 * Hook pour une action avec mutation (créer, annuler, etc.).
 * Retourne { execute, loading, error, data }
 */
export function useMutation<T, P extends any[]>(
  mutationFn: (...args: P) => Promise<ApiResponse<T>>
) {
  const [state, setState] = useState<HookState<T>>({ data: null, loading: false, error: null })

  const execute = useCallback(async (...args: P) => {
    setState({ data: null, loading: true, error: null })
    try {
      const res = await mutationFn(...args)
      if (res.success) {
        setState({ data: res.data || null, loading: false, error: null })
        return res.data || null
      } else {
        setState({ data: null, loading: false, error: res.error?.message || 'Mutation failed' })
        return null
      }
    } catch (err: any) {
      setState({ data: null, loading: false, error: err.message || 'Network error' })
      return null
    }
  }, [])

  return { ...state, execute }
}

/**
 * Simule un état "loading" minimal (pour les démos / transitions).
 */
export function useLoading(initial = false) {
  const [loading, setLoading] = useState(initial)
  const withLoading = useCallback(async <T>(fn: () => Promise<T>): Promise<T> => {
    setLoading(true)
    try { return await fn() }
    finally { setLoading(false) }
  }, [])
  return { loading, setLoading, withLoading }
}
