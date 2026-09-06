"""Temporary Streamlit deployment entry point.

OAuth and Supabase are now configured externally in Streamlit secrets, so this
wrapper only executes the original application script on every Streamlit rerun.
"""

import runpy

runpy.run_path("latin_morph.py", run_name="__main__")
