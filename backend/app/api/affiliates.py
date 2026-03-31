from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.affiliate import Affiliate
from app.models.user import User, UserRole
from app.schemas.affiliate import AffiliateCreate, AffiliateUpdate, AffiliateOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/affiliates", tags=["affiliates"])


@router.get("/", response_model=list[AffiliateOut])
async def list_affiliates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    status: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = select(Affiliate)
    if status:
        q = q.where(Affiliate.status == status)
    if search:
        q = q.where(Affiliate.name.ilike(f"%{search}%"))
    q = q.order_by(Affiliate.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/count")
async def count_affiliates(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(func.count(Affiliate.id)))
    return {"count": result.scalar()}


@router.get("/{affiliate_id}", response_model=AffiliateOut)
async def get_affiliate(affiliate_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Affiliate).where(Affiliate.id == affiliate_id))
    aff = result.scalar_one_or_none()
    if not aff:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    return aff


@router.post("/", response_model=AffiliateOut, status_code=201)
async def create_affiliate(data: AffiliateCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    aff = Affiliate(**data.model_dump())
    db.add(aff)
    await db.commit()
    await db.refresh(aff)
    return aff


@router.put("/{affiliate_id}", response_model=AffiliateOut)
async def update_affiliate(affiliate_id: int, data: AffiliateUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Affiliate).where(Affiliate.id == affiliate_id))
    aff = result.scalar_one_or_none()
    if not aff:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(aff, k, v)
    await db.commit()
    await db.refresh(aff)
    return aff


@router.delete("/{affiliate_id}", status_code=204)
async def delete_affiliate(affiliate_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Affiliate).where(Affiliate.id == affiliate_id))
    aff = result.scalar_one_or_none()
    if not aff:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    await db.delete(aff)
    await db.commit()
