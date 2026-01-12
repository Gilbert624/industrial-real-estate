"""
Professional Chart Styling for Plotly
Consistent with industrial real estate platform theme
"""

import plotly.graph_objects as go
from config.theme import LIGHT_THEME, DARK_THEME

def get_chart_layout(theme='light', title='', height=400):
    """
    Get professional chart layout configuration
    
    Args:
        theme: 'light' or 'dark'
        title: Chart title
        height: Chart height in pixels
        
    Returns:
        Dictionary with layout configuration
    """
    colors = LIGHT_THEME if theme == 'light' else DARK_THEME
    
    layout = {
        'title': {
            'text': title,
            'font': {
                'size': 18,
                'color': colors['text_primary'],
                'family': 'Inter, -apple-system, sans-serif',
                'weight': 700
            },
            'x': 0,
            'xanchor': 'left'
        },
        'paper_bgcolor': colors['surface_raised'],
        'plot_bgcolor': colors['bg_secondary'],
        'font': {
            'family': 'Inter, -apple-system, sans-serif',
            'size': 12,
            'color': colors['text_secondary']
        },
        'height': height,
        'margin': {'l': 60, 'r': 40, 't': 60, 'b': 60},
        'hovermode': 'x unified',
        'hoverlabel': {
            'bgcolor': colors['surface_raised'],
            'bordercolor': colors['border_medium'],
            'font': {
                'size': 13,
                'color': colors['text_primary']
            }
        },
        'xaxis': {
            'gridcolor': colors['border_light'],
            'linecolor': colors['border_medium'],
            'zerolinecolor': colors['border_medium'],
            'tickfont': {'color': colors['text_secondary']},
            'title': {'font': {'color': colors['text_primary'], 'size': 14}}
        },
        'yaxis': {
            'gridcolor': colors['border_light'],
            'linecolor': colors['border_medium'],
            'zerolinecolor': colors['border_medium'],
            'tickfont': {'color': colors['text_secondary']},
            'title': {'font': {'color': colors['text_primary'], 'size': 14}}
        },
        'legend': {
            'bgcolor': colors['surface_raised'],
            'bordercolor': colors['border_light'],
            'borderwidth': 1,
            'font': {'color': colors['text_primary']}
        }
    }
    
    return layout

# Professional color schemes
CHART_COLORS = {
    'primary': ['#0A4D8C', '#1A6BB5', '#3B82F6', '#60A5FA', '#93C5FD'],
    'success': ['#10B981', '#34D399', '#6EE7B7', '#A7F3D0'],
    'warning': ['#F59E0B', '#FBBF24', '#FCD34D', '#FDE68A'],
    'danger': ['#EF4444', '#F87171', '#FCA5A5', '#FECACA'],
    'multi': ['#0A4D8C', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'],
    'gradient_blue': ['#0A4D8C', '#1E40AF', '#1D4ED8', '#2563EB', '#3B82F6'],
    'gradient_green': ['#047857', '#059669', '#10B981', '#34D399', '#6EE7B7']
}

def style_bar_chart(fig, theme='light', color_scheme='primary'):
    """Apply professional styling to bar charts"""
    colors = CHART_COLORS[color_scheme]
    
    fig.update_traces(
        marker=dict(
            color=colors[0],
            line=dict(color=colors[1], width=1.5)
        ),
        hovertemplate='<b>%{x}</b><br>%{y:,.0f}<extra></extra>'
    )
    
    return fig

def style_line_chart(fig, theme='light', color_scheme='primary'):
    """Apply professional styling to line charts"""
    colors = CHART_COLORS[color_scheme]
    
    fig.update_traces(
        line=dict(width=3, color=colors[0]),
        marker=dict(size=8, color=colors[1]),
        hovertemplate='<b>%{x}</b><br>%{y:,.2f}<extra></extra>'
    )
    
    return fig

def style_pie_chart(fig, theme='light'):
    """Apply professional styling to pie charts"""
    
    fig.update_traces(
        marker=dict(
            colors=CHART_COLORS['multi'],
            line=dict(color='white', width=2)
        ),
        textposition='inside',
        textinfo='percent+label',
        textfont=dict(size=12, color='white'),
        hovertemplate='<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>'
    )
    
    return fig

def create_professional_metric_card(value, label, delta=None, delta_color='normal'):
    """
    Create a professional metric display card
    
    Args:
        value: Main value to display
        label: Metric label
        delta: Optional change indicator
        delta_color: 'normal', 'inverse', 'off'
        
    Returns:
        HTML string for metric card
    """
    delta_html = ''
    if delta:
        color = '#10B981' if (delta_color == 'normal' and delta > 0) or (delta_color == 'inverse' and delta < 0) else '#EF4444'
        arrow = '↗' if delta > 0 else '↘'
        delta_html = f'<div style="color: {color}; font-size: 0.875rem; margin-top: 0.5rem;">{arrow} {delta}</div>'
    
    html = f"""
    <div class="bento-card" style="text-align: center; padding: 1.5rem;">
        <div style="color: var(--text-secondary); font-size: 0.875rem; font-weight: 600; 
                    text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">
            {label}
        </div>
        <div style="color: var(--primary); font-size: 2rem; font-weight: 700; line-height: 1;">
            {value}
        </div>
        {delta_html}
    </div>
    """
    
    return html

def apply_professional_theme_to_figure(fig, theme='light'):
    """Apply complete professional theme to any Plotly figure"""
    layout = get_chart_layout(theme)
    fig.update_layout(**layout)
    
    # Add subtle grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=layout['xaxis']['gridcolor'])
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=layout['yaxis']['gridcolor'])
    
    return fig
