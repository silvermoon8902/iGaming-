const colors: Record<string, { bg: string; text: string }> = {
  active: { bg: '#1f5c3a', text: '#4ade80' },
  moderate: { bg: '#5c4d1f', text: '#fbbf24' },
  low: { bg: '#5c1f1f', text: '#f87171' },
  inactive: { bg: '#374151', text: '#9ca3af' },
  draft: { bg: '#374151', text: '#9ca3af' },
  calculating: { bg: '#5c4d1f', text: '#fbbf24' },
  review: { bg: '#1e3a5f', text: '#60a5fa' },
  approved: { bg: '#1f5c3a', text: '#4ade80' },
  paid: { bg: '#1f5c3a', text: '#4ade80' },
  cpa: { bg: '#3b1f5c', text: '#a78bfa' },
  rev: { bg: '#1e3a5f', text: '#60a5fa' },
  hybrid: { bg: '#5c4d1f', text: '#fbbf24' },
}

export default function StatusBadge({ status }: { status: string }) {
  const c = colors[status] || colors.inactive
  return (
    <span style={{
      padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600,
      background: c.bg, color: c.text, textTransform: 'capitalize',
    }}>
      {status}
    </span>
  )
}
