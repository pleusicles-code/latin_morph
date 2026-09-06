"""Temporary Streamlit deployment entry point used while reproducing auth setup."""

import runpy
import time
import uuid

import jwt
import streamlit as st

# Keep a lightweight local signing diagnostic while letting the original app
# perform the real Google-token / Supabase fallback logic.
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

if st.user.is_logged_in and st.sidebar.button("Log out and sign in again"):
    st.logout()

# The original app now has everything it needs to try Google ID-token sign-in
# first and, if that token has expired, run refresh_user_token() using the
# configured Supabase secret key plus our active ES256 signing key.
runpy.run_path("latin_morph.py", run_name="__main__")
