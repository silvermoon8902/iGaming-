"""
Rules engine for commission calculations.
Supports: carry_over, non_carry_over, baseline, min_qualification.
Rules are stored as JSON config per campaign and evaluated dynamically.
"""
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class CampaignMetrics:
    ftd_count: int = 0
    qftd_count: int = 0
    deposits: Decimal = Decimal("0")
    ngr: Decimal = Decimal("0")
    registrations: int = 0


@dataclass
class RuleResult:
    qualifies: bool = True
    cpa_amount: Decimal = Decimal("0")
    rev_amount: Decimal = Decimal("0")
    carry_over: Decimal = Decimal("0")
    adjustments: Decimal = Decimal("0")
    notes: str = ""


class RulesEngine:
    def evaluate(
        self,
        deal_type: str,
        cpa_value: Decimal,
        rev_percentage: Decimal,
        metrics: CampaignMetrics,
        rules: list[dict],
        previous_carry_over: Decimal = Decimal("0"),
    ) -> RuleResult:
        result = RuleResult()

        # Check minimum qualification rules first
        for rule in rules:
            if rule["rule_type"] == "min_qualification" and rule.get("is_active", True):
                config = rule["config"]
                min_ftd = config.get("min_ftd", 0)
                min_ngr = Decimal(str(config.get("min_ngr", 0)))
                if metrics.ftd_count < min_ftd or metrics.ngr < min_ngr:
                    result.qualifies = False
                    result.notes = f"Did not meet minimum: FTD {metrics.ftd_count}/{min_ftd}, NGR {metrics.ngr}/{min_ngr}"
                    return result

        # Calculate CPA
        if deal_type in ("cpa", "hybrid"):
            result.cpa_amount = cpa_value * metrics.qftd_count

        # Calculate REV share
        if deal_type in ("rev", "hybrid"):
            raw_rev = metrics.ngr * (rev_percentage / Decimal("100"))

            # Apply carry over / baseline rules
            for rule in rules:
                if not rule.get("is_active", True):
                    continue

                if rule["rule_type"] == "carry_over":
                    # Negative REV carries to next period
                    adjusted_rev = raw_rev + previous_carry_over
                    if adjusted_rev < 0:
                        result.carry_over = adjusted_rev
                        result.rev_amount = Decimal("0")
                        result.notes = f"Carry over: {adjusted_rev}"
                    else:
                        result.rev_amount = adjusted_rev
                        result.carry_over = Decimal("0")
                    break

                elif rule["rule_type"] == "non_carry_over":
                    # No carry over — negative REV = 0
                    result.rev_amount = max(raw_rev, Decimal("0"))
                    result.carry_over = Decimal("0")
                    break

                elif rule["rule_type"] == "baseline":
                    # Subtract baseline from NGR before calculating REV
                    baseline_value = Decimal(str(rule["config"].get("baseline_ngr", 0)))
                    effective_ngr = metrics.ngr - baseline_value
                    result.rev_amount = max(effective_ngr * (rev_percentage / Decimal("100")), Decimal("0"))
                    break
            else:
                # No REV rule found — default: no carry over
                result.rev_amount = max(raw_rev, Decimal("0"))

        return result
