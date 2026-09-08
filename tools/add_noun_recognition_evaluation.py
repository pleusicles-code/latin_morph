from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()

anchor = '''def parse_noun_analysis_answer(text):
    """Parse NUMBER CASE+ (NUMBER CASE+)* from free-form noun analysis input."""
'''
if anchor not in text:
    raise RuntimeError("noun parser anchor not found")

# Insert helpers just before noun_endings, after parser definition.
marker = '''noun_endings = {1: {"sg": {"gen": "ae",
'''
helpers = '''NOUN_ANALYSIS_CASE_ORDER = {case: index for index, case in enumerate(("nom", "voc", "acc", "gen", "dat", "abl"))}
NOUN_ANALYSIS_NUMBER_ORDER = {"sg": 0, "pl": 1}


def canonicalize_noun_analyses(analyses):
    """Return noun analyses in canonical singular-then-plural case order."""
    return sorted(
        analyses,
        key=lambda analysis: (
            NOUN_ANALYSIS_NUMBER_ORDER[analysis[0]],
            NOUN_ANALYSIS_CASE_ORDER[analysis[1]],
        ),
    )


def evaluate_noun_recognition_answer(user_analyses, possible_analyses, expect_all):
    """Return correct / partial / incorrect for a parsed noun recognition answer."""
    user_analyses = set(user_analyses)
    possible_analyses = set(possible_analyses)
    correct_supplied = user_analyses & possible_analyses
    impossible_supplied = user_analyses - possible_analyses

    if len(possible_analyses) == 1:
        return "correct" if user_analyses == possible_analyses else "incorrect"

    if expect_all:
        if user_analyses == possible_analyses:
            return "correct"
        if correct_supplied:
            return "partial"
        return "incorrect"

    if correct_supplied and not impossible_supplied:
        return "correct"
    if correct_supplied and impossible_supplied:
        return "partial"
    return "incorrect"


'''
if text.count(marker) != 1:
    raise RuntimeError(f"Expected noun_endings marker once, found {text.count(marker)}")
text = text.replace(marker, helpers + marker, 1)

old = '''                def submit_noun_answer():
                    recognition_answer = None
                    if exercise_type == "recognize" and st.session_state.get("answer_input"):
                        recognition_answer = st.session_state.answer_input
                        st.session_state.correct_answer = recognition_answer
                    submit_and_check_answer()
                    if recognition_answer:
                        parsed_answer = parse_noun_analysis_answer(recognition_answer)
                        if parsed_answer["valid"]:
                            analyses_display = sorted(parsed_answer["analyses"])
                            st.session_state.answer_display_message = (
                                f":green-background[Your answer is correct: "
                                f"tokens={parsed_answer['tokens']}; analyses={analyses_display}]"
                            )
                        else:
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
new = '''                def submit_noun_answer():
                    recognition_answer = None
                    parsed_answer = None
                    evaluation = None

                    if exercise_type == "recognize" and st.session_state.get("answer_input"):
                        recognition_answer = st.session_state.answer_input
                        parsed_answer = parse_noun_analysis_answer(recognition_answer)

                        if parsed_answer["valid"]:
                            evaluation = evaluate_noun_recognition_answer(
                                parsed_answer["analyses"],
                                matching_analyses,
                                st.session_state[widget_key(page_id, "expect_all_answers")],
                            )
                            # Let the shared checker perform score/history/logging. It only
                            # understands binary correctness, so partial answers are logged
                            # as not correct for adaptive-learning purposes.
                            st.session_state.correct_answer = (
                                recognition_answer
                                if evaluation == "correct"
                                else "__noun_recognition_incorrect__"
                            )
                        else:
                            # Use the temporary self-match only so the shared function can
                            # execute safely; all of its submission effects are rolled back below.
                            st.session_state.correct_answer = recognition_answer

                    submit_and_check_answer()

                    if recognition_answer and parsed_answer:
                        if not parsed_answer["valid"]:
                            st.session_state.button_disable = False
                            st.session_state.answer_checked = False
                            st.session_state.total_questions = max(0, st.session_state.total_questions - 1)
                            st.session_state.append_answer = True
                            st.session_state.result_message = ""
                            st.session_state.auto_advance_trigger = False
                            st.session_state.answer_display_message = (
                                f"Please check your answer and try again. "
                                f"tokens={parsed_answer['tokens']}; parser error: {parsed_answer['error']}"
                            )
                            return

                        user_display = canonicalize_noun_analyses(parsed_answer["analyses"])
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
if text.count(old) != 1:
    raise RuntimeError(f"Expected noun submit callback once, found {text.count(old)}")
text = text.replace(old, new, 1)

path.write_text(text)
