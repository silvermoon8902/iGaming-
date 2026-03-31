export interface User {
  id: number
  email: string
  name: string
  role: string
  is_active: boolean
  created_at: string
}

export interface Affiliate {
  id: number
  name: string
  email: string
  contact: string | null
  status: 'active' | 'moderate' | 'low' | 'inactive'
  created_at: string
}

export interface Operator {
  id: number
  name: string
  api_endpoint: string | null
  is_active: boolean
  created_at: string
}

export interface Campaign {
  id: number
  name: string
  affiliate_id: number
  operator_id: number
  deal_type: 'cpa' | 'rev' | 'hybrid'
  cpa_value: number
  rev_percentage: number
  is_active: boolean
  created_at: string
}

export interface TrackingLink {
  id: number
  campaign_id: number
  token: string
  label: string | null
  url: string
  clicks: number
  created_at: string
}

export interface Commission {
  id: number
  affiliate_id: number
  campaign_id: number
  period: string
  ftd_count: number
  qftd_count: number
  deposits: number
  ngr: number
  cpa_amount: number
  rev_amount: number
  adjustments: number
  total: number
  carry_over: number
  notes: string | null
  created_at: string
}

export interface MonthlyClosing {
  id: number
  period: string
  status: 'draft' | 'calculating' | 'review' | 'approved' | 'paid'
  total_commissions: number
  total_affiliates: number
  closed_by: number | null
  closed_at: string | null
  created_at: string
}

export interface DashboardMetrics {
  total_ftd: number
  total_qftd: number
  total_ngr: number
  total_commissions: number
  total_affiliates: number
  total_campaigns: number
  total_deposits: number
}

export interface AffiliatePerformance {
  affiliate_id: number
  affiliate_name: string
  campaign_name: string
  ftd: number
  qftd: number
  ngr: number
  commissions: number
  status: string
}
