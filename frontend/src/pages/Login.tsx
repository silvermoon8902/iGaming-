import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const form = new URLSearchParams()
      form.append('username', email)
      form.append('password', password)
      const { data } = await api.post('/auth/login', form)
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      navigate('/')
    } catch {
      setError('Credenciais inválidas')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      minHeight: '100vh', background: '#0b1226',
    }}>
      <form onSubmit={handleSubmit} style={{
        background: '#121c3f', border: '1px solid #1e2d5a', borderRadius: 16,
        padding: 40, width: 400,
      }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>🎰 Affiliate System</h1>
        <p style={{ color: '#94a3b8', marginBottom: 32 }}>iGaming Management Platform</p>

        {error && <p style={{ color: '#ef4444', marginBottom: 16, fontSize: 14 }}>{error}</p>}

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', fontSize: 13, color: '#94a3b8', marginBottom: 6 }}>Email</label>
          <input
            type="email" value={email} onChange={e => setEmail(e.target.value)}
            required style={{ width: '100%' }}
            placeholder="admin@example.com"
          />
        </div>

        <div style={{ marginBottom: 24 }}>
          <label style={{ display: 'block', fontSize: 13, color: '#94a3b8', marginBottom: 6 }}>Senha</label>
          <input
            type="password" value={password} onChange={e => setPassword(e.target.value)}
            required style={{ width: '100%' }}
            placeholder="••••••••"
          />
        </div>

        <button type="submit" className="btn-primary" disabled={loading}
          style={{ width: '100%', padding: '12px', fontSize: 15 }}>
          {loading ? 'Entrando...' : 'Entrar'}
        </button>
      </form>
    </div>
  )
}
