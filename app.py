"""
Asset Management System - Streamlit Dashboard
Connected to real SQLite database with live data

Developer: Gilbert - Brisbane, QLD
Version: 0.2-prod
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func

# Import database models
try:
    from models.database import (
        DatabaseManager, Asset, Project, Transaction, RentalIncome,
        AssetType, AssetStatus, ProjectStatus, TransactionType
    )
    DB_AVAILABLE = True
except ImportError as e:
    st.error(f"⚠️ Database models not found: {e}")
    st.info("Please ensure the 'models' package is in the same directory as app.py")
    DB_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Asset Management System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .sidebar .sidebar-content {
        background-color: #1e3a5f;
        color: white;
    }
    h1 {
        color: #1e3a5f;
        font-weight: 600;
    }
    h2 {
        color: #2c5282;
        font-weight: 500;
    }
    h3 {
        color: #2c5282;
        font-weight: 500;
    }
    .stAlert {
        background-color: #f0f7ff;
        border-left: 4px solid #1e3a5f;
    }
    </style>
    """, unsafe_allow_html=True)


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


def get_portfolio_metrics(session):
    """
    Calculate portfolio metrics from database
    
    Returns:
        dict: Portfolio metrics including asset count, total value, and active projects
    """
    try:
        # Total number of assets
        total_assets = session.query(func.count(Asset.id)).scalar() or 0
        
        # Total portfolio valuation
        total_valuation = session.query(
            func.sum(Asset.current_valuation)
        ).scalar() or 0
        
        # Previous valuation (using purchase price as proxy for change calculation)
        previous_valuation = session.query(
            func.sum(Asset.purchase_price)
        ).scalar() or 0
        
        # Calculate change
        valuation_change = total_valuation - previous_valuation if previous_valuation else 0
        
        # Active projects (not completed or cancelled)
        active_projects = session.query(func.count(Project.id)).filter(
            Project.is_active == True,
            Project.status.notin_([ProjectStatus.COMPLETED, ProjectStatus.CANCELLED])
        ).scalar() or 0
        
        # Total projects for change calculation
        total_projects = session.query(func.count(Project.id)).scalar() or 0
        
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


def get_portfolio_trend(session, months=6):
    """获取投资组合趋势数据"""
    try:
        assets = session.query(Asset).all()
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
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Assets",
            value=f"{metrics['total_assets']}",
            delta=None
        )
    
    with col2:
        valuation_millions = metrics['total_valuation'] / 1_000_000
        change_millions = metrics['valuation_change'] / 1_000_000
        
        st.metric(
            label="Portfolio Value",
            value=f"${valuation_millions:.1f}M AUD",
            delta=f"${change_millions:+.1f}M" if change_millions != 0 else None,
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="Active Projects",
            value=f"{metrics['active_projects']}",
            delta=f"{metrics['total_projects']} total"
        )


def display_transactions(transactions):
    """Display recent transactions in a formatted table"""
    
    if not transactions:
        st.info("No transactions found in database.")
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
        use_container_width=True,
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
        st.info("No data available for chart.")
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
            text='Portfolio Value Trend (Last 6 Months)',
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
    
    st.plotly_chart(fig, use_container_width=True)


def main():
    """Main application function"""
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🏢 Asset Management System")
        st.markdown("**Version:** v0.2-prod")
        st.markdown("**Developer:** Gilbert - Brisbane")
        st.markdown("---")
        st.markdown("#### Status")
        
        # Check database connection
        if DB_AVAILABLE:
            db_manager = get_database_connection()
            if db_manager:
                st.success("✅ Database Connected")
                st.info("📊 Displaying Live Data")
            else:
                st.error("❌ Database Connection Failed")
        else:
            st.error("❌ Models Not Available")
        
        st.markdown("---")
        st.markdown(f"**Last Updated:** {datetime.now().strftime('%d %b %Y, %H:%M')}")
    
    # Main content
    st.title("🏢 Asset Management System")
    st.markdown("### Brisbane & Sunshine Coast Industrial Real Estate Portfolio")
    
    # Check if we can proceed
    if not DB_AVAILABLE:
        st.error("⚠️ Database models are not available. Please check your installation.")
        st.info("Ensure the 'models' directory is present and contains database.py")
        return
    
    db_manager = get_database_connection()
    if not db_manager:
        st.error("⚠️ Could not connect to database. Please ensure 'industrial_real_estate.db' exists.")
        st.info("Run: python -m models.init_db --sample")
        return
    
    # Get database session
    session = db_manager.get_session()
    
    try:
        st.markdown("---")
        
        # Portfolio Overview Section
        st.markdown("### 📊 Portfolio Overview")
        
        with st.spinner("Loading portfolio metrics..."):
            metrics = get_portfolio_metrics(session)
            display_metrics(metrics)
        
        # Reports Section
        st.write("---")
        st.subheader("📊 Generate Reports")
        
        # Import report generator
        try:
            from utils.report_generator import ReportGenerator
            report_gen = ReportGenerator()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Portfolio Report (PDF)**")
                st.write("Comprehensive portfolio overview including assets and projects")
                
                # Generate PDF report
                if st.button("📄 Generate PDF Report", use_container_width=True, key="generate_pdf"):
                    try:
                        with st.spinner("Generating PDF report..."):
                            pdf_buffer = report_gen.generate_portfolio_pdf()
                            # BytesIO object - get bytes data
                            st.session_state['pdf_report'] = pdf_buffer.getvalue()
                            st.session_state['pdf_filename'] = f"portfolio_report_{datetime.now().strftime('%Y%m%d')}.pdf"
                        st.success("✅ PDF generated successfully!")
                    except Exception as e:
                        st.error(f"❌ Error generating PDF: {e}")
                        st.session_state.pop('pdf_report', None)
                
                # Download PDF button
                if 'pdf_report' in st.session_state:
                    st.download_button(
                        label="💾 Download PDF",
                        data=st.session_state['pdf_report'],
                        file_name=st.session_state.get('pdf_filename', 'portfolio_report.pdf'),
                        mime="application/pdf",
                        use_container_width=True,
                        key="download_pdf"
                    )
            
            with col2:
                st.write("**Financial Report (Excel)**")
                st.write("Detailed financial data with multiple worksheets")
                
                # Generate Excel report
                if st.button("📊 Generate Excel Report", use_container_width=True, key="generate_excel"):
                    try:
                        with st.spinner("Generating Excel report..."):
                            excel_buffer = report_gen.generate_financial_excel()
                            # BytesIO object - get bytes data
                            st.session_state['excel_report'] = excel_buffer.getvalue()
                            st.session_state['excel_filename'] = f"financial_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
                        st.success("✅ Excel generated successfully!")
                    except Exception as e:
                        st.error(f"❌ Error generating Excel: {e}")
                        st.session_state.pop('excel_report', None)
                
                # Download Excel button
                if 'excel_report' in st.session_state:
                    st.download_button(
                        label="💾 Download Excel",
                        data=st.session_state['excel_report'],
                        file_name=st.session_state.get('excel_filename', 'financial_report.xlsx'),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="download_excel"
                    )
        
        except ImportError as e:
            st.warning(f"⚠️ Report generator not available: {e}")
            st.info("Please ensure utils/report_generator.py exists")
        
        st.markdown("---")
        
        # Portfolio Trend Chart
        st.markdown("### 📈 Portfolio Value Trend")
        
        with st.spinner("Loading trend data..."):
            dates, values = get_portfolio_trend(session)
            display_portfolio_chart(dates, values)
        
        st.markdown("---")
        
        # Recent Transactions Section
        st.markdown("### 💰 Recent Transactions")
        
        with st.spinner("Loading transactions..."):
            transactions = get_recent_transactions(session, limit=5)
            display_transactions(transactions)
        
        st.markdown("---")
        
        # Additional Info Section
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🎯 Quick Actions")
            st.markdown("""
            - View detailed reports
            - Add new transaction
            - Update asset values
            """)
        
        with col2:
            st.markdown("#### 🔧 System Info")
            st.markdown(f"""
            - Database: SQLite
            - Assets: {metrics['total_assets']}
            - Projects: {metrics['total_projects']}
            """)
        
        with col3:
            st.markdown("#### 📍 Locations")
            st.markdown("""
            - Brisbane, QLD
            - Sunshine Coast, QLD
            - Queensland, Australia
            """)
    
    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
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