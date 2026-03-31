from decimal import Decimal

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.affiliate import Affiliate
from app.models.campaign import Campaign
from app.models.commission import Commission, CommissionRule, MonthlyClosing
from app.models.player_event import PlayerEvent, EventType
from app.models.campaign import TrackingLink  # noqa — accessed via campaign
from app.services.rules_engine import RulesEngine, CampaignMetrics


class CommissionCalculator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.engine = RulesEngine()

    async def calculate_period(self, closing: MonthlyClosing):
        period = closing.period

        # Delete existing commissions for this period/closing
        existing = await self.db.execute(
            select(Commission).where(Commission.closing_id == closing.id)
        )
        for c in existing.scalars().all():
            await self.db.delete(c)

        # Get all active campaigns with rules
        campaigns_result = await self.db.execute(
            select(Campaign)
            .where(Campaign.is_active == True)
            .options(selectinload(Campaign.rules), selectinload(Campaign.tracking_links))
        )
        campaigns = campaigns_result.scalars().all()

        total_commissions = Decimal("0")
        affiliate_ids = set()

        for campaign in campaigns:
            link_ids = [link.id for link in campaign.tracking_links]
            if not link_ids:
                continue

            metrics = await self._get_metrics(link_ids, period)

            # Get previous carry over
            prev_commission = await self.db.execute(
                select(Commission)
                .where(
                    Commission.campaign_id == campaign.id,
                    Commission.period < period,
                )
                .order_by(Commission.period.desc())
                .limit(1)
            )
            prev = prev_commission.scalar_one_or_none()
            previous_carry = Decimal(str(prev.carry_over)) if prev else Decimal("0")

            # Prepare rules as dicts
            rules_data = [
                {"rule_type": r.rule_type.value, "config": r.config, "is_active": r.is_active}
                for r in campaign.rules
            ]

            result = self.engine.evaluate(
                deal_type=campaign.deal_type.value,
                cpa_value=Decimal(str(campaign.cpa_value)),
                rev_percentage=Decimal(str(campaign.rev_percentage)),
                metrics=metrics,
                rules=rules_data,
                previous_carry_over=previous_carry,
            )

            total = result.cpa_amount + result.rev_amount + result.adjustments
            commission = Commission(
                affiliate_id=campaign.affiliate_id,
                campaign_id=campaign.id,
                closing_id=closing.id,
                period=period,
                ftd_count=metrics.ftd_count,
                qftd_count=metrics.qftd_count,
                deposits=float(metrics.deposits),
                ngr=float(metrics.ngr),
                cpa_amount=float(result.cpa_amount),
                rev_amount=float(result.rev_amount),
                adjustments=float(result.adjustments),
                total=float(total),
                carry_over=float(result.carry_over),
                notes=result.notes or None,
            )
            self.db.add(commission)
            total_commissions += total
            affiliate_ids.add(campaign.affiliate_id)

        closing.total_commissions = float(total_commissions)
        closing.total_affiliates = len(affiliate_ids)
        await self.db.commit()

    async def _get_metrics(self, link_ids: list[int], period: str) -> CampaignMetrics:
        year, month = period.split("-")
        date_start = f"{year}-{month}-01"
        if int(month) == 12:
            date_end = f"{int(year) + 1}-01-01"
        else:
            date_end = f"{year}-{int(month) + 1:02d}-01"

        base_filter = and_(
            PlayerEvent.tracking_link_id.in_(link_ids),
            PlayerEvent.event_date >= date_start,
            PlayerEvent.event_date < date_end,
        )

        # FTD count
        ftd_result = await self.db.execute(
            select(func.count(PlayerEvent.id))
            .where(base_filter, PlayerEvent.event_type == EventType.FTD)
        )
        ftd_count = ftd_result.scalar() or 0

        # QFTD count
        qftd_result = await self.db.execute(
            select(func.count(PlayerEvent.id))
            .where(base_filter, PlayerEvent.event_type == EventType.QFTD)
        )
        qftd_count = qftd_result.scalar() or 0

        # Deposits
        dep_result = await self.db.execute(
            select(func.coalesce(func.sum(PlayerEvent.amount), 0))
            .where(base_filter, PlayerEvent.event_type == EventType.DEPOSIT)
        )
        deposits = Decimal(str(dep_result.scalar() or 0))

        # NGR = deposits - withdrawals - wins + bets (simplified)
        for event_type, multiplier in [
            (EventType.WITHDRAWAL, -1), (EventType.WIN, -1), (EventType.BET, 1)
        ]:
            amt_result = await self.db.execute(
                select(func.coalesce(func.sum(PlayerEvent.amount), 0))
                .where(base_filter, PlayerEvent.event_type == event_type)
            )
            deposits_adj = Decimal(str(amt_result.scalar() or 0))
            if event_type == EventType.BET:
                pass  # bets don't affect NGR directly in this model
            else:
                deposits += deposits_adj * multiplier

        # NGR is a simplified calculation: deposits - withdrawals
        ngr = deposits  # Already adjusted above

        return CampaignMetrics(
            ftd_count=ftd_count,
            qftd_count=qftd_count,
            deposits=deposits,
            ngr=ngr,
        )
