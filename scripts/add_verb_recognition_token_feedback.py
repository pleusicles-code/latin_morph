from pathlib import Path

path = Path('verbs.py')
text = path.read_text()
old = '''                def submit_verb_answer():
                    original_correct_answer = st.session_state.correct_answer
                    st.session_state.correct_answer = participial_answer_variants(original_correct_answer)
                    submit_and_check_answer()
                    st.session_state.correct_answer = original_correct_answer
                    if not st.session_state.get("answer_input"):
                        st.session_state.answer_display_message = (
                            "A válaszmező üres. Írj be egy alakot, majd kattints a **Válasz ellenőrzése** gombra, "
                            "vagy az **Új kérdés** gombbal ugord át a kérdést."
                        )
                    elif st.session_state.answer_checked:
                        if "Good job!" in st.session_state.result_message:
                            st.session_state.answer_display_message = feedback_box(
                                "<strong>Helyes válasz!</strong>", "correct"
                            )
                        else:
                            answers = st.session_state.correct_answer
                            compact_answer = compact_participial_answer(answers)
                            if compact_answer:
                                correct_html = heavy(compact_answer, italic=True)
                                label = "A helyes válasz"
                            else:
                                if not isinstance(answers, list):
                                    answers = [answers]
                                correct_html = " <span style='font-weight:700;'>vagy</span> ".join(
                                    heavy(answer, italic=True) for answer in answers
                                )
                                label = "A helyes válasz" if len(answers) == 1 else "A helyes válaszok"
                            st.session_state.answer_display_message = feedback_box(
                                f"<strong>Helytelen válasz. {label}: {correct_html}.</strong>",
                                "incorrect",
                            )
'''
new = '''                def submit_verb_answer():
                    if exercise_type == "recognize":
                        user_answer = st.session_state.get("answer_input", "")
                        if not user_answer:
                            st.session_state.button_disable = False
                            st.session_state.answer_display_message = (
                                "A válaszmező üres. Írj be egy alakot, majd kattints a **Válasz ellenőrzése** gombra, "
                                "vagy az **Új kérdés** gombbal ugord át a kérdést."
                            )
                            return

                        recognized_tokens = [
                            token for token in tokenize_morphology_answer(user_answer)
                            if token in VERB_MORPHOLOGY_ALIASES
                        ]
                        recognized_html = " ".join(html.escape(token) for token in recognized_tokens) or "&nbsp;"
                        st.session_state.button_disable = True
                        st.session_state.answer_checked = True
                        st.session_state.result_message = "**Good job!**"
                        st.session_state.answer_display_message = feedback_box(
                            recognized_html, "correct"
                        )
                        st.session_state.auto_advance_trigger = bool(st.session_state.auto_advance)
                        return

                    original_correct_answer = st.session_state.correct_answer
                    st.session_state.correct_answer = participial_answer_variants(original_correct_answer)
                    submit_and_check_answer()
                    st.session_state.correct_answer = original_correct_answer
                    if not st.session_state.get("answer_input"):
                        st.session_state.answer_display_message = (
                            "A válaszmező üres. Írj be egy alakot, majd kattints a **Válasz ellenőrzése** gombra, "
                            "vagy az **Új kérdés** gombbal ugord át a kérdést."
                        )
                    elif st.session_state.answer_checked:
                        if "Good job!" in st.session_state.result_message:
                            st.session_state.answer_display_message = feedback_box(
                                "<strong>Helyes válasz!</strong>", "correct"
                            )
                        else:
                            answers = st.session_state.correct_answer
                            compact_answer = compact_participial_answer(answers)
                            if compact_answer:
                                correct_html = heavy(compact_answer, italic=True)
                                label = "A helyes válasz"
                            else:
                                if not isinstance(answers, list):
                                    answers = [answers]
                                correct_html = " <span style='font-weight:700;'>vagy</span> ".join(
                                    heavy(answer, italic=True) for answer in answers
                                )
                                label = "A helyes válasz" if len(answers) == 1 else "A helyes válaszok"
                            st.session_state.answer_display_message = feedback_box(
                                f"<strong>Helytelen válasz. {label}: {correct_html}.</strong>",
                                "incorrect",
                            )
'''
if text.count(old) != 1:
    raise SystemExit(f'Expected exactly one submit block, found {text.count(old)}')
text = text.replace(old, new)
compile(text, 'verbs.py', 'exec')
path.write_text(text)
