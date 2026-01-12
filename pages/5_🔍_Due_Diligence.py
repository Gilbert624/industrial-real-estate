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
        st.subheader("📊 Financial Model & Returns")
        
        # 检查是否所有必需参数都已填写
        required_params = [
            'purchase_price', 'construction_cost', 'estimated_monthly_rent'
        ]
        
        missing_params = [p for p in required_params if not project.__dict__.get(p)]
        
        if missing_params:
            st.warning(f"⚠️ Please fill in required parameters in Tab 1: {', '.join(missing_params)}")
        else:
            # 导入财务模型
            from utils.financial_model import FinancialModel, format_currency, format_percentage
            
            # 准备参数
            model_params = {
                'purchase_price': project.purchase_price or 0,
                'acquisition_costs': project.acquisition_costs or 0,
                'construction_cost': project.construction_cost or 0,
                'construction_duration_months': project.construction_duration_months or 12,
                'contingency_percentage': project.contingency_percentage or 10.0,
                'equity_percentage': project.equity_percentage or 30.0,
                'debt_percentage': project.debt_percentage or 70.0,
                'interest_rate': project.interest_rate or 6.0,
                'loan_term_years': project.loan_term_years or 25,
                'estimated_monthly_rent': project.estimated_monthly_rent or 0,
                'rent_growth_rate': project.rent_growth_rate or 3.0,
                'occupancy_rate': project.occupancy_rate or 95.0,
                'operating_expense_ratio': project.operating_expense_ratio or 30.0,
                'holding_period_years': project.holding_period_years or 10,
                'exit_cap_rate': project.exit_cap_rate or 6.5
            }
            
            # 创建模型并计算
            try:
                model = FinancialModel(model_params)
                returns = model.calculate_returns()
                cf_model = returns['cash_flow_model']
                
                # ========== 顶部：关键指标卡片 ==========
                st.write("### 🎯 Key Investment Metrics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    irr_color = "normal" if returns['irr'] and returns['irr'] > 15 else "inverse"
                    st.metric(
                        "IRR",
                        format_percentage(returns['irr']),
                        help="Internal Rate of Return - Target: >15%"
                    )
                
                with col2:
                    st.metric(
                        "Equity Multiple",
                        f"{returns['equity_multiple']:.2f}x" if returns['equity_multiple'] else "N/A",
                        help="Total return / Initial equity - Target: >2.0x"
                    )
                
                with col3:
                    st.metric(
                        "NPV",
                        format_currency(returns['npv']),
                        help="Net Present Value at 12% discount rate"
                    )
                
                with col4:
                    dscr_color = "normal" if returns['avg_dscr'] and returns['avg_dscr'] > 1.25 else "inverse"
                    st.metric(
                        "Avg DSCR",
                        f"{returns['avg_dscr']:.2f}x" if returns['avg_dscr'] else "N/A",
                        help="Debt Service Coverage Ratio - Min: 1.25x"
                    )
                
                st.write("---")
                
                # ========== 投资摘要 ==========
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("### 💰 Investment Summary")
                    
                    summary_data = {
                        "Total Development Cost": format_currency(cf_model['development_costs']['total_development_cost']),
                        "Equity Required": format_currency(returns['total_equity_invested']),
                        "Debt Financing": format_currency(cf_model['financing']['debt_amount']),
                        "Capitalized Interest": format_currency(cf_model['capitalized_interest']),
                        "Total Loan at Completion": format_currency(cf_model['total_loan_at_completion'])
                    }
                    
                    for label, value in summary_data.items():
                        st.write(f"**{label}:** {value}")
                
                with col2:
                    st.write("### 📈 Returns Summary")
                    
                    returns_data = {
                        "Cash-on-Cash (Year 1)": format_percentage(returns['cash_on_cash_return']),
                        "Profit Margin": format_percentage(returns['profit_margin']),
                        "Exit Value": format_currency(cf_model['exit_value']),
                        "Equity Proceeds": format_currency(returns['total_equity_returned']),
                        "Total Profit": format_currency(returns['total_profit'])
                    }
                    
                    for label, value in returns_data.items():
                        st.write(f"**{label}:** {value}")
                
                st.write("---")
                
                # ========== 开发成本明细 ==========
                st.write("### 🏗️ Development Cost Breakdown")
                
                costs = cf_model['development_costs']
                
                cost_df = pd.DataFrame([
                    {"Category": "Land Acquisition", "Amount": costs['land_cost']},
                    {"Category": "Acquisition Costs", "Amount": costs['acquisition_costs']},
                    {"Category": "Hard Costs", "Amount": costs['hard_costs']},
                    {"Category": "Contingency", "Amount": costs['contingency']},
                    {"Category": "Soft Costs", "Amount": costs['soft_costs']},
                    {"Category": "Total", "Amount": costs['total_development_cost'], "bold": True}
                ])
                
                # 创建饼图
                import plotly.graph_objects as go
                
                pie_data = [
                    costs['total_land'],
                    costs['hard_costs'],
                    costs['contingency'],
                    costs['soft_costs']
                ]
                
                pie_labels = ['Land & Acquisition', 'Hard Costs', 'Contingency', 'Soft Costs']
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=pie_labels,
                    values=pie_data,
                    hole=0.3,
                    marker=dict(colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'])
                )])
                
                fig_pie.update_layout(
                    title="Cost Distribution",
                    height=400
                )
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # 显示表格
                    for _, row in cost_df.iterrows():
                        if row.get('bold'):
                            st.write(f"**{row['Category']}:** **{format_currency(row['Amount'])}**")
                        else:
                            st.write(f"{row['Category']}: {format_currency(row['Amount'])}")
                
                with col2:
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                st.write("---")
                
                # ========== 施工贷款提款时间表 ==========
                st.write("### 🏦 Construction Loan Draw Schedule")
                
                draws = cf_model['construction_draws']
                
                if draws:
                    # 创建提款可视化
                    draw_months = [d['month'] for d in draws]
                    draw_amounts = [d['draw_amount'] / 1e6 for d in draws]  # 转换为百万
                    cumulative_draws = [d['cumulative_draw'] / 1e6 for d in draws]
                    cumulative_interest = [d['cumulative_interest'] / 1e6 for d in draws]
                    
                    fig_draws = go.Figure()
                    
                    fig_draws.add_trace(go.Bar(
                        x=draw_months,
                        y=draw_amounts,
                        name='Monthly Draw',
                        marker_color='#4ECDC4'
                    ))
                    
                    fig_draws.add_trace(go.Scatter(
                        x=draw_months,
                        y=cumulative_draws,
                        name='Cumulative Draws',
                        mode='lines+markers',
                        line=dict(color='#FF6B6B', width=2),
                        yaxis='y2'
                    ))
                    
                    fig_draws.add_trace(go.Scatter(
                        x=draw_months,
                        y=cumulative_interest,
                        name='Cumulative Interest',
                        mode='lines+markers',
                        line=dict(color='#FFA07A', width=2, dash='dash'),
                        yaxis='y2'
                    ))
                    
                    fig_draws.update_layout(
                        title="Construction Draw Schedule",
                        xaxis_title="Month",
                        yaxis_title="Monthly Draw ($M)",
                        yaxis2=dict(
                            title="Cumulative ($M)",
                            overlaying='y',
                            side='right'
                        ),
                        hovermode='x unified',
                        height=400
                    )
                    
                    st.plotly_chart(fig_draws, use_container_width=True)
                    
                    # 显示汇总
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Drawn", format_currency(draws[-1]['cumulative_draw']))
                    with col2:
                        st.metric("Capitalized Interest", format_currency(draws[-1]['cumulative_interest']))
                    with col3:
                        st.metric("Total Loan Balance", format_currency(draws[-1]['outstanding_balance']))
                
                st.write("---")
                
                # ========== 年度现金流 ==========
                st.write("### 💵 Annual Cash Flow Projections")
                
                annual_cfs = cf_model['annual_cash_flows']
                
                # 准备数据
                years = []
                noi_values = []
                debt_service_values = []
                cash_flow_values = []
                cumulative_cf_values = []
                
                for cf in annual_cfs:
                    if cf['period'] != 'Development':
                        years.append(cf['year'])
                        noi_values.append(cf.get('noi', 0) / 1e6)
                        debt_service_values.append(cf.get('debt_service', 0) / 1e6)
                        
                        # Exit year combines operating + exit CF
                        if cf['period'] == 'Exit':
                            total_cf = cf.get('equity_proceeds', 0) / 1e6
                        else:
                            total_cf = cf.get('cash_flow', 0) / 1e6
                        
                        cash_flow_values.append(total_cf)
                        cumulative_cf_values.append(cf.get('cumulative_cash_flow', 0) / 1e6)
                
                # 创建现金流图表
                fig_cf = go.Figure()
                
                fig_cf.add_trace(go.Bar(
                    x=years,
                    y=noi_values,
                    name='NOI',
                    marker_color='#4ECDC4'
                ))
                
                fig_cf.add_trace(go.Bar(
                    x=years,
                    y=[-d for d in debt_service_values],
                    name='Debt Service',
                    marker_color='#FF6B6B'
                ))
                
                fig_cf.add_trace(go.Scatter(
                    x=years,
                    y=cash_flow_values,
                    name='Net Cash Flow',
                    mode='lines+markers',
                    line=dict(color='#45B7D1', width=3),
                    yaxis='y2'
                ))
                
                fig_cf.update_layout(
                    title="Annual Cash Flows",
                    xaxis_title="Year",
                    yaxis_title="NOI / Debt Service ($M)",
                    yaxis2=dict(
                        title="Net Cash Flow ($M)",
                        overlaying='y',
                        side='right'
                    ),
                    barmode='relative',
                    hovermode='x unified',
                    height=450
                )
                
                st.plotly_chart(fig_cf, use_container_width=True)
                
                # ========== 累计现金流 ==========
                fig_cumulative = go.Figure()
                
                # 添加Year 0
                all_years = [0] + years
                all_cumulative = [-returns['total_equity_invested']/1e6] + cumulative_cf_values
                
                fig_cumulative.add_trace(go.Scatter(
                    x=all_years,
                    y=all_cumulative,
                    mode='lines+markers',
                    fill='tozeroy',
                    line=dict(color='#4ECDC4', width=3),
                    marker=dict(size=8)
                ))
                
                # 添加零线
                fig_cumulative.add_hline(y=0, line_dash="dash", line_color="gray")
                
                fig_cumulative.update_layout(
                    title="Cumulative Cash Flow",
                    xaxis_title="Year",
                    yaxis_title="Cumulative Cash Flow ($M)",
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig_cumulative, use_container_width=True)
                
                # ========== 详细现金流表 ==========
                with st.expander("📋 View Detailed Cash Flow Table"):
                    cf_table_data = []
                    
                    for cf in annual_cfs:
                        if cf['period'] == 'Development':
                            cf_table_data.append({
                                'Year': 0,
                                'Period': 'Development',
                                'Equity Invested': format_currency(abs(cf['equity_invested'])),
                                'NOI': '-',
                                'Debt Service': '-',
                                'Cash Flow': format_currency(cf['cash_flow']),
                                'Cumulative CF': format_currency(cf['cumulative_cash_flow'])
                            })
                        elif cf['period'] == 'Exit':
                            cf_table_data.append({
                                'Year': cf['year'],
                                'Period': 'Exit',
                                'Exit Value': format_currency(cf.get('exit_value', 0)),
                                'Loan Payoff': format_currency(cf.get('loan_payoff', 0)),
                                'Equity Proceeds': format_currency(cf.get('equity_proceeds', 0)),
                                'Cash Flow': format_currency(cf['cash_flow']),
                                'Cumulative CF': format_currency(cf.get('cumulative_cash_flow', 0))
                            })
                        else:
                            cf_table_data.append({
                                'Year': cf['year'],
                                'Period': 'Operating',
                                'NOI': format_currency(cf.get('noi', 0)),
                                'Debt Service': format_currency(cf.get('debt_service', 0)),
                                'Cash Flow': format_currency(cf['cash_flow']),
                                'Cumulative CF': format_currency(cf['cumulative_cash_flow'])
                            })
                    
                    st.dataframe(pd.DataFrame(cf_table_data), use_container_width=True)
                
                # ========== 保存计算结果到项目 ==========
                if st.button("💾 Save Calculated Metrics to Project", use_container_width=True):
                    update_data = {
                        'irr': returns['irr'],
                        'npv': returns['npv'],
                        'equity_multiple': returns['equity_multiple'],
                        'cash_on_cash_return': returns['cash_on_cash_return']
                    }
                    
                    db.update_dd_project(project.id, update_data)
                    st.success("✅ Metrics saved to project!")
                    st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error calculating financial model: {e}")
                import traceback
                with st.expander("🔍 Error Details"):
                    st.code(traceback.format_exc())
    
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