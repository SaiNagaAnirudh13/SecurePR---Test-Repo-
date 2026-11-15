export function DataState({
  loading,
  error,
  empty,
}: {
  loading: boolean
  error: string | null
  empty: boolean
}) {
  if (loading) return <div className="state-message">Loading operational data…</div>
  if (error) return <div className="state-message state-error">{error}</div>
  if (empty) return <div className="state-message">No records found.</div>
  return null
}
