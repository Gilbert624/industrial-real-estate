"""
Session State Manager
管理Due Diligence模块的数据流和状态同步
"""

import streamlit as st
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from enum import Enum


class DataSource(Enum):
    """数据来源标识"""
    MANUAL = "manual"  # 手动输入
    COST_BREAKDOWN = "cost_breakdown"  # 来自成本细分
    LOAN_CALCULATOR = "loan_calculator"  # 来自贷款计算
    DATABASE = "database"  # 来自数据库


@dataclass
class ProjectCostData:
    """项目成本数据"""
    # 土地成本
    land_area_sqm: float = 0.0
    land_price_per_sqm: float = 0.0
    land_purchase_price: float = 0.0
    land_acquisition_costs: float = 0.0
    total_land_cost: float = 0.0

    # 建筑成本
    gross_floor_area: float = 0.0
    construction_rate_per_sqm: float = 0.0
    base_construction_cost: float = 0.0

    # 场地工程
    total_site_works: float = 0.0

    # 应急储备
    total_contingency: float = 0.0

    # 软成本
    total_professional_fees: float = 0.0
    total_government_charges: float = 0.0
    total_other_soft_costs: float = 0.0

    # 汇总
    total_hard_costs: float = 0.0
    total_soft_costs: float = 0.0
    total_development_cost: float = 0.0

    # 数据来源
    source: str = DataSource.MANUAL.value


@dataclass
class ProjectFinancingData:
    """项目融资数据"""
    # 建筑贷款
    construction_loan_amount: float = 0.0
    construction_ltc_pct: float = 65.0
    construction_interest_rate: float = 8.5
    construction_duration_months: int = 12
    construction_total_interest: float = 0.0
    construction_loan_at_completion: float = 0.0

    # 投资贷款
    completion_value: float = 0.0
    investment_loan_amount: float = 0.0
    investment_lvr_pct: float = 60.0
    investment_interest_rate: float = 6.75
    investment_term_years: int = 25
    interest_only_years: int = 5
    monthly_io_payment: float = 0.0
    monthly_pi_payment: float = 0.0

    # 权益
    total_equity_required: float = 0.0
    equity_percentage: float = 35.0

    # DSCR
    expected_annual_noi: float = 0.0
    dscr: float = 0.0

    # 数据来源
    source: str = DataSource.MANUAL.value


@dataclass
class ProjectFinancialMetrics:
    """项目财务指标"""
    # 收益预测
    target_rent_per_sqm: float = 0.0
    occupancy_rate: float = 95.0
    annual_gross_income: float = 0.0
    operating_expense_ratio: float = 15.0
    annual_noi: float = 0.0

    # 回报指标
    entry_yield: float = 0.0
    exit_cap_rate: float = 6.0
    holding_period_years: int = 10

    # 计算结果
    irr: float = 0.0
    npv: float = 0.0
    equity_multiple: float = 0.0
    cash_on_cash_year1: float = 0.0
    profit_margin: float = 0.0


class DDSessionStateManager:
    """
    Due Diligence Session State Manager

    管理跨标签页的数据同步
    """

    # Session state keys
    COST_DATA_KEY = "dd_cost_data"
    FINANCING_DATA_KEY = "dd_financing_data"
    METRICS_DATA_KEY = "dd_metrics_data"
    SYNC_STATUS_KEY = "dd_sync_status"

    @classmethod
    def initialize(cls):
        """初始化session state"""
        if cls.COST_DATA_KEY not in st.session_state:
            st.session_state[cls.COST_DATA_KEY] = ProjectCostData()

        if cls.FINANCING_DATA_KEY not in st.session_state:
            st.session_state[cls.FINANCING_DATA_KEY] = ProjectFinancingData()

        if cls.METRICS_DATA_KEY not in st.session_state:
            st.session_state[cls.METRICS_DATA_KEY] = ProjectFinancialMetrics()

        if cls.SYNC_STATUS_KEY not in st.session_state:
            st.session_state[cls.SYNC_STATUS_KEY] = {
                "cost_updated": False,
                "financing_updated": False,
                "metrics_updated": False,
                "last_update_source": None,
            }

    @classmethod
    def get_cost_data(cls) -> ProjectCostData:
        """获取成本数据"""
        cls.initialize()
        return st.session_state[cls.COST_DATA_KEY]

    @classmethod
    def set_cost_data(cls, data: ProjectCostData):
        """设置成本数据并触发同步"""
        cls.initialize()
        st.session_state[cls.COST_DATA_KEY] = data
        st.session_state[cls.SYNC_STATUS_KEY]["cost_updated"] = True
        st.session_state[cls.SYNC_STATUS_KEY]["last_update_source"] = "cost_breakdown"

        # 自动同步到融资数据
        cls._sync_cost_to_financing()

    @classmethod
    def get_financing_data(cls) -> ProjectFinancingData:
        """获取融资数据"""
        cls.initialize()
        return st.session_state[cls.FINANCING_DATA_KEY]

    @classmethod
    def set_financing_data(cls, data: ProjectFinancingData):
        """设置融资数据"""
        cls.initialize()
        st.session_state[cls.FINANCING_DATA_KEY] = data
        st.session_state[cls.SYNC_STATUS_KEY]["financing_updated"] = True
        st.session_state[cls.SYNC_STATUS_KEY]["last_update_source"] = "loan_calculator"

    @classmethod
    def get_metrics_data(cls) -> ProjectFinancialMetrics:
        """获取财务指标数据"""
        cls.initialize()
        return st.session_state[cls.METRICS_DATA_KEY]

    @classmethod
    def set_metrics_data(cls, data: ProjectFinancialMetrics):
        """设置财务指标数据"""
        cls.initialize()
        st.session_state[cls.METRICS_DATA_KEY] = data
        st.session_state[cls.SYNC_STATUS_KEY]["metrics_updated"] = True

    @classmethod
    def _sync_cost_to_financing(cls):
        """将成本数据同步到融资数据"""
        cost_data = cls.get_cost_data()
        financing_data = cls.get_financing_data()

        # 更新总开发成本
        if cost_data.total_development_cost > 0:
            financing_data.construction_loan_amount = (
                cost_data.total_development_cost
                * (financing_data.construction_ltc_pct / 100)
            )
            financing_data.total_equity_required = (
                cost_data.total_development_cost
                - financing_data.construction_loan_amount
            )
            financing_data.equity_percentage = (
                (
                    financing_data.total_equity_required
                    / cost_data.total_development_cost
                )
                * 100
                if cost_data.total_development_cost > 0
                else 35.0
            )

        st.session_state[cls.FINANCING_DATA_KEY] = financing_data

    @classmethod
    def get_sync_status(cls) -> Dict[str, Any]:
        """获取同步状态"""
        cls.initialize()
        return st.session_state[cls.SYNC_STATUS_KEY]

    @classmethod
    def reset_all(cls):
        """重置所有数据"""
        st.session_state[cls.COST_DATA_KEY] = ProjectCostData()
        st.session_state[cls.FINANCING_DATA_KEY] = ProjectFinancingData()
        st.session_state[cls.METRICS_DATA_KEY] = ProjectFinancialMetrics()
        st.session_state[cls.SYNC_STATUS_KEY] = {
            "cost_updated": False,
            "financing_updated": False,
            "metrics_updated": False,
            "last_update_source": None,
        }

    @classmethod
    def get_summary_for_display(cls) -> Dict[str, Any]:
        """获取用于显示的汇总数据"""
        cost = cls.get_cost_data()
        financing = cls.get_financing_data()
        metrics = cls.get_metrics_data()

        return {
            "cost": {
                "total_development_cost": cost.total_development_cost,
                "total_hard_costs": cost.total_hard_costs,
                "total_soft_costs": cost.total_soft_costs,
                "cost_per_sqm": (
                    cost.total_development_cost / cost.gross_floor_area
                    if cost.gross_floor_area > 0
                    else 0
                ),
            },
            "financing": {
                "construction_loan": financing.construction_loan_amount,
                "investment_loan": financing.investment_loan_amount,
                "total_equity": financing.total_equity_required,
                "equity_pct": financing.equity_percentage,
                "dscr": financing.dscr,
            },
            "metrics": {
                "irr": metrics.irr,
                "npv": metrics.npv,
                "equity_multiple": metrics.equity_multiple,
                "profit_margin": metrics.profit_margin,
            },
            "sync_status": cls.get_sync_status(),
        }


def render_data_sync_status():
    """渲染数据同步状态指示器"""
    status = DDSessionStateManager.get_sync_status()

    col1, col2, col3 = st.columns(3)

    with col1:
        if status["cost_updated"]:
            st.success("✅ Cost Data")
        else:
            st.warning("⚠️ Cost Data - Not Set")

    with col2:
        if status["financing_updated"]:
            st.success("✅ Financing Data")
        else:
            st.warning("⚠️ Financing Data - Not Set")

    with col3:
        if status["metrics_updated"]:
            st.success("✅ Metrics Calculated")
        else:
            st.warning("⚠️ Metrics - Not Calculated")

    if status["last_update_source"]:
        st.caption(f"Last updated from: {status['last_update_source']}")
