"""
Seed script — run with: python seed.py
Requires DATABASE_URL env var or defaults to localhost.
"""
import asyncio
import random
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.database import Base
from app.models.user import User, UserRole
from app.models.affiliate import Affiliate, AffiliateStatus
from app.models.operator import Operator
from app.models.campaign import Campaign, TrackingLink, DealType
from app.models.commission import CommissionRule, Commission, MonthlyClosing, RuleType, ClosingStatus
from app.models.player_event import PlayerEvent, EventType
from app.core.security import hash_password

DATABASE_URL = "postgresql+asyncpg://admin:admin123@localhost:5432/igaming_affiliates"


async def seed():
    engine_db = create_async_engine(DATABASE_URL)

    async with engine_db.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine_db, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as db:
        # Users
        users = [
            User(email="admin@affiliate.io", name="Admin", hashed_password=hash_password("admin123"), role=UserRole.ADMIN),
            User(email="finance@affiliate.io", name="Financeiro", hashed_password=hash_password("finance123"), role=UserRole.FINANCIAL),
            User(email="manager@affiliate.io", name="Manager", hashed_password=hash_password("manager123"), role=UserRole.MANAGER),
        ]
        db.add_all(users)
        await db.flush()

        # Operators
        operators = [
            Operator(name="Casino Europa", api_endpoint="https://api.casinoeu.example"),
            Operator(name="Sports LATAM", api_endpoint="https://api.sportslatam.example"),
            Operator(name="Slots Global", api_endpoint="https://api.slotsglobal.example"),
            Operator(name="Poker Brasil", api_endpoint="https://api.pokerbr.example"),
        ]
        db.add_all(operators)
        await db.flush()

        # Affiliates
        affiliates = [
            Affiliate(name="Alpha Media", email="alpha@media.io", contact="Telegram: @alphamedia", status=AffiliateStatus.ACTIVE),
            Affiliate(name="Bet Traffic", email="contact@bettraffic.io", contact="WhatsApp: +55 11 99999", status=AffiliateStatus.ACTIVE),
            Affiliate(name="ClickAds", email="ops@clickads.io", contact="Skype: clickads_team", status=AffiliateStatus.MODERATE),
            Affiliate(name="GamblePro", email="info@gamblepro.io", contact="Telegram: @gamblepro", status=AffiliateStatus.ACTIVE),
            Affiliate(name="TrafficKing", email="king@traffic.io", contact="Email only", status=AffiliateStatus.LOW),
            Affiliate(name="AffNet Digital", email="hello@affnet.io", contact="Telegram: @affnet", status=AffiliateStatus.ACTIVE),
        ]
        db.add_all(affiliates)
        await db.flush()

        # Campaigns
        campaigns_data = [
            ("Casino EU Premium", affiliates[0], operators[0], DealType.HYBRID, 45.0, 30.0),
            ("Sports LATAM Gold", affiliates[1], operators[1], DealType.CPA, 35.0, 0.0),
            ("Slots VIP", affiliates[2], operators[2], DealType.REV, 0.0, 40.0),
            ("Casino EU Standard", affiliates[3], operators[0], DealType.CPA, 25.0, 0.0),
            ("Poker BR Launch", affiliates[4], operators[3], DealType.HYBRID, 30.0, 25.0),
            ("Sports LATAM Silver", affiliates[5], operators[1], DealType.REV, 0.0, 35.0),
            ("Slots Global Push", affiliates[0], operators[2], DealType.CPA, 40.0, 0.0),
            ("Casino EU Rev", affiliates[3], operators[0], DealType.REV, 0.0, 35.0),
        ]
        campaigns = []
        for name, aff, op, deal, cpa, rev in campaigns_data:
            c = Campaign(name=name, affiliate_id=aff.id, operator_id=op.id, deal_type=deal, cpa_value=cpa, rev_percentage=rev)
            campaigns.append(c)
        db.add_all(campaigns)
        await db.flush()

        # Commission Rules
        rules = [
            CommissionRule(campaign_id=campaigns[0].id, rule_type=RuleType.CARRY_OVER, config={}),
            CommissionRule(campaign_id=campaigns[2].id, rule_type=RuleType.NON_CARRY_OVER, config={}),
            CommissionRule(campaign_id=campaigns[4].id, rule_type=RuleType.BASELINE, config={"baseline_ngr": 5000}),
            CommissionRule(campaign_id=campaigns[0].id, rule_type=RuleType.MIN_QUALIFICATION, config={"min_ftd": 10, "min_ngr": 1000}),
            CommissionRule(campaign_id=campaigns[5].id, rule_type=RuleType.CARRY_OVER, config={}),
            CommissionRule(campaign_id=campaigns[7].id, rule_type=RuleType.NON_CARRY_OVER, config={}),
        ]
        db.add_all(rules)
        await db.flush()

        # Tracking Links
        links = []
        for c in campaigns:
            for i in range(random.randint(1, 3)):
                link = TrackingLink(
                    campaign_id=c.id,
                    label=f"{c.name} - Link {i+1}",
                    url=f"https://track.affiliate.io/r/{c.id}/{i+1}",
                )
                links.append(link)
        db.add_all(links)
        await db.flush()

        # Player Events (generate realistic data for 3 months)
        events = []
        periods = ["2026-01", "2026-02", "2026-03"]
        for link in links:
            for period in periods:
                year, month = period.split("-")
                n_players = random.randint(20, 120)
                for p in range(n_players):
                    player_id = f"P{link.id}_{period}_{p}"
                    event_date = datetime(int(year), int(month), random.randint(1, 28), tzinfo=timezone.utc)

                    # Registration
                    events.append(PlayerEvent(
                        tracking_link_id=link.id, player_external_id=player_id,
                        event_type=EventType.REGISTRATION, amount=0, event_date=event_date,
                    ))

                    # FTD (70% chance)
                    if random.random() < 0.7:
                        ftd_amount = random.uniform(20, 500)
                        events.append(PlayerEvent(
                            tracking_link_id=link.id, player_external_id=player_id,
                            event_type=EventType.FTD, amount=round(ftd_amount, 2),
                            event_date=event_date + timedelta(hours=random.randint(1, 48)),
                        ))

                        # QFTD (60% of FTD)
                        if random.random() < 0.6:
                            events.append(PlayerEvent(
                                tracking_link_id=link.id, player_external_id=player_id,
                                event_type=EventType.QFTD, amount=round(ftd_amount, 2),
                                event_date=event_date + timedelta(days=random.randint(1, 7)),
                            ))

                        # Deposits
                        for _ in range(random.randint(1, 5)):
                            events.append(PlayerEvent(
                                tracking_link_id=link.id, player_external_id=player_id,
                                event_type=EventType.DEPOSIT, amount=round(random.uniform(10, 300), 2),
                                event_date=event_date + timedelta(days=random.randint(0, 25)),
                            ))

                        # Withdrawals (40% chance)
                        if random.random() < 0.4:
                            events.append(PlayerEvent(
                                tracking_link_id=link.id, player_external_id=player_id,
                                event_type=EventType.WITHDRAWAL, amount=round(random.uniform(20, 200), 2),
                                event_date=event_date + timedelta(days=random.randint(3, 25)),
                            ))

        db.add_all(events)
        await db.flush()

        # Pre-calculate commissions for the 3 months
        from app.services.rules_engine import RulesEngine, CampaignMetrics
        from decimal import Decimal

        rules_engine = RulesEngine()

        for period in periods:
            closing = MonthlyClosing(period=period, status=ClosingStatus.APPROVED if period != "2026-03" else ClosingStatus.DRAFT)
            db.add(closing)
            await db.flush()

            total_comm = Decimal("0")
            aff_ids = set()

            for campaign in campaigns:
                campaign_links = [l for l in links if l.campaign_id == campaign.id]
                link_ids = [l.id for l in campaign_links]
                if not link_ids:
                    continue

                # Count events for this campaign/period
                year, month = period.split("-")
                campaign_events = [
                    e for e in events
                    if e.tracking_link_id in link_ids
                    and e.event_date.year == int(year)
                    and e.event_date.month == int(month)
                ]

                ftd = sum(1 for e in campaign_events if e.event_type == EventType.FTD)
                qftd = sum(1 for e in campaign_events if e.event_type == EventType.QFTD)
                deposits = sum(e.amount for e in campaign_events if e.event_type == EventType.DEPOSIT)
                withdrawals = sum(e.amount for e in campaign_events if e.event_type == EventType.WITHDRAWAL)
                ngr = deposits - withdrawals

                metrics = CampaignMetrics(
                    ftd_count=ftd, qftd_count=qftd,
                    deposits=Decimal(str(round(deposits, 2))),
                    ngr=Decimal(str(round(ngr, 2))),
                )

                rules_data = [
                    {"rule_type": r.rule_type.value, "config": r.config, "is_active": r.is_active}
                    for r in rules if r.campaign_id == campaign.id
                ]

                result = rules_engine.evaluate(
                    deal_type=campaign.deal_type.value,
                    cpa_value=Decimal(str(campaign.cpa_value)),
                    rev_percentage=Decimal(str(campaign.rev_percentage)),
                    metrics=metrics,
                    rules=rules_data,
                )

                total = result.cpa_amount + result.rev_amount
                commission = Commission(
                    affiliate_id=campaign.affiliate_id, campaign_id=campaign.id,
                    closing_id=closing.id, period=period,
                    ftd_count=ftd, qftd_count=qftd,
                    deposits=float(deposits), ngr=float(ngr),
                    cpa_amount=float(result.cpa_amount), rev_amount=float(result.rev_amount),
                    adjustments=0, total=float(total), carry_over=float(result.carry_over),
                    notes=result.notes or None,
                )
                db.add(commission)
                total_comm += total
                aff_ids.add(campaign.affiliate_id)

            closing.total_commissions = float(total_comm)
            closing.total_affiliates = len(aff_ids)
            if closing.status == ClosingStatus.APPROVED:
                closing.closed_by = users[0].id
                closing.closed_at = datetime.now(timezone.utc)

        await db.commit()
        print("Seed completed successfully!")
        print(f"  Users: {len(users)}")
        print(f"  Operators: {len(operators)}")
        print(f"  Affiliates: {len(affiliates)}")
        print(f"  Campaigns: {len(campaigns)}")
        print(f"  Tracking Links: {len(links)}")
        print(f"  Player Events: {len(events)}")
        print(f"  Closings: {len(periods)}")
        print(f"\nLogin: admin@affiliate.io / admin123")

    await engine_db.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
