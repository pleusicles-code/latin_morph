from pathlib import Path

path = Path('verbs.py')
text = path.read_text()
old = '''                            if parsed_analyses.get("error") in ["incomplete tense", "missing required parameter"]:
                                st.session_state.answer_display_message = (
                                    "Hiányos válasz - pótold a hiányzó paramétereket!"
                                )
                            else:
                                st.session_state.answer_display_message = (
                                    "Ellenőrizd a válasz paramétereit, majd próbáld újra. "
                                    "A válaszod nincs még értékelve."
                                )
'''
new = '''                            if parsed_analyses.get("error") in ["incomplete tense", "missing required parameter"]:
                                st.session_state.answer_display_message = feedback_box(
                                    "<strong>Hiányos válasz - pótold a hiányzó paramétereket!</strong>",
                                    "incorrect",
                                )
                            else:
                                st.session_state.answer_display_message = feedback_box(
                                    "<strong>Ellenőrizd a válasz paramétereit, majd próbáld újra. A válaszod nincs még értékelve.</strong>",
                                    "incorrect",
                                )
'''
if text.count(old) != 1:
    raise SystemExit(f'parse-warning block count: {text.count(old)}')
text = text.replace(old, new)
old = 'f"<strong>Helytelen válasz. {label}:<br>{correct_text}</strong>",\n'
new = 'f"<strong>Helytelen válasz. {label}: {correct_text}</strong>",\n'
if text.count(old) != 1:
    raise SystemExit(f'incorrect message block count: {text.count(old)}')
text = text.replace(old, new)
compile(text, 'verbs.py', 'exec')
path.write_text(text)
