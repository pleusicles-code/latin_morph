"""Streamlit deployment entry point."""

import runpy

import streamlit as st

if st.user.is_logged_in and st.sidebar.button("Log out and sign in again"):
    st.logout()

runpy.run_path("latin_morph.py", run_name="__main__")
