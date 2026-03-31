from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.affiliate import Affiliate
from app.models.campaign import Campaign
from app.models.commission import Commission
from app.models.player_event import PlayerEvent, EventType
from app.models.user import User
from app.schemas.commission import DashboardMetrics, AffiliatePerformance
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
async def get_metrics(
    period: str | None = None,
    affiliate_id: int | None = None,
    operator_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    comm_q = select(
        func.coalesce(func.sum(Commission.ftd_count), 0),
        func.coalesce(func.sum(Commission.qftd_count), 0),
        func.coalesce(func.sum(Commission.ngr), 0),
        func.coalesce(func.sum(Commission.total), 0),
        func.coalesce(func.sum(Commission.deposits), 0),
    )
    if period:
        comm_q = comm_q.where(Commission.period == period)
    if affiliate_id:
        comm_q = comm_q.where(Commission.affiliate_id == affiliate_id)

    result = await db.execute(comm_q)
    row = result.one()

    aff_count = await db.execute(select(func.count(Affiliate.id)).where(Affiliate.status == "active"))
    camp_count = await db.execute(select(func.count(Campaign.id)).where(Campaign.is_active == True))

    return DashboardMetrics(
        total_ftd=int(row[0]),
        total_qftd=int(row[1]),
        total_ngr=float(row[2]),
        total_commissions=float(row[3]),
        total_affiliates=aff_count.scalar() or 0,
        total_campaigns=camp_count.scalar() or 0,
        total_deposits=float(row[4]),
    )


@router.get("/performance", response_model=list[AffiliatePerformance])
async def get_performance(
    period: str | None = None,
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = (
        select(
            Commission.affiliate_id,
            Affiliate.name.label("affiliate_name"),
            Campaign.name.label("campaign_name"),
            func.sum(Commission.ftd_count).label("ftd"),
            func.sum(Commission.qftd_count).label("qftd"),
            func.sum(Commission.ngr).label("ngr"),
            func.sum(Commission.total).label("commissions"),
            Affiliate.status,
        )
        .join(Affiliate, Commission.affiliate_id == Affiliate.id)
        .join(Campaign, Commission.campaign_id == Campaign.id)
        .group_by(Commission.affiliate_id, Affiliate.name, Campaign.name, Affiliate.status)
    )
    if period:
        q = q.where(Commission.period == period)
    q = q.order_by(func.sum(Commission.ngr).desc()).limit(limit)

    result = await db.execute(q)
    rows = result.all()
    return [
        AffiliatePerformance(
            affiliate_id=r.affiliate_id,
            affiliate_name=r.affiliate_name,
            campaign_name=r.campaign_name,
            ftd=int(r.ftd or 0),
            qftd=int(r.qftd or 0),
            ngr=float(r.ngr or 0),
            commissions=float(r.commissions or 0),
            status=r.status.value if hasattr(r.status, 'value') else str(r.status),
        )
        for r in rows
    ]
