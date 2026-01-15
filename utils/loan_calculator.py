"""Compatibility wrapper for loan calculator module."""

from .loan_models import (
    ConstructionLoanModel,
    InvestmentLoanModel,
    DualPhaseLoanModel,
    AU_LOAN_BENCHMARKS,
    create_sunshine_coast_loan_example,
)

__all__ = [
    "ConstructionLoanModel",
    "InvestmentLoanModel",
    "DualPhaseLoanModel",
    "AU_LOAN_BENCHMARKS",
    "create_sunshine_coast_loan_example",
]
