"""
Database operation helpers with error logging.
"""

from __future__ import annotations

import logging

import streamlit as st


logging.basicConfig(filename="app.log", level=logging.ERROR)


def run_db_operation(operation, *args, **kwargs):
    """Run a database operation with standardized error handling."""
    try:
        return operation(*args, **kwargs)
    except Exception as exc:
        logging.error(f"Database error: {str(exc)}")
        st.error("An error occurred. Please contact support.")
        return None
