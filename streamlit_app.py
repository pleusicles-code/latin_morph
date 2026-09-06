"""Streamlit deployment entry point for the fork.

The upstream app expects Supabase URL/key entries in ``st.secrets`` even for
anonymous sessions.  For deployments that do not yet have Supabase configured,
provide inert placeholders so the app can boot in session-only guest mode.
Once real Streamlit secrets are configured, this wrapper leaves them untouched.
"""

import streamlit as st

try:
    st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
except (FileNotFoundError, KeyError):
    # These values are never used to contact Supabase for an anonymous user;
    # latin_morph.py only creates a Supabase client after a successful login.
    st.secrets = {
        "connections": {
            "supabase": {
                "SUPABASE_URL": "https://supabase-not-configured.invalid",
                "SUPABASE_KEY": "supabase-not-configured",
            }
        }
    }

import latin_morph  # noqa: E402,F401
