from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()

old = '''                        elif evaluation == "partial":
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
'''
new = '''                        elif evaluation == "partial":
                            st.session_state.result_message = "**Partially correct.**"
                            feedback_parts = []
                            if correct_supplied:
                                feedback_parts.append(
                                    '<div style="background:#d9f2df;padding:0.15rem 0.35rem;border-radius:0.25rem;">'
                                    f'Correct: {format_noun_analysis_list(correct_supplied)}'</div>'
                                )
                            if incorrect_supplied:
                                feedback_parts.append(
                                    '<div style="background:#f7d7d9;padding:0.15rem 0.35rem;border-radius:0.25rem;">'
                                    f'Incorrect: {format_noun_analysis_list(incorrect_supplied)}'</div>'
                                )
                            if missing_analyses:
                                feedback_parts.append(
                                    '<div style="background:#dbeafe;padding:0.15rem 0.35rem;border-radius:0.25rem;">'
                                    f'Missing: {format_noun_analysis_list(missing_analyses)}'</div>'
                                )
                            st.session_state.answer_display_message = (
                                '<table style="border-collapse:collapse;border:none;background:#fff3cd;width:100%;">'
                                '<tr>'
                                '<td style="border:none;vertical-align:middle;padding:0.45rem 0.6rem;white-space:nowrap;">'
                                '<strong>Partially correct answer:</strong>'
                                '</td>'
                                '<td style="border:none;vertical-align:middle;padding:0.45rem 0.6rem;">'
                                + ''.join(feedback_parts) +
                                '</td>'
                                '</tr></table>'
                            )
'''
# fix deliberately split html string literals above into valid Python expressions
new = new.replace("f'Correct: {format_noun_analysis_list(correct_supplied)}'</div>'", "f'Correct: {format_noun_analysis_list(correct_supplied)}</div>'")
new = new.replace("f'Incorrect: {format_noun_analysis_list(incorrect_supplied)}'</div>'", "f'Incorrect: {format_noun_analysis_list(incorrect_supplied)}</div>'")
new = new.replace("f'Missing: {format_noun_analysis_list(missing_analyses)}'</div>'", "f'Missing: {format_noun_analysis_list(missing_analyses)}</div>'")

if text.count(old) != 1:
    raise RuntimeError(f"Expected partial feedback block once, found {text.count(old)}")
text = text.replace(old, new, 1)

old_render = '''            with user_answer_col:
                st.markdown(st.session_state.answer_display_message)
'''
new_render = '''            with user_answer_col:
                if st.session_state.answer_display_message.lstrip().startswith("<table"):
                    st.html(st.session_state.answer_display_message)
                else:
                    st.markdown(st.session_state.answer_display_message)
'''
if text.count(old_render) != 1:
    raise RuntimeError(f"Expected answer render block once, found {text.count(old_render)}")
text = text.replace(old_render, new_render, 1)

path.write_text(text)
