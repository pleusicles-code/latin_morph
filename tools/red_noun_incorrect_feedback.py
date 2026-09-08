from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()
old = '''                            st.session_state.answer_display_message = (\n                                f":red-background[Your answer: {incorrect_text}]  \\n"\n                                f":green-background[Correct: {all_possible_text}]"\n                            )\n'''
new = '''                            st.session_state.answer_display_message = (\n                                f":red-background[Your answer: {incorrect_text}]  \\n"\n                                f":red-background[Correct: {all_possible_text}]"\n                            )\n'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected incorrect-feedback block once, found {text.count(old)}")
path.write_text(text.replace(old, new, 1))
