from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.commission import Commission, MonthlyClosing, ClosingStatus
from app.models.user import User, UserRole
from app.schemas.commission import CommissionOut, MonthlyClosingOut, ClosingCreate
from app.core.dependencies import get_current_user, require_roles
from app.services.commission_calculator import CommissionCalculator

router = APIRouter(prefix="/financial", tags=["financial"])


@router.get("/commissions", response_model=list[CommissionOut])
async def list_commissions(
    period: str | None = None,
    affiliate_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = select(Commission)
    if period:
        q = q.where(Commission.period == period)
    if affiliate_id:
        q = q.where(Commission.affiliate_id == affiliate_id)
    q = q.order_by(Commission.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/closings", response_model=list[MonthlyClosingOut])
async def list_closings(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(MonthlyClosing).order_by(MonthlyClosing.period.desc()))
    return result.scalars().all()


@router.post("/closings", response_model=MonthlyClosingOut, status_code=201)
async def create_closing(
    data: ClosingCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FINANCIAL)),
):
    exists = await db.execute(select(MonthlyClosing).where(MonthlyClosing.period == data.period))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Closing already exists for this period")
    closing = MonthlyClosing(period=data.period, status=ClosingStatus.DRAFT)
    db.add(closing)
    await db.commit()
    await db.refresh(closing)
    return closing


@router.post("/closings/{closing_id}/calculate", response_model=MonthlyClosingOut)
async def calculate_closing(
    closing_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FINANCIAL)),
):
    result = await db.execute(select(MonthlyClosing).where(MonthlyClosing.id == closing_id))
    closing = result.scalar_one_or_none()
    if not closing:
        raise HTTPException(status_code=404, detail="Closing not found")
    if closing.status not in (ClosingStatus.DRAFT, ClosingStatus.REVIEW):
        raise HTTPException(status_code=400, detail="Closing already finalized")

    closing.status = ClosingStatus.CALCULATING
    await db.commit()

    calculator = CommissionCalculator(db)
    await calculator.calculate_period(closing)

    closing.status = ClosingStatus.REVIEW
    await db.commit()
    await db.refresh(closing)
    return closing


@router.post("/closings/{closing_id}/approve", response_model=MonthlyClosingOut)
async def approve_closing(
    closing_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN)),
):
    result = await db.execute(select(MonthlyClosing).where(MonthlyClosing.id == closing_id))
    closing = result.scalar_one_or_none()
    if not closing:
        raise HTTPException(status_code=404, detail="Closing not found")
    if closing.status != ClosingStatus.REVIEW:
        raise HTTPException(status_code=400, detail="Closing must be in review status")

    closing.status = ClosingStatus.APPROVED
    closing.closed_by = user.id
    closing.closed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(closing)
    return closing
