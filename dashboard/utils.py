import os
import streamlit as st

def format_currency(value):
    """Converts numbers to readable format ($1.5M, $200k)."""
    if not value:
        return "$0"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.0f}k"
    return f"${value:,.0f}"

def get_secret(key):
    """
    Retrieve secrets by first searching environment variables (Docker)
    and then Streamlit's native secrets (Cloud).
    """

    env_val = os.environ.get(key)
    if env_val is not None:
        return env_val

    try:
        if key in st.secrets:
            return st.secrets[key]
    except (FileNotFoundError, AttributeError):
        pass
    
    return None