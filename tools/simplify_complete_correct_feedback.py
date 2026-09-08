from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()
old = '''                        if evaluation == "correct":
                            st.session_state.result_message = "**Good job!**"
                            st.session_state.answer_display_message = (
                                f":green-background[**The correct answer is: {all_possible_text}**]"
                            )
                            if (
                                not st.session_state[widget_key(page_id, "expect_all_answers")]
                                and len(possible_analyses) > 1
                                and missing_analyses
                            ):
                                st.session_state.answer_display_message += (
                                    "  \\n:yellow-background[Take note, however, that other analyses are possible!]"
                                )
                                st.session_state.nouns_recognition_extra_delay = 5
'''
new = '''                        if evaluation == "correct":
                            st.session_state.result_message = "**Good job!**"
                            if missing_analyses:
                                st.session_state.answer_display_message = (
                                    f":green-background[**The correct answer is: {all_possible_text}**]"
                                )
                                if (
                                    not st.session_state[widget_key(page_id, "expect_all_answers")]
                                    and len(possible_analyses) > 1
                                ):
                                    st.session_state.answer_display_message += (
                                        "  \\n:yellow-background[Take note, however, that other analyses are possible!]"
                                    )
                                    st.session_state.nouns_recognition_extra_delay = 5
                            else:
                                st.session_state.answer_display_message = (
                                    ":green-background[**Correct answer!**]"
                                )
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected correct-feedback block once, found {text.count(old)}")
path.write_text(text.replace(old, new, 1))
