import enum
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AffiliateStatus(str, enum.Enum):
    ACTIVE = "active"
    MODERATE = "moderate"
    LOW = "low"
    INACTIVE = "inactive"


class Affiliate(Base):
    __tablename__ = "affiliates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    contact: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[AffiliateStatus] = mapped_column(Enum(AffiliateStatus), default=AffiliateStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    operators: Mapped[list["AffiliateOperator"]] = relationship(back_populates="affiliate", cascade="all, delete-orphan")
    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="affiliate", cascade="all, delete-orphan")


class AffiliateOperator(Base):
    __tablename__ = "affiliate_operators"

    id: Mapped[int] = mapped_column(primary_key=True)
    affiliate_id: Mapped[int] = mapped_column(ForeignKey("affiliates.id"))
    operator_id: Mapped[int] = mapped_column(ForeignKey("operators.id"))
    external_id: Mapped[str | None] = mapped_column(String(255))

    affiliate: Mapped["Affiliate"] = relationship(back_populates="operators")
    operator: Mapped["Operator"] = relationship()


from app.models.campaign import Campaign  # noqa: E402
from app.models.operator import Operator  # noqa: E402
