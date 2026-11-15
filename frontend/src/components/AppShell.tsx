import { BarChart3, Boxes, Building2, ClipboardList, LayoutDashboard, LogOut, Package, Users } from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'
import type { User } from '../types'

const navigation = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/orders', label: 'Orders', icon: ClipboardList },
  { to: '/products', label: 'Products', icon: Package },
  { to: '/inventory', label: 'Inventory', icon: Boxes },
  { to: '/customers', label: 'Customers', icon: Building2 },
  { to: '/reports', label: 'Reports', icon: BarChart3 },
  { to: '/admin', label: 'Administration', icon: Users },
]

export function AppShell({ user, onLogout }: { user: User; onLogout: () => void }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">E</span><span>EOMP<span className="brand-sub">OPERATIONS</span></span></div>
        <div className="workspace-label">WORKSPACE</div>
        <nav aria-label="Primary navigation">
          {navigation.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
              <Icon size={18} strokeWidth={1.8} /><span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="user-chip"><div className="avatar">{user.full_name.slice(0, 1).toUpperCase()}</div><div><strong>{user.full_name}</strong><span>{user.role}</span></div></div>
          <button className="logout-button" onClick={onLogout}><LogOut size={17} />Sign out</button>
        </div>
      </aside>
      <main className="main-content">
        <header className="topbar"><div><span className="eyebrow">OPERATIONS CONSOLE</span><span className="environment-tag">LIVE DATA</span></div><div className="topbar-user">{user.email}</div></header>
        <div className="page-content"><Outlet /></div>
      </main>
    </div>
  )
}
