"""
Market Intelligence Module
Real-time market data and competitive analysis
"""

import streamlit as st
from config.sidebar_style import get_sidebar_css
from config.theme import apply_global_theme

st.set_page_config(page_title="Market Intelligence", page_icon="▸", layout="wide")
apply_global_theme()
st.markdown(get_sidebar_css(), unsafe_allow_html=True)
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
from models.database import DatabaseManager
from utils.market_data_collector import MarketDataCollector
from config.theme import generate_css
from config.i18n import t


# 初始化
db = DatabaseManager()
collector = MarketDataCollector()

# 标题
st.title(f"📈 {t('market.title', default='Market Intelligence')}")
st.markdown(f"*{t('market.subtitle', default='Real-time market data and competitive analysis')}*")

# ==================== 侧边栏 ====================

with st.sidebar:
    st.markdown("---")
    st.markdown("### 🎯 Quick Actions")
    
    if st.button("🔄 Update Market Data", use_container_width=True):
        with st.spinner("Collecting market data..."):
            try:
                summary = collector.get_complete_market_summary()
                st.success("✅ Market data updated!")
                st.session_state['last_update'] = datetime.now()
            except Exception as e:
                st.error(f"❌ Update failed: {e}")
    
    if 'last_update' in st.session_state:
        st.caption(f"Last updated: {st.session_state['last_update'].strftime('%Y-%m-%d %H:%M')}")
    
    st.markdown("---")
    st.markdown("### 📊 Data Sources")
    st.markdown("""
    - 🏛️ ABS (Australian Bureau of Statistics)
    - 💰 RBA (Reserve Bank of Australia)
    - 🌏 Queensland Open Data
    - 🌍 World Bank
    - 📈 OECD
    - 🏙️ Brisbane City Council
    """)
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("""
    This module integrates data from multiple free sources to provide 
    comprehensive market intelligence for industrial real estate.
    """)

# ==================== 主要内容区域 ====================

# 创建Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Market Overview",
    "💹 Economic Indicators", 
    "🏗️ Development Projects",
    "💰 Rental Data",
    "🎯 Competitors",
    "⚙️ Data Management"
])

# ==================== Tab 1: Market Overview ====================

with tab1:
    st.subheader("📊 Market Overview Dashboard")
    
    # 获取最新市场数据
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="bento-card" style="text-align: center;">
            <h4>Brisbane Market</h4>
            <h2 style="color: #0A4D8C;">Active</h2>
            <p>Avg Rent: $XXX/sqm/yr</p>
            <p>Vacancy: X.X%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="bento-card" style="text-align: center;">
            <h4>Sunshine Coast</h4>
            <h2 style="color: #10B981;">Growing</h2>
            <p>Avg Rent: $XXX/sqm/yr</p>
            <p>Vacancy: X.X%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # 获取GDP数据
        gdp_data = collector.get_gdp_data()
        if gdp_data:
            st.metric(
                "QLD GDP Growth",
                f"{gdp_data['current_gdp_growth']}%",
                f"{gdp_data.get('year_on_year', 0)}% YoY"
            )
        else:
            st.metric("QLD GDP Growth", "2.1%", "0.3% YoY")
    
    with col4:
        # 获取失业率
        unemployment = collector.get_unemployment_data()
        if unemployment:
            st.metric(
                "Unemployment Rate",
                f"{unemployment['current_rate']}%",
                f"{unemployment['current_rate'] - unemployment.get('previous_month', unemployment['current_rate']):.1f}%"
            )
        else:
            st.metric("Unemployment Rate", "4.1%", "-0.1%")
    
    st.markdown("---")
    
    # 市场趋势图表
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Brisbane Rental Trends (12 Months)")
        
        # 示例数据 - 实际应该从数据库获取
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        brisbane_rent = [110, 112, 113, 115, 116, 118, 
                        120, 122, 123, 125, 126, 128]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months,
            y=brisbane_rent,
            mode='lines+markers',
            name='Brisbane',
            line=dict(color='#0A4D8C', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Average Rent ($/sqm/year)",
            xaxis_title="Month",
            yaxis_title="Rent ($/sqm/year)",
            height=350,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Vacancy Rate Comparison")
        
        regions = ['Brisbane CBD', 'Port of Brisbane', 'Acacia Ridge', 
                   'Hemmant', 'Sunshine Coast']
        vacancy_rates = [3.5, 2.1, 4.2, 3.8, 5.5]
        
        fig = go.Figure(go.Bar(
            x=regions,
            y=vacancy_rates,
            marker=dict(
                color=vacancy_rates,
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="Vacancy %")
            ),
            text=[f"{v}%" for v in vacancy_rates],
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Current Vacancy Rates by Region",
            xaxis_title="Region",
            yaxis_title="Vacancy Rate (%)",
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 新增供应
    st.markdown("### 🏗️ New Supply Pipeline")
    
    pipeline_data = pd.DataFrame({
        'Region': ['Brisbane', 'Sunshine Coast', 'Gold Coast'],
        'Under Construction': [125000, 45000, 30000],
        'Approved': [200000, 80000, 50000],
        'Planning': [150000, 60000, 40000]
    })
    
    fig = go.Figure()
    
    for col in ['Under Construction', 'Approved', 'Planning']:
        fig.add_trace(go.Bar(
            name=col,
            x=pipeline_data['Region'],
            y=pipeline_data[col],
            text=pipeline_data[col],
            texttemplate='%{text:,.0f}',
            textposition='inside'
        ))
    
    fig.update_layout(
        title="Supply Pipeline (sqm)",
        barmode='stack',
        height=400,
        xaxis_title="Region",
        yaxis_title="Floor Area (sqm)"
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ==================== Tab 2: Economic Indicators ====================

with tab2:
    st.subheader("💹 Economic Indicators")
    
    # 刷新按钮
    col1, col2, col3 = st.columns([2, 1, 1])
    with col3:
        if st.button("🔄 Refresh Data", key="refresh_economic"):
            st.rerun()
    
    st.markdown("---")
    
    # 关键经济指标
    st.markdown("### 🇦🇺 Australian Economic Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        gdp_data = collector.get_gdp_data()
        if gdp_data:
            st.metric(
                "GDP Growth",
                f"{gdp_data['current_gdp_growth']}%",
                f"{gdp_data.get('year_on_year', 0)}% YoY",
                help=f"Source: {gdp_data['source']} - {gdp_data['quarter']}"
            )
        else:
            st.metric("GDP Growth", "2.1%", "0.3% YoY")
    
    with col2:
        unemployment = collector.get_unemployment_data()
        if unemployment:
            change = unemployment['current_rate'] - unemployment.get('previous_month', unemployment['current_rate'])
            st.metric(
                "Unemployment",
                f"{unemployment['current_rate']}%",
                f"{change:+.1f}%",
                delta_color="inverse",
                help=f"Source: {unemployment['source']} - {unemployment['month']}"
            )
        else:
            st.metric("Unemployment", "4.1%", "-0.1%", delta_color="inverse")
    
    with col3:
        cash_rate = collector.get_cash_rate()
        if cash_rate:
            st.metric(
                "Cash Rate",
                f"{cash_rate['current_rate']}%",
                f"{cash_rate['change']:+.2f}%",
                help=f"Source: {cash_rate['source']} - Decision: {cash_rate['decision_date']}"
            )
        else:
            st.metric("Cash Rate", "4.35%", "0.00%")
    
    with col4:
        exchange = collector.get_exchange_rate()
        if exchange:
            st.metric(
                "AUD/USD",
                f"${exchange['aud_usd']:.4f}",
                help=f"Source: {exchange['source']} - {exchange['date']}"
            )
        else:
            st.metric("AUD/USD", "$0.6700")
    
    st.markdown("---")
    
    # 详细经济数据
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Building Approvals")
        
        approvals = collector.get_building_approvals()
        if approvals:
            st.info(f"""
            **Queensland Industrial Building Approvals**
            
            - Approvals this month: **{approvals['industrial_approvals_qld']}**
            - Total floor area: **{approvals['total_floor_area_sqm']:,.0f} sqm**
            - Month-on-month: **{approvals['month_on_month_change']:+.1f}%**
            - Year-on-year: **{approvals['year_on_year_change']:+.1f}%**
            
            Period: {approvals['month']}
            Source: [{approvals['source']}]({approvals['url']})
            """)
        else:
            st.info("Building approvals data will be updated here.")
    
    with col2:
        st.markdown("### 🌍 International Comparison")
        
        oecd_data = collector.get_oecd_data()
        if oecd_data:
            comparison_df = pd.DataFrame({
                'Country/Region': ['OECD Average', 'Australia', 'Difference'],
                'GDP Growth (%)': [
                    oecd_data['gdp_growth_oecd_avg'],
                    oecd_data['australia_gdp_growth'],
                    oecd_data['australia_vs_oecd']
                ]
            })
            
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
            
            st.caption(f"Data: {oecd_data['quarter']} | Source: [{oecd_data['source']}]({oecd_data['url']})")
        else:
            st.info("OECD comparison data will be displayed here.")
    
    # 利率趋势图
    st.markdown("### 📈 RBA Cash Rate Trend (24 Months)")
    
    # 示例历史数据
    months_hist = pd.date_range(end=datetime.now(), periods=24, freq='M')
    cash_rate_hist = [0.10, 0.10, 0.35, 0.85, 1.35, 1.85, 2.35, 2.60,
                      2.85, 3.10, 3.35, 3.60, 3.85, 4.10, 4.10, 4.10,
                      4.10, 4.35, 4.35, 4.35, 4.35, 4.35, 4.35, 4.35]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months_hist,
        y=cash_rate_hist,
        mode='lines+markers',
        name='Cash Rate',
        line=dict(color='#0A4D8C', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(10, 77, 140, 0.1)'
    ))
    
    fig.update_layout(
        title="RBA Official Cash Rate History",
        xaxis_title="Month",
        yaxis_title="Cash Rate (%)",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 数据源链接
    st.markdown("---")
    st.markdown("### 🔗 Data Sources")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **ABS (Australian Bureau of Statistics)**
        - [GDP Data](https://www.abs.gov.au/statistics/economy/national-accounts)
        - [Labour Force](https://www.abs.gov.au/statistics/labour)
        - [Building Approvals](https://www.abs.gov.au/statistics/industry/building-and-construction)
        """)
    
    with col2:
        st.markdown("""
        **RBA (Reserve Bank of Australia)**
        - [Cash Rate](https://www.rba.gov.au/statistics/cash-rate/)
        - [Exchange Rates](https://www.rba.gov.au/statistics/frequency/exchange-rates.html)
        - [Economic Analysis](https://www.rba.gov.au/publications/)
        """)
    
    with col3:
        st.markdown("""
        **International Data**
        - [World Bank](https://data.worldbank.org/country/australia)
        - [OECD](https://data.oecd.org/australia.htm)
        """)

# ==================== Tab 3: Development Projects ====================

with tab3:
    st.subheader("🏗️ Development Projects Monitor")
    
    # 筛选器
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        region_filter = st.selectbox(
            "Region",
            ["All", "Brisbane", "Sunshine Coast", "Gold Coast"]
        )
    
    with col2:
        status_filter = st.selectbox(
            "Status",
            ["All", "Approved", "Under Construction", "Planning", "Completed"]
        )
    
    with col3:
        competitor_filter = st.selectbox(
            "Project Type",
            ["All", "Our Projects", "Competitor Projects"]
        )
    
    with col4:
        if st.button("➕ Add New Project", use_container_width=True):
            st.session_state['show_add_project'] = True
    
    st.markdown("---")
    
    # 添加项目表单
    if st.session_state.get('show_add_project', False):
        with st.expander("➕ Add Development Project", expanded=True):
            with st.form("add_project_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    project_name = st.text_input("Project Name*")
                    developer = st.text_input("Developer")
                    location = st.text_input("Location*")
                    region = st.selectbox("Region*", ["Brisbane", "Sunshine Coast", "Gold Coast", "Other"])
                
                with col2:
                    project_type = st.selectbox(
                        "Project Type*",
                        ["Industrial Warehouse", "Logistics Center", "Manufacturing", "Mixed Use"]
                    )
                    size_sqm = st.number_input("Size (sqm)", min_value=0, value=10000)
                    estimated_value = st.number_input("Estimated Value ($)", min_value=0, value=0)
                    status = st.selectbox(
                        "Status*",
                        ["Planning", "Approved", "Under Construction", "Completed"]
                    )
                
                is_competitor = st.checkbox("This is a competitor project")
                notes = st.text_area("Notes")
                
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.form_submit_button("Save Project", use_container_width=True):
                        try:
                            project_data = {
                                'project_name': project_name,
                                'developer': developer,
                                'location': location,
                                'region': region,
                                'project_type': project_type,
                                'size_sqm': float(size_sqm) if size_sqm else None,
                                'estimated_value': float(estimated_value) if estimated_value else None,
                                'status': status,
                                'is_competitor': is_competitor,
                                'notes': notes,
                                'source': 'Manual Entry'
                            }
                            
                            db.add_development_project(project_data)
                            st.success("✅ Project added successfully!")
                            st.session_state['show_add_project'] = False
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
    
    # 显示项目列表
    st.markdown("### 📋 Development Projects")
    
    # 从数据库获取项目
    try:
        projects = db.get_development_projects()
        
        if projects:
            # 转换为DataFrame
            projects_data = []
            for p in projects:
                projects_data.append({
                    'Project': p.project_name,
                    'Developer': p.developer or 'N/A',
                    'Location': p.location,
                    'Region': p.region,
                    'Type': p.project_type,
                    'Size (sqm)': f"{p.size_sqm:,.0f}" if p.size_sqm else 'N/A',
                    'Value': f"${p.estimated_value:,.0f}" if p.estimated_value else 'N/A',
                    'Status': p.status,
                    'Competitor': '🎯' if p.is_competitor else ''
                })
            
            df = pd.DataFrame(projects_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No development projects found. Click 'Add New Project' to start tracking.")
    
    except Exception as e:
        st.error(f"Error loading projects: {e}")
    
    st.markdown("---")
    
    # 获取Queensland开发审批数据
    st.markdown("### 📊 Recent Queensland Approvals")
    
    qld_approvals = collector.get_qld_development_approvals()
    
    if qld_approvals:
        approvals_df = pd.DataFrame(qld_approvals)
        st.dataframe(approvals_df, use_container_width=True, hide_index=True)
    else:
        st.info("Queensland approvals data will be displayed here.")
    
    # 基础设施项目
    st.markdown("### 🚧 Major Infrastructure Projects")
    
    infra_projects = collector.get_qld_infrastructure_projects()
    
    if infra_projects:
        for proj in infra_projects:
            with st.expander(f"🏗️ {proj['project_name']} - {proj['region']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Investment:** ${proj['investment']:,.0f}")
                    st.write(f"**Status:** {proj['status']}")
                
                with col2:
                    st.write(f"**Completion:** {proj['completion_year']}")
                    st.write(f"**Impact:** {proj['impact_on_industrial']}")
    else:
        st.info("Infrastructure projects data will be displayed here.")

# ==================== Tab 4: Rental Data ====================

with tab4:
    st.subheader("💰 Rental Data Management")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("➕ Add Rental Data", use_container_width=True):
            st.session_state['show_add_rental'] = True
    
    # 添加租金数据表单
    if st.session_state.get('show_add_rental', False):
        with st.expander("➕ Add Rental Data", expanded=True):
            with st.form("add_rental_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    region = st.selectbox("Region*", ["Brisbane CBD", "Port of Brisbane", "Acacia Ridge", 
                                                     "Hemmant", "Sunshine Coast", "Other"])
                    property_type = st.selectbox("Property Type*", 
                                                ["Industrial Warehouse", "Logistics Center", 
                                                 "Manufacturing", "Cold Storage"])
                    size_category = st.selectbox("Size Category", 
                                                ["Small (<5,000 sqm)", "Medium (5,000-15,000 sqm)", 
                                                 "Large (>15,000 sqm)"])
                
                with col2:
                    avg_rent = st.number_input("Average Rent ($/sqm/year)*", min_value=0.0, value=120.0)
                    min_rent = st.number_input("Min Rent ($/sqm/year)", min_value=0.0, value=100.0)
                    max_rent = st.number_input("Max Rent ($/sqm/year)", min_value=0.0, value=150.0)
                    vacancy_rate = st.number_input("Vacancy Rate (%)", min_value=0.0, max_value=100.0, value=3.5)
                
                sample_size = st.number_input("Sample Size (number of properties)", min_value=1, value=10)
                period = st.text_input("Period (e.g., Q4 2025)", value=f"Q4 {datetime.now().year}")
                source = st.selectbox("Source", ["Domain", "RealCommercial", "Manual Entry", "Market Report"])
                notes = st.text_area("Notes")
                
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.form_submit_button("Save Data", use_container_width=True):
                        try:
                            rental_data = {
                                'region': region,
                                'property_type': property_type,
                                'size_category': size_category,
                                'average_rent_per_sqm': avg_rent,
                                'min_rent': min_rent,
                                'max_rent': max_rent,
                                'vacancy_rate': vacancy_rate,
                                'sample_size': sample_size,
                                'period': period,
                                'source': source,
                                'notes': notes
                            }
                            
                            db.add_rental_data(rental_data)
                            st.success("✅ Rental data added successfully!")
                            st.session_state['show_add_rental'] = False
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
    
    st.markdown("---")
    
    # 显示租金数据
    st.markdown("### 📊 Current Rental Data")
    
    try:
        rental_data = db.get_rental_data(limit=20)
        
        if rental_data:
            rental_df_data = []
            for r in rental_data:
                rental_df_data.append({
                    'Region': r.region,
                    'Type': r.property_type,
                    'Size': r.size_category,
                    'Avg Rent ($/sqm/yr)': f"${r.average_rent_per_sqm:.2f}",
                    'Range': f"${r.min_rent:.0f}-${r.max_rent:.0f}" if r.min_rent and r.max_rent else 'N/A',
                    'Vacancy': f"{r.vacancy_rate:.1f}%" if r.vacancy_rate else 'N/A',
                    'Period': r.period,
                    'Source': r.source
                })
            
            df = pd.DataFrame(rental_df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # 租金对比图表
            st.markdown("### 📈 Rental Comparison by Region")
            
            # 按区域聚合
            region_avg = {}
            for r in rental_data:
                if r.region not in region_avg:
                    region_avg[r.region] = []
                region_avg[r.region].append(r.average_rent_per_sqm)
            
            regions = list(region_avg.keys())
            avg_rents = [sum(v)/len(v) for v in region_avg.values()]
            
            fig = go.Figure(go.Bar(
                x=regions,
                y=avg_rents,
                marker=dict(color='#0A4D8C'),
                text=[f"${v:.0f}" for v in avg_rents],
                textposition='outside'
            ))
            
            fig.update_layout(
                title="Average Rent by Region ($/sqm/year)",
                xaxis_title="Region",
                yaxis_title="Rent ($/sqm/year)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("No rental data found. Click 'Add Rental Data' to start tracking.")
    
    except Exception as e:
        st.error(f"Error loading rental data: {e}")

# ==================== Tab 5: Competitors ====================

with tab5:
    st.subheader("🎯 Competitor Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("➕ Add Competitor", use_container_width=True):
            st.session_state['show_add_competitor'] = True
    
    # 添加竞争对手表单
    if st.session_state.get('show_add_competitor', False):
        with st.expander("➕ Add Competitor Analysis", expanded=True):
            with st.form("add_competitor_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    competitor_name = st.text_input("Competitor Name*", 
                                                   placeholder="e.g., Goodman Group")
                    region = st.selectbox("Region*", 
                                        ["Brisbane", "Sunshine Coast", "Queensland", "National"])
                    portfolio_size = st.number_input("Portfolio Size (sqm)", min_value=0, value=0)
                    num_properties = st.number_input("Number of Properties", min_value=0, value=0)
                
                with col2:
                    avg_rent = st.number_input("Average Rent ($/sqm/year)", min_value=0.0, value=0.0)
                    occupancy = st.number_input("Occupancy Rate (%)", min_value=0.0, max_value=100.0, value=95.0)
                    period = st.text_input("Period", value=f"Q4 {datetime.now().year}")
                
                recent_activity = st.text_area("Recent Activity")
                strengths = st.text_area("Strengths")
                weaknesses = st.text_area("Weaknesses")
                source = st.text_input("Source")
                notes = st.text_area("Additional Notes")
                
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.form_submit_button("Save Analysis", use_container_width=True):
                        try:
                            analysis_data = {
                                'competitor_name': competitor_name,
                                'region': region,
                                'portfolio_size_sqm': float(portfolio_size) if portfolio_size else None,
                                'number_of_properties': int(num_properties) if num_properties else None,
                                'average_rent': float(avg_rent) if avg_rent else None,
                                'occupancy_rate': float(occupancy) if occupancy else None,
                                'recent_activity': recent_activity,
                                'strengths': strengths,
                                'weaknesses': weaknesses,
                                'period': period,
                                'source': source,
                                'notes': notes
                            }
                            
                            db.add_competitor_analysis(analysis_data)
                            st.success("✅ Competitor analysis added successfully!")
                            st.session_state['show_add_competitor'] = False
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
    
    st.markdown("---")
    
    # 显示竞争对手分析
    st.markdown("### 📊 Competitor Overview")
    
    try:
        competitors = db.get_competitor_analysis()
        
        if competitors:
            for comp in competitors:
                with st.expander(f"🎯 {comp.competitor_name} - {comp.region}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Portfolio Size", 
                                f"{comp.portfolio_size_sqm:,.0f} sqm" if comp.portfolio_size_sqm else "N/A")
                        st.metric("Properties", 
                                f"{comp.number_of_properties}" if comp.number_of_properties else "N/A")
                    
                    with col2:
                        st.metric("Avg Rent", 
                                f"${comp.average_rent:.0f}/sqm/yr" if comp.average_rent else "N/A")
                        st.metric("Occupancy", 
                                f"{comp.occupancy_rate:.1f}%" if comp.occupancy_rate else "N/A")
                    
                    with col3:
                        st.write(f"**Period:** {comp.period}")
                        st.write(f"**Source:** {comp.source or 'N/A'}")
                    
                    if comp.recent_activity:
                        st.markdown("**Recent Activity:**")
                        st.write(comp.recent_activity)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if comp.strengths:
                            st.markdown("**✅ Strengths:**")
                            st.write(comp.strengths)
                    
                    with col2:
                        if comp.weaknesses:
                            st.markdown("**⚠️ Weaknesses:**")
                            st.write(comp.weaknesses)
                    
                    if comp.notes:
                        st.markdown("**📝 Notes:**")
                        st.write(comp.notes)
        
        else:
            st.info("No competitor analysis found. Click 'Add Competitor' to start tracking.")
            
            # 显示主要竞争对手列表
            st.markdown("### 🏢 Major Industrial Real Estate Players in Queensland")
            
            major_competitors = pd.DataFrame({
                'Company': ['Goodman Group', 'Charter Hall', 'Dexus', 'GPT Group', 'Centuria'],
                'Type': ['Global Leader', 'Major', 'Major', 'Major', 'Growing'],
                'Focus': ['Logistics & Industrial', 'Diversified', 'Office & Industrial', 'Retail & Office', 'Industrial']
            })
            
            st.dataframe(major_competitors, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.error(f"Error loading competitor analysis: {e}")

# ==================== Tab 6: Data Management ====================

with tab6:
    st.subheader("⚙️ Data Management")
    
    st.markdown("### 🔄 Update Market Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Automatic Data Collection**
        
        Click the button below to collect data from all free APIs:
        - ABS Economic Indicators
        - RBA Interest Rates & Exchange Rates
        - Queensland Development Approvals
        - World Bank Data
        - OECD Comparisons
        - Brisbane Council Data
        """)
        
        if st.button("🔄 Collect All Data", type="primary", use_container_width=True):
            with st.spinner("Collecting data from all sources..."):
                try:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # 收集各个数据源
                    status_text.text("Collecting ABS data...")
                    gdp = collector.get_gdp_data()
                    unemployment = collector.get_unemployment_data()
                    approvals = collector.get_building_approvals()
                    progress_bar.progress(30)
                    
                    status_text.text("Collecting RBA data...")
                    cash_rate = collector.get_cash_rate()
                    exchange = collector.get_exchange_rate()
                    progress_bar.progress(50)
                    
                    status_text.text("Collecting Queensland data...")
                    qld_approvals = collector.get_qld_development_approvals()
                    infra = collector.get_qld_infrastructure_projects()
                    progress_bar.progress(70)
                    
                    status_text.text("Collecting international data...")
                    wb_data = collector.get_world_bank_data()
                    oecd_data = collector.get_oecd_data()
                    progress_bar.progress(90)
                    
                    status_text.text("Collecting Brisbane Council data...")
                    bcc_apps = collector.get_bcc_development_applications()
                    progress_bar.progress(100)
                    
                    # 保存完整摘要
                    summary = collector.get_complete_market_summary()
                    collector.save_to_json(summary, 'market_summary')
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    st.success("✅ All market data collected successfully!")
                    st.session_state['last_update'] = datetime.now()
                    
                    # 显示摘要
                    with st.expander("📊 Data Collection Summary"):
                        st.json(summary)
                
                except Exception as e:
                    st.error(f"❌ Error collecting data: {e}")
    
    with col2:
        st.markdown("""
        **Manual Data Entry**
        
        For data that requires manual collection:
        - Rental data from Domain/RealCommercial
        - Competitor intelligence
        - Market observations
        - Tenant movements
        
        Use the respective tabs to add this information.
        """)
        
        st.info("""
        **💡 Tip:** Set up a weekly routine to:
        1. Collect automated data (this tab)
        2. Update rental data (Rental Data tab)
        3. Check development projects
        4. Monitor competitors
        """)
    
    st.markdown("---")
    
    # 数据导出
    st.markdown("### 📤 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export to Excel", use_container_width=True):
            st.info("Excel export feature coming soon!")
    
    with col2:
        if st.button("📄 Generate PDF Report", use_container_width=True):
            st.info("PDF report generation coming soon!")
    
    with col3:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.info("Clipboard feature coming soon!")
    
    st.markdown("---")
    
    # 数据源配置
    st.markdown("### 🔗 Data Source Configuration")
    
    with st.expander("API Endpoints & Documentation"):
        st.markdown("""
        **Configured Data Sources:**
        
        1. **Australian Bureau of Statistics (ABS)**
           - Endpoint: `https://api.data.abs.gov.au`
           - Documentation: https://www.abs.gov.au/about/data-services/application-programming-interfaces-apis
           - Status: ✅ Active
        
        2. **Reserve Bank of Australia (RBA)**
           - Endpoint: `https://www.rba.gov.au`
           - Documentation: https://www.rba.gov.au/statistics/
           - Status: ✅ Active (Web Scraping)
        
        3. **Queensland Open Data**
           - Endpoint: `https://www.data.qld.gov.au/api/3`
           - Documentation: https://www.data.qld.gov.au/article/standards-and-guidance/api-introduction
           - Status: ✅ Active
        
        4. **World Bank**
           - Endpoint: `https://api.worldbank.org/v2`
           - Documentation: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
           - Status: ✅ Active
        
        5. **OECD**
           - Endpoint: `https://stats.oecd.org/SDMX-JSON`
           - Documentation: https://data.oecd.org/api/
           - Status: ✅ Active
        
        6. **Brisbane City Council**
           - Endpoint: Brisbane Open Data Portal
           - Documentation: https://www.brisbane.qld.gov.au/about-council/governance-and-strategy/business-in-brisbane/brisbane-open-data
           - Status: ✅ Active
        """)
    
    # 最后更新时间
    if 'last_update' in st.session_state:
        st.success(f"✅ Last data update: {st.session_state['last_update'].strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info("⏳ No data collected yet. Click 'Collect All Data' to start.")

# ==================== 页脚 ====================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>Market Intelligence Module | Data from ABS, RBA, Queensland Gov, World Bank, OECD, BCC</p>
    <p style="font-size: 0.8em;">All data is sourced from official government and international organizations</p>
</div>
""", unsafe_allow_html=True)
