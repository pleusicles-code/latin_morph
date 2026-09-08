from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()

marker = '''def evaluate_noun_recognition_answer(user_analyses, possible_analyses, expect_all):
'''
helper = '''def format_noun_analysis(analysis):
    """Format one canonical noun analysis for user-facing feedback."""
    number, case = analysis
    return f"{number}. {case}."


def format_noun_analysis_list(analyses):
    """Format noun analyses in canonical order."""
    return "; ".join(
        format_noun_analysis(analysis)
        for analysis in canonicalize_noun_analyses(analyses)
    )


'''
if text.count(marker) != 1:
    raise RuntimeError(f"Expected evaluation marker once, found {text.count(marker)}")
text = text.replace(marker, helper + marker, 1)

old = '''                        user_display = canonicalize_noun_analyses(parsed_answer["analyses"])
                        possible_display = canonicalize_noun_analyses(matching_analyses)
                        diagnostic = (
                            f"tokens={parsed_answer['tokens']}; "
                            f"analyses={user_display}; possible={possible_display}"
                        )

                        if evaluation == "correct":
                            st.session_state.result_message = "**Good job!**"
                            st.session_state.answer_display_message = (
                                f":green-background[Your answer is correct: {diagnostic}]"
                            )
                        elif evaluation == "partial":
                            st.session_state.result_message = "**Partially correct.**"
                            st.session_state.answer_display_message = (
                                f":orange-background[Your answer is partially correct: {diagnostic}]"
                            )
                        else:
                            st.session_state.result_message = "**Incorrect. Better luck next time!**"
                            st.session_state.answer_display_message = (
                                f":red-background[Your answer is incorrect: {diagnostic}]"
                            )
'''
new = '''                        user_analyses = set(parsed_answer["analyses"])
                        possible_analyses = set(matching_analyses)
                        correct_supplied = user_analyses & possible_analyses
                        incorrect_supplied = user_analyses - possible_analyses
                        missing_analyses = possible_analyses - user_analyses
                        all_possible_text = format_noun_analysis_list(possible_analyses)
                        st.session_state.nouns_recognition_extra_delay = 0

                        if evaluation == "correct":
                            st.session_state.result_message = "**Good job!**"
                            st.session_state.answer_display_message = (
                                f":green-background[{all_possible_text}]"
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
                        elif evaluation == "partial":
                            st.session_state.result_message = "**Partially correct.**"
                            feedback_parts = []
                            if correct_supplied:
                                feedback_parts.append(
                                    f":green-background[Correct: {format_noun_analysis_list(correct_supplied)}]"
                                )
                            if incorrect_supplied:
                                feedback_parts.append(
                                    f":red-background[Incorrect: {format_noun_analysis_list(incorrect_supplied)}]"
                                )
                            if missing_analyses:
                                feedback_parts.append(
                                    f":blue-background[Missing: {format_noun_analysis_list(missing_analyses)}]"
                                )
                            st.session_state.answer_display_message = "  \\n".join(feedback_parts)
                        else:
                            st.session_state.result_message = "**Incorrect. Better luck next time!**"
                            incorrect_text = format_noun_analysis_list(user_analyses)
                            st.session_state.answer_display_message = (
                                f":red-background[Your answer: {incorrect_text}]  \\n"
                                f":green-background[Correct: {all_possible_text}]"
                            )
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected diagnostic feedback block once, found {text.count(old)}")
text = text.replace(old, new, 1)

old_parse = '''                            st.session_state.auto_advance_trigger = False
                            st.session_state.answer_display_message = (
'''
new_parse = '''                            st.session_state.auto_advance_trigger = False
                            st.session_state.nouns_recognition_extra_delay = 0
                            st.session_state.answer_display_message = (
'''
if text.count(old_parse) != 1:
    raise RuntimeError(f"Expected parse error block once, found {text.count(old_parse)}")
text = text.replace(old_parse, new_parse, 1)

old_sleep = '''    if st.session_state.auto_advance_trigger and st.session_state.answer_checked:
        time.sleep(auto_advance_delay())
        new_question(st.session_state.gen_func)
'''
new_sleep = '''    if st.session_state.auto_advance_trigger and st.session_state.answer_checked:
        advance_delay = auto_advance_delay()
        if exercise_type == "recognize":
            advance_delay = min(
                60,
                advance_delay + st.session_state.get("nouns_recognition_extra_delay", 0),
            )
        time.sleep(advance_delay)
        new_question(st.session_state.gen_func)
'''
if text.count(old_sleep) != 1:
    raise RuntimeError(f"Expected auto-advance block once, found {text.count(old_sleep)}")
text = text.replace(old_sleep, new_sleep, 1)

path.write_text(text)
