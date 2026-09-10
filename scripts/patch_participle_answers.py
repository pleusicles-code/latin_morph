from pathlib import Path

p = Path('verbs.py')
s = p.read_text()

marker = '''def heavy(text, italic=False):
    escaped = html.escape(str(text))
    if italic:
        escaped = f"<em>{escaped}</em>"
    return f'<span style="font-weight:900;">{escaped}</span>'
'''
insert = marker + '''\n\ndef participial_answer_variants(answers):
    """Add compact `3` variants when three gender forms share the same auxiliary."""
    answer_list = list(answers) if isinstance(answers, list) else [answers]
    split_answers = [answer.split(maxsplit=1) for answer in answer_list if isinstance(answer, str)]
    if len(answer_list) != 3 or len(split_answers) != 3 or any(len(parts) != 2 for parts in split_answers):
        return answer_list
    remainders = {parts[1] for parts in split_answers}
    if len(remainders) != 1:
        return answer_list

    remainder = split_answers[0][1]
    expanded = list(answer_list)
    for participle, _ in split_answers:
        expanded.append(f"{participle} 3 {remainder}")
        expanded.append(f"{participle}3 {remainder}")
    return expanded


def compact_participial_answer(answers):
    """Display a three-gender participial paradigm as e.g. `gestus 3 est`."""
    answer_list = list(answers) if isinstance(answers, list) else [answers]
    split_answers = [answer.split(maxsplit=1) for answer in answer_list if isinstance(answer, str)]
    if len(answer_list) == 3 and len(split_answers) == 3 and all(len(parts) == 2 for parts in split_answers):
        remainders = {parts[1] for parts in split_answers}
        if len(remainders) == 1:
            return f"{split_answers[0][0]} 3 {split_answers[0][1]}"
    return None
'''
if marker not in s:
    raise RuntimeError('helper insertion marker not found')
s = s.replace(marker, insert, 1)

old_submit = '''                def submit_verb_answer():
                    submit_and_check_answer()
                    if not st.session_state.get("answer_input"):
'''
new_submit = '''                def submit_verb_answer():
                    original_correct_answer = st.session_state.correct_answer
                    st.session_state.correct_answer = participial_answer_variants(original_correct_answer)
                    submit_and_check_answer()
                    st.session_state.correct_answer = original_correct_answer
                    if not st.session_state.get("answer_input"):
'''
if old_submit not in s:
    raise RuntimeError('submit block marker not found')
s = s.replace(old_submit, new_submit, 1)

old_feedback = '''                        else:
                            answers = st.session_state.correct_answer
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
new_feedback = '''                        else:
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
if old_feedback not in s:
    raise RuntimeError('feedback block marker not found')
s = s.replace(old_feedback, new_feedback, 1)

compile(s, 'verbs.py', 'exec')
p.write_text(s)
