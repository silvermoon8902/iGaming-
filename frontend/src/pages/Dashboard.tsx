import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import api from '../services/api'
import StatCard from '../components/StatCard'
import StatusBadge from '../components/StatusBadge'
import type { DashboardMetrics, AffiliatePerformance } from '../types'

const fmt = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)
const COLORS = ['#4f7cff', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

export default function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [performance, setPerformance] = useState<AffiliatePerformance[]>([])
  const [period, setPeriod] = useState('')

  useEffect(() => {
    const params = period ? { period } : {}
    api.get('/dashboard/metrics', { params }).then(r => setMetrics(r.data)).catch(() => {})
    api.get('/dashboard/performance', { params }).then(r => setPerformance(r.data)).catch(() => {})
  }, [period])

  if (!metrics) return <p>Carregando...</p>

  const chartData = performance.map(p => ({
    name: p.affiliate_name,
    NGR: p.ngr,
    FTD: p.ftd,
    Comissões: p.commissions,
  }))

  const pieData = performance.map((p, i) => ({
    name: p.affiliate_name,
    value: p.ngr,
    color: COLORS[i % COLORS.length],
  }))

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700 }}>Dashboard</h1>
          <p style={{ color: '#94a3b8', fontSize: 14 }}>Visão geral da performance de afiliados</p>
        </div>
        <input type="month" value={period} onChange={e => setPeriod(e.target.value)}
          style={{ padding: '8px 12px' }} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        <StatCard title="FTD" value={metrics.total_ftd.toLocaleString()} color="#4f7cff" />
        <StatCard title="QFTD" value={metrics.total_qftd.toLocaleString()} color="#10b981" />
        <StatCard title="NGR" value={fmt(metrics.total_ngr)} color="#f59e0b" />
        <StatCard title="Comissões" value={fmt(metrics.total_commissions)} color="#ef4444" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 24 }}>
        <StatCard title="Afiliados Ativos" value={metrics.total_affiliates} color="#8b5cf6" />
        <StatCard title="Campanhas Ativas" value={metrics.total_campaigns} color="#06b6d4" />
        <StatCard title="Depósitos" value={fmt(metrics.total_deposits)} color="#10b981" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, marginBottom: 24 }}>
        <div style={{ background: '#121c3f', border: '1px solid #1e2d5a', borderRadius: 12, padding: 20 }}>
          <h3 style={{ marginBottom: 16, fontSize: 16 }}>Performance por Afiliado</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2d5a" />
              <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip contentStyle={{ background: '#1a2750', border: '1px solid #2a3b6b', borderRadius: 8 }} />
              <Bar dataKey="NGR" fill="#4f7cff" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Comissões" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={{ background: '#121c3f', border: '1px solid #1e2d5a', borderRadius: 12, padding: 20 }}>
          <h3 style={{ marginBottom: 16, fontSize: 16 }}>Distribuição NGR</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label={({ name }) => name}>
                {pieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#1a2750', border: '1px solid #2a3b6b', borderRadius: 8 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ background: '#121c3f', border: '1px solid #1e2d5a', borderRadius: 12, padding: 20 }}>
        <h3 style={{ marginBottom: 16, fontSize: 16 }}>Afiliados - Top Performance</h3>
        <table>
          <thead>
            <tr>
              <th>Afiliado</th>
              <th>Campanha</th>
              <th>FTD</th>
              <th>QFTD</th>
              <th>NGR</th>
              <th>Comissões</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {performance.map((p, i) => (
              <tr key={i}>
                <td style={{ fontWeight: 600 }}>{p.affiliate_name}</td>
                <td>{p.campaign_name}</td>
                <td>{p.ftd}</td>
                <td>{p.qftd}</td>
                <td>{fmt(p.ngr)}</td>
                <td>{fmt(p.commissions)}</td>
                <td><StatusBadge status={p.status} /></td>
              </tr>
            ))}
            {performance.length === 0 && (
              <tr><td colSpan={7} style={{ textAlign: 'center', color: '#64748b', padding: 40 }}>
                Nenhum dado disponível para o período selecionado
              </td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
