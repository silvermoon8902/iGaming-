from datetime import datetime
from pydantic import BaseModel

from app.models.affiliate import AffiliateStatus


class AffiliateCreate(BaseModel):
    name: str
    email: str
    contact: str | None = None
    status: AffiliateStatus = AffiliateStatus.ACTIVE


class AffiliateUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    contact: str | None = None
    status: AffiliateStatus | None = None


class AffiliateOut(BaseModel):
    id: int
    name: str
    email: str
    contact: str | None
    status: AffiliateStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class OperatorCreate(BaseModel):
    name: str
    api_endpoint: str | None = None
    api_key: str | None = None


class OperatorOut(BaseModel):
    id: int
    name: str
    api_endpoint: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
