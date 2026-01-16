import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from models.database import DatabaseManager
from datetime import datetime
import pandas as pd
from config.theme import generate_css
from utils.chart_styles import get_chart_layout, apply_professional_theme_to_figure, CHART_COLORS
from config.i18n import t, get_current_language
from utils.development_costs import (
    DevelopmentCostBreakdown,
    SiteWorksBreakdown,
    PropertyType,
    QLD_COST_BENCHMARKS,
    QLD_GOVERNMENT_CHARGES,
    PROFESSIONAL_FEE_BENCHMARKS,
)
from utils.loan_calculator import DualPhaseLoanModel, AU_LOAN_BENCHMARKS
from utils.session_state_manager import (
    DDSessionStateManager,
    ProjectCostData,
    ProjectFinancingData,
    ProjectFinancialMetrics,
    DataSource,
    render_data_sync_status,
)

# 页面配置
st.set_page_config(page_title="Due Diligence - Industrial RE", page_icon="🔍", layout="wide")

# 应用专业主题
st.markdown(generate_css('light'), unsafe_allow_html=True)

st.title("🔍 Due Diligence Analysis")
st.write(t('dd.subtitle'))

# 初始化
db = DatabaseManager()

# Session state
if 'selected_dd_project' not in st.session_state:
    st.session_state.selected_dd_project = None


def render_project_overview_tab():
    """渲染项目概览标签页 - 汇总显示"""
    st.header("📋 Project Overview")

    # 初始化状态管理器
    DDSessionStateManager.initialize()

    # 显示同步状态
    st.subheader("📊 Data Status")
    render_data_sync_status()

    st.markdown("---")

    # 获取汇总数据
    summary = DDSessionStateManager.get_summary_for_display()
    cost = summary["cost"]
    financing = summary["financing"]
    metrics = summary["metrics"]

    # 检查是否有数据
    has_cost_data = cost["total_development_cost"] > 0
    has_financing_data = financing["construction_loan"] > 0
    has_metrics_data = metrics["irr"] != 0

    if not has_cost_data:
        st.info("👉 Please start by entering cost details in the **Cost Breakdown** tab")

        # 快速开始选项
        st.subheader("🚀 Quick Start")

        if st.button("Load Sunshine Coast Warehouse Example", type="primary"):
            from utils.development_costs import create_sunshine_coast_warehouse_example

            example = create_sunshine_coast_warehouse_example()
            result = example.calculate_total_development_cost()

            cost_data = ProjectCostData(
                land_area_sqm=example.land_area_sqm,
                land_price_per_sqm=example.land_price_per_sqm,
                land_purchase_price=result["hard_costs"]["land_costs"][
                    "land_purchase_price"
                ],
                total_land_cost=result["hard_costs"]["land_costs"]["total_land_cost"],
                gross_floor_area=example.gross_floor_area,
                construction_rate_per_sqm=example.construction_rate_per_sqm,
                base_construction_cost=result["hard_costs"]["construction_costs"][
                    "base_construction_cost"
                ],
                total_site_works=result["hard_costs"]["site_works"]["total"],
                total_contingency=result["hard_costs"]["contingency"][
                    "total_contingency"
                ],
                total_professional_fees=result["soft_costs"]["professional_fees"]["total"],
                total_government_charges=result["soft_costs"]["government_charges"][
                    "total"
                ],
                total_hard_costs=result["summary"]["total_hard_costs"],
                total_soft_costs=result["summary"]["total_soft_costs"],
                total_development_cost=result["summary"]["total_development_cost"],
                source=DataSource.COST_BREAKDOWN.value,
            )
            DDSessionStateManager.set_cost_data(cost_data)
            st.rerun()

        return

    # 显示汇总数据
    st.subheader("💰 Cost Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Development Cost",
            f"${cost['total_development_cost']:,.0f}",
        )

    with col2:
        st.metric(
            "Hard Costs",
            f"${cost['total_hard_costs']:,.0f}",
        )

    with col3:
        st.metric(
            "Soft Costs",
            f"${cost['total_soft_costs']:,.0f}",
        )

    with col4:
        st.metric(
            "Cost per sqm",
            f"${cost['cost_per_sqm']:,.0f}",
        )

    if has_financing_data:
        st.markdown("---")
        st.subheader("🏦 Financing Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Construction Loan",
                f"${financing['construction_loan']:,.0f}",
            )

        with col2:
            st.metric(
                "Investment Loan",
                f"${financing['investment_loan']:,.0f}",
            )

        with col3:
            st.metric(
                "Total Equity",
                f"${financing['total_equity']:,.0f}",
                f"{financing['equity_pct']:.1f}%",
            )

        with col4:
            dscr_color = "normal" if financing["dscr"] >= 1.25 else "inverse"
            st.metric(
                "DSCR",
                f"{financing['dscr']:.2f}x" if financing["dscr"] > 0 else "N/A",
                delta_color=dscr_color,
            )
    else:
        st.info("👉 Configure financing in the **Loan Calculator** tab")

    if has_metrics_data:
        st.markdown("---")
        st.subheader("📈 Return Metrics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            irr_color = "normal" if metrics["irr"] >= 15 else "inverse"
            st.metric(
                "IRR",
                f"{metrics['irr']:.1f}%",
                delta_color=irr_color,
            )

        with col2:
            st.metric(
                "NPV",
                f"${metrics['npv']:,.0f}",
            )

        with col3:
            st.metric(
                "Equity Multiple",
                f"{metrics['equity_multiple']:.2f}x",
            )

        with col4:
            st.metric(
                "Profit Margin",
                f"{metrics['profit_margin']:.1f}%",
            )
    else:
        st.info("👉 Calculate returns in the **Financial Model** tab")

    st.markdown("---")
    st.caption(
        "**Data Flow:**\n"
        "1. **Cost Breakdown** → Enter detailed development costs\n"
        "2. **Loan Calculator** → Configure construction & investment loans  \n"
        "3. **Financial Model** → Calculate IRR, NPV, and returns\n"
        "4. **Scenarios** → Run sensitivity analysis\n"
        "5. **Report** → Generate professional reports"
    )

    st.markdown("---")
    with st.expander("🔧 Debug: Session State Data"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**Cost Data**")
            cost_data = DDSessionStateManager.get_cost_data()
            st.json(
                {
                    "total_development_cost": cost_data.total_development_cost,
                    "total_hard_costs": cost_data.total_hard_costs,
                    "total_soft_costs": cost_data.total_soft_costs,
                    "gross_floor_area": cost_data.gross_floor_area,
                    "source": cost_data.source,
                }
            )

        with col2:
            st.write("**Financing Data**")
            fin = DDSessionStateManager.get_financing_data()
            st.json(
                {
                    "construction_loan_amount": fin.construction_loan_amount,
                    "investment_loan_amount": fin.investment_loan_amount,
                    "total_equity_required": fin.total_equity_required,
                    "dscr": fin.dscr,
                    "source": fin.source,
                }
            )

        with col3:
            st.write("**Sync Status**")
            status = DDSessionStateManager.get_sync_status()
            st.json(status)

        if st.button("🔄 Reset All Data", type="secondary"):
            DDSessionStateManager.reset_all()
            st.rerun()


def render_quick_setup_tab():
    """快速设置标签页 - 简化输入"""
    st.header("⚡ Quick Setup")
    st.markdown("Quick project setup for rapid feasibility analysis")

    with st.form("quick_setup_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Project Basics")
            land_cost = st.number_input("Land Cost ($)", value=2_975_000.0)
            construction_cost = st.number_input(
                "Construction Cost ($)", value=5_250_000.0
            )
            other_costs = st.number_input(
                "Other Development Costs ($)", value=800_000.0
            )

        with col2:
            st.subheader("Financing")
            ltc = st.slider("Loan-to-Cost %", 50, 75, 65)
            interest_rate = st.slider("Blended Interest Rate %", 6.0, 10.0, 7.5)
            completion_value = st.number_input(
                "Expected Completion Value ($)", value=10_200_000.0
            )

        submitted = st.form_submit_button("Apply Quick Setup", type="primary")

        if submitted:
            total_dev_cost = land_cost + construction_cost + other_costs

            cost_data = ProjectCostData(
                total_land_cost=land_cost,
                base_construction_cost=construction_cost,
                total_soft_costs=other_costs,
                total_hard_costs=land_cost + construction_cost,
                total_development_cost=total_dev_cost,
                source=DataSource.MANUAL.value,
            )
            DDSessionStateManager.set_cost_data(cost_data)

            financing_data = ProjectFinancingData(
                construction_ltc_pct=ltc,
                construction_loan_amount=total_dev_cost * (ltc / 100),
                construction_interest_rate=interest_rate,
                completion_value=completion_value,
                investment_lvr_pct=60,
                investment_loan_amount=completion_value * 0.6,
                total_equity_required=total_dev_cost * (1 - ltc / 100),
                equity_percentage=100 - ltc,
                source=DataSource.MANUAL.value,
            )
            DDSessionStateManager.set_financing_data(financing_data)

            st.success("✅ Quick setup applied! Data synced to all tabs.")
            st.info(
                "💡 For detailed breakdown, use the Cost Breakdown and Loan Calculator tabs."
            )


def render_cost_breakdown_tab():
    """渲染成本细分标签页 - 更新版"""
    st.header("💵 Development Cost Breakdown")
    st.markdown(
        "Detailed cost analysis for industrial property development in Queensland"
    )

    DDSessionStateManager.initialize()
    sync_status = DDSessionStateManager.get_sync_status()
    if sync_status["cost_updated"]:
        st.success("✅ Cost data is synced with other tabs")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.subheader("🏗️ Project Parameters")
        project_name = st.text_input(
            "Project Name", value="Industrial Warehouse Project"
        )
        location = st.selectbox(
            "Location",
            options=["brisbane", "sunshine_coast", "moreton_bay"],
            format_func=lambda x: x.replace("_", " ").title(),
        )
        property_type = st.selectbox(
            "Property Type",
            options=[pt for pt in PropertyType],
            format_func=lambda x: x.value.replace("_", " ").title(),
        )

        benchmarks = QLD_COST_BENCHMARKS.get(property_type, {})
        st.info(
            f"💡 Reference rate for {property_type.value}: "
            f"${benchmarks.get('construction_rate_typical', 1250):,.0f}/sqm"
        )
        council = QLD_GOVERNMENT_CHARGES.get(location, QLD_GOVERNMENT_CHARGES["brisbane"])
        st.caption(
            f"Queensland infra charge: "
            f"${council['infrastructure_charge_per_sqm']:.0f}/sqm"
        )

        st.markdown("---")
        st.subheader("📐 Area & Land")
        land_area = st.number_input(
            "Land Area (sqm)",
            min_value=1000.0,
            max_value=100000.0,
            value=8500.0,
            step=100.0,
        )
        land_price = st.number_input(
            "Land Price ($/sqm)",
            min_value=100.0,
            max_value=2000.0,
            value=350.0,
            step=10.0,
        )
        gfa = st.number_input(
            "Gross Floor Area (sqm)",
            min_value=500.0,
            max_value=50000.0,
            value=4200.0,
            step=100.0,
        )
        construction_rate = st.number_input(
            "Construction Rate ($/sqm)",
            min_value=500.0,
            max_value=5000.0,
            value=float(benchmarks.get("construction_rate_typical", 1250)),
            step=50.0,
            help=(
                f"Benchmark range: "
                f"${benchmarks.get('construction_rate_min', 900):,.0f} - "
                f"${benchmarks.get('construction_rate_max', 1800):,.0f}/sqm"
            ),
        )

    with col2:
        st.subheader("🔧 Site Works")
        site_clearing = st.number_input("Site Clearing ($)", value=25000.0, step=5000.0)
        earthworks = st.number_input("Earthworks ($)", value=150000.0, step=10000.0)
        stormwater = st.number_input(
            "Stormwater Drainage ($)", value=80000.0, step=5000.0
        )
        sewer = st.number_input("Sewer Connection ($)", value=35000.0, step=5000.0)
        water = st.number_input("Water Connection ($)", value=25000.0, step=5000.0)
        electrical = st.number_input(
            "Electrical Connection ($)", value=45000.0, step=5000.0
        )
        road_works = st.number_input("Road Works ($)", value=120000.0, step=10000.0)
        car_parking = st.number_input("Car Parking ($)", value=85000.0, step=5000.0)
        hardstand = st.number_input("Hardstand ($)", value=180000.0, step=10000.0)
        landscaping = st.number_input("Landscaping ($)", value=35000.0, step=5000.0)
        fencing = st.number_input("Fencing ($)", value=45000.0, step=5000.0)
        site_works_total = (
            site_clearing
            + earthworks
            + stormwater
            + sewer
            + water
            + electrical
            + road_works
            + car_parking
            + hardstand
            + landscaping
            + fencing
        )

    with col3:
        st.subheader("📋 Professional Fees")

        fee_input_mode = st.radio(
            "Input Mode",
            options=["Percentage of Construction", "Fixed Amount"],
            horizontal=True,
            key="fee_input_mode",
        )

        if fee_input_mode == "Percentage of Construction":
            base_construction = gfa * construction_rate
            st.caption(f"Base: ${base_construction:,.0f} (GFA × Rate)")

            architect_pct = st.slider("Architect (%)", 1.0, 6.0, 3.0, 0.5)
            structural_pct = st.slider("Structural Engineer (%)", 0.5, 3.0, 1.5, 0.5)
            civil_pct = st.slider("Civil Engineer (%)", 0.5, 2.5, 1.5, 0.5)
            mep_pct = st.slider("MEP Engineer (%)", 1.0, 4.0, 2.0, 0.5)
            qs_pct = st.slider("Quantity Surveyor (%)", 0.5, 2.0, 1.0, 0.5)
            pm_pct = st.slider("Project Manager (%)", 1.5, 6.0, 3.0, 0.5)

            architect_fee = base_construction * (architect_pct / 100)
            structural_fee = base_construction * (structural_pct / 100)
            civil_fee = base_construction * (civil_pct / 100)
            mep_fee = base_construction * (mep_pct / 100)
            qs_fee = base_construction * (qs_pct / 100)
            pm_fee = base_construction * (pm_pct / 100)
        else:
            architect_fee = st.number_input(
                "Architect ($)", value=150000.0, step=10000.0
            )
            structural_fee = st.number_input(
                "Structural Engineer ($)", value=75000.0, step=5000.0
            )
            civil_fee = st.number_input(
                "Civil Engineer ($)", value=75000.0, step=5000.0
            )
            mep_fee = st.number_input("MEP Engineer ($)", value=100000.0, step=5000.0)
            qs_fee = st.number_input(
                "Quantity Surveyor ($)", value=50000.0, step=5000.0
            )
            pm_fee = st.number_input(
                "Project Manager ($)", value=150000.0, step=10000.0
            )

            base_construction = gfa * construction_rate
            if base_construction > 0:
                architect_pct = (architect_fee / base_construction) * 100
                structural_pct = (structural_fee / base_construction) * 100
                civil_pct = (civil_fee / base_construction) * 100
                mep_pct = (mep_fee / base_construction) * 100
                qs_pct = (qs_fee / base_construction) * 100
                pm_pct = (pm_fee / base_construction) * 100

        total_professional_fees = (
            architect_fee
            + structural_fee
            + civil_fee
            + mep_fee
            + qs_fee
            + pm_fee
        )
        st.metric("Total Professional Fees", f"${total_professional_fees:,.0f}")

        st.markdown("---")
        st.subheader("⚠️ Contingency")

        contingency_mode = st.radio(
            "Input Mode",
            options=["Percentage", "Fixed Amount"],
            horizontal=True,
            key="contingency_input_mode",
        )

        base_for_contingency = (gfa * construction_rate) + site_works_total

        if contingency_mode == "Percentage":
            st.caption(
                f"Base: ${base_for_contingency:,.0f} (Construction + Site Works)"
            )

            design_contingency_pct = st.slider(
                "Design Contingency (%)", 0.0, 10.0, 5.0, 1.0
            )
            construction_contingency_pct = st.slider(
                "Construction Contingency (%)", 0.0, 15.0, 5.0, 1.0
            )

            design_contingency = base_for_contingency * (design_contingency_pct / 100)
            construction_contingency = base_for_contingency * (
                construction_contingency_pct / 100
            )
        else:
            design_contingency = st.number_input(
                "Design Contingency ($)", value=250000.0, step=25000.0
            )
            construction_contingency = st.number_input(
                "Construction Contingency ($)", value=250000.0, step=25000.0
            )

            if base_for_contingency > 0:
                design_contingency_pct = (
                    design_contingency / base_for_contingency
                ) * 100
                construction_contingency_pct = (
                    construction_contingency / base_for_contingency
                ) * 100

        total_contingency = design_contingency + construction_contingency
        st.metric("Total Contingency", f"${total_contingency:,.0f}")

        st.markdown("---")
        st.subheader("💰 Other Costs")
        legal_fees = st.number_input("Legal Fees ($)", value=30000.0, step=5000.0)
        valuation_fees = st.number_input(
            "Valuation Fees ($)", value=8000.0, step=1000.0
        )

    st.markdown("---")
    if st.button("📊 Calculate & Sync", type="primary", use_container_width=True):
        site_works_obj = SiteWorksBreakdown(
            site_clearing=site_clearing,
            earthworks=earthworks,
            stormwater_drainage=stormwater,
            sewer_connection=sewer,
            water_connection=water,
            electrical_connection=electrical,
            road_works=road_works,
            car_parking=car_parking,
            hardstand=hardstand,
            landscaping=landscaping,
            fencing=fencing,
        )
        cost_model = DevelopmentCostBreakdown(
            project_name=project_name,
            location=location,
            property_type=property_type,
            land_area_sqm=land_area,
            land_price_per_sqm=land_price,
            gross_floor_area=gfa,
            construction_rate_per_sqm=construction_rate,
            site_works=site_works_obj,
            design_contingency_pct=design_contingency_pct,
            construction_contingency_pct=construction_contingency_pct,
            architect_pct=architect_pct,
            structural_engineer_pct=structural_pct,
            civil_engineer_pct=civil_pct,
            mep_engineer_pct=mep_pct,
            quantity_surveyor_pct=qs_pct,
            project_manager_pct=pm_pct,
            legal_fees=legal_fees,
            valuation_fees=valuation_fees,
        )

        result = cost_model.calculate_total_development_cost()
        st.session_state["cost_breakdown_result"] = result
        st.session_state["cost_model"] = cost_model

        cost_data = ProjectCostData(
            land_area_sqm=land_area,
            land_price_per_sqm=land_price,
            land_purchase_price=result["hard_costs"]["land_costs"][
                "land_purchase_price"
            ],
            land_acquisition_costs=result["hard_costs"]["land_costs"][
                "acquisition_costs"
            ],
            total_land_cost=result["hard_costs"]["land_costs"]["total_land_cost"],
            gross_floor_area=gfa,
            construction_rate_per_sqm=construction_rate,
            base_construction_cost=result["hard_costs"]["construction_costs"][
                "base_construction_cost"
            ],
            total_site_works=result["hard_costs"]["site_works"]["total"],
            total_contingency=result["hard_costs"]["contingency"]["total_contingency"],
            total_professional_fees=result["soft_costs"]["professional_fees"]["total"],
            total_government_charges=result["soft_costs"]["government_charges"]["total"],
            total_other_soft_costs=sum(result["soft_costs"]["other_costs"].values()),
            total_hard_costs=result["summary"]["total_hard_costs"],
            total_soft_costs=result["summary"]["total_soft_costs"],
            total_development_cost=result["summary"]["total_development_cost"],
            source=DataSource.COST_BREAKDOWN.value,
        )

        DDSessionStateManager.set_cost_data(cost_data)
        st.success("✅ Cost data calculated and synced!")
        st.info("💡 Data is now available in Loan Calculator and Financial Model tabs")

        if st.button("💾 Save to Project", type="secondary", key="save_cost_to_project"):
            if not st.session_state.selected_dd_project:
                st.warning("Please select a DD project first.")
            else:
                base_construction = gfa * construction_rate
                base_for_contingency = base_construction + site_works_total
                contingency_pct = (
                    (total_contingency / base_for_contingency) * 100
                    if base_for_contingency > 0
                    else 0
                )
                update_data = {
                    "land_area_sqm": land_area,
                    "building_area_sqm": gfa,
                    "purchase_price": result["hard_costs"]["land_costs"][
                        "land_purchase_price"
                    ],
                    "acquisition_costs": result["hard_costs"]["land_costs"][
                        "acquisition_costs"
                    ],
                    "construction_cost": (
                        result["hard_costs"]["construction_costs"][
                            "base_construction_cost"
                        ]
                        + result["hard_costs"]["site_works"]["total"]
                        + result["hard_costs"]["contingency"]["total_contingency"]
                    ),
                    "contingency_percentage": contingency_pct,
                }
                try:
                    db.update_dd_project(st.session_state.selected_dd_project, update_data)
                    st.success("✅ Saved cost data to project.")
                except Exception as e:
                    st.error(f"❌ Failed to save cost data: {e}")

    if "cost_breakdown_result" in st.session_state:
        result = st.session_state["cost_breakdown_result"]
        total_dev_cost = result["summary"]["total_development_cost"]
        if total_dev_cost > 1_000_000_000:
            st.error(
                f"⚠️ Calculation error detected: "
                f"${total_dev_cost:,.0f} seems too high. Please check inputs."
            )
            with st.expander("🔍 Debug: Check Input Values"):
                st.write(f"GFA: {gfa} sqm")
                st.write(f"Construction Rate: ${construction_rate}/sqm")
                st.write(f"Base Construction: ${gfa * construction_rate:,.0f}")
                st.write(f"Land Area: {land_area} sqm")
                st.write(f"Land Price: ${land_price}/sqm")
                st.write(f"Land Cost: ${land_area * land_price:,.0f}")
            return
        with st.expander("🔍 Debug: Calculation Summary"):
            st.write("DEBUG - Result from calculation:")
            st.write(f"Hard: {result['summary']['total_hard_costs']}")
            st.write(f"Soft: {result['summary']['total_soft_costs']}")
            st.write(f"Total: {result['summary']['total_development_cost']}")
        st.markdown("---")
        st.header("📈 Results")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Total Development Cost",
                f"${result['summary']['total_development_cost']:,.0f}",
            )
        with col2:
            st.metric(
                "Hard Costs",
                f"${result['summary']['total_hard_costs']:,.0f}",
                f"{result['summary']['hard_cost_percentage']:.1f}%",
            )
        with col3:
            st.metric(
                "Soft Costs",
                f"${result['summary']['total_soft_costs']:,.0f}",
                f"{result['summary']['soft_cost_percentage']:.1f}%",
            )
        with col4:
            st.metric(
                "Cost per sqm (GFA)",
                f"${result['summary']['cost_per_sqm_gfa']:,.0f}",
            )

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💵 Cost Distribution")
            fig_pie = go.Figure(
                data=[
                    go.Pie(
                        labels=["Hard Costs", "Soft Costs"],
                        values=[
                            result["summary"]["total_hard_costs"],
                            result["summary"]["total_soft_costs"],
                        ],
                        hole=0.4,
                        marker_colors=["#1f77b4", "#ff7f0e"],
                    )
                ]
            )
            fig_pie.update_layout(height=350)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            st.subheader("🏗️ Hard Cost Breakdown")
            hard = result["hard_costs"]["summary"]
            fig_bar = go.Figure(
                data=[
                    go.Bar(
                        x=["Land", "Construction", "Site Works", "Contingency"],
                        y=[
                            hard["total_land"],
                            hard["total_construction"],
                            hard["total_site_works"],
                            hard["total_contingency"],
                        ],
                        marker_color=["#2ca02c", "#1f77b4", "#9467bd", "#d62728"],
                    )
                ]
            )
            fig_bar.update_layout(height=350, yaxis_title="Amount (AUD)")
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        with st.expander("📋 View Detailed Cost Table"):
            cost_model = st.session_state.get("cost_model")
            if cost_model:
                rows = cost_model.generate_cost_summary_table()
                df = pd.DataFrame(rows)
                df["Amount"] = df["Amount"].apply(
                    lambda x: f"${x:,.0f}"
                    if isinstance(x, (int, float)) and x != ""
                    else x
                )
                st.dataframe(df, use_container_width=True, hide_index=True)


def render_loan_calculator_tab():
    """渲染贷款计算器标签页 - 更新版"""
    st.header("🏦 Dual-Phase Loan Calculator")
    st.markdown(
        "Calculate construction and investment loan requirements for your development"
    )

    DDSessionStateManager.initialize()
    cost_data = DDSessionStateManager.get_cost_data()

    if cost_data.total_development_cost == 0:
        st.warning(
            "⚠️ No cost data available. Please complete the **Cost Breakdown** tab first."
        )

        use_manual = st.checkbox("Or enter development cost manually")
        if use_manual:
            manual_cost = st.number_input(
                "Total Development Cost ($)",
                min_value=1_000_000.0,
                max_value=100_000_000.0,
                value=8_500_000.0,
                step=100_000.0,
            )
            cost_data.total_development_cost = manual_cost
        else:
            return
    else:
        st.success(f"✅ Using cost data: ${cost_data.total_development_cost:,.0f}")
        st.caption(f"Source: {cost_data.source}")

    default_dev_cost = cost_data.total_development_cost

    loan_tab1, loan_tab2, loan_tab3 = st.tabs(
        ["📝 Parameters", "📊 Construction Loan", "🏠 Investment Loan"]
    )

    with loan_tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🏗️ Project Parameters")
            max_dev_cost = 500_000_000.0
            total_dev_cost = st.number_input(
                "Total Development Cost ($)",
                min_value=1_000_000.0,
                max_value=max_dev_cost,
                value=min(default_dev_cost, max_dev_cost),
                step=100_000.0,
                help="From Cost Breakdown tab or enter manually",
            )
            max_completion_value = 10_000_000_000.0
            default_completion_value = total_dev_cost * 1.20
            completion_value = st.number_input(
                "Expected Completion Value ($)",
                min_value=0.0,
                max_value=max_completion_value,
                value=min(default_completion_value, max_completion_value),
                step=100_000.0,
                help="Expected market value on completion",
            )
            construction_months = st.slider(
                "Construction Duration (months)",
                min_value=6,
                max_value=36,
                value=14,
            )
            expected_noi = st.number_input(
                "Expected Annual NOI ($)",
                min_value=0.0,
                max_value=100_000_000_000.0,
                value=completion_value * 0.065,
                step=10_000.0,
                help="For DSCR calculation",
            )

        with col2:
            st.subheader("🏦 Construction Loan")
            const_ltc = st.slider(
                "Loan-to-Cost (LTC) %",
                min_value=50,
                max_value=75,
                value=65,
                help=(
                    f"Typical range: "
                    f"{AU_LOAN_BENCHMARKS['construction']['ltc_min']}-"
                    f"{AU_LOAN_BENCHMARKS['construction']['ltc_max']}%"
                ),
            )
            const_rate = st.slider(
                "Interest Rate (% p.a.)",
                min_value=6.0,
                max_value=12.0,
                value=8.5,
                step=0.25,
            )

            st.markdown("**Loan Fees**")
            col_fee1, col_fee2 = st.columns(2)
            with col_fee1:
                establishment_fee_pct = st.number_input(
                    "Establishment Fee (%)",
                    min_value=0.0,
                    max_value=3.0,
                    value=1.0,
                    step=0.25,
                    help="One-time fee charged at loan setup",
                )
            with col_fee2:
                line_fee_pct = st.number_input(
                    "Line Fee (%)",
                    min_value=0.0,
                    max_value=2.0,
                    value=0.5,
                    step=0.25,
                    help="Annual fee on undrawn facility",
                )

            capitalize_interest = st.checkbox("Capitalize Interest", value=True)

            st.markdown("---")
            st.subheader("🏠 Investment Loan")
            inv_lvr = st.slider(
                "Loan-to-Value (LVR) %",
                min_value=40,
                max_value=70,
                value=60,
            )
            inv_rate = st.slider(
                "Interest Rate (% p.a.)",
                min_value=5.0,
                max_value=9.0,
                value=6.75,
                step=0.25,
            )
            inv_term = st.slider(
                "Loan Term (years)", min_value=10, max_value=30, value=25
            )
            io_years = st.slider(
                "Interest-Only Period (years)", min_value=0, max_value=10, value=5
            )

        st.markdown("---")
        if st.button("🧮 Calculate & Sync", type="primary", use_container_width=True):
            dual_loan = DualPhaseLoanModel(
                total_development_cost=total_dev_cost,
                completion_value=completion_value,
                construction_duration_months=construction_months,
                construction_ltc=const_ltc,
                construction_rate=const_rate,
                construction_establishment_fee=establishment_fee_pct,
                construction_line_fee=line_fee_pct,
                capitalize_interest=capitalize_interest,
                investment_lvr=inv_lvr,
                investment_rate=inv_rate,
                investment_term_years=inv_term,
                interest_only_years=io_years,
                expected_annual_noi=expected_noi,
            )
            result = dual_loan.calculate_full_financing()
            st.session_state["loan_result"] = result
            st.session_state["dual_loan_model"] = dual_loan
            financing_data = ProjectFinancingData(
                construction_loan_amount=result["construction_phase"]["loan_parameters"][
                    "loan_amount"
                ],
                construction_ltc_pct=const_ltc,
                construction_interest_rate=const_rate,
                construction_duration_months=construction_months,
                construction_total_interest=result["construction_phase"]["interest"][
                    "total_interest"
                ],
                construction_loan_at_completion=result["construction_phase"]["totals"][
                    "total_loan_at_completion"
                ],
                completion_value=completion_value,
                investment_loan_amount=result["investment_phase"]["loan_parameters"][
                    "loan_amount"
                ],
                investment_lvr_pct=inv_lvr,
                investment_interest_rate=inv_rate,
                investment_term_years=inv_term,
                interest_only_years=io_years,
                monthly_io_payment=result["investment_phase"]["payments"][
                    "monthly_io_payment"
                ],
                monthly_pi_payment=result["investment_phase"]["payments"][
                    "monthly_pi_payment"
                ],
                total_equity_required=result["equity_analysis"]["total_equity_required"],
                equity_percentage=result["equity_analysis"]["equity_pct_of_cost"],
                expected_annual_noi=expected_noi,
                dscr=result["debt_metrics"]["dscr"],
                source=DataSource.LOAN_CALCULATOR.value,
            )
            DDSessionStateManager.set_financing_data(financing_data)
            st.success("✅ Financing data calculated and synced!")

            if st.button("💾 Save to Project", type="secondary", key="save_loan_to_project"):
                if not st.session_state.selected_dd_project:
                    st.warning("Please select a DD project first.")
                else:
                    update_data = {
                        "construction_duration_months": construction_months,
                        "equity_percentage": financing_data.equity_percentage,
                        "debt_percentage": 100 - financing_data.equity_percentage,
                        "interest_rate": const_rate,
                        "loan_term_years": inv_term,
                    }
                    try:
                        db.update_dd_project(
                            st.session_state.selected_dd_project, update_data
                        )
                        st.success("✅ Saved financing data to project.")
                    except Exception as e:
                        st.error(f"❌ Failed to save financing data: {e}")

    with loan_tab2:
        st.subheader("📊 Construction Loan Analysis")
        if "loan_result" not in st.session_state:
            st.info("👆 Please calculate loans in the Parameters tab first")
            return
        result = st.session_state["loan_result"]
        const = result["construction_phase"]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Loan Amount",
                f"${const['loan_parameters']['loan_amount']:,.0f}",
            )
        with col2:
            st.metric(
                "Total Interest",
                f"${const['interest']['total_interest']:,.0f}",
            )
        with col3:
            st.metric(
                "Loan at Completion",
                f"${const['totals']['total_loan_at_completion']:,.0f}",
            )
        with col4:
            st.metric(
                "Equity Required",
                f"${const['totals']['equity_required']:,.0f}",
            )

        st.markdown("---")
        st.subheader("📈 Draw Schedule & Interest")
        schedule = const["draw_schedule"]
        months = [item["month"] for item in schedule]
        draws = [item["draw_amount"] for item in schedule]
        cumulative = [item["cumulative_drawn"] for item in schedule]
        interest = [item["cumulative_interest"] for item in schedule]

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(x=months, y=draws, name="Monthly Draw", marker_color="#1f77b4"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=months,
                y=cumulative,
                name="Cumulative Draw",
                line=dict(color="#2ca02c", width=3),
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=months,
                y=interest,
                name="Cumulative Interest",
                line=dict(color="#d62728", width=2, dash="dash"),
            ),
            secondary_y=True,
        )
        fig.update_layout(
            height=400,
            xaxis_title="Month",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        fig.update_yaxes(title_text="Draw Amount (AUD)", secondary_y=False)
        fig.update_yaxes(title_text="Cumulative Interest (AUD)", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 View Draw Schedule Table"):
            df = pd.DataFrame(schedule)
            df["draw_amount"] = df["draw_amount"].apply(lambda x: f"${x:,.0f}")
            df["cumulative_drawn"] = df["cumulative_drawn"].apply(
                lambda x: f"${x:,.0f}"
            )
            df["interest"] = df["interest"].apply(lambda x: f"${x:,.0f}")
            df["cumulative_interest"] = df["cumulative_interest"].apply(
                lambda x: f"${x:,.0f}"
            )
            df["total_outstanding"] = df["total_outstanding"].apply(
                lambda x: f"${x:,.0f}"
            )
            df["draw_percentage"] = df["draw_percentage"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(df, use_container_width=True, hide_index=True)

    with loan_tab3:
        st.subheader("🏠 Investment Loan Analysis")
        if "loan_result" not in st.session_state:
            st.info("👆 Please calculate loans in the Parameters tab first")
            return
        result = st.session_state["loan_result"]
        inv = result["investment_phase"]
        refinance = result["refinance_analysis"]
        equity = result["equity_analysis"]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Loan Amount",
                f"${inv['loan_parameters']['loan_amount']:,.0f}",
            )
        with col2:
            st.metric(
                "Monthly IO Payment",
                f"${inv['payments']['monthly_io_payment']:,.0f}",
            )
        with col3:
            st.metric(
                "Monthly P&I Payment",
                f"${inv['payments']['monthly_pi_payment']:,.0f}",
            )
        with col4:
            dscr = result["debt_metrics"]["dscr"]
            dscr_color = "normal" if dscr >= 1.25 else "inverse"
            st.metric(
                "DSCR",
                f"{dscr:.2f}x",
                "Adequate" if dscr >= 1.25 else "Below 1.25x",
                delta_color=dscr_color,
            )

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔄 Refinance Analysis")
            st.write(
                f"**Construction Loan Payoff:** "
                f"${refinance['construction_loan_payoff']:,.0f}"
            )
            st.write(
                f"**Investment Loan Amount:** "
                f"${refinance['investment_loan_amount']:,.0f}"
            )
            if refinance["refinance_feasible"]:
                st.success(
                    f"✅ Refinance Feasible - Cash Out: "
                    f"${refinance['equity_release']:,.0f}"
                )
            else:
                st.error(
                    f"❌ Additional Equity Required: "
                    f"${refinance['additional_equity_required']:,.0f}"
                )
        with col2:
            st.subheader("💰 Equity Summary")
            st.write(
                f"**Total Equity Required:** "
                f"${equity['total_equity_required']:,.0f}"
            )
            st.write(f"**Equity % of Cost:** {equity['equity_pct_of_cost']:.1f}%")
            st.write(
                f"**Equity Release at Refinance:** "
                f"${equity['equity_release_at_refinance']:,.0f}"
            )
            st.write(
                f"**Net Equity Invested:** "
                f"${equity['net_equity_invested']:,.0f}"
            )

        st.markdown("---")
        st.subheader("📈 Development Margin")
        project = result["project_summary"]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Development Cost", f"${project['total_development_cost']:,.0f}")
        with col2:
            st.metric("Completion Value", f"${project['completion_value']:,.0f}")
        with col3:
            margin_color = "normal" if project["development_margin_pct"] >= 15 else "inverse"
            st.metric(
                "Development Margin",
                f"${project['development_margin']:,.0f}",
                f"{project['development_margin_pct']:.1f}%",
                delta_color=margin_color,
            )


def build_financial_model_params(project, cost_data, financing_data):
    """Build FinancialModel parameters from session state with fallbacks."""
    base_construction = cost_data.base_construction_cost
    base_for_contingency = base_construction + cost_data.total_site_works
    contingency_pct = (
        (cost_data.total_contingency / base_for_contingency) * 100
        if base_for_contingency > 0
        else (project.contingency_percentage or 10.0)
    )

    equity_pct = financing_data.equity_percentage or (project.equity_percentage or 30.0)
    debt_pct = 100 - equity_pct

    annual_noi = financing_data.expected_annual_noi or 0.0
    monthly_rent = project.estimated_monthly_rent or (
        annual_noi / 12 if annual_noi > 0 else 0
    )

    return {
        "purchase_price": cost_data.land_purchase_price or project.purchase_price or 0,
        "acquisition_costs": cost_data.land_acquisition_costs
        or project.acquisition_costs
        or 0,
        "construction_cost": (
            cost_data.base_construction_cost
            + cost_data.total_site_works
            + cost_data.total_contingency
            if cost_data.base_construction_cost > 0
            else (project.construction_cost or 0)
        ),
        "construction_duration_months": financing_data.construction_duration_months
        or project.construction_duration_months
        or 12,
        "contingency_percentage": contingency_pct,
        "equity_percentage": equity_pct,
        "debt_percentage": debt_pct,
        "interest_rate": financing_data.construction_interest_rate
        or project.interest_rate
        or 6.0,
        "loan_term_years": financing_data.investment_term_years
        or project.loan_term_years
        or 25,
        "estimated_monthly_rent": monthly_rent,
        "rent_growth_rate": project.rent_growth_rate or 3.0,
        "occupancy_rate": project.occupancy_rate or 95.0,
        "operating_expense_ratio": project.operating_expense_ratio or 30.0,
        "holding_period_years": project.holding_period_years or 10,
        "exit_cap_rate": project.exit_cap_rate or 6.5,
    }


def is_financial_model_ready() -> bool:
    """Guard for older deployments missing DDSessionStateManager helpers."""
    checker = getattr(DDSessionStateManager, "is_ready_for_financial_model", None)
    if callable(checker):
        return checker()
    cost = DDSessionStateManager.get_cost_data()
    return cost.total_development_cost > 0


def render_financial_model_tab():
    """渲染财务模型标签页"""
    st.header("📊 Financial Model")

    DDSessionStateManager.initialize()
    cost_data = DDSessionStateManager.get_cost_data()
    financing_data = DDSessionStateManager.get_financing_data()

    if not is_financial_model_ready():
        st.warning("⚠️ Please complete the **Cost Breakdown** tab first.")
        st.info("Required: Total Development Cost > 0")

        with st.expander("🔍 Debug: Current Data Status"):
            st.write("**Cost Data:**")
            st.json(
                {
                    "total_development_cost": cost_data.total_development_cost,
                    "total_hard_costs": cost_data.total_hard_costs,
                    "total_soft_costs": cost_data.total_soft_costs,
                    "source": cost_data.source,
                }
            )

            st.write("**Financing Data:**")
            st.json(
                {
                    "construction_loan_amount": financing_data.construction_loan_amount,
                    "total_equity_required": financing_data.total_equity_required,
                    "source": financing_data.source,
                }
            )
        return

    st.success(f"✅ Using development cost: ${cost_data.total_development_cost:,.0f}")
    if financing_data.construction_loan_amount > 0:
        st.success("✅ Using financing data from Loan Calculator")
    else:
        st.info("💡 Financing data not set - using default assumptions")

    st.markdown('<div class="bento-card" style="margin: 1rem 0;">', unsafe_allow_html=True)
    st.subheader("📊 Financial Model & Returns")

    # 导入财务模型
    from utils.financial_model import FinancialModel, format_currency, format_percentage

    st.markdown("### 🧾 Assumptions")
    col1, col2, col3 = st.columns(3)
    with col1:
        monthly_rent = st.number_input(
            "Monthly Rent (AUD)",
            min_value=0.0,
            value=float(project.estimated_monthly_rent or 0),
            step=5000.0,
            key="fm_monthly_rent",
        )
        occupancy = st.number_input(
            "Occupancy Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(project.occupancy_rate or 95.0),
            step=1.0,
            key="fm_occupancy",
        )
    with col2:
        rent_growth = st.number_input(
            "Rent Growth (%)",
            min_value=0.0,
            max_value=20.0,
            value=float(project.rent_growth_rate or 3.0),
            step=0.5,
            key="fm_rent_growth",
        )
        opex_ratio = st.number_input(
            "Opex Ratio (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(project.operating_expense_ratio or 30.0),
            step=5.0,
            key="fm_opex",
        )
    with col3:
        holding_period = st.number_input(
            "Holding Period (years)",
            min_value=1,
            max_value=30,
            value=int(project.holding_period_years or 10),
            step=1,
            key="fm_holding",
        )
        exit_cap_rate = st.number_input(
            "Exit Cap Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=float(project.exit_cap_rate or 6.5),
            step=0.25,
            key="fm_exit_cap",
        )

    model_params = build_financial_model_params(project, cost_data, financing_data)
    model_params.update(
        {
            "estimated_monthly_rent": monthly_rent,
            "rent_growth_rate": rent_growth,
            "occupancy_rate": occupancy,
            "operating_expense_ratio": opex_ratio,
            "holding_period_years": holding_period,
            "exit_cap_rate": exit_cap_rate,
        }
    )

    # 创建模型并计算
    try:
        model = FinancialModel(model_params)
        returns = model.calculate_returns()
        cf_model = returns["cash_flow_model"]
        operating_noi = [
            cf["noi"]
            for cf in cf_model["annual_cash_flows"]
            if cf.get("period") == "Operating"
        ]
        annual_noi_stabilized = operating_noi[-1] if operating_noi else 0

        # ========== 顶部：关键指标卡片 ==========
        st.write("### 🎯 Key Investment Metrics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            irr_color = "normal" if returns["irr"] and returns["irr"] > 15 else "inverse"
            st.metric(
                "IRR",
                format_percentage(returns["irr"]),
                help="Internal Rate of Return - Target: >15%",
            )

        with col2:
            st.metric(
                "Equity Multiple",
                f"{returns['equity_multiple']:.2f}x"
                if returns["equity_multiple"]
                else "N/A",
                help="Total return / Initial equity - Target: >2.0x",
            )

        with col3:
            st.metric(
                "NPV",
                format_currency(returns["npv"]),
                help="Net Present Value at 12% discount rate",
            )

        with col4:
            dscr_color = (
                "normal"
                if returns["avg_dscr"] and returns["avg_dscr"] > 1.25
                else "inverse"
            )
            st.metric(
                "Avg DSCR",
                f"{returns['avg_dscr']:.2f}x" if returns["avg_dscr"] else "N/A",
                help="Debt Service Coverage Ratio - Min: 1.25x",
            )

        st.write("---")

        # ========== 投资摘要 ==========
        col1, col2 = st.columns(2)

        with col1:
            st.write("### 💰 Investment Summary")

            summary_data = {
                "Total Development Cost": format_currency(
                    cf_model["development_costs"]["total_development_cost"]
                ),
                "Equity Required": format_currency(returns["total_equity_invested"]),
                "Debt Financing": format_currency(cf_model["financing"]["debt_amount"]),
                "Capitalized Interest": format_currency(
                    cf_model["capitalized_interest"]
                ),
                "Total Loan at Completion": format_currency(
                    cf_model["total_loan_at_completion"]
                ),
            }

            for label, value in summary_data.items():
                st.write(f"**{label}:** {value}")

        with col2:
            st.write("### 📈 Returns Summary")

            returns_data = {
                "Cash-on-Cash (Year 1)": format_percentage(
                    returns["cash_on_cash_return"]
                ),
                "Profit Margin": format_percentage(returns["profit_margin"]),
                "Total Return": format_currency(returns["total_profit"]),
                "Annual NOI (Stabilized)": format_currency(annual_noi_stabilized),
                "Exit Value": format_currency(returns["cash_flow_model"]["exit_value"]),
            }

            for label, value in returns_data.items():
                st.write(f"**{label}:** {value}")

        st.write("---")

        # ========== Year by Year Cash Flow ==========
        st.write("### 📊 Cash Flow Timeline")

        # Create cash flow chart
        cash_flow_rows = returns["cash_flow_model"]["annual_cash_flows"]
        years = [row.get("year", idx) for idx, row in enumerate(cash_flow_rows)]
        cash_flows = [row.get("cash_flow", 0) for row in cash_flow_rows]

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=years,
                y=cash_flows,
                name="Annual Cash Flow",
                marker_color=[
                    "#d62728" if cf < 0 else "#2ca02c" for cf in cash_flows
                ],
            )
        )

        fig.update_layout(
            title="Annual Cash Flow",
            xaxis_title="Year",
            yaxis_title="Cash Flow (AUD)",
            height=400,
        )

        st.plotly_chart(fig, use_container_width=True)

        st.write("---")

        # ========== Detailed Metrics ==========
        with st.expander("📋 View Detailed Metrics"):
            metrics_data = {
                "IRR": format_percentage(returns["irr"]),
                "NPV": format_currency(returns["npv"]),
                "Equity Multiple": f"{returns['equity_multiple']:.2f}x",
                "Cash-on-Cash Return": format_percentage(
                    returns["cash_on_cash_return"]
                ),
                "Profit Margin": format_percentage(returns["profit_margin"]),
                "Total Return": format_currency(returns["total_profit"]),
                "Total Equity Invested": format_currency(
                    returns["total_equity_invested"]
                ),
                "Debt Amount": format_currency(
                    returns["cash_flow_model"]["financing"]["debt_amount"]
                ),
                "Exit Value": format_currency(returns["cash_flow_model"]["exit_value"]),
                "Annual NOI (Stabilized)": format_currency(annual_noi_stabilized),
                "Average DSCR": f"{returns['avg_dscr']:.2f}x"
                if returns["avg_dscr"]
                else "N/A",
            }

            df = pd.DataFrame(
                [{"Metric": k, "Value": v} for k, v in metrics_data.items()]
            )
            st.dataframe(df, use_container_width=True, hide_index=True)

        # ========== Save ==========
        st.write("---")
        if st.button("💾 Save Calculated Metrics to Project", width="stretch"):
            update_data = {
                "irr": returns["irr"],
                "npv": returns["npv"],
                "equity_multiple": returns["equity_multiple"],
                "cash_on_cash_return": returns["cash_on_cash_return"],
            }

            db.update_dd_project(project.id, update_data)
            st.success("✅ Metrics saved to project!")
            st.rerun()

    except Exception as e:
        st.error(f"❌ Error calculating financial model: {e}")
        import traceback
        with st.expander("🔍 Error Details"):
            st.code(traceback.format_exc())

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== 顶部：项目选择 ====================
col1, col2 = st.columns([3, 1])

with col1:
    # 获取所有DD项目
    dd_projects = db.get_all_dd_projects()
    
    if dd_projects:
        project_options = {f"{p.name} ({p.status})": p.id for p in dd_projects}
        project_options["+ Create New Project"] = None
        
        selected = st.selectbox(
            t('dd.select_project'),
            options=list(project_options.keys()),
            index=0
        )
        
        selected_id = project_options[selected]
        
        if selected_id:
            st.session_state.selected_dd_project = selected_id
        else:
            st.session_state.selected_dd_project = None
    else:
        st.info("📭 No projects yet. Create your first investment opportunity below.")
        st.session_state.selected_dd_project = None

with col2:
    if st.button(f"🗑️ {t('dd.delete_project')}", width='stretch', disabled=not st.session_state.selected_dd_project):
        if st.session_state.selected_dd_project:
            db.delete_dd_project(st.session_state.selected_dd_project)
            st.session_state.selected_dd_project = None
            st.success(f"✅ {t('messages.delete_success')}")
            st.rerun()

st.write("---")

# ==================== 主要内容：Tab布局 ====================
if st.session_state.selected_dd_project:
    # 编辑现有项目
    project = db.get_dd_project_by_id(st.session_state.selected_dd_project)
    
    if not project:
        st.error("Project not found!")
        st.stop()
    
    # 创建tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📋 Overview",
        "⚡ Quick Setup",
        "💵 Cost Breakdown",
        "🏦 Loan Calculator",
        "📊 Financial Model",
        f"🎯 {t('dd.tabs.scenarios')}",
        f"📄 {t('dd.tabs.report')}"
    ])
    
    # ===== Tab 1: Project Overview =====
    with tab1:
        render_project_overview_tab()

    # ===== Tab 2: Quick Setup =====
    with tab2:
        render_quick_setup_tab()

    # ===== Tab 3: Cost Breakdown =====
    with tab3:
        render_cost_breakdown_tab()

    # ===== Tab 4: Loan Calculator =====
    with tab4:
        render_loan_calculator_tab()

    # ===== Tab 5: Financial Model =====
    with tab5:
        render_financial_model_tab()

    # ===== Tab 6: Scenarios =====
    with tab6:
        st.markdown('<div class="bento-card" style="margin: 1rem 0;">', unsafe_allow_html=True)
        st.subheader("📈 Scenario & Sensitivity Analysis")
        
        cost_data = DDSessionStateManager.get_cost_data()
        financing_data = DDSessionStateManager.get_financing_data()
        if not is_financial_model_ready():
            st.warning("⚠️ Please complete the Cost Breakdown tab first.")
        else:
            from utils.financial_model import FinancialModel, format_currency, format_percentage
            import plotly.graph_objects as go

            st.markdown("### 🧾 Assumptions")
            col1, col2, col3 = st.columns(3)
            with col1:
                monthly_rent = st.number_input(
                    "Monthly Rent (AUD)",
                    min_value=0.0,
                    value=float(project.estimated_monthly_rent or 0),
                    step=5000.0,
                    key="scenario_monthly_rent",
                )
                occupancy = st.number_input(
                    "Occupancy Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(project.occupancy_rate or 95.0),
                    step=1.0,
                    key="scenario_occupancy",
                )
            with col2:
                rent_growth = st.number_input(
                    "Rent Growth (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=float(project.rent_growth_rate or 3.0),
                    step=0.5,
                    key="scenario_rent_growth",
                )
                opex_ratio = st.number_input(
                    "Opex Ratio (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(project.operating_expense_ratio or 30.0),
                    step=5.0,
                    key="scenario_opex",
                )
            with col3:
                holding_period = st.number_input(
                    "Holding Period (years)",
                    min_value=1,
                    max_value=30,
                    value=int(project.holding_period_years or 10),
                    step=1,
                    key="scenario_holding",
                )
                exit_cap_rate = st.number_input(
                    "Exit Cap Rate (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=float(project.exit_cap_rate or 6.5),
                    step=0.25,
                    key="scenario_exit_cap",
                )

            model_params = build_financial_model_params(project, cost_data, financing_data)
            model_params.update(
                {
                    "estimated_monthly_rent": monthly_rent,
                    "rent_growth_rate": rent_growth,
                    "occupancy_rate": occupancy,
                    "operating_expense_ratio": opex_ratio,
                    "holding_period_years": holding_period,
                    "exit_cap_rate": exit_cap_rate,
                }
            )
            
            try:
                model = FinancialModel(model_params)
                
                # ========== 三情景分析 ==========
                st.write("### 🎯 Three Scenario Comparison")
                
                with st.spinner("Calculating scenarios..."):
                    scenarios = model.calculate_three_scenarios()
                
                # 情景对比表
                col1, col2, col3 = st.columns(3)
                
                scenario_names = {
                    'pessimistic': ('Pessimistic', '😰', '#FF6B6B'),
                    'base': ('Base Case', '😐', '#4ECDC4'),
                    'optimistic': ('Optimistic', '😊', '#45B7D1')
                }
                
                for idx, (key, (name, emoji, color)) in enumerate(scenario_names.items()):
                    scenario = scenarios[key]
                    col = [col1, col2, col3][idx]
                    
                    with col:
                        st.markdown(f"### {emoji} {name}")
                        
                        # 显示关键指标
                        metrics = {
                            'IRR': format_percentage(scenario.get('irr')),
                            'NPV': format_currency(scenario.get('npv')),
                            'Equity Multiple': f"{scenario.get('equity_multiple', 0):.2f}x",
                            'Total Profit': format_currency(scenario.get('total_profit'))
                        }
                        
                        for metric_name, value in metrics.items():
                            st.write(f"**{metric_name}:** {value}")
                        
                        # 显示假设
                        if key == 'optimistic':
                            st.caption("📈 Assumptions:")
                            st.caption("- Construction: -10%")
                            st.caption("- Rent: +20%")
                            st.caption("- Occupancy: +3pts")
                            st.caption("- Exit Cap: -0.5pts")
                        elif key == 'pessimistic':
                            st.caption("📉 Assumptions:")
                            st.caption("- Construction: +15%")
                            st.caption("- Rent: -15%")
                            st.caption("- Occupancy: -5pts")
                            st.caption("- Exit Cap: +1.0pts")
                
                st.write("---")
                
                # 雷达图对比
                st.write("### 📊 Scenario Comparison - Radar Chart")
                
                # 准备雷达图数据
                categories = ['IRR', 'NPV', 'Equity Multiple', 'Cash-on-Cash', 'DSCR']
                
                # 标准化函数（转换为0-100分数）
                def normalize(value, target, max_val):
                    if value is None:
                        return 0
                    # 按照目标值作为100分标准
                    return min(100, (value / target) * 100)
                
                # 目标值
                targets = {
                    'irr': 20.0,  # 20% IRR = 100分
                    'npv': scenarios['base'].get('npv', 1000000),  # Base NPV = 100分
                    'equity_multiple': 3.0,  # 3x = 100分
                    'cash_on_cash_return': 15.0,  # 15% = 100分
                    'avg_dscr': 2.0  # 2.0x = 100分
                }
                
                fig_radar = go.Figure()
                
                for key, (name, emoji, color) in scenario_names.items():
                    scenario = scenarios[key]
                    
                    values = [
                        normalize(scenario.get('irr'), targets['irr'], 40),
                        normalize(scenario.get('npv'), targets['npv'], targets['npv'] * 2),
                        normalize(scenario.get('equity_multiple'), targets['equity_multiple'], 5),
                        normalize(scenario.get('cash_on_cash_return'), targets['cash_on_cash_return'], 30),
                        normalize(scenario.get('avg_dscr'), targets['avg_dscr'], 3)
                    ]
                    
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name=f"{emoji} {name}",
                        line=dict(color=color, width=2)
                    ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )
                    ),
                    showlegend=True,
                    height=500
                )
                
                fig_radar = apply_professional_theme_to_figure(fig_radar, theme='light')
                
                st.plotly_chart(fig_radar, width='stretch')
                
                st.write("---")
                
                # ========== 敏感性分析 ==========
                st.write("### 🎚️ Sensitivity Analysis")
                
                st.write("**How does IRR change when we adjust key variables?**")
                
                # 选择要分析的变量
                sensitivity_vars = {
                    'Land Cost': 'purchase_price',
                    'Construction Cost': 'construction_cost',
                    'Rental Income': 'rent',
                    'Occupancy Rate': 'occupancy',
                    'Exit Cap Rate': 'exit_cap'
                }
                
                selected_var = st.selectbox(
                    "Select variable to analyze:",
                    options=list(sensitivity_vars.keys())
                )
                
                var_key = sensitivity_vars[selected_var]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    range_pct = st.slider(
                        "Adjustment range (±%)",
                        min_value=10,
                        max_value=50,
                        value=30,
                        step=5,
                        help="Range of variation to test"
                    )
                
                with col2:
                    steps = st.slider(
                        "Number of data points",
                        min_value=5,
                        max_value=21,
                        value=11,
                        step=2
                    )
                
                if st.button("🔍 Run Sensitivity Analysis", type="primary"):
                    with st.spinner("Calculating sensitivity..."):
                        sensitivity = model.sensitivity_analysis(var_key, range_pct, steps)
                    
                    # 创建敏感性图表
                    fig_sens = go.Figure()
                    
                    # IRR线
                    fig_sens.add_trace(go.Scatter(
                        x=sensitivity['adjustments'],
                        y=sensitivity['irr'],
                        mode='lines+markers',
                        name='IRR',
                        line=dict(color='#4ECDC4', width=3),
                        marker=dict(size=8)
                    ))
                    
                    # 添加基准线
                    fig_sens.add_hline(
                        y=scenarios['base'].get('irr'),
                        line_dash="dash",
                        line_color="gray",
                        annotation_text="Base Case"
                    )
                    
                    # 添加目标线（15% IRR）
                    fig_sens.add_hline(
                        y=15.0,
                        line_dash="dot",
                        line_color="green",
                        annotation_text="Target 15%"
                    )
                    
                    fig_sens.update_layout(
                        title=f"IRR Sensitivity to {selected_var}",
                        xaxis_title=f"{selected_var} Change (%)",
                        yaxis_title="IRR (%)",
                        hovermode='x unified',
                        height=400
                    )
                    
                    fig_sens = apply_professional_theme_to_figure(fig_sens, theme='light')
                    
                    st.plotly_chart(fig_sens, width='stretch')
                    
                    # 显示关键洞察
                    irr_range = max(sensitivity['irr']) - min(sensitivity['irr'])
                    st.info(f"""
                    💡 **Key Insight:** 
                    A ±{range_pct}% change in {selected_var} results in a {irr_range:.1f} percentage point swing in IRR
                    (from {min(sensitivity['irr']):.1f}% to {max(sensitivity['irr']):.1f}%)
                    """)
                
                st.write("---")
                
                # ========== 龙卷风图 ==========
                st.write("### 🌪️ Tornado Analysis - Variable Impact Ranking")
                
                st.write("**Which variables have the biggest impact on IRR?**")
                
                tornado_range = st.slider(
                    "Test range (±%)",
                    min_value=10,
                    max_value=30,
                    value=20,
                    step=5,
                    key="tornado_range"
                )
                
                if st.button("🌪️ Generate Tornado Chart", type="primary"):
                    with st.spinner("Calculating variable impacts..."):
                        tornado = model.tornado_analysis(tornado_range)
                    
                    # 创建龙卷风图
                    tornado_data = tornado['tornado_data']
                    base_irr = tornado['base_irr']
                    
                    fig_tornado = go.Figure()
                    
                    # 为每个变量添加条形
                    for i, item in enumerate(tornado_data):
                        # 低值条（向左）
                        fig_tornado.add_trace(go.Bar(
                            y=[item['variable']],
                            x=[item['low_irr'] - base_irr],
                            name=item['low_label'],
                            orientation='h',
                            marker=dict(color='#FF6B6B'),
                            text=[f"{item['low_irr']:.1f}%"],
                            textposition='inside',
                            showlegend=(i == 0),
                            legendgroup='low'
                        ))
                        
                        # 高值条（向右）
                        fig_tornado.add_trace(go.Bar(
                            y=[item['variable']],
                            x=[item['high_irr'] - base_irr],
                            name=item['high_label'],
                            orientation='h',
                            marker=dict(color='#4ECDC4'),
                            text=[f"{item['high_irr']:.1f}%"],
                            textposition='inside',
                            showlegend=(i == 0),
                            legendgroup='high'
                        ))
                    
                    # 添加基准线
                    fig_tornado.add_vline(x=0, line_width=2, line_color="black")
                    
                    fig_tornado.update_layout(
                        title=f"IRR Impact - Variables Ranked by Importance (±{tornado_range}%)",
                        xaxis_title="IRR Deviation from Base Case (%)",
                        yaxis_title="",
                        barmode='overlay',
                        height=400,
                        showlegend=True
                    )
                    
                    fig_tornado = apply_professional_theme_to_figure(fig_tornado, theme='light')
                    
                    st.plotly_chart(fig_tornado, width='stretch')
                    
                    # 显示排名表
                    st.write("**Impact Ranking:**")
                    
                    ranking_df = pd.DataFrame([
                        {
                            'Rank': i + 1,
                            'Variable': item['variable'],
                            'IRR Range': f"{item['low_irr']:.1f}% to {item['high_irr']:.1f}%",
                            'Impact': f"{item['impact']:.1f} pts",
                            'Sensitivity': '🔴 High' if item['impact'] > 10 else '🟡 Medium' if item['impact'] > 5 else '🟢 Low'
                        }
                        for i, item in enumerate(tornado_data)
                    ])
                    
                    st.dataframe(ranking_df, width='stretch', hide_index=True)
                    
                    # 关键洞察
                    top_var = tornado_data[0]
                    st.success(f"""
                    🎯 **Most Critical Variable:** {top_var['variable']}
                    
                    This variable has the highest impact on returns. Focus risk mitigation efforts here.
                    """)
                
            except Exception as e:
                st.error(f"❌ Error in scenario analysis: {e}")
                import traceback
                with st.expander("🔍 Error Details"):
                    st.code(traceback.format_exc())
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== Tab 7: Report =====
    with tab7:
        st.markdown('<div class="bento-card" style="margin: 1rem 0;">', unsafe_allow_html=True)
        st.subheader("📄 Investment Decision Report")
        
        cost_data = DDSessionStateManager.get_cost_data()
        financing_data = DDSessionStateManager.get_financing_data()
        if not is_financial_model_ready():
            st.warning(
                "⚠️ Please complete the Cost Breakdown tab first to generate report"
            )
        else:
            from utils.financial_model import FinancialModel, format_currency, format_percentage
            from utils.dd_report_generator import DDReportGenerator

            st.markdown("### 🧾 Report Assumptions")
            col1, col2, col3 = st.columns(3)
            with col1:
                monthly_rent = st.number_input(
                    "Monthly Rent (AUD)",
                    min_value=0.0,
                    value=float(project.estimated_monthly_rent or 0),
                    step=5000.0,
                    key="report_monthly_rent",
                )
                occupancy = st.number_input(
                    "Occupancy Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(project.occupancy_rate or 95.0),
                    step=1.0,
                    key="report_occupancy",
                )
            with col2:
                rent_growth = st.number_input(
                    "Rent Growth (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=float(project.rent_growth_rate or 3.0),
                    step=0.5,
                    key="report_rent_growth",
                )
                opex_ratio = st.number_input(
                    "Opex Ratio (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(project.operating_expense_ratio or 30.0),
                    step=5.0,
                    key="report_opex",
                )
            with col3:
                holding_period = st.number_input(
                    "Holding Period (years)",
                    min_value=1,
                    max_value=30,
                    value=int(project.holding_period_years or 10),
                    step=1,
                    key="report_holding",
                )
                exit_cap_rate = st.number_input(
                    "Exit Cap Rate (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=float(project.exit_cap_rate or 6.5),
                    step=0.25,
                    key="report_exit_cap",
                )

            model_params = build_financial_model_params(project, cost_data, financing_data)
            model_params.update(
                {
                    "estimated_monthly_rent": monthly_rent,
                    "rent_growth_rate": rent_growth,
                    "occupancy_rate": occupancy,
                    "operating_expense_ratio": opex_ratio,
                    "holding_period_years": holding_period,
                    "exit_cap_rate": exit_cap_rate,
                }
            )
            
            try:
                # 计算财务模型
                model = FinancialModel(model_params)
                returns = model.calculate_returns()
                scenarios = model.calculate_three_scenarios()
                
                # ========== 投资推荐 ==========
                st.write("### 🎯 Investment Recommendation")
                
                irr = returns.get('irr', 0)
                
                # 决定推荐
                if irr and irr >= 20:
                    recommendation = "STRONG BUY"
                    rec_color = "green"
                    rec_icon = "✅"
                elif irr and irr >= 15:
                    recommendation = "BUY"
                    rec_color = "blue"
                    rec_icon = "👍"
                elif irr and irr >= 12:
                    recommendation = "HOLD"
                    rec_color = "orange"
                    rec_icon = "⚠️"
                else:
                    recommendation = "PASS"
                    rec_color = "red"
                    rec_icon = "❌"
                
                st.markdown(
                    f"<h2 style='text-align: center; color: {rec_color};'>{rec_icon} {recommendation}</h2>",
                    unsafe_allow_html=True
                )
                
                # 推荐理由
                if irr >= 20:
                    rationale = f"""
                    **Strong investment opportunity with exceptional returns:**
                    - Projected IRR of {format_percentage(irr)} significantly exceeds target (15%)
                    - Equity multiple of {returns.get('equity_multiple', 0):.2f}x demonstrates strong value creation
                    - Positive NPV of {format_currency(returns.get('npv'))} creates shareholder value
                    - Recommend proceeding to final due diligence and contract negotiation
                    """
                elif irr >= 15:
                    rationale = f"""
                    **Solid investment meeting return criteria:**
                    - Projected IRR of {format_percentage(irr)} meets target hurdle rate
                    - Returns are acceptable with manageable risk profile
                    - Recommend proceeding with careful monitoring of key assumptions
                    """
                elif irr >= 12:
                    rationale = f"""
                    **Marginal investment requiring optimization:**
                    - Projected IRR of {format_percentage(irr)} is below target but acceptable
                    - Consider value enhancement opportunities before proceeding
                    - Recommend renegotiation of terms or cost reduction initiatives
                    """
                else:
                    rationale = f"""
                    **Investment does not meet criteria:**
                    - Projected IRR of {format_percentage(irr)} falls short of minimum requirements
                    - Returns do not justify the risk profile
                    - Recommend passing or substantial restructuring of deal terms
                    """
                
                st.info(rationale)
                
                st.write("---")
                
                # ========== 报告预览 ==========
                st.write("### 📋 Report Preview")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Report Contents:**")
                    st.write("✅ Executive Summary")
                    st.write("✅ Project Overview")
                    st.write("✅ Development Cost Analysis")
                    st.write("✅ Financing Structure")
                    st.write("✅ Return Metrics")
                    st.write("✅ Scenario Analysis")
                    st.write("✅ Risk Assessment")
                    st.write("✅ Investment Recommendation")
                
                with col2:
                    st.write("**Key Metrics Summary:**")
                    st.write(f"IRR: **{format_percentage(irr)}**")
                    st.write(f"NPV: **{format_currency(returns.get('npv'))}**")
                    st.write(f"Equity Multiple: **{returns.get('equity_multiple', 0):.2f}x**")
                    st.write(f"Total Profit: **{format_currency(returns.get('total_profit'))}**")
                    st.write(f"DSCR (Avg): **{returns.get('avg_dscr', 0):.2f}x**")
                
                st.write("---")
                
                # ========== 情景对比 ==========
                st.write("### 📊 Scenario Summary")
                
                scenario_summary = pd.DataFrame([
                    {
                        'Scenario': '😰 Pessimistic',
                        'IRR': format_percentage(scenarios['pessimistic'].get('irr')),
                        'NPV': format_currency(scenarios['pessimistic'].get('npv')),
                        'Multiple': f"{scenarios['pessimistic'].get('equity_multiple', 0):.2f}x"
                    },
                    {
                        'Scenario': '😐 Base Case',
                        'IRR': format_percentage(scenarios['base'].get('irr')),
                        'NPV': format_currency(scenarios['base'].get('npv')),
                        'Multiple': f"{scenarios['base'].get('equity_multiple', 0):.2f}x"
                    },
                    {
                        'Scenario': '😊 Optimistic',
                        'IRR': format_percentage(scenarios['optimistic'].get('irr')),
                        'NPV': format_currency(scenarios['optimistic'].get('npv')),
                        'Multiple': f"{scenarios['optimistic'].get('equity_multiple', 0):.2f}x"
                    }
                ])
                
                st.dataframe(scenario_summary, width='stretch', hide_index=True)
                
                st.write("---")
                
                # ========== PDF下载 ==========
                st.write("### 📥 Download Report")
                
                st.write("Generate a comprehensive PDF report for stakeholders and investors.")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col2:
                    if st.button("📄 Generate PDF Report", type="primary", width='stretch'):
                        with st.spinner("Generating professional report..."):
                            try:
                                # 生成报告
                                report_gen = DDReportGenerator(project, db)
                                pdf_buffer = report_gen.generate_report()
                                
                                # 提供下载
                                filename = f"DD_Report_{project.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
                                
                                st.download_button(
                                    label="💾 Download PDF",
                                    data=pdf_buffer,
                                    file_name=filename,
                                    mime="application/pdf",
                                    width='stretch'
                                )
                                
                                st.success("✅ Report generated successfully!")
                                
                            except Exception as e:
                                st.error(f"❌ Error generating report: {e}")
                                import traceback
                                with st.expander("🔍 Error Details"):
                                    st.code(traceback.format_exc())
                
                # ========== 快速操作 ==========
                st.write("---")
                st.write("### ⚡ Quick Actions")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔄 Recalculate All Metrics", width='stretch'):
                        st.info("All metrics are automatically calculated based on current parameters.")
                        st.rerun()
                
                with col2:
                    if st.button("📧 Email Report (Coming Soon)", width='stretch', disabled=True):
                        st.info("Email functionality will be available in a future update.")
                
                # ========== 项目状态更新 ==========
                st.write("---")
                st.write("### 🏷️ Update Project Status")
                
                current_status = project.status
                
                new_status = st.selectbox(
                    "Change project status:",
                    ["Under Review", "Approved", "Rejected", "On Hold"],
                    index=["Under Review", "Approved", "Rejected", "On Hold"].index(current_status) if current_status else 0
                )
                
                if new_status != current_status:
                    if st.button(f"Update Status to: {new_status}", type="primary"):
                        db.update_dd_project(project.id, {'status': new_status})
                        st.success(f"✅ Status updated to: {new_status}")
                        st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error loading report: {e}")
                import traceback
                with st.expander("🔍 Error Details"):
                    st.code(traceback.format_exc())
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # 创建新项目
    st.subheader("➕ Create New Investment Opportunity")
    
    with st.form("new_dd_project_form"):
        st.write("**Quick Start - Basic Information**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Project Name*", placeholder="e.g., Brisbane North Industrial Hub")
            location = st.text_input("Location*", placeholder="e.g., Brisbane North")
        
        with col2:
            property_type = st.selectbox(
                "Property Type*",
                ["Industrial Warehouse", "Land Development", "Mixed Use", "Logistics Center"]
            )
            
            purchase_price = st.number_input(
                "Estimated Purchase Price (AUD)*",
                min_value=0.0,
                step=100000.0,
                format="%.0f"
            )
        
        description = st.text_area(
            "Description",
            placeholder="Brief description of the opportunity...",
            height=100
        )
        
        submitted = st.form_submit_button("➕ Create Project", width='stretch', type="primary")
        
        if submitted:
            if not name or not location:
                st.error("Name and Location are required")
            elif purchase_price <= 0:
                st.error("Purchase price must be positive")
            else:
                # 创建新项目（使用默认值）
                new_project_data = {
                    'name': name,
                    'location': location,
                    'property_type': property_type,
                    'description': description,
                    'purchase_price': purchase_price,
                    'status': 'Under Review'
                }
                
                try:
                    new_project = db.add_dd_project(new_project_data)
                    if new_project:
                        st.success(f"✅ Project '{name}' created!")
                        st.session_state.selected_dd_project = new_project.id
                        st.rerun()
                    else:
                        st.error("Failed to create project")
                except Exception as e:
                    st.error(f"Error: {e}")

# ==================== 侧边栏：帮助信息 ====================
with st.sidebar:
    st.header("ℹ️ About Due Diligence")
    
    st.write("**What is Due Diligence?**")
    st.write("Comprehensive analysis before investing in a property:")
    
    st.write("✅ Financial feasibility")
    st.write("✅ Risk assessment")
    st.write("✅ Return projections")
    st.write("✅ Scenario planning")
    
    st.write("---")
    
    st.write("**Key Metrics:**")
    st.write("**IRR** - Internal Rate of Return")
    st.write("**NPV** - Net Present Value")
    st.write("**Cap Rate** - Capitalization Rate")
    st.write("**DSCR** - Debt Service Coverage")
    
    st.write("---")
    
    st.write("**Typical Timeline:**")
    st.write("1. Initial screening (1-2 days)")
    st.write("2. Detailed analysis (1-2 weeks)")
    st.write("3. Final decision (1 week)")
    
    st.write("---")
    
    if st.session_state.selected_dd_project:
        project = db.get_dd_project_by_id(st.session_state.selected_dd_project)
        if project:
            st.write("**Current Project:**")
            st.write(f"📍 {project.name}")
            st.write(f"Status: {project.status}")
            if project.purchase_price:
                st.write(f"Price: ${project.purchase_price/1e6:.1f}M")