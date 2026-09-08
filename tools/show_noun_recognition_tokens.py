from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()

old_import = "from utils import radio_change, reset, new_question, submit_and_check_answer, clear_page, send_setting, save_defaults, clear_defaults, auto_advance_delay, remove_macrons\n"
new_import = "from utils import radio_change, reset, new_question, submit_and_check_answer, clear_page, send_setting, save_defaults, clear_defaults, auto_advance_delay, remove_macrons, tokenize_morphology_answer\n"
if text.count(old_import) != 1:
    raise RuntimeError(f"Expected one utils import line, found {text.count(old_import)}")
text = text.replace(old_import, new_import, 1)

old_callback = '''                def submit_noun_answer():
                    if exercise_type == "recognize" and st.session_state.get("answer_input"):
                        st.session_state.correct_answer = st.session_state.answer_input
                    submit_and_check_answer()
'''
new_callback = '''                def submit_noun_answer():
                    recognition_answer = None
                    if exercise_type == "recognize" and st.session_state.get("answer_input"):
                        recognition_answer = st.session_state.answer_input
                        st.session_state.correct_answer = recognition_answer
                    submit_and_check_answer()
                    if recognition_answer:
                        tokens = tokenize_morphology_answer(recognition_answer)
                        st.session_state.answer_display_message = (
                            f":green-background[Your answer is correct: {tokens}]"
                        )
'''
if text.count(old_callback) != 1:
    raise RuntimeError(f"Expected one noun submit callback, found {text.count(old_callback)}")
text = text.replace(old_callback, new_callback, 1)

path.write_text(text)
