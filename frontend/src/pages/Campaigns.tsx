import { useEffect, useState } from 'react'
import api from '../services/api'
import StatusBadge from '../components/StatusBadge'
import type { Campaign, Affiliate, Operator } from '../types'

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [affiliates, setAffiliates] = useState<Affiliate[]>([])
  const [operators, setOperators] = useState<Operator[]>([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    name: '', affiliate_id: '', operator_id: '', deal_type: 'cpa', cpa_value: '0', rev_percentage: '0',
  })

  const load = () => {
    api.get('/campaigns/').then(r => setCampaigns(r.data))
    api.get('/affiliates/').then(r => setAffiliates(r.data))
    api.get('/operators/').then(r => setOperators(r.data))
  }

  useEffect(() => { load() }, [])

  const save = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.post('/campaigns/', {
      ...form,
      affiliate_id: Number(form.affiliate_id),
      operator_id: Number(form.operator_id),
      cpa_value: Number(form.cpa_value),
      rev_percentage: Number(form.rev_percentage),
    })
    setShowForm(false)
    setForm({ name: '', affiliate_id: '', operator_id: '', deal_type: 'cpa', cpa_value: '0', rev_percentage: '0' })
    load()
  }

  const affMap = Object.fromEntries(affiliates.map(a => [a.id, a.name]))
  const opMap = Object.fromEntries(operators.map(o => [o.id, o.name]))

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>Campanhas</h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>+ Nova Campanha</button>
      </div>

      {showForm && (
        <form onSubmit={save} style={{
          background: '#121c3f', border: '1px solid #1e2d5a', borderRadius: 12,
          padding: 20, marginBottom: 24, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12,
        }}>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>Nome</label>
            <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required style={{ width: '100%' }} />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>Afiliado</label>
            <select value={form.affiliate_id} onChange={e => setForm({ ...form, affiliate_id: e.target.value })} required style={{ width: '100%' }}>
              <option value="">Selecione...</option>
              {affiliates.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
            </select>
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>Operadora</label>
            <select value={form.operator_id} onChange={e => setForm({ ...form, operator_id: e.target.value })} required style={{ width: '100%' }}>
              <option value="">Selecione...</option>
              {operators.map(o => <option key={o.id} value={o.id}>{o.name}</option>)}
            </select>
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>Tipo</label>
            <select value={form.deal_type} onChange={e => setForm({ ...form, deal_type: e.target.value })} style={{ width: '100%' }}>
              <option value="cpa">CPA</option>
              <option value="rev">REV Share</option>
              <option value="hybrid">Híbrido</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>Valor CPA ($)</label>
            <input type="number" step="0.01" value={form.cpa_value} onChange={e => setForm({ ...form, cpa_value: e.target.value })} style={{ width: '100%' }} />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>REV Share (%)</label>
            <input type="number" step="0.01" value={form.rev_percentage} onChange={e => setForm({ ...form, rev_percentage: e.target.value })} style={{ width: '100%' }} />
          </div>
          <div style={{ gridColumn: 'span 3', display: 'flex', justifyContent: 'flex-end' }}>
            <button type="submit" className="btn-primary">Criar Campanha</button>
          </div>
        </form>
      )}

      <div style={{ background: '#121c3f', border: '1px solid #1e2d5a', borderRadius: 12, padding: 20 }}>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nome</th>
              <th>Afiliado</th>
              <th>Operadora</th>
              <th>Tipo</th>
              <th>CPA</th>
              <th>REV %</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {campaigns.map(c => (
              <tr key={c.id}>
                <td>#{c.id}</td>
                <td style={{ fontWeight: 600 }}>{c.name}</td>
                <td>{affMap[c.affiliate_id] || c.affiliate_id}</td>
                <td>{opMap[c.operator_id] || c.operator_id}</td>
                <td><StatusBadge status={c.deal_type} /></td>
                <td>${c.cpa_value}</td>
                <td>{c.rev_percentage}%</td>
                <td><StatusBadge status={c.is_active ? 'active' : 'inactive'} /></td>
              </tr>
            ))}
            {campaigns.length === 0 && (
              <tr><td colSpan={8} style={{ textAlign: 'center', color: '#64748b', padding: 40 }}>Nenhuma campanha cadastrada</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
