"""
Custom Sidebar Styling - Modern Professional Design
自定义侧边栏样式 - 现代专业设计
基于 Shadcn UI 设计系统
"""

import streamlit as st


def get_sidebar_css():
    """返回侧边栏CSS样式 - 现代浅色风格"""
    return """
    <style>
    /* ========== 侧边栏主体 ========== */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid rgba(0, 0, 0, 0.08);
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.04);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
        background: #ffffff;
    }
    
    /* ========== Logo 区域 ========== */
    .sidebar-logo {
        text-align: left;
        padding: 1.2rem 1.5rem 1.5rem 1.5rem;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    }
    
    .sidebar-logo h1 {
        color: #030213;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
        line-height: 1.4;
        letter-spacing: -0.02em;
    }
    
    .sidebar-logo p {
        color: #717182;
        font-size: 0.813rem;
        margin: 0.25rem 0 0 0;
        font-weight: 400;
        line-height: 1.5;
    }
    
    /* ========== 导航分组标题 ========== */
    .nav-section {
        color: #717182;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 1rem 1.5rem 0.5rem 1.5rem;
        margin-top: 0.5rem;
    }
    
    .nav-section-desc {
        color: #9ca3af;
        font-size: 0.688rem;
        font-weight: 400;
        padding: 0 1.5rem 0.75rem 1.5rem;
        margin: 0;
        line-height: 1.4;
    }
    
    /* ========== 导航链接 ========== */
    [data-testid="stSidebar"] a {
        color: #4b5563 !important;
        text-decoration: none !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        padding: 0.625rem 1rem !important;
        margin: 0.125rem 0.75rem !important;
        border-radius: 0.5rem !important;
        transition: all 0.15s ease !important;
        display: flex !important;
        align-items: center !important;
        line-height: 1.5 !important;
    }
    
    [data-testid="stSidebar"] a:hover {
        background: #f3f4f6 !important;
        color: #030213 !important;
    }
    
    /* 当前页面高亮 */
    [data-testid="stSidebar"] a[aria-current="page"] {
        background: #030213 !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    
    /* ========== 状态指示器 ========== */
    .status-section {
        margin-top: 1.5rem;
        padding: 1rem 1.5rem;
        background: #f9fafb;
        border-radius: 0.75rem;
        margin-left: 0.75rem;
        margin-right: 0.75rem;
    }
    
    .status-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #717182;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.75rem;
    }
    
    .status-item {
        display: flex;
        align-items: center;
        padding: 0.5rem 0;
        font-size: 0.813rem;
        color: #4b5563;
    }
    
    .status-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .status-indicator.connected {
        background: #10b981;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
    }
    
    .status-indicator.live {
        background: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    
    /* ========== 分隔线 ========== */
    [data-testid="stSidebar"] hr {
        border: none;
        border-top: 1px solid rgba(0, 0, 0, 0.06);
        margin: 1rem 1.5rem;
    }
    
    /* ========== 底部信息 ========== */
    [data-testid="stSidebar"] .stCaption {
        color: #9ca3af !important;
        font-size: 0.75rem !important;
        padding: 0 1.5rem !important;
    }
    
    /* ========== 页面图标前缀 ========== */
    .nav-prefix {
        display: inline-block;
        width: 20px;
        color: #9ca3af;
        font-size: 0.875rem;
        margin-right: 0.5rem;
    }
    
    /* ========== 响应式调整 ========== */
    @media (max-width: 768px) {
        .sidebar-logo h1 {
            font-size: 1.125rem;
        }
        
        [data-testid="stSidebar"] a {
            font-size: 0.813rem !important;
            padding: 0.5rem 0.875rem !important;
        }
    }
    </style>
    """


def render_sidebar_header():
    """渲染侧边栏头部 - 现代简洁风格"""
    st.markdown("""
    <div class="sidebar-logo">
        <h1>Industrial RE</h1>
        <p>Asset Management Platform</p>
    </div>
    """, unsafe_allow_html=True)


def render_nav_section(title, description=""):
    """渲染导航分组标题"""
    st.markdown(f"""
    <div class="nav-section">{title}</div>
    """, unsafe_allow_html=True)
    
    if description:
        st.markdown(f"""
        <div class="nav-section-desc">{description}</div>
        """, unsafe_allow_html=True)


def render_status_panel():
    """渲染状态面板"""
    st.markdown("""
    <div class="status-section">
        <div class="status-title">Status</div>
        <div class="status-item">
            <span class="status-indicator connected"></span>
            Database Connected
        </div>
        <div class="status-item">
            <span class="status-indicator live"></span>
            Displaying Live Data
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_page_config(page_name):
    """获取页面配置"""
    configs = {
        'Dashboard': {
            'title': 'Dashboard | Industrial Real Estate',
            'icon': '▸',
            'layout': 'wide'
        },
        'Assets': {
            'title': 'Assets Portfolio | Industrial Real Estate',
            'icon': '▸',
            'layout': 'wide'
        },
        'Finance': {
            'title': 'Financial Overview | Industrial Real Estate',
            'icon': '▸',
            'layout': 'wide'
        },
        'Projects': {
            'title': 'Project Pipeline | Industrial Real Estate',
            'icon': '▸',
            'layout': 'wide'
        },
        'AI Assistant': {
            'title': 'AI Assistant | Industrial Real Estate',
            'icon': '▸',
            'layout': 'wide'
        },
        'Due Diligence': {
            'title': 'Due Diligence Analysis | Industrial Real Estate',
            'icon': '▸',
            'layout': 'wide'
        },
        'Market Intelligence': {
            'title': 'Market Intelligence | Industrial Real Estate',
            'icon': '▸',
            'layout': 'wide'
        }
    }
    
    return configs.get(page_name, {
        'title': 'Industrial Real Estate Management',
        'icon': '▸',
        'layout': 'wide'
    })
