"""
Language Switcher Component
Smooth language switching without page reload
"""

import streamlit as st
from config.i18n import get_language, set_language, SUPPORTED_LANGUAGES

def render_language_switcher(location='sidebar', show_label=True):
    """
    Render language switcher component
    
    Args:
        location: 'sidebar' or 'main' - where to render the switcher
        show_label: Whether to show the language label
    
    Returns:
        Selected language code
    """
    current_lang = get_language()
    
    # Language options with flags and names
    lang_options = {
        'en': '🇬🇧 English',
        'zh': '🇨🇳 中文'
    }
    
    # Get list of language codes
    lang_codes = list(lang_options.keys())
    
    # Find current index
    try:
        current_index = lang_codes.index(current_lang)
    except ValueError:
        current_index = 0
    
    # Style for the language switcher
    if location == 'sidebar':
        # Compact sidebar version
        st.markdown("""
            <style>
            div[data-testid="stSelectbox"] > div:first-child {
                font-size: 0.9rem;
            }
            .language-switcher {
                background: var(--surface-raised);
                padding: 0.75rem;
                border-radius: 0.5rem;
                border: 1px solid var(--border-light);
                margin-bottom: 1rem;
            }
            .language-switcher label {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-weight: 600;
                color: var(--text-primary);
                font-size: 0.875rem;
            }
            .stSelectbox [data-baseweb="select"] {
                background: var(--bg-secondary);
                border-radius: 0.5rem;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="language-switcher">', unsafe_allow_html=True)
        
        # Use a unique key to force re-render
        if 'language_change_counter' not in st.session_state:
            st.session_state.language_change_counter = 0
        
        selected_lang_label = st.selectbox(
            "🌐 Language" if show_label else "",
            options=lang_codes,
            index=current_index,
            format_func=lambda x: lang_options[x],
            key=f"lang_selector_{st.session_state.language_change_counter}",
            label_visibility="visible" if show_label else "collapsed"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        # Main page version (horizontal pills)
        st.markdown("""
            <style>
            .language-pills {
                display: flex;
                gap: 0.5rem;
                padding: 0.5rem;
                background: var(--bg-tertiary);
                border-radius: 0.75rem;
                width: fit-content;
            }
            .language-pill {
                padding: 0.5rem 1rem;
                border-radius: 0.5rem;
                cursor: pointer;
                transition: all 0.2s ease;
                font-weight: 500;
                font-size: 0.875rem;
            }
            .language-pill.active {
                background: var(--primary);
                color: white;
            }
            .language-pill:not(.active) {
                background: transparent;
                color: var(--text-secondary);
            }
            .language-pill:not(.active):hover {
                background: var(--bg-secondary);
                color: var(--text-primary);
            }
            </style>
        """, unsafe_allow_html=True)
        
        cols = st.columns([1, 1, 3])
        
        selected_lang_label = None
        
        with cols[0]:
            if st.button(
                "🇬🇧 English",
                key="lang_en",
                width='stretch',
                type="primary" if current_lang == 'en' else "secondary"
            ):
                selected_lang_label = 'en'
        
        with cols[1]:
            if st.button(
                "🇨🇳 中文",
                key="lang_zh",
                width='stretch',
                type="primary" if current_lang == 'zh' else "secondary"
            ):
                selected_lang_label = 'zh'
    
    # Handle language change without full page reload
    if selected_lang_label and selected_lang_label != current_lang:
        # Set the new language
        set_language(selected_lang_label)
        
        # Increment counter to force selectbox re-render with new default
        if 'language_change_counter' not in st.session_state:
            st.session_state.language_change_counter = 0
        st.session_state.language_change_counter += 1
        
        # Force re-render by updating a dummy state
        if 'force_rerun' not in st.session_state:
            st.session_state.force_rerun = 0
        st.session_state.force_rerun += 1
        
        # Show brief success message
        if location == 'sidebar':
            st.toast(f"✓ Language changed to {lang_options[selected_lang_label]}", icon="🌐")
        
        # Trigger rerun to update all text
        st.rerun()
    
    return current_lang


def render_language_switcher_compact():
    """
    Render a very compact language switcher (just flags)
    Useful for headers or tight spaces
    """
    current_lang = get_language()
    
    st.markdown("""
        <style>
        .compact-lang-switcher {
            display: flex;
            gap: 0.25rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🇬🇧", key="compact_en", help="English", 
                    type="primary" if current_lang == 'en' else "secondary"):
            set_language('en')
            st.rerun()
    
    with col2:
        if st.button("🇨🇳", key="compact_zh", help="中文",
                    type="primary" if current_lang == 'zh' else "secondary"):
            set_language('zh')
            st.rerun()
