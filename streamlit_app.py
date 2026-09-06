"""Temporary Streamlit deployment entry point used while reproducing auth setup."""

import runpy
import time
import uuid

import jwt
import streamlit as st
from supabase import create_client

# Validate that the private ES256 signing key added to Streamlit secrets can be
# read and used locally before we activate it in Supabase. The diagnostic JWT is
# never sent anywhere and is never displayed.
try:
    _sb_secrets = st.secrets["connections"]["supabase"]
    _private_key = _sb_secrets["SUPABASE_PRIVATE_KEY"]
    _private_key_id = _sb_secrets["SUPABASE_PRIVATE_KEY_ID"]
    _now = int(time.time())
    _diagnostic_jwt = jwt.encode(
        {
            "role": "authenticated",
            "aud": "authenticated",
            "sub": str(uuid.uuid4()),
            "iat": _now,
            "exp": _now + 300,
        },
        key=_private_key,
        algorithm="ES256",
        headers={"kid": _private_key_id},
    )
    _header = jwt.get_unverified_header(_diagnostic_jwt)
    if _header.get("alg") != "ES256" or _header.get("kid") != _private_key_id:
        raise RuntimeError("Generated JWT header does not match the configured ES256 key ID.")
    st.sidebar.success("Signing-key diagnostic: OK")
except Exception as exc:
    st.error(f"Signing-key diagnostic failed: {type(exc).__name__}: {exc}")
    st.stop()

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
