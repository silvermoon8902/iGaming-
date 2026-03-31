from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.campaign import Campaign, TrackingLink
from app.models.commission import CommissionRule
from app.models.user import User
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignOut,
    TrackingLinkCreate, TrackingLinkOut,
    RuleCreate, RuleOut,
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("/", response_model=list[CampaignOut])
async def list_campaigns(
    affiliate_id: int | None = None,
    operator_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = select(Campaign)
    if affiliate_id:
        q = q.where(Campaign.affiliate_id == affiliate_id)
    if operator_id:
        q = q.where(Campaign.operator_id == operator_id)
    q = q.order_by(Campaign.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=CampaignOut, status_code=201)
async def create_campaign(data: CampaignCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    c = Campaign(**data.model_dump())
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return c


@router.put("/{campaign_id}", response_model=CampaignOut)
async def update_campaign(campaign_id: int, data: CampaignUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    await db.commit()
    await db.refresh(c)
    return c


# Tracking Links
@router.get("/links", response_model=list[TrackingLinkOut])
async def list_links(
    campaign_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = select(TrackingLink)
    if campaign_id:
        q = q.where(TrackingLink.campaign_id == campaign_id)
    result = await db.execute(q.order_by(TrackingLink.created_at.desc()))
    return result.scalars().all()


@router.post("/links", response_model=TrackingLinkOut, status_code=201)
async def create_link(data: TrackingLinkCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    link = TrackingLink(**data.model_dump())
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


# Commission Rules
@router.get("/rules", response_model=list[RuleOut])
async def list_rules(
    campaign_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = select(CommissionRule)
    if campaign_id:
        q = q.where(CommissionRule.campaign_id == campaign_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/rules", response_model=RuleOut, status_code=201)
async def create_rule(data: RuleCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    rule = CommissionRule(**data.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule
