"""
Asset Management System - Test Application
A simple Streamlit app to validate the development environment
Developer: Gilbert - Brisbane, QLD
Version: 0.1-dev
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

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
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🏢 Asset Management System")
    st.markdown("**Version:** v0.1-dev")
    st.markdown("**Developer:** Gilbert - Brisbane")
    st.markdown("---")
    st.markdown("#### Navigation")
    st.info("This is a test application to validate the development environment. "
            "Full features will be available in future releases.")
    st.markdown("---")
    if st.button("刷新数据"):
        st.success("数据刷新成功！")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%d %b %Y')}")

# Main content
st.title("🏢 Asset Management System")
st.markdown("### Welcome to Your Industrial Real Estate Portfolio Dashboard")
st.markdown("This test application validates the Streamlit environment and demonstrates "
            "the core UI components for the full asset management system.")

st.markdown("---")

# Metrics section
st.markdown("### 📊 Portfolio Overview")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total Assets",
        value="8",
        delta="3",
        delta_color="normal"
    )

with col2:
    st.metric(
        label="Total Value",
        value="$50M AUD",
        delta="+$8M",
        delta_color="normal"
    )

with col3:
    st.metric(
        label="Active Projects",
        value="3",
        delta="2 in progress",
        delta_color="normal"
    )

st.markdown("---")

# Chart section
st.markdown("### 📈 Portfolio Value Trend (Last 6 Months)")

# Generate test data for the last 6 months
months = []
values = []
start_date = datetime.now() - timedelta(days=180)

for i in range(6):
    month_date = start_date + timedelta(days=30*i)
    months.append(month_date.strftime("%b %Y"))
    # Simulated growth values in millions AUD
    values.append(35 + i*2.5 + (i*0.5))

# Create DataFrame
df = pd.DataFrame({
    'Month': months,
    'Value (M AUD)': values
})

# Create Plotly chart with professional styling
fig = go.Figure()

fig.add_trace(go.Bar(
    x=df['Month'],
    y=df['Value (M AUD)'],
    marker=dict(
        color=df['Value (M AUD)'],
        colorscale='Blues',
        line=dict(color='#1e3a5f', width=1.5)
    ),
    text=df['Value (M AUD)'].apply(lambda x: f'${x:.1f}M'),
    textposition='outside',
    hovertemplate='<b>%{x}</b><br>Value: $%{y:.2f}M AUD<extra></extra>'
))

fig.update_layout(
    title=dict(
        text='Total Portfolio Value by Month',
        font=dict(size=18, color='#1e3a5f', family='Arial')
    ),
    xaxis=dict(
        title='Month',
        titlefont=dict(size=14, color='#2c5282'),
        showgrid=False
    ),
    yaxis=dict(
        title='Value (Million AUD)',
        titlefont=dict(size=14, color='#2c5282'),
        gridcolor='#e2e8f0'
    ),
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=450,
    margin=dict(t=60, b=40, l=60, r=40),
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Footer section
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🎯 Next Steps")
    st.markdown("""
    - Database integration
    - User authentication
    - Real-time data sync
    """)

with col2:
    st.markdown("#### 🔧 Tech Stack")
    st.markdown("""
    - Streamlit
    - Plotly
    - PostgreSQL (planned)
    """)

with col3:
    st.markdown("#### 📍 Location")
    st.markdown("""
    - Brisbane, QLD
    - Sunshine Coast
    - Australia
    """)

st.markdown("---")
st.markdown("*© 2025 Gilbert Industrial Real Estate Development | Brisbane, Queensland, Australia*")
# Add a footer section with contact information
st.markdown("---")
st.markdown("#### 📞 Contact Us")
st.markdown("""
- **Email:** [contact@gilbertire.com](mailto:contact@gilbertire.com)
- **Phone:** +61 4 1234 5678
- **Address:** 123 Main St, Brisbane, QLD 4000
""")
