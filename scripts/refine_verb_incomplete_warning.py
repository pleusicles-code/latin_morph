from pathlib import Path

path = Path('verbs.py')
text = path.read_text()
old = '''                        if not parsed_analyses["valid"]:
                            st.session_state.button_disable = False
                            st.session_state.answer_checked = False
                            st.session_state.result_message = ""
                            st.session_state.auto_advance_trigger = False
                            st.session_state.answer_display_message = (
                                "Ellenőrizd a válasz paramétereit, majd próbáld újra. "
                                "A válaszod nincs még értékelve."
                            )
                            return
'''
new = '''                        if not parsed_analyses["valid"]:
                            st.session_state.button_disable = False
                            st.session_state.answer_checked = False
                            st.session_state.result_message = ""
                            st.session_state.auto_advance_trigger = False
                            if parsed_analyses.get("error") in ["incomplete tense", "missing required parameter"]:
                                st.session_state.answer_display_message = (
                                    "Hiányos válasz - pótold a hiányzó paramétereket!"
                                )
                            else:
                                st.session_state.answer_display_message = (
                                    "Ellenőrizd a válasz paramétereit, majd próbáld újra. "
                                    "A válaszod nincs még értékelve."
                                )
                            return
'''
if text.count(old) != 1:
    raise SystemExit(f'Expected recognition parse-error block once, found {text.count(old)}')
text = text.replace(old, new)
compile(text, 'verbs.py', 'exec')
path.write_text(text)
