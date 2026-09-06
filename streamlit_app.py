"""Deployment entry point that permits Latin Morph! to run without Supabase.

When Supabase secrets are configured, the original application uses them unchanged.
When they are absent, placeholder values are supplied only so the application shell
can start in anonymous/session-only mode; no Supabase client is created unless a
user is logged in.
"""

import streamlit as st

try:
    st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
except (FileNotFoundError, KeyError):
    st.secrets = {
        "connections": {
            "supabase": {
                "SUPABASE_URL": "https://supabase-not-configured.invalid",
                "SUPABASE_KEY": "supabase-not-configured",
            }
        }
    }

import latin_morph  # noqa: E402,F401
