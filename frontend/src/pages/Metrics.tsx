import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import api from '../services/api'
import StatCard from '../components/StatCard'
import type { Commission } from '../types'

const fmt = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)

export default function Metrics() {
  const [commissions, setCommissions] = useState<Commission[]>([])
  const [affiliateId, setAffiliateId] = useState('')
  const [affiliates, setAffiliates] = useState<{ id: number; name: string }[]>([])

  useEffect(() => {
    api.get('/affiliates/').then(r => setAffiliates(r.data))
  }, [])

  useEffect(() => {
    const params: Record<string, string> = {}
    if (affiliateId) params.affiliate_id = affiliateId
    api.get('/financial/commissions', { params: { ...params, limit: 100 } }).then(r => setCommissions(r.data))
  }, [affiliateId])

  const byPeriod = commissions.reduce<Record<string, { period: string; ngr: number; commissions: number; ftd: number; deposits: number }>>((acc, c) => {
    if (!acc[c.period]) acc[c.period] = { period: c.period, ngr: 0, commissions: 0, ftd: 0, deposits: 0 }
    acc[c.period].ngr += c.ngr
    acc[c.period].commissions += c.total
    acc[c.period].ftd += c.ftd_count
    acc[c.period].deposits += c.deposits
    return acc
  }, {})

  const chartData = Object.values(byPeriod).sort((a, b) => a.period.localeCompare(b.period))

  const totals = commissions.reduce((acc, c) => ({
    ngr: acc.ngr + c.ngr,
    commissions: acc.commissions + c.total,
    ftd: acc.ftd + c.ftd_count,
    qftd: acc.qftd + c.qftd_count,
  }), { ngr: 0, commissions: 0, ftd: 0, qftd: 0 })

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>Métricas</h1>
        <select value={affiliateId} onChange={e => setAffiliateId(e.target.value)} style={{ minWidth: 200 }}>
          <option value="">Todos os afiliados</option>
          {affiliates.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
        </select>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        <StatCard title="Total FTD" value={totals.ftd} color="#4f7cff" />
        <StatCard title="Total QFTD" value={totals.qftd} color="#10b981" />
        <StatCard title="NGR Total" value={fmt(totals.ngr)} color="#f59e0b" />
        <StatCard title="Comissões Total" value={fmt(totals.commissions)} color="#ef4444" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
        <div style={{ background: '#121c3f', border: '1px solid #1e2d5a', borderRadius: 12, padding: 20 }}>
          <h3 style={{ marginBottom: 16, fontSize: 16 }}>NGR por Período</h3>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2d5a" />
              <XAxis dataKey="period" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip contentStyle={{ background: '#1a2750', border: '1px solid #2a3b6b', borderRadius: 8 }} />
              <Area type="monotone" dataKey="ngr" stroke="#4f7cff" fill="rgba(79,124,255,0.2)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div style={{ background: '#121c3f', border: '1px solid #1e2d5a', borderRadius: 12, padding: 20 }}>
          <h3 style={{ marginBottom: 16, fontSize: 16 }}>FTD por Período</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2d5a" />
              <XAxis dataKey="period" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip contentStyle={{ background: '#1a2750', border: '1px solid #2a3b6b', borderRadius: 8 }} />
              <Line type="monotone" dataKey="ftd" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ background: '#121c3f', border: '1px solid #1e2d5a', borderRadius: 12, padding: 20 }}>
        <h3 style={{ marginBottom: 16, fontSize: 16 }}>Detalhamento de Comissões</h3>
        <table>
          <thead>
            <tr>
              <th>Período</th>
              <th>Campanha</th>
              <th>FTD</th>
              <th>QFTD</th>
              <th>NGR</th>
              <th>CPA</th>
              <th>REV</th>
              <th>Total</th>
              <th>Carry Over</th>
            </tr>
          </thead>
          <tbody>
            {commissions.map(c => (
              <tr key={c.id}>
                <td>{c.period}</td>
                <td>#{c.campaign_id}</td>
                <td>{c.ftd_count}</td>
                <td>{c.qftd_count}</td>
                <td>{fmt(c.ngr)}</td>
                <td>{fmt(c.cpa_amount)}</td>
                <td>{fmt(c.rev_amount)}</td>
                <td style={{ fontWeight: 600, color: '#4ade80' }}>{fmt(c.total)}</td>
                <td style={{ color: c.carry_over < 0 ? '#f87171' : '#64748b' }}>{fmt(c.carry_over)}</td>
              </tr>
            ))}
            {commissions.length === 0 && (
              <tr><td colSpan={9} style={{ textAlign: 'center', color: '#64748b', padding: 40 }}>Sem dados de comissões</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
