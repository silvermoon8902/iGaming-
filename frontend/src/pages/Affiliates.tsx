import { useEffect, useState } from 'react'
import api from '../services/api'
import StatusBadge from '../components/StatusBadge'
import type { Affiliate } from '../types'

export default function Affiliates() {
  const [affiliates, setAffiliates] = useState<Affiliate[]>([])
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', email: '', contact: '', status: 'active' })
  const [editing, setEditing] = useState<number | null>(null)

  const load = () => {
    api.get('/affiliates/', { params: search ? { search } : {} }).then(r => setAffiliates(r.data))
  }

  useEffect(() => { load() }, [search])

  const save = async (e: React.FormEvent) => {
    e.preventDefault()
    if (editing) {
      await api.put(`/affiliates/${editing}`, form)
    } else {
      await api.post('/affiliates/', form)
    }
    setShowForm(false)
    setEditing(null)
    setForm({ name: '', email: '', contact: '', status: 'active' })
    load()
  }

  const edit = (a: Affiliate) => {
    setForm({ name: a.name, email: a.email, contact: a.contact || '', status: a.status })
    setEditing(a.id)
    setShowForm(true)
  }

  const remove = async (id: number) => {
    if (confirm('Remover este afiliado?')) {
      await api.delete(`/affiliates/${id}`)
      load()
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>Afiliados</h1>
        <div style={{ display: 'flex', gap: 12 }}>
          <input placeholder="Buscar..." value={search} onChange={e => setSearch(e.target.value)} />
          <button className="btn-primary" onClick={() => { setShowForm(!showForm); setEditing(null); setForm({ name: '', email: '', contact: '', status: 'active' }) }}>
            + Novo Afiliado
          </button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={save} style={{
          background: '#121c3f', border: '1px solid #1e2d5a', borderRadius: 12,
          padding: 20, marginBottom: 24, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr auto', gap: 12, alignItems: 'end',
        }}>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>Nome</label>
            <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required style={{ width: '100%' }} />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>Email</label>
            <input type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} required style={{ width: '100%' }} />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>Contato</label>
            <input value={form.contact} onChange={e => setForm({ ...form, contact: e.target.value })} style={{ width: '100%' }} />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>Status</label>
            <select value={form.status} onChange={e => setForm({ ...form, status: e.target.value })} style={{ width: '100%' }}>
              <option value="active">Ativo</option>
              <option value="moderate">Moderado</option>
              <option value="low">Baixo</option>
              <option value="inactive">Inativo</option>
            </select>
          </div>
          <button type="submit" className="btn-primary">{editing ? 'Salvar' : 'Criar'}</button>
        </form>
      )}

      <div style={{ background: '#121c3f', border: '1px solid #1e2d5a', borderRadius: 12, padding: 20 }}>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nome</th>
              <th>Email</th>
              <th>Contato</th>
              <th>Status</th>
              <th>Criado em</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {affiliates.map(a => (
              <tr key={a.id}>
                <td>#{a.id}</td>
                <td style={{ fontWeight: 600 }}>{a.name}</td>
                <td>{a.email}</td>
                <td>{a.contact || '—'}</td>
                <td><StatusBadge status={a.status} /></td>
                <td style={{ color: '#64748b' }}>{new Date(a.created_at).toLocaleDateString('pt-BR')}</td>
                <td>
                  <button className="btn-secondary" style={{ marginRight: 8, padding: '4px 12px', fontSize: 12 }} onClick={() => edit(a)}>Editar</button>
                  <button className="btn-danger" style={{ padding: '4px 12px', fontSize: 12 }} onClick={() => remove(a.id)}>Remover</button>
                </td>
              </tr>
            ))}
            {affiliates.length === 0 && (
              <tr><td colSpan={7} style={{ textAlign: 'center', color: '#64748b', padding: 40 }}>Nenhum afiliado cadastrado</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
