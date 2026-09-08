"""Streamlit deployment entry point."""

import runpy

import streamlit as st

# The recognition exercises retain an optional polling fragment so the former
# delayed answer check can be restored by setting ANSWER_CHECK_DELAY > 0.
# With the current 0-second delay, their decorator receives run_every=None.
# In that specific idle case, do not touch Streamlit's fragment machinery at all;
# otherwise its scheduler can initialize ThreadPoolExecutor workers that later
# emit missing-ScriptRunContext warnings even on other pages.
if not getattr(st.fragment, "_bevlat_idle_recognition_guard", False):
    _streamlit_fragment = st.fragment

    def _bevlat_fragment(*args, **kwargs):
        run_every = kwargs.get("run_every")

        if run_every is None and not (args and callable(args[0])):
            def decorator(func):
                if func.__name__ == "recognition_check_timer":
                    return func
                # Lazily create the real fragment only for non-recognition use.
                return _streamlit_fragment(*args, **kwargs)(func)

            return decorator

        return _streamlit_fragment(*args, **kwargs)

    _bevlat_fragment._bevlat_idle_recognition_guard = True
    st.fragment = _bevlat_fragment

runpy.run_path("latin_morph.py", run_name="__main__")
