from pathlib import Path

# new_question must never mutate a widget key after that widget has been instantiated
# in the current Streamlit run. Queue the clear instead.
path = Path('utils.py')
text = path.read_text()
old = '''    st.session_state.answer_checked = False
    st.session_state.answer_to_check = ""
    st.session_state.answer_input = ""
    st.session_state.result_message = ""
'''
new = '''    st.session_state.answer_checked = False
    st.session_state.answer_to_check = ""
    st.session_state["_bevlat_clear_answer_input"] = True
    st.session_state.result_message = ""
'''
if text.count(old) != 1:
    raise SystemExit(f'utils answer clear block: expected 1, found {text.count(old)}')
path.write_text(text.replace(old, new))

# Consume the queued clear immediately before the next answer_input widget is built.
path = Path('streamlit_app.py')
text = path.read_text()
anchor = '''if not getattr(st, "_bevlat_noun_multiple_answer_inline", False):
'''
insert = '''# Clear the shared answer widget safely on the run after a new question is generated.
# This must happen before the widget with key ``answer_input`` is instantiated;
# mutating that key later in the same run raises StreamlitAPIException.
if not getattr(st, "_bevlat_deferred_answer_input_clear", False):
    _previous_text_input_for_clear = st.text_input

    def _bevlat_deferred_clear_text_input(*args, **kwargs):
        key = kwargs.get("key")
        if key == "answer_input" and st.session_state.pop("_bevlat_clear_answer_input", False):
            st.session_state.pop("answer_input", None)
        return _previous_text_input_for_clear(*args, **kwargs)

    st.text_input = _bevlat_deferred_clear_text_input
    st._bevlat_deferred_answer_input_clear = True


'''
if text.count(anchor) != 1:
    raise SystemExit(f'streamlit_app insertion anchor: expected 1, found {text.count(anchor)}')
text = text.replace(anchor, insert + anchor)
compile(text, 'streamlit_app.py', 'exec')
path.write_text(text)

compile(Path('utils.py').read_text(), 'utils.py', 'exec')
