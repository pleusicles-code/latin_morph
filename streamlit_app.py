"""Streamlit deployment entry point."""

import runpy
import streamlit as st
import vocab


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


if not getattr(vocab, "_bevlat_noun_data_fixes", False):
    _original_import_nouns = vocab.import_nouns

    def _bevlat_import_nouns():
        noun_vocab = _original_import_nouns()
        mare = noun_vocab.get("mare")
        if mare:
            mare.get("irreg", {}).get("pl", {}).pop("gen", None)
        return noun_vocab

    vocab.import_nouns = _bevlat_import_nouns
    vocab._bevlat_noun_data_fixes = True


runpy.run_path("latin_morph.py", run_name="__main__")
