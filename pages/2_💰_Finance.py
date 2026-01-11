"""
Financial Dashboard Page
Displays financial metrics, cashflow trends, and transaction history

Developer: Gilbert - Brisbane, QLD
"""

import streamlit as st
import plotly.graph_objects as go
from models.database import DatabaseManager
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Finance",
    page_icon="💰",
    layout="wide"
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
    h1 {
        color: #1e3a5f;
        font-weight: 600;
    }
    h2, h3 {
        color: #2c5282;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def get_database():
    """Get cached database connection"""
    try:
        return DatabaseManager('sqlite:///industrial_real_estate.db')
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None


def format_currency_millions(amount: float) -> str:
    """
    Format currency amount in millions (e.g., $6M)
    
    Args:
        amount: Amount in dollars
        
    Returns:
        Formatted string
    """
    millions = amount / 1_000_000
    return f"${millions:,.0f}M"


def display_cashflow_trend_chart(trend_data, months):
    """
    Display cashflow trend line chart (Plotly 5.x compatible)
    
    Args:
        trend_data: List of dicts with 'year', 'month', 'income', 'expense', 'net'
        months: Number of months to display
    """
    if not trend_data:
        st.info("No trend data available.")
        return
    
    # Prepare x-axis labels (Month YYYY format)
    x_labels = [f"{item['year']}-{item['month']:02d}" for item in trend_data]
    
    # Extract data
    income_data = [item['income'] / 1_000_000 for item in trend_data]
    expense_data = [item['expense'] / 1_000_000 for item in trend_data]
    net_data = [item['net'] / 1_000_000 for item in trend_data]
    
    # Create figure
    fig = go.Figure()
    
    # Add income line (green)
    fig.add_trace(go.Scatter(
        x=x_labels,
        y=income_data,
        mode='lines+markers',
        name='Income',
        line=dict(color='#2ecc71', width=3),
        marker=dict(size=8, color='#2ecc71'),
        hovertemplate='<b>%{x}</b><br>Income: $%{y:.2f}M<extra></extra>'
    ))
    
    # Add expense line (red)
    fig.add_trace(go.Scatter(
        x=x_labels,
        y=expense_data,
        mode='lines+markers',
        name='Expense',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=8, color='#e74c3c'),
        hovertemplate='<b>%{x}</b><br>Expense: $%{y:.2f}M<extra></extra>'
    ))
    
    # Add net line (blue)
    fig.add_trace(go.Scatter(
        x=x_labels,
        y=net_data,
        mode='lines+markers',
        name='Net Cashflow',
        line=dict(color='#3498db', width=3, dash='dash'),
        marker=dict(size=8, color='#3498db'),
        hovertemplate='<b>%{x}</b><br>Net: $%{y:.2f}M<extra></extra>'
    ))
    
    # Update layout (Plotly 5.x compatible)
    fig.update_layout(
        title=dict(
            text=f'Cash Flow Trend (Last {months} Months)',
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
            title=dict(text='Amount (Million AUD)', font=dict(size=14, color='#2c5282')),
            showgrid=True,
            gridcolor='#e2e8f0',
            showline=True,
            linewidth=1,
            linecolor='#e2e8f0',
            zeroline=True,
            zerolinecolor='#95a5a6',
            zerolinewidth=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=450,
        margin=dict(t=80, b=60, l=70, r=40),
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_income_expense_comparison(trend_data):
    """
    Display income vs expense comparison bar chart
    
    Args:
        trend_data: List of dicts with 'year', 'month', 'income', 'expense'
    """
    if not trend_data:
        st.info("No comparison data available.")
        return
    
    # Prepare x-axis labels
    x_labels = [f"{item['year']}-{item['month']:02d}" for item in trend_data]
    
    # Extract data
    income_data = [item['income'] / 1_000_000 for item in trend_data]
    expense_data = [item['expense'] / 1_000_000 for item in trend_data]
    
    # Create figure
    fig = go.Figure()
    
    # Add income bars (green)
    fig.add_trace(go.Bar(
        x=x_labels,
        y=income_data,
        name='Income',
        marker_color='#2ecc71',
        hovertemplate='<b>%{x}</b><br>Income: $%{y:.2f}M<extra></extra>'
    ))
    
    # Add expense bars (red)
    fig.add_trace(go.Bar(
        x=x_labels,
        y=expense_data,
        name='Expense',
        marker_color='#e74c3c',
        hovertemplate='<b>%{x}</b><br>Expense: $%{y:.2f}M<extra></extra>'
    ))
    
    # Update layout (Plotly 5.x compatible)
    fig.update_layout(
        title=dict(
            text='Income vs Expense Comparison',
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
            title=dict(text='Amount (Million AUD)', font=dict(size=14, color='#2c5282')),
            showgrid=True,
            gridcolor='#e2e8f0',
            showline=True,
            linewidth=1,
            linecolor='#e2e8f0',
            zeroline=True,
            zerolinecolor='#95a5a6',
            zerolinewidth=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=450,
        margin=dict(t=80, b=60, l=70, r=40),
        hovermode='x unified',
        barmode='group',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)


def format_transactions_dataframe(transactions):
    """
    Convert transactions to formatted DataFrame for display
    
    Args:
        transactions: List of Transaction objects
        
    Returns:
        DataFrame: Formatted transaction data
    """
    if not transactions:
        return pd.DataFrame()
    
    data = []
    for trans in transactions:
        # Format transaction type
        type_display = trans.transaction_type.value.replace('_', ' ').title()
        
        # Format category
        category = trans.category or (trans.expense_category.value.replace('_', ' ').title() if trans.expense_category else 'N/A')
        
        # Format project
        project = trans.project.project_name if trans.project else 'N/A'
        
        data.append({
            'Date': trans.transaction_date.strftime('%Y-%m-%d'),
            'Type': type_display,
            'Category': category,
            'Amount': float(trans.amount),
            'Project': project,
            'Description': trans.description[:60] + '...' if len(trans.description) > 60 else trans.description
        })
    
    df = pd.DataFrame(data)
    
    # Format amount column for display
    if not df.empty:
        df['Amount_Formatted'] = df['Amount'].apply(lambda x: f"${x:,.2f}")
    
    return df


def main():
    """Main application function"""
    
    # Title
    st.title("💰 Financial Dashboard")
    
    # Initialize database
    db = get_database()
    if not db:
        st.error("⚠️ Could not connect to database.")
        return
    
    # Get current date
    now = datetime.now()
    
    # Sidebar
    with st.sidebar:
        st.header("🔍 Filters")
        months = st.selectbox(
            "Time Range",
            options=[1, 3, 6, 12],
            index=2,  # Default to 6 months
            help="Select the number of months to display in charts"
        )
        st.markdown("---")
        st.markdown("**Last Updated:**")
        st.markdown(f"{now.strftime('%d %b %Y, %H:%M')}")
    
    # Top metrics cards
    st.markdown("---")
    st.markdown("### 📊 Financial Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        try:
            balance = db.get_cash_balance()
            st.metric(
                label="Cash Balance",
                value=format_currency_millions(balance),
                help="Total cash balance from all transactions"
            )
        except Exception as e:
            st.error(f"Error loading cash balance: {e}")
            st.metric(label="Cash Balance", value="$0.0M")
    
    with col2:
        try:
            income = db.get_monthly_income(now.year, now.month)
            st.metric(
                label="This Month Income",
                value=format_currency_millions(income),
                help=f"Total income for {now.strftime('%B %Y')}"
            )
        except Exception as e:
            st.error(f"Error loading monthly income: {e}")
            st.metric(label="This Month Income", value="$0.0M")
    
    with col3:
        try:
            expense = db.get_monthly_expense(now.year, now.month)
            st.metric(
                label="This Month Expense",
                value=format_currency_millions(expense),
                help=f"Total expenses for {now.strftime('%B %Y')}"
            )
        except Exception as e:
            st.error(f"Error loading monthly expense: {e}")
            st.metric(label="This Month Expense", value="$0.0M")
    
    with col4:
        try:
            income = db.get_monthly_income(now.year, now.month)
            expense = db.get_monthly_expense(now.year, now.month)
            net_cashflow = income - expense
            delta = format_currency_millions(abs(net_cashflow)) if net_cashflow != 0 else None
            delta_color = "normal" if net_cashflow >= 0 else "inverse"
            st.metric(
                label="Net Cashflow",
                value=format_currency_millions(net_cashflow),
                delta=delta if net_cashflow < 0 else None,
                delta_color=delta_color,
                help=f"Net cashflow for {now.strftime('%B %Y')} (Income - Expense)"
            )
        except Exception as e:
            st.error(f"Error calculating net cashflow: {e}")
            st.metric(label="Net Cashflow", value="$0.0M")
    
    st.markdown("---")
    
    # Cashflow trend chart
    st.subheader("📈 Cash Flow Trend")
    try:
        with st.spinner("Loading cashflow trend data..."):
            trend_data = db.get_cashflow_trend(months=months)
            display_cashflow_trend_chart(trend_data, months)
    except Exception as e:
        st.error(f"Error loading cashflow trend: {e}")
        import traceback
        with st.expander("Show Error Details"):
            st.code(traceback.format_exc())
    
    st.markdown("---")
    
    # Income vs Expense comparison
    st.subheader("📊 Income vs Expense Comparison")
    try:
        with st.spinner("Loading comparison data..."):
            trend_data = db.get_cashflow_trend(months=months)
            display_income_expense_comparison(trend_data)
    except Exception as e:
        st.error(f"Error loading comparison data: {e}")
        import traceback
        with st.expander("Show Error Details"):
            st.code(traceback.format_exc())
    
    st.markdown("---")
    
    # Recent transactions table
    st.subheader("💳 Recent Transactions")
    try:
        with st.spinner("Loading recent transactions..."):
            transactions = db.get_recent_transactions(limit=20)
            
            if not transactions:
                st.info("No transactions found in database.")
            else:
                # Format as DataFrame
                df = format_transactions_dataframe(transactions)
                
                if not df.empty:
                    # Display DataFrame with proper formatting
                    display_df = df[['Date', 'Type', 'Category', 'Amount_Formatted', 'Project', 'Description']].copy()
                    display_df.columns = ['Date', 'Type', 'Category', 'Amount', 'Project', 'Description']
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            'Date': st.column_config.TextColumn('Date', width='small'),
                            'Type': st.column_config.TextColumn('Type', width='medium'),
                            'Category': st.column_config.TextColumn('Category', width='medium'),
                            'Amount': st.column_config.TextColumn('Amount', width='small'),
                            'Project': st.column_config.TextColumn('Project', width='medium'),
                            'Description': st.column_config.TextColumn('Description', width='large')
                        }
                    )
                    
                    # Summary stats
                    col1, col2, col3 = st.columns(3)
                    total_amount = df['Amount'].sum()
                    income_total = df[df['Type'] == 'Income']['Amount'].sum()
                    expense_total = df[df['Type'] == 'Expense']['Amount'].sum()
                    
                    with col1:
                        st.metric("Total Amount", f"${total_amount:,.2f}")
                    with col2:
                        st.metric("Total Income", f"${income_total:,.2f}")
                    with col3:
                        st.metric("Total Expense", f"${expense_total:,.2f}")
    except Exception as e:
        st.error(f"Error loading recent transactions: {e}")
        import traceback
        with st.expander("Show Error Details"):
            st.code(traceback.format_exc())
    
    st.markdown("---")
    st.markdown("*© 2025 Gilbert Industrial Real Estate Development | Brisbane, Queensland, Australia*")


if __name__ == "__main__":
    main()
