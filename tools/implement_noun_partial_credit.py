from pathlib import Path

root = Path(__file__).resolve().parents[1]
nouns_path = root / "nouns.py"
utils_path = root / "utils.py"

nouns = nouns_path.read_text()
utils = utils_path.read_text()

# Rename the exercise-specific setting everywhere in nouns.py.
nouns = nouns.replace('"expect_all_answers": bool_setting(False),', '"award_partial_credit": bool_setting(False),')
nouns = nouns.replace('expect_all_answers = st.checkbox(\n            "Expect all correct answers?",\n            help="If checked, the answer will be deemed fully correct only if each possible analysis is given; otherwise, any possible analysis will be accepted as correct.",\n            key=widget_key(page_id, "expect_all_answers"),\n        )',
'''award_partial_credit = st.checkbox(
            "Award partial credit?",
            help="If enabled, partially correct answers receive half credit; otherwise, only fully correct answers receive credit.",
            key=widget_key(page_id, "award_partial_credit"),
        )''')
nouns = nouns.replace('"expect_all_answers": st.session_state[widget_key(page_id, "expect_all_answers")],', '"award_partial_credit": st.session_state[widget_key(page_id, "award_partial_credit")],')
nouns = nouns.replace('"expect_all_answers": False,', '"award_partial_credit": False,')
nouns = nouns.replace('st.session_state.nouns_expect_all_answers = False', 'st.session_state.nouns_award_partial_credit = False')

old_eval = '''def evaluate_noun_recognition_answer(user_analyses, possible_analyses, expect_all):
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
new_eval = '''def evaluate_noun_recognition_answer(user_analyses, possible_analyses):
    """Return correct / partial / incorrect using complete-analysis semantics."""
    user_analyses = set(user_analyses)
    possible_analyses = set(possible_analyses)
    correct_supplied = user_analyses & possible_analyses

    if user_analyses == possible_analyses:
        return "correct"
    if correct_supplied:
        return "partial"
    return "incorrect"
'''
if nouns.count(old_eval) != 1:
    raise RuntimeError(f"Expected old evaluator once, found {nouns.count(old_eval)}")
nouns = nouns.replace(old_eval, new_eval, 1)

old_call = '''                            evaluation = evaluate_noun_recognition_answer(
                                parsed_answer["analyses"],
                                matching_analyses,
                                st.session_state[widget_key(page_id, "expect_all_answers")],
                            )
'''
new_call = '''                            evaluation = evaluate_noun_recognition_answer(
                                parsed_answer["analyses"],
                                matching_analyses,
                            )
'''
if nouns.count(old_call) != 1:
    raise RuntimeError(f"Expected evaluator call once, found {nouns.count(old_call)}")
nouns = nouns.replace(old_call, new_call, 1)

old_shared_setup = '''                            st.session_state.correct_answer = (
                                recognition_answer
                                if evaluation == "correct"
                                else "__noun_recognition_incorrect__"
                            )
'''
new_shared_setup = '''                            st.session_state.correct_answer = (
                                recognition_answer
                                if evaluation == "correct"
                                else "__noun_recognition_incorrect__"
                            )
                            if evaluation == "partial":
                                st.session_state.answer_credit_override = (
                                    0.5
                                    if st.session_state[widget_key(page_id, "award_partial_credit")]
                                    else 0
                                )
'''
if nouns.count(old_shared_setup) != 1:
    raise RuntimeError(f"Expected shared-checker setup once, found {nouns.count(old_shared_setup)}")
nouns = nouns.replace(old_shared_setup, new_shared_setup, 1)

old_correct_feedback = '''                        if evaluation == "correct":
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
new_correct_feedback = '''                        if evaluation == "correct":
                            st.session_state.result_message = "**Good job!**"
                            st.session_state.answer_display_message = (
                                ":green-background[**Correct answer!**]"
                            )
'''
if nouns.count(old_correct_feedback) != 1:
    raise RuntimeError(f"Expected old correct-feedback block once, found {nouns.count(old_correct_feedback)}")
nouns = nouns.replace(old_correct_feedback, new_correct_feedback, 1)

# Shared checker: support a numeric credit override while keeping binary rendering semantics.
old_score = '''            # set correct/incorrect result message
            if correct_flag is True:
                st.session_state.current_score += 1
                st.session_state.result_message = "**Good job!**"
            else:
                st.session_state.result_message = "**Incorrect. Better luck next time!**"
'''
new_score = '''            # set score and correct/incorrect result message
            credit_override = st.session_state.pop("answer_credit_override", None)
            answer_credit = (1 if correct_flag else 0) if credit_override is None else credit_override
            st.session_state.current_score += answer_credit
            if correct_flag is True:
                st.session_state.result_message = "**Good job!**"
            else:
                st.session_state.result_message = "**Incorrect. Better luck next time!**"
'''
if utils.count(old_score) != 1:
    raise RuntimeError(f"Expected score block once, found {utils.count(old_score)}")
utils = utils.replace(old_score, new_score, 1)

old_log = '''                st.session_state.question_list[-1]["answer"] = user_answer
                st.session_state.question_list[-1]["correct"] = correct_flag  # write correctness to question_list
'''
new_log = '''                st.session_state.question_list[-1]["answer"] = user_answer
                st.session_state.question_list[-1]["correct"] = (
                    answer_credit if credit_override is not None else correct_flag
                )  # write correctness / partial credit to question_list
'''
if utils.count(old_log) != 1:
    raise RuntimeError(f"Expected logging block once, found {utils.count(old_log)}")
utils = utils.replace(old_log, new_log, 1)

# Ensure an override can never leak into a later question.
old_newq = '''    st.session_state.append_answer = True
    st.session_state.gen_string = None

    st.session_state.current_question = gen_question()
'''
new_newq = '''    st.session_state.append_answer = True
    st.session_state.gen_string = None
    st.session_state.pop("answer_credit_override", None)

    st.session_state.current_question = gen_question()
'''
if utils.count(old_newq) != 1:
    raise RuntimeError(f"Expected new_question reset block once, found {utils.count(old_newq)}")
utils = utils.replace(old_newq, new_newq, 1)

nouns_path.write_text(nouns)
utils_path.write_text(utils)
