interface Props {
  title: string
  value: string | number
  subtitle?: string
  color?: string
}

export default function StatCard({ title, value, subtitle, color = '#4f7cff' }: Props) {
  return (
    <div style={{
      background: '#121c3f', border: '1px solid #1e2d5a', borderRadius: 12,
      padding: 20, borderTop: `3px solid ${color}`,
    }}>
      <p style={{ fontSize: 12, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
        {title}
      </p>
      <p style={{ fontSize: 28, fontWeight: 700, color: '#fff' }}>{value}</p>
      {subtitle && <p style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>{subtitle}</p>}
    </div>
  )
}
