"""
Finance Dashboard (Read-only)
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config.theme import generate_css
from models.database import DatabaseManager, Transaction, TransactionType


st.set_page_config(page_title="Finance Dashboard", page_icon="💰", layout="wide")
st.markdown(generate_css("light"), unsafe_allow_html=True)


@st.cache_resource
def get_database() -> DatabaseManager:
    return DatabaseManager("sqlite:///industrial_real_estate.db")


def display_cashflow_trend(db: DatabaseManager, months: int):
    trend = db.get_cashflow_trend(months=months)
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
        title=f"Cashflow Trend (Last {months} Months, AUD Millions)",
        height=360,
        margin=dict(t=60, b=40, l=40, r=20),
    )
    st.plotly_chart(fig, width="stretch")


def compute_financial_health(trend: List[Dict[str, float]]) -> Dict[str, float]:
    if not trend:
        return {"ratio": 0, "avg_net": 0, "volatility": 0}
    income = [row["income"] for row in trend]
    expense = [abs(row["expense"]) for row in trend]
    net = [row["net"] for row in trend]
    ratio = (sum(income) / sum(expense)) if sum(expense) else 0
    avg_net = sum(net) / len(net)
    volatility = (
        sum(abs(net[i] - net[i - 1]) for i in range(1, len(net))) / (len(net) - 1)
        if len(net) > 1
        else 0
    )
    return {"ratio": ratio, "avg_net": avg_net, "volatility": volatility}


def get_vendor_payments(session) -> pd.DataFrame:
    rows = (
        session.query(Transaction.vendor_payee, Transaction.amount)
        .filter(Transaction.transaction_type == TransactionType.EXPENSE)
        .all()
    )
    data = {}
    for vendor, amount in rows:
        key = vendor or "Unknown"
        data[key] = data.get(key, 0) + abs(float(amount or 0))
    df = pd.DataFrame(
        [{"Vendor": vendor, "Total Paid (AUD)": total} for vendor, total in data.items()]
    )
    if df.empty:
        return pd.DataFrame(columns=["Vendor", "Total Paid (AUD)"])
    return df.sort_values("Total Paid (AUD)", ascending=False)


def main():
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.header("📊 Finance Dashboard")
    with col2:
        if st.button("➕ Add Transaction", use_container_width=True):
            st.switch_page("pages/2_data_input.py")
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    st.caption("This is a read-only view. To add/edit data, use the Data Input Center.")
    st.divider()

    db = get_database()
    now = datetime.now()
    months = st.selectbox("Time Range (Months)", options=[3, 6, 12], index=1)

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    balance = db.get_cash_balance()
    income = db.get_monthly_income(now.year, now.month)
    expense = db.get_monthly_expense(now.year, now.month)
    net = income - expense
    metric_col1.metric("Cash Balance", f"${balance:,.0f}")
    metric_col2.metric("This Month Income", f"${income:,.0f}")
    metric_col3.metric("This Month Expense", f"${expense:,.0f}")
    metric_col4.metric("Net Cashflow", f"${net:,.0f}")

    st.subheader("Monthly Cashflow")
    display_cashflow_trend(db, months)

    st.divider()
    st.subheader("Financial Health Indicators")
    trend = db.get_cashflow_trend(months=months)
    health = compute_financial_health(trend)
    health_col1, health_col2, health_col3 = st.columns(3)
    health_col1.metric("Income / Expense Ratio", f"{health['ratio']:.2f}x")
    health_col2.metric("Avg Monthly Net", f"${health['avg_net']:,.0f}")
    health_col3.metric("Cashflow Volatility", f"${health['volatility']:,.0f}")

    st.divider()
    st.subheader("Vendor Payment Analysis")
    session = db.get_session()
    try:
        vendor_df = get_vendor_payments(session)
    finally:
        db.close_session(session)

    if vendor_df.empty:
        st.info("No vendor payment data available.")
    else:
        st.dataframe(vendor_df.head(10), width="stretch", hide_index=True)
        fig = px.bar(
            vendor_df.head(10),
            x="Vendor",
            y="Total Paid (AUD)",
            title="Top Vendor Payments",
        )
        st.plotly_chart(fig, width="stretch")

    st.divider()
    st.subheader("Transaction History")
    session = db.get_session()
    try:
        transactions = (
            session.query(Transaction)
            .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
            .limit(200)
            .all()
        )
    finally:
        db.close_session(session)

    if not transactions:
        st.info("No transactions found.")
        return

    rows = []
    for tx in transactions:
        rows.append(
            {
                "Date": tx.transaction_date.strftime("%Y-%m-%d"),
                "Type": tx.transaction_type.value.title(),
                "Category": tx.category or "-",
                "Amount (AUD)": abs(float(tx.amount)),
                "Asset": tx.asset.name if tx.asset else "-",
                "Project": tx.project.project_name if tx.project else "-",
                "Vendor": tx.vendor_payee or "-",
                "Description": tx.description,
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
