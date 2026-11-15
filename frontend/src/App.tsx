import { useEffect, useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { AdminPage } from './pages/AdminPage'
import { CustomersPage } from './pages/CustomersPage'
import { DashboardPage } from './pages/DashboardPage'
import { InventoryPage } from './pages/InventoryPage'
import { LoginPage } from './pages/LoginPage'
import { OrdersPage } from './pages/OrdersPage'
import { ProductsPage } from './pages/ProductsPage'
import { ReportsPage } from './pages/ReportsPage'
import { api } from './services/api'
import type { User } from './types'

export default function App() {
  const [user, setUser] = useState<User | null>(null)
  const [checking, setChecking] = useState(true)
  const [loginError, setLoginError] = useState<string | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('eomp.accessToken')
    if (!token) {
      setChecking(false)
      return
    }
    api.me().then(setUser).catch(() => localStorage.removeItem('eomp.accessToken')).finally(() => setChecking(false))
  }, [])

  async function login(email: string, password: string) {
    setLoginError(null)
    try {
      const result = await api.login(email, password)
      localStorage.setItem('eomp.accessToken', result.access_token)
      setUser(result.user)
    } catch (error) {
      setLoginError(error instanceof Error ? error.message : 'Unable to sign in')
      throw error
    }
  }

  function logout() {
    localStorage.removeItem('eomp.accessToken')
    setUser(null)
  }

  if (checking) return <div className="app-loading">Loading your workspace…</div>
  if (!user) return <LoginPage onLogin={login} error={loginError} />

  return <BrowserRouter><Routes><Route element={<AppShell user={user} onLogout={logout} />}>
    <Route index element={<DashboardPage />} />
    <Route path="orders" element={<OrdersPage />} />
    <Route path="products" element={<ProductsPage />} />
    <Route path="inventory" element={<InventoryPage />} />
    <Route path="customers" element={<CustomersPage />} />
    <Route path="reports" element={<ReportsPage />} />
    <Route path="admin" element={<AdminPage user={user} />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Route></Routes></BrowserRouter>
}
