"""
Financial Dashboard Page
Displays financial metrics, cashflow trends, and transaction history

Developer: Gilbert - Brisbane, QLD
"""

import streamlit as st
import plotly.graph_objects as go
from models.database import DatabaseManager, TransactionType
from datetime import datetime, date
import pandas as pd
import time
from config.theme import generate_css
from utils.chart_styles import get_chart_layout, apply_professional_theme_to_figure, CHART_COLORS
from config.i18n import t, get_current_language

# Page configuration
st.set_page_config(
    page_title="Finance",
    page_icon="💰",
    layout="wide"
)

# 应用专业主题
st.markdown(generate_css('light'), unsafe_allow_html=True)


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
    
    fig = apply_professional_theme_to_figure(fig, theme='light')
    
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
    
    fig = apply_professional_theme_to_figure(fig, theme='light')
    
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
            'Amount': abs(float(trans.amount)),  # 显示为正数
            'Project': project,
            'Description': trans.description[:60] + '...' if len(trans.description) > 60 else trans.description,
            'ID': trans.id  # 用于操作
        })
    
    df = pd.DataFrame(data)
    
    # Format amount column for display
    if not df.empty:
        df['Amount_Formatted'] = df['Amount'].apply(lambda x: f"${x:,.2f}")
    
    return df


def main():
    """Main application function"""
    
    # Title
    st.title(f"💰 {t('finance.title')}")
    
    # Initialize database
    db = get_database()
    if not db:
        st.error("⚠️ Could not connect to database.")
        return
    
    # Get current date
    now = datetime.now()
    
    # Sidebar
    with st.sidebar:
        st.header(f"💳 {t('finance.transaction_management')}")
        
        # 添加/编辑模式
        if 'edit_transaction_id' not in st.session_state:
            st.session_state.edit_transaction_id = None
        
        mode = t('finance.edit_transaction') if st.session_state.edit_transaction_id else t('finance.record_transaction')
        st.subheader(mode)
        
        # 如果是编辑模式，加载现有数据
        editing = st.session_state.edit_transaction_id is not None
        transaction = None
        if editing:
            transaction = db.get_transaction_by_id(st.session_state.edit_transaction_id)
            if not transaction:
                st.error("Transaction not found!")
                st.session_state.edit_transaction_id = None
                st.rerun()
        
        with st.form("transaction_form"):
            # 交易类型（突出显示）
            type_options = ["Income", "Expense"]
            type_index = 0
            if editing and transaction:
                type_index = 0 if transaction.transaction_type == TransactionType.INCOME else 1
            
            transaction_type = st.radio(
                f"{t('finance.transaction_type')}*",
                type_options,
                horizontal=True,
                index=type_index
            )
            
            # 基本信息
            default_date = date.today()
            if editing and transaction:
                default_date = transaction.transaction_date
            
            transaction_date = st.date_input(
                f"{t('finance.transaction_date')}*",
                value=default_date
            )
            
            # Category选项
            category_options = [
                t('finance.categories.rental_income'),
                t('finance.categories.construction_cost'),
                t('finance.categories.land_acquisition'),
                t('finance.categories.professional_fees'),
                t('finance.categories.financing'),
                t('finance.categories.maintenance'),
                t('finance.categories.other')
            ]
            category_index = 0
            if editing and transaction and transaction.category:
                try:
                    # Map category to translation key
                    category_map = {
                        "Rental Income": t('finance.categories.rental_income'),
                        "Construction Cost": t('finance.categories.construction_cost'),
                        "Land Acquisition": t('finance.categories.land_acquisition'),
                        "Professional Fees": t('finance.categories.professional_fees'),
                        "Financing": t('finance.categories.financing'),
                        "Maintenance": t('finance.categories.maintenance'),
                        "Other": t('finance.categories.other')
                    }
                    if transaction.category in category_map:
                        category_index = category_options.index(category_map[transaction.category])
                except ValueError:
                    category_index = 0
            
            category = st.selectbox(
                f"{t('finance.category')}*",
                category_options,
                index=category_index
            )
            
            # 金额（大号突出）
            default_amount = 0.0
            if editing and transaction:
                default_amount = abs(float(transaction.amount))
            
            amount = st.number_input(
                f"{t('common.amount')} (AUD)*",
                min_value=0.0,
                step=1000.0,
                format="%.2f",
                value=default_amount
            )
            
            # 关联资产/项目
            assets = db.get_all_assets_for_dropdown()
            asset_options = ["None"] + [f"{a['name']}" for a in assets]
            asset_index = 0
            if editing and transaction and transaction.asset_id:
                try:
                    # 找到对应的asset
                    for idx, a in enumerate(assets):
                        if a['id'] == transaction.asset_id:
                            asset_index = idx + 1
                            break
                except:
                    asset_index = 0
            
            asset_id = st.selectbox(
                t('finance.related_asset'),
                asset_options,
                index=asset_index
            )
            
            # 描述
            default_description = ""
            if editing and transaction:
                default_description = transaction.description or ""
            
            description = st.text_area(
                f"{t('common.description')}*",
                placeholder="Payment for Q4 rent, Invoice #1234, etc.",
                value=default_description
            )
            
            # 按钮
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button(f"💾 {t('common.save')}", use_container_width=True)
            with col2:
                cancelled = st.form_submit_button(f"❌ {t('common.cancel')}", use_container_width=True)
            
            if submitted:
                # 验证
                if amount <= 0:
                    st.error(f"{t('common.amount')} {t('validation.positive_number')}")
                elif not description:
                    st.error(f"{t('common.description')} {t('validation.required')}")
                else:
                    # 准备数据
                    # Expense金额存为负数
                    final_amount = amount if transaction_type == "Income" else -amount
                    
                    # 获取asset_id
                    selected_asset_id = None
                    if asset_id != "None":
                        asset_idx = asset_options.index(asset_id) - 1
                        selected_asset_id = assets[asset_idx]['id']
                    
                    transaction_data = {
                        "transaction_date": transaction_date,
                        "transaction_type": transaction_type,
                        "category": category,
                        "amount": final_amount,
                        "asset_id": selected_asset_id,
                        "description": description
                    }
                    
                    try:
                        if st.session_state.edit_transaction_id:
                            db.update_transaction(st.session_state.edit_transaction_id, transaction_data)
                            st.success(f"✅ {t('finance.transaction_saved')}")
                        else:
                            db.add_transaction(transaction_data)
                            st.success(f"✅ {t('finance.transaction_saved')}")
                        
                        st.session_state.edit_transaction_id = None
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"{t('messages.error_occurred')}: {e}")
            
            if cancelled:
                st.session_state.edit_transaction_id = None
                st.rerun()
        
        st.markdown("---")
        st.header(f"🔍 {t('common.filter')}")
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
    st.markdown('<div style="margin-bottom: 2rem;">', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"### 📊 {t('finance.title')}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        try:
            balance = db.get_cash_balance()
            st.metric(
                label=t('home.cash_balance'),
                value=format_currency_millions(balance),
                help="Total cash balance from all transactions"
            )
        except Exception as e:
            st.error(f"Error loading cash balance: {e}")
            st.metric(label=t('home.cash_balance'), value="$0.0M")
    
    with col2:
        try:
            income = db.get_monthly_income(now.year, now.month)
            st.metric(
                label=t('finance.this_month_income'),
                value=format_currency_millions(income),
                help=f"Total income for {now.strftime('%B %Y')}"
            )
        except Exception as e:
            st.error(f"Error loading monthly income: {e}")
            st.metric(label=t('finance.this_month_income'), value="$0.0M")
    
    with col3:
        try:
            expense = db.get_monthly_expense(now.year, now.month)
            st.metric(
                label=t('finance.this_month_expense'),
                value=format_currency_millions(expense),
                help=f"Total expenses for {now.strftime('%B %Y')}"
            )
        except Exception as e:
            st.error(f"Error loading monthly expense: {e}")
            st.metric(label=t('finance.this_month_expense'), value="$0.0M")
    
    with col4:
        try:
            income = db.get_monthly_income(now.year, now.month)
            expense = db.get_monthly_expense(now.year, now.month)
            net_cashflow = income - expense
            delta = format_currency_millions(abs(net_cashflow)) if net_cashflow != 0 else None
            delta_color = "normal" if net_cashflow >= 0 else "inverse"
            st.metric(
                label=t('finance.net_cashflow'),
                value=format_currency_millions(net_cashflow),
                delta=delta if net_cashflow < 0 else None,
                delta_color=delta_color,
                help=f"Net cashflow for {now.strftime('%B %Y')} (Income - Expense)"
            )
        except Exception as e:
            st.error(f"Error calculating net cashflow: {e}")
            st.metric(label=t('finance.net_cashflow'), value="$0.0M")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Cashflow trend chart
    st.subheader(f"📈 {t('finance.cash_flow_trend')}")
    try:
        with st.spinner(t('common.loading')):
            trend_data = db.get_cashflow_trend(months=months)
            display_cashflow_trend_chart(trend_data, months)
    except Exception as e:
        st.error(f"{t('messages.error_occurred')}: {e}")
        import traceback
        with st.expander("Show Error Details"):
            st.code(traceback.format_exc())
    
    st.markdown("---")
    
    # Income vs Expense comparison
    st.subheader(f"📊 {t('finance.income_vs_expense_comparison')}")
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
    st.subheader(f"💳 {t('finance.recent_transactions')}")
    try:
        with st.spinner(t('common.loading')):
            # Get more transactions for pagination (limit increased to support pagination)
            transactions = db.get_recent_transactions(limit=200)
            
            if not transactions:
                st.info(t('common.no_data'))
            else:
                # Pagination
                items_per_page = 20
                total_pages = (len(transactions) + items_per_page - 1) // items_per_page if transactions else 1
                
                # Page selector
                col_page1, col_page2, col_page3 = st.columns([1, 1, 6])
                with col_page1:
                    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1, key="tx_page")
                with col_page2:
                    st.write("")  # Spacer
                    st.caption(f"of {total_pages}")
                with col_page3:
                    st.caption(f"Showing {len(transactions)} total transaction(s)")
                
                # Calculate pagination
                start = (page - 1) * items_per_page
                end = start + items_per_page
                display_transactions = transactions[start:end]
                
                # Initialize delete confirmation state (only for displayed transactions)
                for tx in display_transactions:
                    if f'confirm_delete_tx_{tx.id}' not in st.session_state:
                        st.session_state[f'confirm_delete_tx_{tx.id}'] = False
                
                # Create table header using columns
                st.markdown("---")
                header_cols = st.columns([2, 1.5, 2, 1.5, 2, 3, 1, 1])
                with header_cols[0]:
                    st.markdown("**Date**")
                with header_cols[1]:
                    st.markdown("**Type**")
                with header_cols[2]:
                    st.markdown("**Category**")
                with header_cols[3]:
                    st.markdown("**Amount**")
                with header_cols[4]:
                    st.markdown("**Asset**")
                with header_cols[5]:
                    st.markdown("**Description**")
                with header_cols[6]:
                    st.markdown("**Edit**")
                with header_cols[7]:
                    st.markdown("**Delete**")
                
                st.markdown("---")
                
                # Display each transaction as a row
                for tx in display_transactions:
                    # Create columns for this row
                    row_cols = st.columns([2, 1.5, 2, 1.5, 2, 3, 1, 1])
                    
                    with row_cols[0]:
                        st.write(tx.transaction_date.strftime("%Y-%m-%d"))
                    
                    with row_cols[1]:
                        type_display = tx.transaction_type.value.replace('_', ' ').title()
                        # Color code: Income = green, Expense = red
                        if tx.transaction_type == TransactionType.INCOME:
                            st.markdown(f'<span style="color: #2ecc71;">{type_display}</span>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<span style="color: #e74c3c;">{type_display}</span>', unsafe_allow_html=True)
                    
                    with row_cols[2]:
                        category = tx.category or (tx.expense_category.value.replace('_', ' ').title() if tx.expense_category else "-")
                        st.write(category)
                    
                    with row_cols[3]:
                        amount_str = f"${abs(float(tx.amount)):,.2f}"
                        if tx.transaction_type == TransactionType.INCOME:
                            st.markdown(f'<span style="color: #2ecc71; font-weight: bold;">{amount_str}</span>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<span style="color: #e74c3c; font-weight: bold;">{amount_str}</span>', unsafe_allow_html=True)
                    
                    with row_cols[4]:
                        asset_name = tx.asset.name if tx.asset else "-"
                        st.write(asset_name)
                    
                    with row_cols[5]:
                        desc_short = tx.description[:60] + "..." if len(tx.description) > 60 else tx.description
                        # Use markdown with title attribute for tooltip on hover
                        if len(tx.description) > 60:
                            st.markdown(f'<span title="{tx.description}">{desc_short}</span>', unsafe_allow_html=True)
                        else:
                            st.write(desc_short)
                    
                    with row_cols[6]:
                        if st.button("✏️", key=f"edit_tx_{tx.id}", help="Edit this transaction", use_container_width=True):
                            st.session_state.edit_transaction_id = tx.id
                            st.rerun()
                    
                    with row_cols[7]:
                        if st.button("🗑️", key=f"delete_tx_{tx.id}", help="Delete this transaction", use_container_width=True):
                            st.session_state[f'confirm_delete_tx_{tx.id}'] = True
                            st.rerun()
                    
                    # Delete confirmation dialog (displayed below the row)
                    if st.session_state.get(f'confirm_delete_tx_{tx.id}', False):
                        st.warning(f"⚠️ Are you sure you want to delete this transaction: **{tx.description[:50]}**? This action cannot be undone.")
                        confirm_col1, confirm_col2 = st.columns(2)
                        with confirm_col1:
                            if st.button("✅ Yes, Delete", key=f"confirm_yes_tx_{tx.id}", type="primary", use_container_width=True):
                                try:
                                    db.delete_transaction(tx.id)
                                    st.success(f"✅ Transaction deleted successfully!")
                                    del st.session_state[f'confirm_delete_tx_{tx.id}']
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error deleting transaction: {str(e)}")
                        
                        with confirm_col2:
                            if st.button("❌ Cancel", key=f"confirm_no_tx_{tx.id}", use_container_width=True):
                                del st.session_state[f'confirm_delete_tx_{tx.id}']
                                st.rerun()
                    
                    st.markdown("---")
                
                # Summary stats (based on all transactions, not just current page)
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                total_income = sum(abs(float(tx.amount)) for tx in transactions if tx.transaction_type == TransactionType.INCOME)
                total_expense = sum(abs(float(tx.amount)) for tx in transactions if tx.transaction_type == TransactionType.EXPENSE)
                
                with col1:
                    st.metric("Total Income", f"${total_income:,.2f}")
                with col2:
                    st.metric("Total Expense", f"${total_expense:,.2f}")
                with col3:
                    st.metric("Net", f"${total_income - total_expense:,.2f}")
    except Exception as e:
        st.error(f"Error loading recent transactions: {e}")
        import traceback
        with st.expander("Show Error Details"):
            st.code(traceback.format_exc())
    
    st.markdown("---")
    st.markdown("*© 2025 Gilbert Industrial Real Estate Development | Brisbane, Queensland, Australia*")


if __name__ == "__main__":
    main()
