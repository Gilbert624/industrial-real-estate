"""
Application Theme Configuration
应用主题配置 - 基于 Shadcn UI 设计系统
"""

import streamlit as st


def apply_global_theme():
    """应用全局主题样式"""
    st.markdown("""
    <style>
    /* ========== 全局基础样式 ========== */
    
    /* 主内容区域 */
    .main {
        background-color: #fafafa;
        padding: 2rem;
    }
    
    .main .block-container {
        max-width: 100%;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    /* ========== 标题样式 ========== */
    
    h1 {
        color: #030213;
        font-weight: 600;
        font-size: 2rem;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }
    
    h2 {
        color: #030213;
        font-weight: 600;
        font-size: 1.5rem;
        letter-spacing: -0.01em;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #1f2937;
        font-weight: 600;
        font-size: 1.125rem;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* ========== 卡片样式 ========== */
    
    .stMetric {
        background: white;
        padding: 1.25rem;
        border-radius: 0.75rem;
        border: 1px solid rgba(0, 0, 0, 0.06);
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }
    
    .stMetric label {
        color: #717182;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #030213;
        font-size: 1.875rem;
        font-weight: 600;
    }
    
    .stMetric [data-testid="stMetricDelta"] {
        font-size: 0.875rem;
    }
    
    /* ========== 按钮样式 ========== */
    
    .stButton > button {
        background-color: #030213;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.625rem 1.25rem;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.15s ease;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    
    .stButton > button:hover {
        background-color: #1f2937;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:active {
        transform: translateY(1px);
    }
    
    /* 次要按钮 */
    .stButton > button[kind="secondary"] {
        background-color: white;
        color: #030213;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #f9fafb;
        border-color: rgba(0, 0, 0, 0.2);
    }
    
    /* ========== 输入框样式 ========== */
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea textarea,
    .stSelectbox > div > div > select {
        background-color: white;
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 0.5rem;
        padding: 0.625rem 0.875rem;
        font-size: 0.875rem;
        color: #030213;
        transition: all 0.15s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #030213;
        box-shadow: 0 0 0 3px rgba(3, 2, 19, 0.1);
        outline: none;
    }
    
    /* ========== 表格样式 ========== */
    
    .dataframe {
        background: white;
        border-radius: 0.75rem;
        border: 1px solid rgba(0, 0, 0, 0.06);
        overflow: hidden;
    }
    
    .dataframe thead tr th {
        background-color: #f9fafb;
        color: #717182;
        font-weight: 600;
        font-size: 0.813rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 1rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    }
    
    .dataframe tbody tr td {
        padding: 0.875rem 1rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.04);
        color: #1f2937;
        font-size: 0.875rem;
    }
    
    .dataframe tbody tr:last-child td {
        border-bottom: none;
    }
    
    .dataframe tbody tr:hover {
        background-color: #f9fafb;
    }
    
    /* ========== Tabs 样式 ========== */
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #717182;
        font-weight: 500;
        font-size: 0.875rem;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem 0.5rem 0 0;
        border: none;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f9fafb;
        color: #030213;
    }
    
    .stTabs [aria-selected="true"] {
        color: #030213;
        font-weight: 600;
        background-color: white;
        border-bottom: 2px solid #030213;
    }
    
    /* ========== Expander 样式 ========== */
    
    .streamlit-expanderHeader {
        background-color: white;
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: 0.5rem;
        padding: 0.875rem 1rem;
        font-weight: 500;
        color: #030213;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #f9fafb;
        border-color: rgba(0, 0, 0, 0.1);
    }
    
    .streamlit-expanderContent {
        background-color: white;
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-top: none;
        border-radius: 0 0 0.5rem 0.5rem;
        padding: 1rem;
    }
    
    /* ========== 警告/信息框样式 ========== */
    
    .stAlert {
        background-color: white;
        border-radius: 0.75rem;
        border: 1px solid rgba(0, 0, 0, 0.06);
        padding: 1rem;
    }
    
    .stSuccess {
        border-left: 4px solid #10b981;
        background-color: #f0fdf4;
    }
    
    .stInfo {
        border-left: 4px solid #3b82f6;
        background-color: #eff6ff;
    }
    
    .stWarning {
        border-left: 4px solid #f59e0b;
        background-color: #fffbeb;
    }
    
    .stError {
        border-left: 4px solid #ef4444;
        background-color: #fef2f2;
    }
    
    /* ========== Plotly 图表样式 ========== */
    
    .js-plotly-plot {
        border-radius: 0.75rem;
        background: white;
        border: 1px solid rgba(0, 0, 0, 0.06);
        padding: 1rem;
    }
    
    /* ========== 分隔线 ========== */
    
    hr {
        border: none;
        border-top: 1px solid rgba(0, 0, 0, 0.06);
        margin: 2rem 0;
    }
    
    /* ========== 字幕文字 ========== */
    
    .stCaption {
        color: #9ca3af;
        font-size: 0.813rem;
    }
    
    /* ========== 隐藏 Streamlit 元素 ========== */
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ========== 响应式 ========== */
    
    @media (max-width: 768px) {
        .main {
            padding: 1rem;
        }
        
        h1 {
            font-size: 1.5rem;
        }
        
        .stMetric {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def get_color_palette():
    """返回颜色调色板"""
    return {
        'primary': '#030213',
        'primary_foreground': '#ffffff',
        'secondary': '#f9fafb',
        'secondary_foreground': '#030213',
        'muted': '#717182',
        'muted_foreground': '#9ca3af',
        'border': 'rgba(0, 0, 0, 0.06)',
        'success': '#10b981',
        'info': '#3b82f6',
        'warning': '#f59e0b',
        'error': '#ef4444'
    }


# ========== 向后兼容函数 ==========

def generate_css(theme_name='light'):
    """
    生成主题CSS（向后兼容函数）
    注意：新设计系统统一使用浅色主题，theme_name 参数保留以兼容旧代码
    """
    return """
    <style>
    /* ========== 全局基础样式 ========== */
    
    /* 主内容区域 */
    .main {
        background-color: #fafafa;
        padding: 2rem;
    }
    
    .main .block-container {
        max-width: 100%;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    /* ========== 标题样式 ========== */
    
    h1 {
        color: #030213;
        font-weight: 600;
        font-size: 2rem;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }
    
    h2 {
        color: #030213;
        font-weight: 600;
        font-size: 1.5rem;
        letter-spacing: -0.01em;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #1f2937;
        font-weight: 600;
        font-size: 1.125rem;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* ========== 卡片样式 ========== */
    
    .stMetric {
        background: white;
        padding: 1.25rem;
        border-radius: 0.75rem;
        border: 1px solid rgba(0, 0, 0, 0.06);
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }
    
    .stMetric label {
        color: #717182;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #030213;
        font-size: 1.875rem;
        font-weight: 600;
    }
    
    .stMetric [data-testid="stMetricDelta"] {
        font-size: 0.875rem;
    }
    
    /* ========== 按钮样式 ========== */
    
    .stButton > button {
        background-color: #030213;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.625rem 1.25rem;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.15s ease;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    
    .stButton > button:hover {
        background-color: #1f2937;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:active {
        transform: translateY(1px);
    }
    
    /* 次要按钮 */
    .stButton > button[kind="secondary"] {
        background-color: white;
        color: #030213;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #f9fafb;
        border-color: rgba(0, 0, 0, 0.2);
    }
    
    /* ========== 输入框样式 ========== */
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea textarea,
    .stSelectbox > div > div > select {
        background-color: white;
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 0.5rem;
        padding: 0.625rem 0.875rem;
        font-size: 0.875rem;
        color: #030213;
        transition: all 0.15s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #030213;
        box-shadow: 0 0 0 3px rgba(3, 2, 19, 0.1);
        outline: none;
    }
    
    /* ========== 表格样式 ========== */
    
    .dataframe {
        background: white;
        border-radius: 0.75rem;
        border: 1px solid rgba(0, 0, 0, 0.06);
        overflow: hidden;
    }
    
    .dataframe thead tr th {
        background-color: #f9fafb;
        color: #717182;
        font-weight: 600;
        font-size: 0.813rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 1rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    }
    
    .dataframe tbody tr td {
        padding: 0.875rem 1rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.04);
        color: #1f2937;
        font-size: 0.875rem;
    }
    
    .dataframe tbody tr:last-child td {
        border-bottom: none;
    }
    
    .dataframe tbody tr:hover {
        background-color: #f9fafb;
    }
    
    /* ========== Tabs 样式 ========== */
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #717182;
        font-weight: 500;
        font-size: 0.875rem;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem 0.5rem 0 0;
        border: none;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f9fafb;
        color: #030213;
    }
    
    .stTabs [aria-selected="true"] {
        color: #030213;
        font-weight: 600;
        background-color: white;
        border-bottom: 2px solid #030213;
    }
    
    /* ========== Expander 样式 ========== */
    
    .streamlit-expanderHeader {
        background-color: white;
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: 0.5rem;
        padding: 0.875rem 1rem;
        font-weight: 500;
        color: #030213;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #f9fafb;
        border-color: rgba(0, 0, 0, 0.1);
    }
    
    .streamlit-expanderContent {
        background-color: white;
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-top: none;
        border-radius: 0 0 0.5rem 0.5rem;
        padding: 1rem;
    }
    
    /* ========== 警告/信息框样式 ========== */
    
    .stAlert {
        background-color: white;
        border-radius: 0.75rem;
        border: 1px solid rgba(0, 0, 0, 0.06);
        padding: 1rem;
    }
    
    .stSuccess {
        border-left: 4px solid #10b981;
        background-color: #f0fdf4;
    }
    
    .stInfo {
        border-left: 4px solid #3b82f6;
        background-color: #eff6ff;
    }
    
    .stWarning {
        border-left: 4px solid #f59e0b;
        background-color: #fffbeb;
    }
    
    .stError {
        border-left: 4px solid #ef4444;
        background-color: #fef2f2;
    }
    
    /* ========== Plotly 图表样式 ========== */
    
    .js-plotly-plot {
        border-radius: 0.75rem;
        background: white;
        border: 1px solid rgba(0, 0, 0, 0.06);
        padding: 1rem;
    }
    
    /* ========== 分隔线 ========== */
    
    hr {
        border: none;
        border-top: 1px solid rgba(0, 0, 0, 0.06);
        margin: 2rem 0;
    }
    
    /* ========== 字幕文字 ========== */
    
    .stCaption {
        color: #9ca3af;
        font-size: 0.813rem;
    }
    
    /* ========== 隐藏 Streamlit 元素 ========== */
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ========== 响应式 ========== */
    
    @media (max-width: 768px) {
        .main {
            padding: 1rem;
        }
        
        h1 {
            font-size: 1.5rem;
        }
        
        .stMetric {
            padding: 1rem;
        }
    }
    </style>
    """


# 向后兼容的常量（保留以避免导入错误）
LIGHT_THEME = {
    'primary': '#030213',
    'bg_primary': '#ffffff',
    'text_primary': '#030213'
}

DARK_THEME = {
    'primary': '#030213',
    'bg_primary': '#0f172a',
    'text_primary': '#f8fafc'
}
