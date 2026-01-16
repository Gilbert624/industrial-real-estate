"""Session state manager compatibility module."""

from .dd_session_state import (
    DDSessionStateManager,
    ProjectCostData,
    ProjectFinancingData,
    ProjectFinancialMetrics,
    DataSource,
    render_data_sync_status,
)

__all__ = [
    "DDSessionStateManager",
    "ProjectCostData",
    "ProjectFinancingData",
    "ProjectFinancialMetrics",
    "DataSource",
    "render_data_sync_status",
]

# Backward-compatible guards for older deployments
if not hasattr(DDSessionStateManager, "is_cost_data_complete"):
    def _is_cost_data_complete(cls) -> bool:
        cost = cls.get_cost_data()
        return cost.total_development_cost > 0

    DDSessionStateManager.is_cost_data_complete = classmethod(_is_cost_data_complete)

if not hasattr(DDSessionStateManager, "is_financing_data_complete"):
    def _is_financing_data_complete(cls) -> bool:
        financing = cls.get_financing_data()
        return (
            financing.construction_loan_amount > 0
            or financing.total_equity_required > 0
        )

    DDSessionStateManager.is_financing_data_complete = classmethod(
        _is_financing_data_complete
    )

if not hasattr(DDSessionStateManager, "is_ready_for_financial_model"):
    def _is_ready_for_financial_model(cls) -> bool:
        return cls.is_cost_data_complete()

    DDSessionStateManager.is_ready_for_financial_model = classmethod(
        _is_ready_for_financial_model
    )
