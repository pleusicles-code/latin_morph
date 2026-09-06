"""Streamlit deployment entry point for the fork.

The upstream app expects Supabase URL/key entries in ``st.secrets`` even for
anonymous sessions, and it assumes Streamlit authentication is configured.
For deployments that do not yet have Supabase/OAuth configured, provide inert
fallbacks so the app can boot in session-only guest mode. Once real Streamlit
secrets/authentication are configured, this wrapper leaves them untouched.
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

# Without Streamlit authentication configured, st.user exists but does not expose
# ``is_logged_in``. Add a fallback property so the upstream app's existing checks
# consistently treat this deployment as an anonymous session. When authentication
# is configured later, Streamlit's own property is already present and untouched.
if not hasattr(st.user, "is_logged_in"):
    type(st.user).is_logged_in = property(lambda self: False)

import latin_morph  # noqa: E402,F401
