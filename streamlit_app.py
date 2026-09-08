"""Streamlit deployment entry point."""

import runpy
import streamlit as st


if not getattr(st, "_bevlat_hungarian_select_placeholders", False):
    _original_selectbox = st.selectbox
    _original_multiselect = st.multiselect

    def _hungarian_selectbox(*args, **kwargs):
        kwargs.setdefault("placeholder", "Válassz egy lehetőséget!")
        return _original_selectbox(*args, **kwargs)

    def _hungarian_multiselect(*args, **kwargs):
        kwargs.setdefault("placeholder", "Válassz egy vagy több lehetőséget!")
        return _original_multiselect(*args, **kwargs)

    st.selectbox = _hungarian_selectbox
    st.multiselect = _hungarian_multiselect
    st._bevlat_hungarian_select_placeholders = True


runpy.run_path("latin_morph.py", run_name="__main__")
