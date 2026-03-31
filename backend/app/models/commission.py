import enum
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, ForeignKey, Numeric, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RuleType(str, enum.Enum):
    CARRY_OVER = "carry_over"
    NON_CARRY_OVER = "non_carry_over"
    BASELINE = "baseline"
    MIN_QUALIFICATION = "min_qualification"


class ClosingStatus(str, enum.Enum):
    DRAFT = "draft"
    CALCULATING = "calculating"
    REVIEW = "review"
    APPROVED = "approved"
    PAID = "paid"


class CommissionRule(Base):
    __tablename__ = "commission_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    rule_type: Mapped[RuleType] = mapped_column(Enum(RuleType))
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    campaign: Mapped["Campaign"] = relationship(back_populates="rules")


class Commission(Base):
    __tablename__ = "commissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    affiliate_id: Mapped[int] = mapped_column(ForeignKey("affiliates.id"), index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
    closing_id: Mapped[int | None] = mapped_column(ForeignKey("monthly_closings.id"))
    period: Mapped[str] = mapped_column(String(7), index=True)  # YYYY-MM
    ftd_count: Mapped[int] = mapped_column(default=0)
    qftd_count: Mapped[int] = mapped_column(default=0)
    deposits: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    ngr: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    cpa_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    rev_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    adjustments: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    carry_over: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    notes: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MonthlyClosing(Base):
    __tablename__ = "monthly_closings"

    id: Mapped[int] = mapped_column(primary_key=True)
    period: Mapped[str] = mapped_column(String(7), unique=True, index=True)
    status: Mapped[ClosingStatus] = mapped_column(Enum(ClosingStatus), default=ClosingStatus.DRAFT)
    total_commissions: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_affiliates: Mapped[int] = mapped_column(default=0)
    closed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


from app.models.campaign import Campaign  # noqa: E402
