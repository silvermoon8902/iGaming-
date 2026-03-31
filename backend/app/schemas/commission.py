from datetime import datetime
from pydantic import BaseModel

from app.models.commission import ClosingStatus


class CommissionOut(BaseModel):
    id: int
    affiliate_id: int
    campaign_id: int
    period: str
    ftd_count: int
    qftd_count: int
    deposits: float
    ngr: float
    cpa_amount: float
    rev_amount: float
    adjustments: float
    total: float
    carry_over: float
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MonthlyClosingOut(BaseModel):
    id: int
    period: str
    status: ClosingStatus
    total_commissions: float
    total_affiliates: int
    closed_by: int | None
    closed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ClosingCreate(BaseModel):
    period: str  # YYYY-MM


class DashboardMetrics(BaseModel):
    total_ftd: int
    total_qftd: int
    total_ngr: float
    total_commissions: float
    total_affiliates: int
    total_campaigns: int
    total_deposits: float


class AffiliatePerformance(BaseModel):
    affiliate_id: int
    affiliate_name: str
    campaign_name: str
    ftd: int
    qftd: int
    ngr: float
    commissions: float
    status: str
