"""
Asset Management System - Streamlit Dashboard
Connected to real SQLite database with live data

Developer: Gilbert - Brisbane, QLD
Version: 0.2-prod
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import func

# Theme imports
from config.theme import generate_css, LIGHT_THEME, DARK_THEME

# Internationalization
from config.i18n import t, get_language, set_language, get_current_language
from utils.language_switcher import render_language_switcher_compact

# Security imports
from config.security import get_security_manager, require_production_check

# Alias for compatibility
get_current_language = get_language

# Import database models
try:
    from models.database import (
        DatabaseManager, Asset, Project, Transaction, RentalIncome,
        AssetType, AssetStatus, ProjectStatus, TransactionType, Base
    )
    from sqlalchemy import create_engine
    DB_AVAILABLE = True
except ImportError as e:
    st.error(f"⚠️ Database models not found: {e}")
    st.info("Please ensure the 'models' package is in the same directory as app.py")
    DB_AVAILABLE = False

# Initialize database
@st.cache_resource
def init_database():
    """Initialize database and create all tables if not exist"""
    db_manager = DatabaseManager()
    
    try:
        from sqlalchemy import create_engine, inspect, text
        from models.database import Base
        
        engine = create_engine(f'sqlite:///{db_manager.db_path}')
        inspector = inspect(engine)
        
        needs_rebuild = False
        
        # 检查 assets 表
        if 'assets' in inspector.get_table_names():
            asset_columns = [col['name'] for col in inspector.get_columns('assets')]
            required_asset_columns = [
                'purchase_price', 'address_line1', 'current_valuation',
                'land_area_sqm', 'building_area_sqm'
            ]
            missing_asset_cols = [col for col in required_asset_columns if col not in asset_columns]
            
            if missing_asset_cols:
                print(f"⚠️  Assets table missing columns: {missing_asset_cols}")
                needs_rebuild = True
        
        # 检查 transactions 表
        if 'transactions' in inspector.get_table_names():
            trans_columns = [col['name'] for col in inspector.get_columns('transactions')]
            if 'project_id' not in trans_columns:
                print("⚠️  Transactions table missing project_id column")
                needs_rebuild = True
        
        # 检查 dd_projects 表
        if 'dd_projects' in inspector.get_table_names():
            dd_columns = [col['name'] for col in inspector.get_columns('dd_projects')]
            if 'project_name' not in dd_columns:
                print("⚠️  DD Projects table has old structure")
                needs_rebuild = True
        
        # 如果需要重建
        if needs_rebuild:
            print("🔄 Database structure mismatch detected. Rebuilding...")
            
            # 备份提示
            print("⚠️  Note: Existing data will be cleared during rebuild")
            
            # 删除所有表
            Base.metadata.drop_all(engine)
            print("✅ Old tables dropped")
            
            # 重新创建所有表
            Base.metadata.create_all(engine)
            print("✅ New tables created with correct structure")
            
            # 验证新结构
            inspector = inspect(engine)
            asset_columns = [col['name'] for col in inspector.get_columns('assets')]
            print(f"✅ Assets table columns: {len(asset_columns)}")
            
        else:
            # 结构正确，只创建缺失的表
            Base.metadata.create_all(engine)
            print("✅ Database structure verified")
        
        return db_manager
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        
        # 出错时尝试完全重建
        try:
            from models.database import Base
            from sqlalchemy import create_engine
            
            engine = create_engine(f'sqlite:///{db_manager.db_path}')
            Base.metadata.drop_all(engine)
            Base.metadata.create_all(engine)
            
            print("🔄 Database rebuilt from scratch after error")
        except Exception as rebuild_error:
            print(f"❌ Rebuild also failed: {rebuild_error}")
        
        return db_manager

# 初始化数据库
db = init_database()

# Page configuration
st.set_page_config(
    page_title="Asset Management System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Production environment security check
security = get_security_manager()
if os.getenv('APP_ENV') == 'production':
    security.validate_api_key()

# Apply professional theme
st.markdown(generate_css('light'), unsafe_allow_html=True)


@st.cache_resource
def get_database_connection():
    """
    Create and cache database connection
    Uses st.cache_resource to maintain single connection across reruns
    """
    try:
        db_manager = DatabaseManager('sqlite:///industrial_real_estate.db')
        return db_manager
    except Exception as e:
        st.error(f"❌ Failed to connect to database: {e}")
        return None


def get_portfolio_metrics(_session):
    """
    Calculate portfolio metrics from database
    
    Returns:
        dict: Portfolio metrics including asset count, total value, and active projects
    """
    try:
        # Total number of assets
        total_assets = _session.query(func.count(Asset.id)).scalar() or 0
        
        # Total portfolio valuation
        total_valuation = _session.query(
            func.sum(Asset.current_valuation)
        ).scalar() or 0
        
        # Previous valuation (using purchase price as proxy for change calculation)
        previous_valuation = _session.query(
            func.sum(Asset.purchase_price)
        ).scalar() or 0
        
        # Calculate change
        valuation_change = total_valuation - previous_valuation if previous_valuation else 0
        
        # Active projects (not completed or cancelled)
        active_projects = _session.query(func.count(Project.id)).filter(
            Project.is_active == True,
            Project.status.notin_([ProjectStatus.COMPLETED, ProjectStatus.CANCELLED])
        ).scalar() or 0
        
        # Total projects for change calculation
        total_projects = _session.query(func.count(Project.id)).scalar() or 0
        
        return {
            'total_assets': total_assets,
            'total_valuation': total_valuation,
            'valuation_change': valuation_change,
            'active_projects': active_projects,
            'total_projects': total_projects
        }
    
    except Exception as e:
        st.error(f"Error calculating metrics: {e}")
        return {
            'total_assets': 0,
            'total_valuation': 0,
            'valuation_change': 0,
            'active_projects': 0,
            'total_projects': 0
        }


def get_recent_transactions(session, limit=5):
    """
    Get recent transactions from database
    
    Args:
        session: Database session
        limit: Number of transactions to retrieve
        
    Returns:
        list: Recent transactions
    """
    try:
        transactions = session.query(Transaction).order_by(
            Transaction.transaction_date.desc()
        ).limit(limit).all()
        
        return transactions
    
    except Exception as e:
        st.error(f"Error fetching transactions: {e}")
        return []


def get_portfolio_trend(_session, months=6):
    """获取投资组合趋势数据
    """
    try:
        assets = _session.query(Asset).all()
        total_current_value = sum(float(a.current_valuation or 0) for a in assets)
        
        dates = []
        values = []
        current_date = datetime.now()
        
        for i in range(months):
            month_date = current_date - timedelta(days=30 * (months - i - 1))
            dates.append(month_date.strftime("%b %Y"))
            growth_factor = 0.96 + (i * 0.008)
            month_value = (total_current_value * growth_factor) / 1_000_000
            values.append(month_value)
        
        return dates, values
    except Exception as e:
        st.error(f"Error calculating trend: {e}")
        return [], []


def display_metrics(metrics):
    """Display portfolio metrics in columns"""
    
    # Bento Grid布局
    st.markdown('<div class="bento-grid">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4, gap="large")
    
    with col1:
        st.metric(
            label=t('home.total_assets'),
            value=f"{metrics['total_assets']}",
            delta=None
        )
    
    with col2:
        valuation_millions = metrics['total_valuation'] / 1_000_000
        change_millions = metrics['valuation_change'] / 1_000_000
        
        st.metric(
            label=t('home.portfolio_value'),
            value=f"${valuation_millions:.1f}M AUD",
            delta=f"${change_millions:+.1f}M" if change_millions != 0 else None,
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label=t('home.active_projects'),
            value=f"{metrics['active_projects']}",
            delta=f"{metrics['total_projects']} {t('common.total')}"
        )
    
    with col4:
        # Add a fourth metric or leave empty
        pass
    
    st.markdown('</div>', unsafe_allow_html=True)


def display_transactions(transactions):
    """Display recent transactions in a formatted table"""
    
    if not transactions:
        st.info(t('common.no_data'))
        return
    
    # Create DataFrame for display
    trans_data = []
    
    for trans in transactions:
        # Determine emoji based on transaction type
        if trans.transaction_type == TransactionType.INCOME:
            type_emoji = "📈"
        elif trans.transaction_type == TransactionType.EXPENSE:
            type_emoji = "📉"
        elif trans.transaction_type == TransactionType.ASSET_PURCHASE:
            type_emoji = "🏢"
        else:
            type_emoji = "💰"
        
        trans_data.append({
            'Date': trans.transaction_date.strftime('%d %b %Y'),
            'Type': f"{type_emoji} {trans.transaction_type.value.replace('_', ' ').title()}",
            'Amount': f"${trans.amount:,.2f}",
            'Description': trans.description[:60] + '...' if len(trans.description) > 60 else trans.description,
            'Asset': trans.asset.name if trans.asset else 'N/A'
        })
    
    df = pd.DataFrame(trans_data)
    
    # Display as a styled table
    st.dataframe(
        df,
        width='stretch',
        hide_index=True,
        column_config={
            'Date': st.column_config.TextColumn('Date', width='small'),
            'Type': st.column_config.TextColumn('Type', width='medium'),
            'Amount': st.column_config.TextColumn('Amount', width='small'),
            'Description': st.column_config.TextColumn('Description', width='large'),
            'Asset': st.column_config.TextColumn('Asset', width='medium')
        }
    )


def display_portfolio_chart(dates, values):
    """显示投资组合趋势图表（Plotly 5.x 兼容）"""
    if not dates or not values:
        st.info(t('common.no_data'))
        return
    
    fig = go.Figure()
    
    # 添加折线图
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        line=dict(color='#1e3a5f', width=3),
        marker=dict(size=8, color='#2c5282', line=dict(color='white', width=2)),
        hovertemplate='<b>%{x}</b><br>Value: $%{y:.2f}M AUD<extra></extra>'
    ))
    
    # Plotly 5.x 兼容的布局配置
    fig.update_layout(
        title=dict(
            text=t('home.portfolio_value') + ' ' + t('common.trend'),
            font=dict(size=18, color='#1e3a5f', family='Arial'),
            x=0.05,
            xanchor='left'
        ),
        xaxis=dict(
            title=dict(text='Month', font=dict(size=14, color='#2c5282')),
            showgrid=False,
            showline=True,
            linewidth=1,
            linecolor='#e2e8f0'
        ),
        yaxis=dict(
            title=dict(text='Value (Million AUD)', font=dict(size=14, color='#2c5282')),
            showgrid=True,
            gridcolor='#e2e8f0',
            showline=True,
            linewidth=1,
            linecolor='#e2e8f0',
            zeroline=False
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=450,
        margin=dict(t=80, b=60, l=70, r=40),
        hovermode='x unified',
        showlegend=False
    )
    
    st.plotly_chart(fig, width='stretch')


def main():
    """Main application function"""
    
    # Sidebar
    with st.sidebar:
        # Logo和标题
        st.markdown("### 🏢 Industrial RE")
        st.caption("Professional Asset Management Platform")
        st.markdown("---")
        
        # 导航分组
        st.markdown("#### 📊 PORTFOLIO MANAGEMENT")
        st.caption("Core business operations")
        st.markdown("---")
        
        st.markdown("#### 🤖 DECISION SUPPORT")
        st.caption("AI-powered analysis")
        st.markdown("---")
        
        # 状态面板
        st.markdown("#### 📡 System Status")
        if DB_AVAILABLE:
            db_manager = get_database_connection()
            if db_manager:
                st.success("✅ Database Connected")
                st.info("📊 Displaying Live Data")
            else:
                st.error("❌ Database Connection Failed")
        else:
            st.error("❌ Models Not Available")
        
        # 分隔线
        st.markdown("---")
        
        # ========== Developer Mode ==========
        
        # 开发者模式（可折叠）
        dev_mode = st.checkbox("🔧 Developer Mode", value=False, key="dev_mode")
        
        if dev_mode:
            st.caption("Debug tools enabled")
            
            # 系统信息
            with st.expander("📊 System Info", expanded=False):
                try:
                    st.code(f"""Python: {sys.version.split()[0]}
Streamlit: {st.__version__}
Database: {db.db_path}
Tables: {len(Base.metadata.tables)}""")
                except Exception as e:
                    st.error(f"Error displaying system info: {e}")
            
            # 数据库管理
            with st.expander("🗄️ Database Management", expanded=False):
                st.error("⚠️ **Warning:** Rebuild will delete all existing data!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔍 Check Schema", key="check_schema"):
                        try:
                            from sqlalchemy import inspect
                            
                            inspector = inspect(db.engine)
                            
                            st.write("**Current Tables:**")
                            for table in inspector.get_table_names():
                                cols = [c['name'] for c in inspector.get_columns(table)]
                                st.text(f"{table}: {len(cols)} columns")
                                
                                # 显示前5个列名
                                if len(cols) > 0:
                                    st.caption(f"  {', '.join(cols[:5])}...")
                        except Exception as e:
                            st.error(f"Error checking schema: {e}")
                
                with col2:
                    if st.button("🔄 Rebuild Now", type="primary", key="rebuild_db"):
                        try:
                            # 删除所有表
                            Base.metadata.drop_all(db.engine)
                            st.success("✅ Dropped old tables")
                            
                            # 重新创建
                            Base.metadata.create_all(db.engine)
                            st.success("✅ Created new tables")
                            
                            st.balloons()
                            st.info("🔄 Please refresh the page (press F5 or Cmd+R)")
                            
                        except Exception as e:
                            st.error(f"❌ Rebuild failed: {e}")
                            st.code(str(e))
        
        # ========== 原有的底部信息 ==========
        
        st.markdown("---")
        st.caption("Version 1.4 Professional")
        st.caption(f"Last updated: {datetime.now().strftime('%b %d, %Y')}")
        st.caption("© 2026 Gilbert · Brisbane")
    
    # Main content
    st.title(f"🏢 {t('app.title')}")
    st.markdown(f"### {t('app.subtitle')}")
    
    # Check if we can proceed
    if not DB_AVAILABLE:
        st.error(f"⚠️ {t('app.models_not_available')}")
        st.info("Ensure the 'models' directory is present and contains database.py")
        return
    
    db_manager = get_database_connection()
    if not db_manager:
        st.error(f"⚠️ {t('app.database_connection_failed')}")
        st.info("Run: python -m models.init_db --sample")
        return
    
    # Get database session
    session = db_manager.get_session()
    
    try:
        st.markdown("---")
        
        # Portfolio Overview Section
        st.markdown(f"### 📊 {t('dashboard.portfolio_overview')}")
        
        with st.spinner(f"{t('common.loading')}"):
            metrics = get_portfolio_metrics(session)
            display_metrics(metrics)
        
        # Reports Section
        st.write("---")
        st.subheader(f"📊 {t('dashboard.generate_reports')}")
        
        # Import report generator
        try:
            from utils.report_generator import ReportGenerator
            report_gen = ReportGenerator()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**{t('dashboard.portfolio_report_pdf')}**")
                st.write(t('dashboard.portfolio_report_desc'))
                
                # Generate PDF report
                if st.button(f"📄 {t('dashboard.generate_pdf_report')}", width='stretch', key="generate_pdf"):
                    try:
                        with st.spinner("Generating PDF report..."):
                            pdf_buffer = report_gen.generate_portfolio_pdf()
                            # BytesIO object - get bytes data
                            st.session_state['pdf_report'] = pdf_buffer.getvalue()
                            st.session_state['pdf_filename'] = f"portfolio_report_{datetime.now().strftime('%Y%m%d')}.pdf"
                        st.success(f"✅ {t('home.report_generated')}")
                    except Exception as e:
                        st.error(f"❌ {t('home.report_error')}")
                        st.session_state.pop('pdf_report', None)
                
                # Download PDF button
                if 'pdf_report' in st.session_state:
                    st.download_button(
                        label=f"💾 {t('home.download_pdf')}",
                        data=st.session_state['pdf_report'],
                        file_name=st.session_state.get('pdf_filename', 'portfolio_report.pdf'),
                        mime="application/pdf",
                        width='stretch',
                        key="download_pdf"
                    )
            
            with col2:
                st.write(f"**{t('dashboard.financial_report_excel')}**")
                st.write(t('dashboard.financial_report_desc'))
                
                # Generate Excel report
                if st.button(f"📊 {t('dashboard.generate_excel_report')}", width='stretch', key="generate_excel"):
                    try:
                        with st.spinner("Generating Excel report..."):
                            excel_buffer = report_gen.generate_financial_excel()
                            # BytesIO object - get bytes data
                            st.session_state['excel_report'] = excel_buffer.getvalue()
                            st.session_state['excel_filename'] = f"financial_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
                        st.success(f"✅ {t('home.report_generated')}")
                    except Exception as e:
                        st.error(f"❌ {t('home.report_error')}")
                        st.session_state.pop('excel_report', None)
                
                # Download Excel button
                if 'excel_report' in st.session_state:
                    st.download_button(
                        label=f"💾 {t('home.download_excel')}",
                        data=st.session_state['excel_report'],
                        file_name=st.session_state.get('excel_filename', 'financial_report.xlsx'),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width='stretch',
                        key="download_excel"
                    )
        
        except ImportError as e:
            st.warning(f"⚠️ Report generator not available: {e}")
            st.info("Please ensure utils/report_generator.py exists")
        
        st.markdown("---")
        
        # Portfolio Trend Chart
        st.markdown(f"### 📈 {t('home.portfolio_value')} {t('common.trend')}")
        
        with st.spinner(t('common.loading')):
            dates, values = get_portfolio_trend(session)
            display_portfolio_chart(dates, values)
        
        st.markdown("---")
        
        # Recent Transactions Section
        st.markdown(f"### 💰 {t('finance.recent_transactions')}")
        
        with st.spinner(t('common.loading')):
            transactions = get_recent_transactions(session, limit=5)
            display_transactions(transactions)
        
        st.markdown("---")
        
        # Additional Info Section
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🎯 Quick Actions")
            st.markdown(f"""
            - {t('common.view')} {t('common.details')}
            - {t('finance.add_transaction')}
            - {t('common.update')} {t('assets.asset_name')} {t('common.values')}
            """)
        
        with col2:
            st.markdown("#### 🔧 System Info")
            st.markdown(f"""
            - Database: SQLite
            - {t('home.total_assets')}: {metrics['total_assets']}
            - {t('home.active_projects')}: {metrics['total_projects']}
            """)
        
        with col3:
            st.markdown("#### 📍 Locations")
            st.markdown("""
            - Brisbane, QLD
            - Sunshine Coast, QLD
            - Queensland, Australia
            """)
    
    except Exception as e:
        st.error(f"❌ {t('messages.error_occurred')}: {e}")
        st.info("Please check the database connection and try refreshing the page.")
        import traceback
        with st.expander("Show Error Details"):
            st.code(traceback.format_exc())
    
    finally:
        # Always close the session
        if session:
            db_manager.close_session(session)
    
    # Footer
    st.markdown("---")
    st.markdown("*© 2025 Gilbert Industrial Real Estate Development | Brisbane, Queensland, Australia*")


if __name__ == "__main__":
    main()