import streamlit as st
import plotly.graph_objects as go
from models.database import DatabaseManager
from datetime import datetime
import pandas as pd

# 页面配置
st.set_page_config(page_title="Due Diligence", page_icon="🔍", layout="wide")

st.title("🔍 Due Diligence & Investment Analysis")
st.write("Evaluate new investment opportunities with comprehensive financial modeling")

# 初始化
db = DatabaseManager()

# Session state
if 'selected_dd_project' not in st.session_state:
    st.session_state.selected_dd_project = None

# ==================== 顶部：项目选择 ====================
col1, col2 = st.columns([3, 1])

with col1:
    # 获取所有DD项目
    dd_projects = db.get_all_dd_projects()
    
    if dd_projects:
        project_options = {f"{p.name} ({p.status})": p.id for p in dd_projects}
        project_options["+ Create New Project"] = None
        
        selected = st.selectbox(
            "Select Project to Analyze:",
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
    if st.button("🗑️ Delete Project", use_container_width=True, disabled=not st.session_state.selected_dd_project):
        if st.session_state.selected_dd_project:
            db.delete_dd_project(st.session_state.selected_dd_project)
            st.session_state.selected_dd_project = None
            st.success("Project deleted!")
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
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Parameters", "📊 Financial Model", "📈 Scenarios", "📄 Report"])
    
    # ===== Tab 1: Parameters =====
    with tab1:
        st.subheader("Project Parameters")
        
        with st.form("dd_parameters_form"):
            # 基本信息
            st.write("**Basic Information**")
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Project Name*", value=project.name)
                location = st.text_input("Location", value=project.location or "")
                property_type = st.selectbox(
                    "Property Type",
                    ["Industrial Warehouse", "Land Development", "Mixed Use", "Logistics Center"],
                    index=["Industrial Warehouse", "Land Development", "Mixed Use", "Logistics Center"].index(project.property_type) if project.property_type else 0
                )
            
            with col2:
                status = st.selectbox(
                    "Status",
                    ["Under Review", "Approved", "Rejected", "On Hold"],
                    index=["Under Review", "Approved", "Rejected", "On Hold"].index(project.status) if project.status else 0
                )
                zoning = st.text_input("Zoning", value=project.zoning or "")
            
            description = st.text_area("Description", value=project.description or "", height=80)
            
            st.write("---")
            
            # 土地和建筑
            st.write("**Land & Building**")
            col1, col2 = st.columns(2)
            
            with col1:
                land_area = st.number_input(
                    "Land Area (sqm)",
                    min_value=0.0,
                    value=float(project.land_area_sqm or 0),
                    step=100.0
                )
            
            with col2:
                building_area = st.number_input(
                    "Building Area (sqm)",
                    min_value=0.0,
                    value=float(project.building_area_sqm or 0),
                    step=100.0
                )
            
            st.write("---")
            
            # 收购成本
            st.write("**Acquisition**")
            col1, col2 = st.columns(2)
            
            with col1:
                purchase_price = st.number_input(
                    "Purchase Price (AUD)",
                    min_value=0.0,
                    value=float(project.purchase_price or 0),
                    step=100000.0,
                    format="%.0f",
                    help="Total land acquisition cost"
                )
            
            with col2:
                acquisition_costs = st.number_input(
                    "Acquisition Costs (AUD)",
                    min_value=0.0,
                    value=float(project.acquisition_costs or 0),
                    step=10000.0,
                    format="%.0f",
                    help="Legal fees, due diligence, stamp duty"
                )
            
            st.write("---")
            
            # 开发成本
            st.write("**Development**")
            col1, col2 = st.columns(2)
            
            with col1:
                construction_cost = st.number_input(
                    "Construction Cost (AUD)",
                    min_value=0.0,
                    value=float(project.construction_cost or 0),
                    step=100000.0,
                    format="%.0f"
                )
                
                construction_duration = st.number_input(
                    "Construction Duration (months)",
                    min_value=1,
                    value=int(project.construction_duration_months or 12),
                    step=1
                )
            
            with col2:
                contingency = st.number_input(
                    "Contingency (%)",
                    min_value=0.0,
                    max_value=30.0,
                    value=float(project.contingency_percentage or 10),
                    step=1.0,
                    help="Construction cost buffer"
                )
            
            st.write("---")
            
            # 融资结构
            st.write("**Financing Structure**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                equity_pct = st.number_input(
                    "Equity (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(project.equity_percentage or 30),
                    step=5.0
                )
            
            with col2:
                debt_pct = st.number_input(
                    "Debt (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(project.debt_percentage or 70),
                    step=5.0,
                    disabled=True,
                    help="Auto-calculated: 100% - Equity"
                )
                # Auto calculate debt
                debt_pct = 100 - equity_pct
            
            with col3:
                interest_rate = st.number_input(
                    "Interest Rate (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=float(project.interest_rate or 6.0),
                    step=0.25
                )
            
            loan_term = st.number_input(
                "Loan Term (years)",
                min_value=1,
                max_value=30,
                value=int(project.loan_term_years or 25),
                step=1
            )
            
            st.write("---")
            
            # 收入假设
            st.write("**Revenue Assumptions**")
            col1, col2 = st.columns(2)
            
            with col1:
                monthly_rent = st.number_input(
                    "Estimated Monthly Rent (AUD)",
                    min_value=0.0,
                    value=float(project.estimated_monthly_rent or 0),
                    step=5000.0,
                    format="%.0f"
                )
                
                rent_growth = st.number_input(
                    "Rent Growth Rate (% p.a.)",
                    min_value=0.0,
                    max_value=20.0,
                    value=float(project.rent_growth_rate or 3.0),
                    step=0.5
                )
            
            with col2:
                occupancy = st.number_input(
                    "Occupancy Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(project.occupancy_rate or 95.0),
                    step=5.0
                )
                
                opex_ratio = st.number_input(
                    "Operating Expense Ratio (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(project.operating_expense_ratio or 30.0),
                    step=5.0,
                    help="% of gross revenue"
                )
            
            st.write("---")
            
            # 退出策略
            st.write("**Exit Strategy**")
            col1, col2 = st.columns(2)
            
            with col1:
                holding_period = st.number_input(
                    "Holding Period (years)",
                    min_value=1,
                    max_value=30,
                    value=int(project.holding_period_years or 10),
                    step=1
                )
            
            with col2:
                exit_cap_rate = st.number_input(
                    "Exit Cap Rate (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=float(project.exit_cap_rate or 6.5),
                    step=0.25,
                    help="Capitalization rate at sale"
                )
            
            # 提交按钮
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Save Parameters", use_container_width=True)
            with col2:
                calculate = st.form_submit_button("🧮 Calculate Returns", use_container_width=True, type="primary")
            
            if submitted or calculate:
                # 验证
                if not name:
                    st.error("Project name is required")
                elif equity_pct + debt_pct != 100:
                    st.error("Equity + Debt must equal 100%")
                else:
                    # 保存数据
                    update_data = {
                        'name': name,
                        'description': description,
                        'location': location,
                        'property_type': property_type,
                        'status': status,
                        'land_area_sqm': land_area if land_area > 0 else None,
                        'building_area_sqm': building_area if building_area > 0 else None,
                        'zoning': zoning,
                        'purchase_price': purchase_price,
                        'acquisition_costs': acquisition_costs,
                        'construction_cost': construction_cost,
                        'construction_duration_months': construction_duration,
                        'contingency_percentage': contingency,
                        'equity_percentage': equity_pct,
                        'debt_percentage': debt_pct,
                        'interest_rate': interest_rate,
                        'loan_term_years': loan_term,
                        'estimated_monthly_rent': monthly_rent,
                        'rent_growth_rate': rent_growth,
                        'occupancy_rate': occupancy,
                        'operating_expense_ratio': opex_ratio,
                        'holding_period_years': holding_period,
                        'exit_cap_rate': exit_cap_rate
                    }
                    
                    try:
                        db.update_dd_project(project.id, update_data)
                        st.success("✅ Parameters saved!")
                        
                        if calculate:
                            st.info("🧮 Financial calculations will be implemented in Day 8")
                        
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    # ===== Tab 2: Financial Model =====
    with tab2:
        st.subheader("Financial Model & Returns")
        st.info("💡 Financial modeling engine will be implemented in Day 8")
        
        # Placeholder for now
        st.write("**Planned Features:**")
        st.write("- IRR (Internal Rate of Return)")
        st.write("- NPV (Net Present Value)")
        st.write("- Cash-on-Cash Return")
        st.write("- Equity Multiple")
        st.write("- DSCR (Debt Service Coverage Ratio)")
        st.write("- Annual cash flow projections")
    
    # ===== Tab 3: Scenarios =====
    with tab3:
        st.subheader("Scenario Analysis")
        st.info("💡 Scenario analysis will be implemented in Day 9")
        
        st.write("**Planned Features:**")
        st.write("- Base Case scenario")
        st.write("- Optimistic scenario (+20% rent, -10% cost)")
        st.write("- Pessimistic scenario (-20% rent, +15% cost)")
        st.write("- Sensitivity analysis charts")
    
    # ===== Tab 4: Report =====
    with tab4:
        st.subheader("Investment Report")
        st.info("💡 Report generation will be implemented in Day 10")
        
        st.write("**Planned Features:**")
        st.write("- Executive summary")
        st.write("- Financial analysis")
        st.write("- Risk assessment")
        st.write("- Investment recommendation")
        st.write("- PDF export")

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
        
        submitted = st.form_submit_button("➕ Create Project", use_container_width=True, type="primary")
        
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