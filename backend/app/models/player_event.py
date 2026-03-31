import enum
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EventType(str, enum.Enum):
    REGISTRATION = "registration"
    FTD = "ftd"
    QFTD = "qftd"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    BET = "bet"
    WIN = "win"


class PlayerEvent(Base):
    __tablename__ = "player_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    tracking_link_id: Mapped[int] = mapped_column(ForeignKey("tracking_links.id"), index=True)
    player_external_id: Mapped[str] = mapped_column(String(255), index=True)
    event_type: Mapped[EventType] = mapped_column(Enum(EventType), index=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
