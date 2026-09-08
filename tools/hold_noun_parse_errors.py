from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()

old = '''                        else:
                            st.session_state.answer_display_message = (
                                f":green-background[Your answer is temporarily accepted. "
                                f"tokens={parsed_answer['tokens']}; parser error: {parsed_answer['error']}]"
                            )
'''
new = '''                        else:
                            st.session_state.button_disable = False
                            st.session_state.answer_checked = False
                            st.session_state.total_questions = max(0, st.session_state.total_questions - 1)
                            st.session_state.append_answer = True
                            st.session_state.result_message = ""
                            st.session_state.answer_display_message = (
                                f"Please check your answer and try again. "
                                f"tokens={parsed_answer['tokens']}; parser error: {parsed_answer['error']}"
                            )
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected parse-error feedback block once, found {text.count(old)}")
path.write_text(text.replace(old, new, 1))
