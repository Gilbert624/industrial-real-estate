"""
Assets Dashboard (Read-only)
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import func

from config.theme import generate_css
from models.database import DatabaseManager, Asset, Project, Transaction, TransactionType


st.set_page_config(page_title="Assets Dashboard", page_icon="🏢", layout="wide")
st.markdown(generate_css("light"), unsafe_allow_html=True)


@st.cache_resource
def get_database() -> DatabaseManager:
    return DatabaseManager("sqlite:///industrial_real_estate.db")


def get_asset_project_counts(session) -> Dict[int, int]:
    rows = (
        session.query(Project.asset_id, func.count(Project.id))
        .group_by(Project.asset_id)
        .all()
    )
    return {row[0]: int(row[1]) for row in rows}


def get_asset_financials(session) -> Dict[int, Dict[str, float]]:
    financials: Dict[int, Dict[str, float]] = {}
    income_rows = (
        session.query(Transaction.asset_id, func.sum(Transaction.amount))
        .filter(Transaction.transaction_type == TransactionType.INCOME)
        .group_by(Transaction.asset_id)
        .all()
    )
    expense_rows = (
        session.query(Transaction.asset_id, func.sum(Transaction.amount))
        .filter(Transaction.transaction_type == TransactionType.EXPENSE)
        .group_by(Transaction.asset_id)
        .all()
    )

    for asset_id, amount in income_rows:
        if asset_id is None:
            continue
        financials.setdefault(asset_id, {})["income"] = float(amount or 0)
    for asset_id, amount in expense_rows:
        if asset_id is None:
            continue
        financials.setdefault(asset_id, {})["expense"] = float(amount or 0)

    for asset_id, values in financials.items():
        income = values.get("income", 0.0)
        expense = values.get("expense", 0.0)
        values["net"] = income + expense
    return financials


def display_cashflow_chart(db: DatabaseManager):
    trend = db.get_cashflow_trend(months=12)
    if not trend:
        st.info("No cashflow trend data available.")
        return

    labels = [f"{row['year']}-{row['month']:02d}" for row in trend]
    income = [row["income"] / 1_000_000 for row in trend]
    expense = [row["expense"] / 1_000_000 for row in trend]
    net = [row["net"] / 1_000_000 for row in trend]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=labels, y=income, mode="lines+markers", name="Income"))
    fig.add_trace(go.Scatter(x=labels, y=expense, mode="lines+markers", name="Expense"))
    fig.add_trace(go.Scatter(x=labels, y=net, mode="lines+markers", name="Net"))
    fig.update_layout(
        title="Portfolio Cashflow Trend (AUD, Millions)",
        height=360,
        margin=dict(t=60, b=40, l=40, r=20),
    )
    st.plotly_chart(fig, width="stretch")


def main():
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.header("📊 Assets Dashboard")
    with col2:
        st.page_link("pages/2_data_input.py", label="➕ Add New Asset", use_container_width=True)
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    st.info("💡 To add new data, go to Data Input Center.")
    st.caption("This is a read-only view. To add/edit data, use the Data Input Center.")
    st.divider()

    db = get_database()
    session = db.get_session()
    try:
        assets = session.query(Asset).order_by(Asset.name).all()
        project_counts = get_asset_project_counts(session)
        financials = get_asset_financials(session)
    finally:
        db.close_session(session)

    if not assets:
        st.info("No assets found.")
        return

    total_valuation = sum(float(a.current_valuation or 0) for a in assets)
    total_income = sum(financials.get(a.id, {}).get("income", 0) for a in assets)
    total_expense = sum(financials.get(a.id, {}).get("expense", 0) for a in assets)

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("Total Assets", len(assets))
    metric_col2.metric("Portfolio Valuation", f"${total_valuation:,.0f}")
    metric_col3.metric("Total Income", f"${total_income:,.0f}")
    metric_col4.metric("Total Expense", f"${abs(total_expense):,.0f}")

    st.subheader("Asset List")
    rows: List[Dict[str, object]] = []
    for asset in assets:
        asset_fin = financials.get(asset.id, {})
        rows.append(
            {
                "Asset": asset.name,
                "Type": asset.asset_type.value if asset.asset_type else "-",
                "Status": asset.status.value if asset.status else "-",
                "Region": asset.region,
                "Projects": project_counts.get(asset.id, 0),
                "Valuation (AUD)": float(asset.current_valuation or 0),
                "Income (AUD)": asset_fin.get("income", 0.0),
                "Expense (AUD)": abs(asset_fin.get("expense", 0.0)),
                "Net (AUD)": asset_fin.get("net", 0.0),
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    st.divider()
    st.subheader("Portfolio Cashflow")
    display_cashflow_chart(db)

    st.divider()
    st.subheader("Asset Details")
    session = db.get_session()
    try:
        for asset in assets:
            asset_fin = financials.get(asset.id, {})
            with st.expander(f"📊 View Details - {asset.name}"):
                detail_col1, detail_col2 = st.columns(2)
                with detail_col1:
                    st.metric("Projects", project_counts.get(asset.id, 0))
                    st.metric("Valuation (AUD)", f"${float(asset.current_valuation or 0):,.0f}")
                with detail_col2:
                    st.metric("Income (AUD)", f"${asset_fin.get('income', 0.0):,.0f}")
                    st.metric("Expense (AUD)", f"${abs(asset_fin.get('expense', 0.0)):,.0f}")

                related_projects = session.query(Project).filter(Project.asset_id == asset.id).all()
                if related_projects:
                    st.subheader("Related Projects")
                    project_rows = [
                        {
                            "Project": p.project_name,
                            "Status": p.status.value if p.status else "-",
                            "Budget (AUD)": float(p.total_budget or 0),
                            "Actual Cost (AUD)": float(p.actual_cost or 0),
                        }
                        for p in related_projects
                    ]
                    st.dataframe(pd.DataFrame(project_rows), width="stretch", hide_index=True)
                else:
                    st.info("No projects linked to this asset.")
    finally:
        db.close_session(session)


if __name__ == "__main__":
    main()
