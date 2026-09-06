"""Temporary Streamlit deployment entry point used while reproducing auth setup."""

import runpy
import streamlit as st
from supabase import create_client

if st.user.is_logged_in:
    if st.sidebar.button("Log out and sign in again"):
        st.logout()

    sb_url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    sb_key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
    try:
        diagnostic_client = create_client(sb_url, sb_key)
        diagnostic_client.auth.sign_in_with_id_token(
            {
                "provider": "google",
                "token": st.user.tokens.id,
                "access_token": st.user.tokens.access,
            }
        )
    except Exception as exc:
        st.error(f"Supabase Google token sign-in failed: {type(exc).__name__}: {exc}")
        st.info("Your Streamlit login session is still active, but the Google ID token is no longer accepted by Supabase. Use the sidebar button to log out, then sign in again.")
        st.stop()

runpy.run_path("latin_morph.py", run_name="__main__")
