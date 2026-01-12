"""
Internationalization (i18n) Module
Supports English and Chinese (Simplified) languages
"""

import json
import os
from pathlib import Path

# Default language
DEFAULT_LANGUAGE = 'en'

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'zh': '中文'
}

# Translation data
_translations = {}

# Public alias for translations (for compatibility)
TRANSLATIONS = _translations

def load_translations():
    """Load translation files"""
    global _translations
    
    # Get the directory of this file
    base_dir = Path(__file__).parent.parent
    translations_dir = base_dir / 'translations'
    
    # Load each language file
    for lang_code in SUPPORTED_LANGUAGES.keys():
        translation_file = translations_dir / f'{lang_code}.json'
        if translation_file.exists():
            with open(translation_file, 'r', encoding='utf-8') as f:
                _translations[lang_code] = json.load(f)
        else:
            # Create empty translations if file doesn't exist
            _translations[lang_code] = {}

def get_language():
    """Get current language from session state"""
    import streamlit as st
    if 'language' not in st.session_state:
        st.session_state.language = DEFAULT_LANGUAGE
    return st.session_state.language

def get_current_language():
    """Alias for get_language() for compatibility"""
    return get_language()

def set_language(lang_code):
    """Set language in session state"""
    import streamlit as st
    if lang_code in SUPPORTED_LANGUAGES:
        st.session_state.language = lang_code

def t(key, lang=None, **kwargs):
    """
    Translate a key to the current language with enhanced error handling
    
    Args:
        key: Translation key (e.g., 'app.title' or 'common.save')
        lang: Optional language override
        **kwargs: Optional format parameters for string interpolation
        
    Returns:
        Translated string with fallback to key if translation not found
    """
    # Initialize translations if not loaded
    if not _translations:
        load_translations()
    
    if lang is None:
        lang = get_current_language()
    
    # Get translations for the language
    translations = TRANSLATIONS.get(lang, {})
    
    # Handle dot notation (e.g., 'app.title')
    keys = key.split('.')
    value = translations
    
    try:
        for k in keys:
            value = value[k]
        
        # Handle string interpolation if kwargs provided
        if kwargs and isinstance(value, str):
            try:
                value = value.format(**kwargs)
            except KeyError as e:
                # If format key is missing, return unformatted string
                print(f"Warning: Missing format key {e} for translation '{key}'")
                pass
        
        return value
    
    except (KeyError, TypeError):
        # Fallback strategy
        # 1. Try English if current language is not English
        if lang != 'en':
            try:
                en_translations = TRANSLATIONS.get('en', {})
                en_value = en_translations
                for k in keys:
                    en_value = en_value[k]
                
                print(f"Warning: Translation '{key}' not found for '{lang}', using English")
                return en_value
            except (KeyError, TypeError):
                pass
        
        # 2. Return the key itself as last resort (better than error)
        # Make it more readable by replacing dots and underscores
        readable_key = key.split('.')[-1].replace('_', ' ').title()
        print(f"Warning: Translation '{key}' not found in any language, using key")
        return readable_key

# Initialize translations on import
load_translations()


def get_language_name(lang_code):
    """Get the full name of a language"""
    names = {
        'en': 'English',
        'zh': '中文'
    }
    return names.get(lang_code, lang_code)


def get_available_languages():
    """Get list of available language codes"""
    return list(SUPPORTED_LANGUAGES.keys())


def get_language_options():
    """Get dictionary of language codes to display names"""
    return {
        'en': '🇬🇧 English',
        'zh': '🇨🇳 中文'
    }
