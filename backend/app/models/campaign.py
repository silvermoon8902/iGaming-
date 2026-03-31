import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DealType(str, enum.Enum):
    CPA = "cpa"
    REV = "rev"
    HYBRID = "hybrid"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    affiliate_id: Mapped[int] = mapped_column(ForeignKey("affiliates.id"))
    operator_id: Mapped[int] = mapped_column(ForeignKey("operators.id"))
    deal_type: Mapped[DealType] = mapped_column(Enum(DealType))
    cpa_value: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    rev_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    affiliate: Mapped["Affiliate"] = relationship(back_populates="campaigns")
    operator: Mapped["Operator"] = relationship()
    tracking_links: Mapped[list["TrackingLink"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")
    rules: Mapped[list["CommissionRule"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")


class TrackingLink(Base):
    __tablename__ = "tracking_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True, default=lambda: uuid.uuid4().hex)
    label: Mapped[str | None] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(500))
    clicks: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    campaign: Mapped["Campaign"] = relationship(back_populates="tracking_links")


from app.models.affiliate import Affiliate  # noqa: E402
from app.models.operator import Operator  # noqa: E402
from app.models.commission import CommissionRule  # noqa: E402
