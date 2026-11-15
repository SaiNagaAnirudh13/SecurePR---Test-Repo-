import { useCallback, useEffect, useState } from 'react'

export function useResource<T>(load: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setData(await load())
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to load data')
    } finally {
      setLoading(false)
    }
  }, [load])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return { data, error, loading, refresh }
}
