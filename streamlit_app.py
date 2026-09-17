import runpy
import bevlat_ui_behavior  # installs shared UI behavior before pages render

runpy.run_path("streamlit_app_impl.py", run_name="__main__")
