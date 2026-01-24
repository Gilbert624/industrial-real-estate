"""
Consultants Dashboard (Read-only)
"""

from __future__ import annotations

from datetime import date
from typing import List

import pandas as pd
import plotly.express as px
import streamlit as st

from config.theme import generate_css
from models.database import DatabaseManager
from utils.consultant_db import (
    calculate_scope_match,
    ensure_consultant_schema,
    get_all_consultants,
    get_quote_history,
    recommend_consultants,
)


st.set_page_config(page_title="Consultants Dashboard", page_icon="👷", layout="wide")
st.markdown(generate_css("light"), unsafe_allow_html=True)


@st.cache_resource
def get_database() -> DatabaseManager:
    db = DatabaseManager("sqlite:///industrial_real_estate.db")
    ensure_consultant_schema(db)
    return db


CATEGORIES = [
    "Town Planning",
    "Architecture",
    "Civil Engineer",
    "QS",
    "Surveyor",
    "Geotechnical",
    "Electrical",
    "Other",
]

PROJECT_TYPES = ["Warehouse", "Office", "Mixed", "Land"]


def render_performance_matrix(consultants: List[dict]):
    if not consultants:
        st.info("No consultant data available for analysis.")
        return
    df = pd.DataFrame(consultants)
    df["quality_rating"] = pd.to_numeric(df.get("quality_rating"), errors="coerce")
    df["reliability_rating"] = pd.to_numeric(df.get("reliability_rating"), errors="coerce")
    df["cost_competitiveness"] = pd.to_numeric(df.get("cost_competitiveness"), errors="coerce")
    df["category"] = df.get("category", "Other").fillna("Other")
    df["label"] = df.get("name")

    fig = px.scatter(
        df,
        x="quality_rating",
        y="reliability_rating",
        size="cost_competitiveness",
        color="category",
        hover_name="label",
        title="Consultant Performance Matrix",
        labels={"quality_rating": "Quality", "reliability_rating": "Reliability"},
    )
    fig.update_layout(height=360, margin=dict(t=60, b=40, l=40, r=20))
    st.plotly_chart(fig, width="stretch")


def render_scope_match_chart(recommendations: List[dict]):
    if not recommendations:
        st.info("No scope match data available.")
        return
    rows = []
    for rec in recommendations:
        consultant = rec["consultant"]
        match = rec["scope_match"]
        rows.append(
            {
                "Consultant": consultant.get("name"),
                "Scope Match %": round(match["match_rate"] * 100, 1),
            }
        )
    df = pd.DataFrame(rows)
    fig = px.bar(df, x="Consultant", y="Scope Match %", title="Scope Match Analysis")
    fig.update_layout(height=320, margin=dict(t=60, b=40, l=40, r=20))
    st.plotly_chart(fig, width="stretch")


def main():
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.header("📊 Consultants Dashboard")
    with col2:
        if st.button("➕ Add Consultant", use_container_width=True):
            st.switch_page("pages/2_data_input.py")
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    st.caption("This is a read-only view. To add/edit data, use the Data Input Center.")
    st.divider()

    db = get_database()
    _ = db  # reserved for potential future reads

    tab_list = [
        "Consultant List",
        "Quote History",
        "Smart Recommendations",
        "Analytics",
    ]
    tab1, tab2, tab3, tab4 = st.tabs(tab_list)

    with tab1:
        st.subheader("Consultant List")
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("Search (Name / Company)")
        with col2:
            category_filter = st.selectbox("Category", ["All"] + CATEGORIES)

        consultants = get_all_consultants(category_filter=category_filter, active_only=True)
        if search_term:
            search_lower = search_term.lower()
            consultants = [
                c
                for c in consultants
                if search_lower in (c.get("name") or "").lower()
                or search_lower in (c.get("company") or "").lower()
            ]

        if not consultants:
            st.info("No consultants found.")
        else:
            display_df = pd.DataFrame(
                [
                    {
                        "Name": c.get("name"),
                        "Company": c.get("company") or "-",
                        "Category": c.get("category") or "-",
                        "Quality": c.get("quality_rating") or "-",
                        "Reliability": c.get("reliability_rating") or "-",
                        "Email": c.get("email") or "-",
                        "Phone": c.get("phone") or "-",
                    }
                    for c in consultants
                ]
            )
            st.dataframe(display_df, width="stretch", hide_index=True)

            st.markdown("---")
            st.subheader("Consultant Details")
            for consultant in consultants:
                with st.expander(f"📋 {consultant.get('name')} - View Details"):
                    st.write(f"Company: {consultant.get('company') or '-'}")
                    st.write(f"Category: {consultant.get('category') or '-'}")
                    st.write(f"Specialty: {consultant.get('specialty') or '-'}")
                    st.write(f"Contact: {consultant.get('contact_person') or '-'}")
                    st.write(f"Email: {consultant.get('email') or '-'}")
                    st.write(f"Phone: {consultant.get('phone') or '-'}")

    with tab2:
        st.subheader("Quote History")
        consultants = get_all_consultants(active_only=False)
        consultant_map = {c["name"]: c["id"] for c in consultants}
        consultant_names = ["All"] + list(consultant_map.keys())

        projects = db.get_all_projects()
        project_map = {p.project_name: p.id for p in projects}
        project_names = ["All"] + list(project_map.keys())

        filter_cols = st.columns([1, 1, 1])
        with filter_cols[0]:
            selected_consultant = st.selectbox("Consultant", consultant_names)
        with filter_cols[1]:
            selected_project = st.selectbox("Project", project_names)
        with filter_cols[2]:
            date_range = st.date_input("Date Range", value=(date.today().replace(day=1), date.today()))

        consultant_id = consultant_map.get(selected_consultant) if selected_consultant != "All" else None
        project_id = project_map.get(selected_project) if selected_project != "All" else None

        history = get_quote_history(project_id=project_id, consultant_id=consultant_id)
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            history = [
                h
                for h in history
                if h.get("quote_date") and start_date <= h["quote_date"] <= end_date
            ]

        if history:
            history_df = pd.DataFrame(history)
            display_df = history_df[
                [
                    "consultant_name",
                    "project_name",
                    "scope_of_work",
                    "quote_amount",
                    "actual_amount",
                    "status",
                ]
            ].rename(
                columns={
                    "consultant_name": "Consultant",
                    "project_name": "Project",
                    "scope_of_work": "Scope of Work",
                    "quote_amount": "Quote Amount",
                    "actual_amount": "Actual Amount",
                }
            )
            st.dataframe(display_df, width="stretch", hide_index=True)
        else:
            st.info("No quote history found.")

    with tab3:
        st.subheader("Smart Recommendations")
        input_cols = st.columns([1, 1, 1])
        with input_cols[0]:
            category = st.selectbox("Service Category", CATEGORIES)
        with input_cols[1]:
            project_type = st.selectbox("Project Type", PROJECT_TYPES)
        with input_cols[2]:
            project_size = st.number_input("Project Size (sqm)", min_value=0.0, step=100.0)
        required_scopes_text = st.text_area("Required Scopes (one per line)", height=120)
        required_scopes = [line.strip() for line in required_scopes_text.splitlines() if line.strip()]

        if st.button("🔍 Generate Recommendations", width="stretch"):
            recommendations = recommend_consultants(category, project_size, required_scopes, project_type)
            if not recommendations:
                st.info("No matching consultants found.")
            else:
                rows = []
                for idx, rec in enumerate(recommendations, start=1):
                    consultant = rec["consultant"]
                    match = rec["scope_match"]
                    rows.append(
                        {
                            "Rank": idx,
                            "Consultant": consultant.get("name"),
                            "Company": consultant.get("company") or "-",
                            "Score": rec["score"],
                            "Scope Match %": round(match["match_rate"] * 100, 1),
                        }
                    )
                st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
                render_scope_match_chart(recommendations)

    with tab4:
        st.subheader("Analytics")
        consultants = get_all_consultants(active_only=True)
        render_performance_matrix(consultants)


if __name__ == "__main__":
    main()
