"""
Loan Calculator Module

Dual-phase loan calculations for industrial development projects in Australia:
- Construction loan with staged draws and capitalized interest
- Investment loan with IO and P&I options
- Combined refinancing analysis
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
import json

import numpy as np
import numpy_financial as npf


class LoanType(Enum):
    """Loan types."""

    CONSTRUCTION = "construction"
    INVESTMENT = "investment"
    MEZZANINE = "mezzanine"


class RepaymentType(Enum):
    """Repayment types."""

    INTEREST_ONLY = "interest_only"
    PRINCIPAL_AND_INTEREST = "principal_and_interest"


# Australia loan benchmarks (2024-2025)
AU_LOAN_BENCHMARKS = {
    "construction": {
        "rate_min": 7.5,
        "rate_max": 10.0,
        "rate_typical": 8.5,
        "ltc_min": 50,
        "ltc_max": 75,
        "ltc_typical": 65,
        "establishment_fee_pct": 1.0,
        "line_fee_pct": 0.5,
    },
    "investment": {
        "rate_min": 6.0,
        "rate_max": 8.0,
        "rate_typical": 6.75,
        "lvr_min": 50,
        "lvr_max": 70,
        "lvr_typical": 60,
        "establishment_fee_pct": 0.5,
    },
}


@dataclass
class DrawScheduleItem:
    """Draw schedule details."""

    month: int
    draw_amount: float
    draw_percentage: float
    cumulative_drawn: float
    interest_this_month: float
    cumulative_interest: float
    total_outstanding: float


@dataclass
class AmortizationScheduleItem:
    """Amortization schedule details."""

    period: int
    date: Optional[datetime]
    payment: float
    principal: float
    interest: float
    balance: float
    phase: str


@dataclass
class ConstructionLoanModel:
    """
    Construction loan model.

    Features:
    - Progress draws with S-curve
    - Interest-only with optional capitalization
    - Short duration (12-24 months typical)
    """

    # Project parameters
    total_development_cost: float = 0.0
    construction_duration_months: int = 12

    # Loan parameters (Australia typicals)
    loan_to_cost_pct: float = AU_LOAN_BENCHMARKS["construction"]["ltc_typical"]
    interest_rate_annual: float = AU_LOAN_BENCHMARKS["construction"]["rate_typical"]
    establishment_fee_pct: float = AU_LOAN_BENCHMARKS["construction"][
        "establishment_fee_pct"
    ]
    line_fee_pct: float = AU_LOAN_BENCHMARKS["construction"]["line_fee_pct"]

    # Interest treatment
    capitalize_interest: bool = True

    # Draw schedule
    draw_schedule_type: str = "s_curve"  # "s_curve", "linear", "custom"
    custom_draw_schedule: Optional[List[float]] = None

    @property
    def loan_amount(self) -> float:
        """Loan amount."""
        return self.total_development_cost * (self.loan_to_cost_pct / 100)

    @property
    def monthly_rate(self) -> float:
        """Monthly interest rate."""
        return self.interest_rate_annual / 100 / 12

    @property
    def establishment_fee(self) -> float:
        """Establishment fee."""
        return self.loan_amount * (self.establishment_fee_pct / 100)

    @property
    def line_fee(self) -> float:
        """Line fee."""
        return self.loan_amount * (self.line_fee_pct / 100)

    def generate_draw_schedule(self) -> List[float]:
        """
        Generate draw schedule percentages (sum = 1.0).

        Returns:
            List[float]: monthly draw percentages
        """
        n = max(1, self.construction_duration_months)
        if self.draw_schedule_type == "custom" and self.custom_draw_schedule:
            schedule = self.custom_draw_schedule[:n]
            total = sum(schedule)
            return [d / total for d in schedule] if total else [1.0 / n] * n
        if self.draw_schedule_type == "linear":
            return [1.0 / n] * n

        # S-curve using sigmoid
        x = np.linspace(-4, 4, n + 1)
        cumulative = 1 / (1 + np.exp(-x))
        monthly = np.diff(cumulative)
        monthly = monthly / monthly.sum()
        return monthly.tolist()

    def calculate_draw_schedule(self) -> List[DrawScheduleItem]:
        """
        Calculate detailed draw schedule.

        Returns:
            List[DrawScheduleItem]
        """
        draw_percentages = self.generate_draw_schedule()
        schedule: List[DrawScheduleItem] = []
        cumulative_drawn = 0.0
        cumulative_interest = 0.0

        for month, draw_pct in enumerate(draw_percentages, 1):
            draw_amount = self.loan_amount * draw_pct
            cumulative_drawn += draw_amount

            # Interest on average balance for the month
            if month == 1:
                interest = (draw_amount / 2) * self.monthly_rate
            else:
                interest = (
                    cumulative_drawn - draw_amount + draw_amount / 2
                ) * self.monthly_rate
            cumulative_interest += interest

            total_outstanding = (
                cumulative_drawn + cumulative_interest
                if self.capitalize_interest
                else cumulative_drawn
            )

            schedule.append(
                DrawScheduleItem(
                    month=month,
                    draw_amount=draw_amount,
                    draw_percentage=draw_pct * 100,
                    cumulative_drawn=cumulative_drawn,
                    interest_this_month=interest,
                    cumulative_interest=cumulative_interest,
                    total_outstanding=total_outstanding,
                )
            )

        return schedule

    def calculate_summary(self) -> Dict[str, Dict]:
        """Calculate loan summary."""
        schedule = self.calculate_draw_schedule()
        final = schedule[-1]
        total_fees = self.establishment_fee + self.line_fee
        total_interest = final.cumulative_interest
        total_loan_at_completion = final.total_outstanding + total_fees

        # Simple weighted average duration proxy
        weighted_months = sum(item.cumulative_drawn for item in schedule) / max(
            self.loan_amount, 1
        )
        effective_duration = (
            weighted_months / len(schedule) * self.construction_duration_months
        )

        total_financing_cost = total_interest + total_fees
        effective_rate = (
            (total_financing_cost / max(self.loan_amount, 1))
            * (12 / self.construction_duration_months)
            * 100
        )

        return {
            "loan_parameters": {
                "total_development_cost": self.total_development_cost,
                "loan_to_cost_pct": self.loan_to_cost_pct,
                "loan_amount": self.loan_amount,
                "interest_rate_annual": self.interest_rate_annual,
                "construction_duration_months": self.construction_duration_months,
            },
            "fees": {
                "establishment_fee": self.establishment_fee,
                "line_fee": self.line_fee,
                "total_fees": total_fees,
            },
            "interest": {
                "total_interest": total_interest,
                "interest_capitalized": self.capitalize_interest,
                "average_monthly_interest": total_interest
                / max(self.construction_duration_months, 1),
            },
            "totals": {
                "total_drawn": final.cumulative_drawn,
                "total_interest": total_interest,
                "total_fees": total_fees,
                "total_loan_at_completion": total_loan_at_completion,
                "equity_required": self.total_development_cost - self.loan_amount,
            },
            "metrics": {
                "effective_interest_rate": effective_rate,
                "weighted_average_loan_term_months": effective_duration,
                "interest_as_pct_of_loan": (total_interest / max(self.loan_amount, 1))
                * 100,
            },
            "draw_schedule": [
                {
                    "month": item.month,
                    "draw_amount": item.draw_amount,
                    "draw_percentage": item.draw_percentage,
                    "cumulative_drawn": item.cumulative_drawn,
                    "interest": item.interest_this_month,
                    "cumulative_interest": item.cumulative_interest,
                    "total_outstanding": item.total_outstanding,
                }
                for item in schedule
            ],
        }


@dataclass
class InvestmentLoanModel:
    """
    Investment loan model.

    Features:
    - Long-term post-completion finance
    - Interest-only period option
    - Amortizing P&I after IO period
    """

    # Asset parameters
    property_value: float = 0.0

    # Loan parameters (Australia typicals)
    loan_to_value_pct: float = AU_LOAN_BENCHMARKS["investment"]["lvr_typical"]
    interest_rate_annual: float = AU_LOAN_BENCHMARKS["investment"]["rate_typical"]
    loan_term_years: int = 25
    interest_only_years: int = 5
    establishment_fee_pct: float = AU_LOAN_BENCHMARKS["investment"][
        "establishment_fee_pct"
    ]

    # Schedule start date
    start_date: Optional[datetime] = None

    @property
    def loan_amount(self) -> float:
        """Loan amount."""
        return self.property_value * (self.loan_to_value_pct / 100)

    @property
    def monthly_rate(self) -> float:
        """Monthly interest rate."""
        return self.interest_rate_annual / 100 / 12

    @property
    def total_months(self) -> int:
        """Total repayment months."""
        return self.loan_term_years * 12

    @property
    def io_months(self) -> int:
        """Interest-only months."""
        return self.interest_only_years * 12

    @property
    def amort_months(self) -> int:
        """Amortizing months."""
        return max(0, self.total_months - self.io_months)

    @property
    def establishment_fee(self) -> float:
        """Establishment fee."""
        return self.loan_amount * (self.establishment_fee_pct / 100)

    def calculate_io_payment(self) -> float:
        """Interest-only monthly payment."""
        return self.loan_amount * self.monthly_rate

    def calculate_pi_payment(self) -> float:
        """Principal & interest monthly payment."""
        if self.amort_months <= 0:
            return 0.0
        return float(npf.pmt(self.monthly_rate, self.amort_months, -self.loan_amount))

    def calculate_schedule(self) -> List[AmortizationScheduleItem]:
        """
        Calculate amortization schedule.

        Returns:
            List[AmortizationScheduleItem]
        """
        schedule: List[AmortizationScheduleItem] = []
        balance = self.loan_amount
        io_payment = self.calculate_io_payment()
        pi_payment = self.calculate_pi_payment()
        current_date = self.start_date or datetime.now()

        # Interest-only phase
        for period in range(1, self.io_months + 1):
            interest = balance * self.monthly_rate
            schedule.append(
                AmortizationScheduleItem(
                    period=period,
                    date=current_date,
                    payment=io_payment,
                    principal=0.0,
                    interest=interest,
                    balance=balance,
                    phase="Interest Only",
                )
            )
            current_date = current_date + timedelta(days=30)

        # P&I phase
        for period in range(self.io_months + 1, self.total_months + 1):
            interest = balance * self.monthly_rate
            principal = pi_payment - interest
            balance = max(0.0, balance - principal)
            schedule.append(
                AmortizationScheduleItem(
                    period=period,
                    date=current_date,
                    payment=pi_payment,
                    principal=principal,
                    interest=interest,
                    balance=balance,
                    phase="Principal & Interest",
                )
            )
            current_date = current_date + timedelta(days=30)

        return schedule

    def calculate_summary(self) -> Dict[str, Dict]:
        """Calculate loan summary."""
        schedule = self.calculate_schedule()
        total_interest = sum(item.interest for item in schedule)
        total_payments = sum(item.payment for item in schedule)
        year1_debt_service = sum(item.payment for item in schedule[:12])

        io_items = [item for item in schedule if item.phase == "Interest Only"]
        io_total_interest = sum(item.interest for item in io_items)
        io_total_payments = sum(item.payment for item in io_items)

        pi_items = [item for item in schedule if item.phase == "Principal & Interest"]
        pi_total_interest = sum(item.interest for item in pi_items)
        pi_total_payments = sum(item.payment for item in pi_items)
        pi_total_principal = sum(item.principal for item in pi_items)

        return {
            "loan_parameters": {
                "property_value": self.property_value,
                "loan_to_value_pct": self.loan_to_value_pct,
                "loan_amount": self.loan_amount,
                "interest_rate_annual": self.interest_rate_annual,
                "loan_term_years": self.loan_term_years,
                "interest_only_years": self.interest_only_years,
            },
            "payments": {
                "monthly_io_payment": self.calculate_io_payment(),
                "monthly_pi_payment": self.calculate_pi_payment(),
                "annual_io_payment": self.calculate_io_payment() * 12,
                "annual_pi_payment": self.calculate_pi_payment() * 12,
            },
            "totals": {
                "total_payments": total_payments,
                "total_interest": total_interest,
                "total_principal_repaid": self.loan_amount,
                "establishment_fee": self.establishment_fee,
            },
            "by_phase": {
                "interest_only": {
                    "months": self.io_months,
                    "total_payments": io_total_payments,
                    "total_interest": io_total_interest,
                },
                "principal_and_interest": {
                    "months": self.amort_months,
                    "total_payments": pi_total_payments,
                    "total_interest": pi_total_interest,
                    "total_principal": pi_total_principal,
                },
            },
            "metrics": {
                "year1_debt_service": year1_debt_service,
                "interest_as_pct_of_loan": (total_interest / max(self.loan_amount, 1))
                * 100,
                "total_cost_of_borrowing": total_interest + self.establishment_fee,
            },
        }

    def calculate_dscr(self, annual_noi: float) -> float:
        """Calculate DSCR using year-1 debt service."""
        year1_debt_service = self.calculate_io_payment() * 12
        return annual_noi / year1_debt_service if year1_debt_service > 0 else 0.0


@dataclass
class DualPhaseLoanModel:
    """
    Dual-phase loan model with construction-to-investment refinance analysis.
    """

    # Project parameters
    total_development_cost: float = 0.0
    completion_value: float = 0.0
    construction_duration_months: int = 12

    # Construction loan parameters
    construction_ltc: float = AU_LOAN_BENCHMARKS["construction"]["ltc_typical"]
    construction_rate: float = AU_LOAN_BENCHMARKS["construction"]["rate_typical"]
    construction_establishment_fee: float = AU_LOAN_BENCHMARKS["construction"][
        "establishment_fee_pct"
    ]
    construction_line_fee: float = AU_LOAN_BENCHMARKS["construction"]["line_fee_pct"]
    capitalize_interest: bool = True

    # Investment loan parameters
    investment_lvr: float = AU_LOAN_BENCHMARKS["investment"]["lvr_typical"]
    investment_rate: float = AU_LOAN_BENCHMARKS["investment"]["rate_typical"]
    investment_term_years: int = 25
    interest_only_years: int = 5
    investment_establishment_fee: float = AU_LOAN_BENCHMARKS["investment"][
        "establishment_fee_pct"
    ]

    # NOI for DSCR
    expected_annual_noi: float = 0.0

    def get_construction_loan(self) -> ConstructionLoanModel:
        """Create construction loan model."""
        return ConstructionLoanModel(
            total_development_cost=self.total_development_cost,
            construction_duration_months=self.construction_duration_months,
            loan_to_cost_pct=self.construction_ltc,
            interest_rate_annual=self.construction_rate,
            establishment_fee_pct=self.construction_establishment_fee,
            line_fee_pct=self.construction_line_fee,
            capitalize_interest=self.capitalize_interest,
        )

    def get_investment_loan(self) -> InvestmentLoanModel:
        """Create investment loan model."""
        return InvestmentLoanModel(
            property_value=self.completion_value,
            loan_to_value_pct=self.investment_lvr,
            interest_rate_annual=self.investment_rate,
            loan_term_years=self.investment_term_years,
            interest_only_years=self.interest_only_years,
            establishment_fee_pct=self.investment_establishment_fee,
        )

    def calculate_full_financing(self) -> Dict[str, Dict]:
        """Calculate full financing and refinance analysis."""
        construction = self.get_construction_loan()
        investment = self.get_investment_loan()
        construction_result = construction.calculate_summary()
        investment_result = investment.calculate_summary()

        construction_payoff = construction_result["totals"]["total_loan_at_completion"]
        investment_loan_amount = investment_result["loan_parameters"]["loan_amount"]
        cash_difference = investment_loan_amount - construction_payoff

        initial_equity = self.total_development_cost - construction.loan_amount
        additional_equity_for_interest = (
            0.0 if self.capitalize_interest else construction_result["interest"]["total_interest"]
        )
        total_equity_required = initial_equity + additional_equity_for_interest

        refinance_feasible = investment_loan_amount >= construction_payoff
        equity_release = max(0.0, cash_difference)

        dscr = (
            investment.calculate_dscr(self.expected_annual_noi)
            if self.expected_annual_noi > 0
            else 0.0
        )

        return {
            "project_summary": {
                "total_development_cost": self.total_development_cost,
                "completion_value": self.completion_value,
                "development_margin": self.completion_value - self.total_development_cost,
                "development_margin_pct": (
                    (self.completion_value - self.total_development_cost)
                    / self.total_development_cost
                    * 100
                    if self.total_development_cost > 0
                    else 0
                ),
            },
            "construction_phase": construction_result,
            "investment_phase": investment_result,
            "refinance_analysis": {
                "construction_loan_payoff": construction_payoff,
                "investment_loan_amount": investment_loan_amount,
                "cash_difference": cash_difference,
                "refinance_feasible": refinance_feasible,
                "equity_release": equity_release,
                "additional_equity_required": max(0.0, -cash_difference),
            },
            "equity_analysis": {
                "initial_equity_required": initial_equity,
                "additional_for_interest": additional_equity_for_interest,
                "total_equity_required": total_equity_required,
                "equity_pct_of_cost": (
                    total_equity_required / self.total_development_cost * 100
                    if self.total_development_cost > 0
                    else 0
                ),
                "equity_release_at_refinance": equity_release,
                "net_equity_invested": total_equity_required - equity_release,
            },
            "debt_metrics": {
                "construction_ltc": self.construction_ltc,
                "investment_lvr": self.investment_lvr,
                "dscr": dscr,
                "dscr_adequate": dscr >= 1.25,
            },
            "total_financing_costs": {
                "construction_interest": construction_result["interest"]["total_interest"],
                "construction_fees": construction_result["fees"]["total_fees"],
                "investment_fees": investment_result["totals"]["establishment_fee"],
                "total_upfront_costs": (
                    construction_result["fees"]["total_fees"]
                    + investment_result["totals"]["establishment_fee"]
                ),
            },
        }

    def generate_comparison_table(self) -> List[Dict[str, str]]:
        """Generate summary table for UI."""
        result = self.calculate_full_financing()
        rows: List[Dict[str, str]] = []

        rows.append(
            {
                "Category": "Construction Loan",
                "Parameter": "Loan Amount",
                "Value": result["construction_phase"]["loan_parameters"]["loan_amount"],
                "Unit": "AUD",
            }
        )
        rows.append(
            {
                "Category": "Construction Loan",
                "Parameter": "LTC Ratio",
                "Value": result["construction_phase"]["loan_parameters"]["loan_to_cost_pct"],
                "Unit": "%",
            }
        )
        rows.append(
            {
                "Category": "Construction Loan",
                "Parameter": "Interest Rate",
                "Value": result["construction_phase"]["loan_parameters"]["interest_rate_annual"],
                "Unit": "% p.a.",
            }
        )
        rows.append(
            {
                "Category": "Construction Loan",
                "Parameter": "Duration",
                "Value": result["construction_phase"]["loan_parameters"][
                    "construction_duration_months"
                ],
                "Unit": "months",
            }
        )
        rows.append(
            {
                "Category": "Construction Loan",
                "Parameter": "Total Interest",
                "Value": result["construction_phase"]["interest"]["total_interest"],
                "Unit": "AUD",
            }
        )
        rows.append(
            {
                "Category": "Construction Loan",
                "Parameter": "Total Fees",
                "Value": result["construction_phase"]["fees"]["total_fees"],
                "Unit": "AUD",
            }
        )
        rows.append(
            {
                "Category": "Construction Loan",
                "Parameter": "Loan at Completion",
                "Value": result["construction_phase"]["totals"]["total_loan_at_completion"],
                "Unit": "AUD",
            }
        )

        rows.append(
            {
                "Category": "Investment Loan",
                "Parameter": "Loan Amount",
                "Value": result["investment_phase"]["loan_parameters"]["loan_amount"],
                "Unit": "AUD",
            }
        )
        rows.append(
            {
                "Category": "Investment Loan",
                "Parameter": "LVR Ratio",
                "Value": result["investment_phase"]["loan_parameters"]["loan_to_value_pct"],
                "Unit": "%",
            }
        )
        rows.append(
            {
                "Category": "Investment Loan",
                "Parameter": "Interest Rate",
                "Value": result["investment_phase"]["loan_parameters"]["interest_rate_annual"],
                "Unit": "% p.a.",
            }
        )
        rows.append(
            {
                "Category": "Investment Loan",
                "Parameter": "Loan Term",
                "Value": result["investment_phase"]["loan_parameters"]["loan_term_years"],
                "Unit": "years",
            }
        )
        rows.append(
            {
                "Category": "Investment Loan",
                "Parameter": "IO Period",
                "Value": result["investment_phase"]["loan_parameters"]["interest_only_years"],
                "Unit": "years",
            }
        )
        rows.append(
            {
                "Category": "Investment Loan",
                "Parameter": "Monthly IO Payment",
                "Value": result["investment_phase"]["payments"]["monthly_io_payment"],
                "Unit": "AUD",
            }
        )
        rows.append(
            {
                "Category": "Investment Loan",
                "Parameter": "Monthly P&I Payment",
                "Value": result["investment_phase"]["payments"]["monthly_pi_payment"],
                "Unit": "AUD",
            }
        )

        rows.append(
            {
                "Category": "Refinance Analysis",
                "Parameter": "Cash Out / Shortfall",
                "Value": result["refinance_analysis"]["cash_difference"],
                "Unit": "AUD",
            }
        )
        rows.append(
            {
                "Category": "Refinance Analysis",
                "Parameter": "Refinance Feasible",
                "Value": "Yes"
                if result["refinance_analysis"]["refinance_feasible"]
                else "No",
                "Unit": "",
            }
        )

        rows.append(
            {
                "Category": "Equity Analysis",
                "Parameter": "Total Equity Required",
                "Value": result["equity_analysis"]["total_equity_required"],
                "Unit": "AUD",
            }
        )
        rows.append(
            {
                "Category": "Equity Analysis",
                "Parameter": "Equity % of Cost",
                "Value": result["equity_analysis"]["equity_pct_of_cost"],
                "Unit": "%",
            }
        )

        return rows

    def to_json(self) -> str:
        """Export full financing to JSON."""
        return json.dumps(self.calculate_full_financing(), indent=2, default=str)


def create_sunshine_coast_loan_example() -> DualPhaseLoanModel:
    """Example loan setup for a Sunshine Coast warehouse project."""
    return DualPhaseLoanModel(
        total_development_cost=8_500_000,
        completion_value=10_200_000,
        construction_duration_months=14,
        construction_ltc=65,
        construction_rate=8.5,
        investment_lvr=60,
        investment_rate=6.75,
        investment_term_years=25,
        interest_only_years=5,
        expected_annual_noi=650_000,
    )
