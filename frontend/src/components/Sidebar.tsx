import { NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Users, Megaphone, BarChart3, DollarSign, Upload, Settings, LogOut } from 'lucide-react'

const links = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/affiliates', icon: Users, label: 'Afiliados' },
  { to: '/campaigns', icon: Megaphone, label: 'Campanhas' },
  { to: '/metrics', icon: BarChart3, label: 'Métricas' },
  { to: '/financial', icon: DollarSign, label: 'Financeiro' },
  { to: '/import', icon: Upload, label: 'Importar Dados' },
]

export default function Sidebar() {
  const navigate = useNavigate()
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  return (
    <aside style={{
      width: 260, background: '#101935', borderRight: '1px solid #1e2d5a',
      display: 'flex', flexDirection: 'column', padding: '20px 12px', height: '100vh', position: 'fixed',
    }}>
      <div style={{ marginBottom: 32, padding: '0 8px' }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, color: '#fff' }}>🎰 Affiliate System</h2>
        <p style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>iGaming Management</p>
      </div>

      <nav style={{ flex: 1 }}>
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            style={({ isActive }) => ({
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '10px 12px', borderRadius: 8, marginBottom: 4,
              color: isActive ? '#4f7cff' : '#94a3b8',
              background: isActive ? 'rgba(79,124,255,0.1)' : 'transparent',
              textDecoration: 'none', fontSize: 14, fontWeight: 500,
              transition: 'all 0.2s',
            })}
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div style={{ borderTop: '1px solid #1e2d5a', paddingTop: 16 }}>
        <div style={{ padding: '8px 12px', fontSize: 13, color: '#94a3b8' }}>
          {user.name || 'User'}
          <br />
          <span style={{ fontSize: 11, color: '#64748b' }}>{user.role}</span>
        </div>
        <button onClick={logout} style={{
          display: 'flex', alignItems: 'center', gap: 8, width: '100%',
          padding: '10px 12px', background: 'transparent', color: '#ef4444',
          fontSize: 14, borderRadius: 8,
        }}>
          <LogOut size={16} /> Sair
        </button>
      </div>
    </aside>
  )
}
