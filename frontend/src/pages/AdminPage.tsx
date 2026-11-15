import { useEffect, useState } from 'react'
import { PageHeader } from '../components/PageHeader'
import { ApiError } from '../services/api'
import type { User } from '../types'

export function AdminPage({ user }: { user: User }) {
  const [health, setHealth] = useState<'checking' | 'healthy' | 'unavailable'>('checking')
  useEffect(() => {
    fetch('/health').then((response) => setHealth(response.ok ? 'healthy' : 'unavailable')).catch(() => setHealth('unavailable'))
  }, [])
  const isAdmin = user.role === 'admin'
  const [access, setAccess] = useState<string | null>(null)
  useEffect(() => {
    if (!isAdmin) {
      setAccess('Administrator role required to view audit history.')
      return
    }
    const token = localStorage.getItem('eomp.accessToken')
    fetch(`${import.meta.env.VITE_API_BASE_URL ?? '/api/v1'}/admin/audit-logs?limit=1`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    }).then(async (response) => {
      if (!response.ok) throw new ApiError('Audit service did not authorize this request', response.status)
      setAccess('Audit log access verified. Use the API to query paginated audit history.')
    }).catch((error: unknown) => setAccess(error instanceof Error ? error.message : 'Audit service unavailable'))
  }, [isAdmin])

  return <><PageHeader title="Administration" description="Platform health, access controls and auditability." />
    <div className="admin-grid"><section className="panel"><div className="panel-heading"><div><h2>Platform health</h2><p>Application endpoint reachability</p></div></div><div className="health-row"><span className={`health-dot health-${health}`} />API service<span className={`health-label health-label-${health}`}>{health}</span></div><div className="health-row"><span className="health-dot health-healthy" />Current session<span className="health-label health-label-healthy">authenticated</span></div></section>
      <section className="panel"><div className="panel-heading"><div><h2>Access overview</h2><p>Signed-in account privileges</p></div></div><div className="access-profile"><div className="avatar large">{user.full_name.slice(0, 1).toUpperCase()}</div><div><strong>{user.full_name}</strong><span>{user.email}</span></div></div><div className="role-line"><span>Assigned role</span><span className="role-pill">{user.role}</span></div></section>
    </div>
    <section className="panel audit-panel"><div className="panel-heading"><div><h2>Audit history</h2><p>Administrative access to recorded business events</p></div></div><div className={isAdmin ? 'audit-state' : 'audit-state audit-denied'}>{access ?? 'Checking audit permissions…'}</div></section>
  </>
}
