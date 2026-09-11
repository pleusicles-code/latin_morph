from pathlib import Path

path = Path('verbs.py')
text = path.read_text()

old = '    "show_principal_parts": bool_setting(False),\n'
new = '    "show_principal_parts": bool_setting(True),\n'
if text.count(old) != 1:
    raise SystemExit(f'Expected show_principal_parts default once, found {text.count(old)}')
text = text.replace(old, new)

old = '''                        if evaluation == "correct":
                            st.session_state.result_message = "**Good job!**"
                            st.session_state.answer_display_message = feedback_box(
                                "<strong>Helyes válasz!</strong>", "correct"
                            )
                        elif evaluation == "partial":
                            st.session_state.result_message = "**Partially correct.**"
                            st.session_state.answer_display_message = feedback_box(
                                "<strong>Részben helyes válasz.</strong> "
                                f"<strong>A helyes válaszok:<br>{correct_text}</strong>",
                                "partial",
                            )
                        else:
                            st.session_state.result_message = "**Incorrect. Better luck next time!**"
                            label = "A helyes válasz" if len(recognition_correct_analyses) == 1 else "A helyes válaszok"
                            st.session_state.answer_display_message = feedback_box(
                                f"<strong>Helytelen válasz. {label}:<br>{correct_text}</strong>",
                                "incorrect",
                            )
                        return
'''
new = '''                        if evaluation == "correct":
                            st.session_state.result_message = "**Good job!**"
                            st.session_state.answer_display_message = feedback_box(
                                "<strong>Helyes válasz!</strong>", "correct"
                            )
                        elif evaluation == "partial":
                            st.session_state.result_message = "**Partially correct.**"
                            st.session_state.answer_display_message = feedback_box(
                                "<strong>Részben helyes válasz.</strong> "
                                f"<strong>A helyes válaszok:<br>{correct_text}</strong>",
                                "partial",
                            )
                        else:
                            st.session_state.result_message = "**Incorrect. Better luck next time!**"
                            label = "A helyes válasz" if len(recognition_correct_analyses) == 1 else "A helyes válaszok"
                            st.session_state.answer_display_message = feedback_box(
                                f"<strong>Helytelen válasz. {label}:<br>{correct_text}</strong>",
                                "incorrect",
                            )
                        # Recognition forms deliberately do not clear on submit so that
                        # parsing errors remain editable. Once parsing succeeds and the
                        # answer has actually been evaluated, clear the widget manually.
                        st.session_state.answer_input = ""
                        return
'''
if text.count(old) != 1:
    raise SystemExit(f'Expected recognition evaluation tail once, found {text.count(old)}')
text = text.replace(old, new)

compile(text, 'verbs.py', 'exec')
path.write_text(text)
