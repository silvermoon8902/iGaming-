from datetime import datetime
from pydantic import BaseModel

from app.models.campaign import DealType
from app.models.commission import RuleType


class CampaignCreate(BaseModel):
    name: str
    affiliate_id: int
    operator_id: int
    deal_type: DealType
    cpa_value: float = 0
    rev_percentage: float = 0


class CampaignUpdate(BaseModel):
    name: str | None = None
    deal_type: DealType | None = None
    cpa_value: float | None = None
    rev_percentage: float | None = None
    is_active: bool | None = None


class CampaignOut(BaseModel):
    id: int
    name: str
    affiliate_id: int
    operator_id: int
    deal_type: DealType
    cpa_value: float
    rev_percentage: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TrackingLinkCreate(BaseModel):
    campaign_id: int
    label: str | None = None
    url: str


class TrackingLinkOut(BaseModel):
    id: int
    campaign_id: int
    token: str
    label: str | None
    url: str
    clicks: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RuleCreate(BaseModel):
    campaign_id: int
    rule_type: RuleType
    config: dict = {}


class RuleOut(BaseModel):
    id: int
    campaign_id: int
    rule_type: RuleType
    config: dict
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
