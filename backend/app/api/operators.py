from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.operator import Operator
from app.models.user import User
from app.schemas.affiliate import OperatorCreate, OperatorOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/operators", tags=["operators"])


@router.get("/", response_model=list[OperatorOut])
async def list_operators(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Operator).order_by(Operator.name))
    return result.scalars().all()


@router.post("/", response_model=OperatorOut, status_code=201)
async def create_operator(data: OperatorCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    op = Operator(**data.model_dump())
    db.add(op)
    await db.commit()
    await db.refresh(op)
    return op


@router.delete("/{operator_id}", status_code=204)
async def delete_operator(operator_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Operator).where(Operator.id == operator_id))
    op = result.scalar_one_or_none()
    if not op:
        raise HTTPException(status_code=404, detail="Operator not found")
    await db.delete(op)
    await db.commit()
