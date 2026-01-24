"""
Projects Dashboard (Read-only)
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config.theme import generate_css
from models.database import DatabaseManager, Project, ProjectStatus


st.set_page_config(page_title="Projects Dashboard", page_icon="🏗️", layout="wide")
st.markdown(generate_css("light"), unsafe_allow_html=True)


@st.cache_resource
def get_database() -> DatabaseManager:
    return DatabaseManager("sqlite:///industrial_real_estate.db")


def status_label(status: ProjectStatus) -> str:
    mapping = {
        ProjectStatus.PLANNING: "Planning",
        ProjectStatus.APPROVAL_PENDING: "Approval Pending",
        ProjectStatus.APPROVED: "Approved",
        ProjectStatus.CONSTRUCTION: "Construction",
        ProjectStatus.COMPLETED: "Completed",
        ProjectStatus.ON_HOLD: "On Hold",
        ProjectStatus.CANCELLED: "Cancelled",
    }
    return mapping.get(status, status.value.title() if status else "-")


def completion_percentage(project: Project) -> float:
    if project.total_budget and project.total_budget > 0:
        actual_cost = float(project.actual_cost or 0)
        total_budget = float(project.total_budget or 0)
        return min(100.0, (actual_cost / total_budget) * 100)
    return 0.0


def build_project_rows(projects: List[Project]) -> pd.DataFrame:
    rows = []
    for proj in projects:
        budget = float(proj.total_budget or 0)
        actual = float(proj.actual_cost or 0)
        rows.append(
            {
                "Project": proj.project_name,
                "Status": status_label(proj.status),
                "Asset": proj.asset.name if proj.asset else "-",
                "Budget (AUD)": budget,
                "Actual Cost (AUD)": actual,
                "Variance (AUD)": budget - actual,
                "Progress %": round(completion_percentage(proj), 1),
            }
        )
    return pd.DataFrame(rows)


def render_budget_vs_actual(projects: List[Project]):
    if not projects:
        st.info("No projects available for comparison.")
        return
    labels = [proj.project_name for proj in projects]
    budget = [float(proj.total_budget or 0) / 1_000_000 for proj in projects]
    actual = [float(proj.actual_cost or 0) / 1_000_000 for proj in projects]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Budget", x=labels, y=budget))
    fig.add_trace(go.Bar(name="Actual", x=labels, y=actual))
    fig.update_layout(
        title="Budget vs Actual Cost (AUD, Millions)",
        barmode="group",
        height=360,
        margin=dict(t=60, b=40, l=40, r=20),
    )
    st.plotly_chart(fig, width="stretch")


def render_progress_chart(projects: List[Project]):
    if not projects:
        st.info("No projects available for progress tracking.")
        return
    labels = [proj.project_name for proj in projects]
    progress = [completion_percentage(proj) for proj in projects]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=progress, name="Progress %"))
    fig.update_layout(
        title="Project Progress Tracking",
        yaxis=dict(range=[0, 100]),
        height=320,
        margin=dict(t=60, b=40, l=40, r=20),
    )
    st.plotly_chart(fig, width="stretch")


def render_kanban(projects: List[Project]):
    if not projects:
        st.info("No projects to display.")
        return
    grouped: Dict[str, List[Project]] = defaultdict(list)
    for proj in projects:
        grouped[status_label(proj.status)].append(proj)

    status_order = [
        "Planning",
        "Approval Pending",
        "Approved",
        "Construction",
        "Completed",
        "On Hold",
        "Cancelled",
    ]

    columns = st.columns(len(status_order))
    for idx, status in enumerate(status_order):
        with columns[idx]:
            st.markdown(f"**{status}**")
            for proj in grouped.get(status, []):
                budget = float(proj.total_budget or 0)
                actual = float(proj.actual_cost or 0)
                st.markdown(
                    f"- {proj.project_name}\n"
                    f"  - Budget: ${budget:,.0f}\n"
                    f"  - Actual: ${actual:,.0f}"
                )


def main():
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.header("📊 Projects Dashboard")
    with col2:
        if st.button("➕ Add New Project", use_container_width=True):
            st.switch_page("pages/2_data_input.py")
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    st.caption("This is a read-only view. To add/edit data, use the Data Input Center.")
    st.divider()

    db = get_database()
    session = db.get_session()
    try:
        all_projects = session.query(Project).order_by(Project.created_at.desc()).all()
    finally:
        db.close_session(session)

    if not all_projects:
        st.info("No projects available.")
        return

    status_options = ["All"] + [status_label(s) for s in ProjectStatus]
    status_filter = st.selectbox("Filter by Status", status_options)
    if status_filter == "All":
        projects = all_projects
    else:
        projects = [p for p in all_projects if status_label(p.status) == status_filter]

    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    metrics_col1.metric("Total Projects", len(projects))
    metrics_col2.metric(
        "Total Budget",
        f"${sum(float(p.total_budget or 0) for p in projects):,.0f}",
    )
    metrics_col3.metric(
        "Total Actual Cost",
        f"${sum(float(p.actual_cost or 0) for p in projects):,.0f}",
    )

    st.subheader("Project List")
    df = build_project_rows(projects)
    st.dataframe(df, width="stretch", hide_index=True)

    st.divider()
    st.subheader("Kanban View")
    render_kanban(projects)

    st.divider()
    st.subheader("Budget vs Actual")
    render_budget_vs_actual(projects)

    st.divider()
    st.subheader("Progress Tracking")
    render_progress_chart(projects)

    st.divider()
    st.subheader("Project Details")
    for proj in projects:
        with st.expander(f"📋 {proj.project_name} - View Details"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Budget (AUD)", f"${float(proj.total_budget or 0):,.0f}")
                st.metric("Actual Cost (AUD)", f"${float(proj.actual_cost or 0):,.0f}")
            with col_b:
                st.metric("Progress %", f"{completion_percentage(proj):.0f}%")
                st.metric("Status", status_label(proj.status))

            st.subheader("Related Data")
            if proj.asset:
                st.write(f"Asset: {proj.asset.name}")
            st.write(
                f"Planned Start: {proj.planned_start_date.strftime('%Y-%m-%d') if proj.planned_start_date else 'N/A'}"
            )
            st.write(
                f"Planned Completion: {proj.planned_completion_date.strftime('%Y-%m-%d') if proj.planned_completion_date else 'N/A'}"
            )


if __name__ == "__main__":
    main()
