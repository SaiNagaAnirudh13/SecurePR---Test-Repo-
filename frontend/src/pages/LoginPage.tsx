import { useState, type FormEvent } from 'react'
import { ArrowRight, Boxes } from 'lucide-react'

export function LoginPage({ onLogin, error }: { onLogin: (email: string, password: string) => Promise<void>; error: string | null }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function submit(event: FormEvent) {
    event.preventDefault()
    setSubmitting(true)
    try {
      await onLogin(email, password)
    } catch {
      // The parent displays the authentication error.
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="login-page">
      <section className="login-panel">
        <div className="login-brand"><span className="brand-mark">E</span><span>EOMP<span className="brand-sub">OPERATIONS PLATFORM</span></span></div>
        <div className="login-copy"><span className="eyebrow">ENTERPRISE OPERATIONS</span><h1>Welcome back.</h1><p>Sign in to manage orders, inventory and fulfillment across your network.</p></div>
        <form onSubmit={submit} className="login-form">
          <label>Email address<input type="email" autoComplete="username" required value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@company.com" /></label>
          <label>Password<input type="password" autoComplete="current-password" required minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter your password" /></label>
          {error && <div role="alert" className="form-error">{error}</div>}
          <button className="primary-button login-submit" disabled={submitting}>{submitting ? 'Signing in…' : 'Sign in'}<ArrowRight size={17} /></button>
        </form>
        <p className="login-footnote"><Boxes size={15} />Secure access for authorized team members</p>
      </section>
      <section className="login-art"><div className="art-copy"><span>ONE PLATFORM. EVERY ORDER.</span><h2>Move your business<br />forward with clarity.</h2><p>Connected operations from first order to final delivery.</p></div><div className="art-grid" /></section>
    </main>
  )
}
