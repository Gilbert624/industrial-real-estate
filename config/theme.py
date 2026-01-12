"""
UI Theme Configuration
Professional industrial real estate platform styling
"""

# ==================== Color Palettes ====================

LIGHT_THEME = {
    'name': 'Professional Light',
    
    # Primary Colors
    'primary': '#0A4D8C',          # Deep Professional Blue
    'primary_dark': '#083A6B',     # Darker Blue
    'primary_light': '#1A6BB5',    # Lighter Blue
    
    # Secondary Colors
    'secondary': '#475569',        # Slate Grey
    'secondary_light': '#64748B',  # Light Slate
    'secondary_dark': '#334155',   # Dark Slate
    
    # Accent Colors
    'accent': '#0EA5E9',           # Sky Blue (for highlights)
    'accent_success': '#10B981',   # Green (positive metrics)
    'accent_warning': '#F59E0B',   # Amber (warnings)
    'accent_danger': '#EF4444',    # Red (alerts)
    
    # Backgrounds
    'bg_primary': '#FFFFFF',       # Main background
    'bg_secondary': '#F8FAFC',     # Secondary background
    'bg_tertiary': '#F1F5F9',      # Card backgrounds
    'bg_sidebar': '#F8FAFC',       # Light sidebar (matching bg_secondary for consistency)
    
    # Text Colors
    'text_primary': '#0F172A',     # Main text
    'text_secondary': '#475569',   # Secondary text
    'text_tertiary': '#94A3B8',    # Tertiary text
    'text_inverse': '#FFFFFF',     # Text on dark backgrounds
    
    # Borders
    'border_light': '#E2E8F0',     # Light borders
    'border_medium': '#CBD5E1',    # Medium borders
    'border_dark': '#94A3B8',      # Dark borders
    
    # Surfaces
    'surface_raised': '#FFFFFF',   # Elevated surfaces
    'surface_overlay': 'rgba(15, 23, 42, 0.5)',  # Overlays
}

DARK_THEME = {
    'name': 'Professional Dark',
    
    # Primary Colors
    'primary': '#3B82F6',          # Bright Blue
    'primary_dark': '#2563EB',     # Darker Blue
    'primary_light': '#60A5FA',    # Lighter Blue
    
    # Secondary Colors
    'secondary': '#64748B',        # Slate
    'secondary_light': '#94A3B8',  # Light Slate
    'secondary_dark': '#475569',   # Dark Slate
    
    # Accent Colors
    'accent': '#0EA5E9',           # Sky Blue
    'accent_success': '#10B981',   # Green
    'accent_warning': '#F59E0B',   # Amber
    'accent_danger': '#EF4444',    # Red
    
    # Backgrounds
    'bg_primary': '#0F172A',       # Main background
    'bg_secondary': '#1E293B',     # Secondary background
    'bg_tertiary': '#334155',      # Card backgrounds
    'bg_sidebar': '#020617',       # Darker sidebar
    
    # Text Colors
    'text_primary': '#F8FAFC',     # Main text
    'text_secondary': '#CBD5E1',   # Secondary text
    'text_tertiary': '#64748B',    # Tertiary text
    'text_inverse': '#0F172A',     # Text on light backgrounds
    
    # Borders
    'border_light': '#334155',     # Light borders
    'border_medium': '#475569',    # Medium borders
    'border_dark': '#64748B',      # Dark borders
    
    # Surfaces
    'surface_raised': '#1E293B',   # Elevated surfaces
    'surface_overlay': 'rgba(0, 0, 0, 0.7)',  # Overlays
}

# ==================== Typography ====================

TYPOGRAPHY = {
    # Font Families
    'font_primary': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    'font_mono': '"SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace',
    'font_display': '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
    
    # Font Sizes
    'text_xs': '0.75rem',      # 12px
    'text_sm': '0.875rem',     # 14px
    'text_base': '1rem',       # 16px
    'text_lg': '1.125rem',     # 18px
    'text_xl': '1.25rem',      # 20px
    'text_2xl': '1.5rem',      # 24px
    'text_3xl': '1.875rem',    # 30px
    'text_4xl': '2.25rem',     # 36px
    
    # Font Weights
    'weight_normal': '400',
    'weight_medium': '500',
    'weight_semibold': '600',
    'weight_bold': '700',
    
    # Line Heights
    'leading_tight': '1.25',
    'leading_normal': '1.5',
    'leading_relaxed': '1.75',
}

# ==================== Spacing ====================

SPACING = {
    'xs': '0.25rem',   # 4px
    'sm': '0.5rem',    # 8px
    'md': '1rem',      # 16px
    'lg': '1.5rem',    # 24px
    'xl': '2rem',      # 32px
    '2xl': '3rem',     # 48px
    '3xl': '4rem',     # 64px
}

# ==================== Border Radius ====================

RADIUS = {
    'none': '0',
    'sm': '0.25rem',   # 4px
    'md': '0.5rem',    # 8px
    'lg': '0.75rem',   # 12px
    'xl': '1rem',      # 16px
    '2xl': '1.5rem',   # 24px
    'full': '9999px',
}

# ==================== Shadows ====================

SHADOWS = {
    'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
}

# ==================== Component Styles ====================

COMPONENTS = {
    'card': {
        'padding': SPACING['lg'],
        'border_radius': RADIUS['lg'],
        'shadow': SHADOWS['md'],
    },
    
    'button_primary': {
        'padding': f"{SPACING['sm']} {SPACING['lg']}",
        'border_radius': RADIUS['md'],
        'font_weight': TYPOGRAPHY['weight_semibold'],
    },
    
    'input': {
        'padding': SPACING['md'],
        'border_radius': RADIUS['md'],
        'border_width': '1px',
    },
    
    'sidebar': {
        'width': '280px',
        'padding': SPACING['lg'],
    },
}

# ==================== Helper Functions ====================

def get_theme(theme_name='light'):
    """Get theme configuration"""
    return LIGHT_THEME if theme_name == 'light' else DARK_THEME

def generate_css(theme_name='light'):
    """Generate complete CSS for the theme"""
    theme = get_theme(theme_name)
    
    css = f"""
    <style>
        /* ==================== Global Styles ==================== */
        
        :root {{
            --primary: {theme['primary']};
            --primary-dark: {theme['primary_dark']};
            --primary-light: {theme['primary_light']};
            --secondary: {theme['secondary']};
            --accent: {theme['accent']};
            --bg-primary: {theme['bg_primary']};
            --bg-secondary: {theme['bg_secondary']};
            --bg-tertiary: {theme['bg_tertiary']};
            --text-primary: {theme['text_primary']};
            --text-secondary: {theme['text_secondary']};
            --border-light: {theme['border_light']};
        }}
        
        /* Main Background */
        .main {{
            background-color: {theme['bg_secondary']};
            font-family: {TYPOGRAPHY['font_primary']};
            color: {theme['text_primary']};
        }}
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background: {theme['bg_sidebar']};
            border-right: 1px solid {theme['border_light']};
        }}
        
        [data-testid="stSidebar"] .css-1d391kg {{
            padding-top: {SPACING['xl']};
        }}
        
        /* Sidebar Text Elements */
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] span {{
            color: {theme['text_primary']};
        }}
        
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown {{
            color: {theme['text_secondary']};
        }}
        
        /* Sidebar Headers */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {{
            color: {theme['text_primary']};
        }}
        
        /* Headers */
        h1, h2, h3 {{
            color: {theme['text_primary']};
            font-weight: {TYPOGRAPHY['weight_bold']};
            letter-spacing: -0.02em;
        }}
        
        h1 {{
            font-size: {TYPOGRAPHY['text_4xl']};
            margin-bottom: {SPACING['lg']};
        }}
        
        h2 {{
            font-size: {TYPOGRAPHY['text_2xl']};
            margin-bottom: {SPACING['md']};
        }}
        
        h3 {{
            font-size: {TYPOGRAPHY['text_xl']};
            margin-bottom: {SPACING['sm']};
            color: {theme['text_secondary']};
        }}
        
        /* Cards & Containers */
        .element-container {{
            background: transparent;
        }}
        
        div.stMetric {{
            background: {theme['surface_raised']};
            padding: {SPACING['lg']};
            border-radius: {RADIUS['lg']};
            border: 1px solid {theme['border_light']};
            box-shadow: {SHADOWS['sm']};
            transition: all 0.3s ease;
        }}
        
        div.stMetric:hover {{
            box-shadow: {SHADOWS['md']};
            transform: translateY(-2px);
        }}
        
        /* Metric Labels */
        div.stMetric label {{
            color: {theme['text_secondary']};
            font-size: {TYPOGRAPHY['text_sm']};
            font-weight: {TYPOGRAPHY['weight_medium']};
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        /* Metric Values */
        div.stMetric [data-testid="stMetricValue"] {{
            color: {theme['primary']};
            font-size: {TYPOGRAPHY['text_3xl']};
            font-weight: {TYPOGRAPHY['weight_bold']};
        }}
        
        /* Buttons */
        .stButton > button {{
            background: {theme['primary']};
            color: {theme['text_inverse']};
            border: none;
            border-radius: {RADIUS['md']};
            padding: {SPACING['sm']} {SPACING['lg']};
            font-weight: {TYPOGRAPHY['weight_semibold']};
            font-size: {TYPOGRAPHY['text_base']};
            transition: all 0.2s ease;
            box-shadow: {SHADOWS['sm']};
        }}
        
        .stButton > button:hover {{
            background: {theme['primary_dark']};
            box-shadow: {SHADOWS['md']};
            transform: translateY(-1px);
        }}
        
        /* Secondary Buttons */
        .stButton > button[kind="secondary"] {{
            background: {theme['bg_tertiary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border_medium']};
        }}
        
        .stButton > button[kind="secondary"]:hover {{
            background: {theme['secondary']};
            color: {theme['text_inverse']};
        }}
        
        /* Input Fields */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {{
            background: {theme['surface_raised']};
            border: 1px solid {theme['border_light']};
            border-radius: {RADIUS['md']};
            padding: {SPACING['md']};
            color: {theme['text_primary']};
            font-size: {TYPOGRAPHY['text_base']};
        }}
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {{
            border-color: {theme['primary']};
            box-shadow: 0 0 0 3px {theme['primary']}22;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: {SPACING['sm']};
            background: {theme['bg_tertiary']};
            padding: {SPACING['sm']};
            border-radius: {RADIUS['lg']};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            border: none;
            border-radius: {RADIUS['md']};
            color: {theme['text_secondary']};
            font-weight: {TYPOGRAPHY['weight_medium']};
            padding: {SPACING['sm']} {SPACING['lg']};
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: {theme['surface_raised']};
            color: {theme['text_primary']};
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {theme['primary']};
            color: {theme['text_inverse']};
        }}
        
        /* Expanders */
        .streamlit-expanderHeader {{
            background: {theme['surface_raised']};
            border: 1px solid {theme['border_light']};
            border-radius: {RADIUS['md']};
            color: {theme['text_primary']};
            font-weight: {TYPOGRAPHY['weight_semibold']};
        }}
        
        .streamlit-expanderHeader:hover {{
            border-color: {theme['primary']};
        }}
        
        /* DataFrames */
        .stDataFrame {{
            border: 1px solid {theme['border_light']};
            border-radius: {RADIUS['lg']};
            overflow: hidden;
        }}
        
        /* Plotly Charts */
        .js-plotly-plot {{
            border-radius: {RADIUS['lg']};
            box-shadow: {SHADOWS['sm']};
        }}
        
        /* Success/Warning/Error Messages */
        .stSuccess {{
            background: {theme['accent_success']}22;
            border-left: 4px solid {theme['accent_success']};
            border-radius: {RADIUS['md']};
            padding: {SPACING['md']};
        }}
        
        .stWarning {{
            background: {theme['accent_warning']}22;
            border-left: 4px solid {theme['accent_warning']};
            border-radius: {RADIUS['md']};
            padding: {SPACING['md']};
        }}
        
        .stError {{
            background: {theme['accent_danger']}22;
            border-left: 4px solid {theme['accent_danger']};
            border-radius: {RADIUS['md']};
            padding: {SPACING['md']};
        }}
        
        .stInfo {{
            background: {theme['accent']}22;
            border-left: 4px solid {theme['accent']};
            border-radius: {RADIUS['md']};
            padding: {SPACING['md']};
        }}
        
        /* Loading Spinner */
        .stSpinner > div {{
            border-top-color: {theme['primary']};
        }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {theme['bg_secondary']};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {theme['border_medium']};
            border-radius: {RADIUS['full']};
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {theme['secondary']};
        }}
        
        /* Progress Bar */
        .stProgress > div > div > div {{
            background: {theme['primary']};
        }}
        
        /* File Uploader */
        [data-testid="stFileUploader"] {{
            background: {theme['surface_raised']};
            border: 2px dashed {theme['border_medium']};
            border-radius: {RADIUS['lg']};
            padding: {SPACING['xl']};
        }}
        
        /* Download Button */
        .stDownloadButton > button {{
            background: {theme['accent_success']};
        }}
        
        .stDownloadButton > button:hover {{
            background: {theme['accent_success']}dd;
        }}
        
        /* ==================== Custom Utility Classes ==================== */
        
        .bento-card {{
            background: {theme['surface_raised']};
            border: 1px solid {theme['border_light']};
            border-radius: {RADIUS['xl']};
            padding: {SPACING['xl']};
            box-shadow: {SHADOWS['md']};
            transition: all 0.3s ease;
        }}
        
        .bento-card:hover {{
            box-shadow: {SHADOWS['lg']};
            transform: translateY(-4px);
        }}
        
        .bento-grid {{
            display: grid;
            gap: {SPACING['lg']};
            margin: {SPACING['lg']} 0;
        }}
        
        .stat-badge {{
            display: inline-block;
            padding: {SPACING['xs']} {SPACING['md']};
            background: {theme['primary']}22;
            color: {theme['primary']};
            border-radius: {RADIUS['full']};
            font-size: {TYPOGRAPHY['text_sm']};
            font-weight: {TYPOGRAPHY['weight_semibold']};
        }}
        
        .section-divider {{
            height: 1px;
            background: linear-gradient(90deg, transparent, {theme['border_medium']}, transparent);
            margin: {SPACING['xl']} 0;
        }}
        
        /* ==================== Language Switcher ==================== */
        .language-switcher {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: {theme['surface_raised']};
            border: 1px solid {theme['border_light']};
            border-radius: {RADIUS['md']};
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: {TYPOGRAPHY['text_sm']};
            font-weight: {TYPOGRAPHY['weight_medium']};
            color: {theme['text_primary']};
            box-shadow: {SHADOWS['sm']};
        }}
        
        .language-switcher:hover {{
            border-color: {theme['primary']};
            box-shadow: {SHADOWS['md']};
            transform: translateY(-1px);
        }}
        
        .language-switcher-icon {{
            font-size: 1rem;
            display: inline-flex;
            align-items: center;
            color: {theme['text_secondary']};
        }}
        
        .language-switcher-select {{
            background: transparent;
            border: none;
            color: {theme['text_primary']};
            font-size: {TYPOGRAPHY['text_sm']};
            font-weight: {TYPOGRAPHY['weight_medium']};
            cursor: pointer;
            outline: none;
            appearance: none;
            -webkit-appearance: none;
            -moz-appearance: none;
            padding: 0;
            margin: 0;
        }}
        
        /* Top Navigation Bar */
        .top-nav-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: {SPACING['md']} {SPACING['xl']};
            background: {theme['surface_raised']};
            border-bottom: 1px solid {theme['border_light']};
            margin-bottom: {SPACING['lg']};
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: {SHADOWS['sm']};
        }}
        
        .nav-controls {{
            display: flex;
            align-items: center;
            gap: {SPACING['md']};
        }}
        
        /* ==================== Language Switcher Animations ==================== */
        
        .language-switcher {{
            transition: all 0.3s ease;
        }}
        
        .language-switcher:hover {{
            transform: translateY(-1px);
            box-shadow: {SHADOWS['md']};
        }}
        
        /* Toast notification for language change */
        .stToast {{
            background: {theme['surface_raised']};
            border: 1px solid {theme['border_light']};
            border-radius: {RADIUS['lg']};
            box-shadow: {SHADOWS['lg']};
        }}
        
        /* Smooth content transition */
        .main .block-container {{
            animation: fadeIn 0.3s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{
                opacity: 0.8;
                transform: translateY(10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        /* Language button hover effects */
        .stButton > button[key^="lang_"] {{
            transition: all 0.2s ease;
        }}
        
        .stButton > button[key^="lang_"]:hover {{
            transform: scale(1.05);
        }}
        
        /* Selectbox smooth transitions */
        div[data-testid="stSelectbox"] {{
            transition: all 0.2s ease;
        }}
    </style>
    """
    
    return css
