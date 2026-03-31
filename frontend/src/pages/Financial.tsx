import { useEffect, useState } from 'react'
import api from '../services/api'
import StatusBadge from '../components/StatusBadge'
import type { MonthlyClosing, Commission } from '../types'

const fmt = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)

export default function Financial() {
  const [closings, setClosings] = useState<MonthlyClosing[]>([])
  const [commissions, setCommissions] = useState<Commission[]>([])
  const [newPeriod, setNewPeriod] = useState('')
  const [selectedPeriod, setSelectedPeriod] = useState('')
  const [loading, setLoading] = useState('')

  const load = () => {
    api.get('/financial/closings').then(r => setClosings(r.data))
  }

  useEffect(() => { load() }, [])

  useEffect(() => {
    if (selectedPeriod) {
      api.get('/financial/commissions', { params: { period: selectedPeriod } }).then(r => setCommissions(r.data))
    }
  }, [selectedPeriod])

  const createClosing = async () => {
    if (!newPeriod) return
    await api.post('/financial/closings', { period: newPeriod })
    setNewPeriod('')
    load()
  }

  const calculate = async (id: number) => {
    setLoading(`calc-${id}`)
    await api.post(`/financial/closings/${id}/calculate`)
    setLoading('')
    load()
  }

  const approve = async (id: number) => {
    setLoading(`approve-${id}`)
    await api.post(`/financial/closings/${id}/approve`)
    setLoading('')
    load()
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700 }}>Financeiro</h1>
          <p style={{ color: '#94a3b8', fontSize: 14 }}>Fechamento mensal de comissões</p>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <input type="month" value={newPeriod} onChange={e => setNewPeriod(e.target.value)} />
          <button className="btn-primary" onClick={createClosing}>+ Novo Fechamento</button>
        </div>
      </div>

      <div style={{ background: '#121c3f', border: '1px solid #1e2d5a', borderRadius: 12, padding: 20, marginBottom: 24 }}>
        <h3 style={{ marginBottom: 16, fontSize: 16 }}>Fechamentos</h3>
        <table>
          <thead>
            <tr>
              <th>Período</th>
              <th>Status</th>
              <th>Afiliados</th>
              <th>Total Comissões</th>
              <th>Fechado em</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {closings.map(c => (
              <tr key={c.id}>
                <td style={{ fontWeight: 600 }}>{c.period}</td>
                <td><StatusBadge status={c.status} /></td>
                <td>{c.total_affiliates}</td>
                <td style={{ fontWeight: 600 }}>{fmt(c.total_commissions)}</td>
                <td style={{ color: '#64748b' }}>{c.closed_at ? new Date(c.closed_at).toLocaleDateString('pt-BR') : '—'}</td>
                <td style={{ display: 'flex', gap: 8 }}>
                  <button className="btn-secondary" style={{ padding: '4px 12px', fontSize: 12 }}
                    onClick={() => setSelectedPeriod(c.period)}>
                    Ver Detalhes
                  </button>
                  {(c.status === 'draft' || c.status === 'review') && (
                    <button className="btn-primary" style={{ padding: '4px 12px', fontSize: 12 }}
                      onClick={() => calculate(c.id)} disabled={loading === `calc-${c.id}`}>
                      {loading === `calc-${c.id}` ? 'Calculando...' : 'Calcular'}
                    </button>
                  )}
                  {c.status === 'review' && (
                    <button className="btn-success" style={{ padding: '4px 12px', fontSize: 12 }}
                      onClick={() => approve(c.id)} disabled={loading === `approve-${c.id}`}>
                      Aprovar
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {closings.length === 0 && (
              <tr><td colSpan={6} style={{ textAlign: 'center', color: '#64748b', padding: 40 }}>Nenhum fechamento criado</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {selectedPeriod && (
        <div style={{ background: '#121c3f', border: '1px solid #1e2d5a', borderRadius: 12, padding: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 style={{ fontSize: 16 }}>Comissões — {selectedPeriod}</h3>
            <button className="btn-secondary" style={{ padding: '4px 12px', fontSize: 12 }} onClick={() => setSelectedPeriod('')}>Fechar</button>
          </div>
          <table>
            <thead>
              <tr>
                <th>Afiliado</th>
                <th>Campanha</th>
                <th>FTD</th>
                <th>QFTD</th>
                <th>NGR</th>
                <th>CPA</th>
                <th>REV</th>
                <th>Ajustes</th>
                <th>Total</th>
                <th>Carry Over</th>
                <th>Notas</th>
              </tr>
            </thead>
            <tbody>
              {commissions.map(c => (
                <tr key={c.id}>
                  <td>#{c.affiliate_id}</td>
                  <td>#{c.campaign_id}</td>
                  <td>{c.ftd_count}</td>
                  <td>{c.qftd_count}</td>
                  <td>{fmt(c.ngr)}</td>
                  <td>{fmt(c.cpa_amount)}</td>
                  <td>{fmt(c.rev_amount)}</td>
                  <td>{fmt(c.adjustments)}</td>
                  <td style={{ fontWeight: 600, color: '#4ade80' }}>{fmt(c.total)}</td>
                  <td style={{ color: c.carry_over < 0 ? '#f87171' : '#64748b' }}>{fmt(c.carry_over)}</td>
                  <td style={{ fontSize: 12, color: '#94a3b8' }}>{c.notes || '—'}</td>
                </tr>
              ))}
              {commissions.length === 0 && (
                <tr><td colSpan={11} style={{ textAlign: 'center', color: '#64748b', padding: 40 }}>Sem comissões para este período</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
