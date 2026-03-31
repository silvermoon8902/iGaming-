import { useState } from 'react'
import api from '../services/api'

export default function Import() {
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<{ imported: number; errors: number; error_details: { row: number; error: string }[] } | null>(null)
  const [loading, setLoading] = useState(false)

  const upload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return
    setLoading(true)
    setResult(null)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await api.post('/import/events', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResult(data)
    } catch (err: any) {
      setResult({ imported: 0, errors: 1, error_details: [{ row: 0, error: err.response?.data?.detail || 'Upload failed' }] })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 24 }}>Importar Dados</h1>

      <div style={{ background: '#121c3f', border: '1px solid #1e2d5a', borderRadius: 12, padding: 24, marginBottom: 24 }}>
        <h3 style={{ marginBottom: 16, fontSize: 16 }}>Upload de Eventos de Jogadores</h3>
        <p style={{ color: '#94a3b8', fontSize: 14, marginBottom: 16 }}>
          Faça upload de um arquivo CSV ou Excel com as colunas:
          <code style={{ background: '#182357', padding: '2px 8px', borderRadius: 4, marginLeft: 8 }}>
            tracking_link_id, player_external_id, event_type, amount, currency, event_date
          </code>
        </p>
        <p style={{ color: '#64748b', fontSize: 13, marginBottom: 24 }}>
          Tipos de evento aceitos: registration, ftd, qftd, deposit, withdrawal, bet, win
        </p>

        <form onSubmit={upload} style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <input type="file" accept=".csv,.xlsx,.xls"
            onChange={e => setFile(e.target.files?.[0] || null)}
            style={{ flex: 1 }}
          />
          <button type="submit" className="btn-primary" disabled={!file || loading}>
            {loading ? 'Importando...' : 'Importar'}
          </button>
        </form>
      </div>

      {result && (
        <div style={{ background: '#121c3f', border: '1px solid #1e2d5a', borderRadius: 12, padding: 24 }}>
          <h3 style={{ marginBottom: 16, fontSize: 16 }}>Resultado da Importação</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
            <div style={{ background: '#1f5c3a', padding: 16, borderRadius: 8 }}>
              <p style={{ fontSize: 28, fontWeight: 700 }}>{result.imported}</p>
              <p style={{ fontSize: 13, color: '#94a3b8' }}>Registros importados</p>
            </div>
            <div style={{ background: result.errors > 0 ? '#5c1f1f' : '#182357', padding: 16, borderRadius: 8 }}>
              <p style={{ fontSize: 28, fontWeight: 700 }}>{result.errors}</p>
              <p style={{ fontSize: 13, color: '#94a3b8' }}>Erros</p>
            </div>
          </div>

          {result.error_details.length > 0 && (
            <div>
              <h4 style={{ fontSize: 14, marginBottom: 8, color: '#f87171' }}>Detalhes dos erros:</h4>
              <table>
                <thead><tr><th>Linha</th><th>Erro</th></tr></thead>
                <tbody>
                  {result.error_details.map((e, i) => (
                    <tr key={i}><td>{e.row}</td><td style={{ color: '#f87171' }}>{e.error}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
