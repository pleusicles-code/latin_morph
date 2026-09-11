from pathlib import Path

path = Path('verbs.py')
text = path.read_text()

def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 occurrence, found {count}')
    text = text.replace(old, new)

# Preserve whether the special 2. imper. marker itself was explicitly typed.
old = '''    for index in range(analysis_count):
        analysis = {"_explicit_categories": set(explicit_categories)}
'''
new = '''    for index in range(analysis_count):
        analysis = {
            "_explicit_categories": set(explicit_categories),
            "_explicit_second_imperative": explicit_second_imperative,
        }
'''
replace_once(old, new, 'explicit second imperative metadata')

start = text.index('def format_correct_verb_recognition_analysis_html(')
end = text.index('\n\ndef canonical_verb_analysis(', start)
old_block = text[start:end]
new_block = '''def verb_recognition_parameter_label(analysis, category, *, correction=False):
    """Return the compact feedback label for one verb-analysis parameter."""
    if category == "mood" and analysis.get("mood") == "impv":
        if correction:
            return "2. imperativus" if analysis.get("relative_tense") == "fut" else "imperativus"
        if analysis.get("_explicit_second_imperative"):
            return "2. imper."
    return VERB_ANALYSIS_CANONICAL_LABELS[(category, analysis[category])]


def verb_recognition_pair_cost(user_analysis, correct_analysis, lexical_voice):
    """Score how closely one supplied analysis resembles one correct analysis."""
    mismatches = verb_recognition_mismatch_categories(
        user_analysis, correct_analysis, lexical_voice
    )
    explicit = set(user_analysis.get("_explicit_categories", set()))
    # Gender is optional but, when supplied, participates in pairing/feedback.
    if "gender" in explicit and user_analysis.get("gender") != correct_analysis.get("gender"):
        mismatches = set(mismatches) | {"gender"}
    return len(mismatches), mismatches


def pair_verb_recognition_analyses(user_analyses, correct_analyses, lexical_voice):
    """Greedily pair supplied analyses with the nearest unused correct analyses."""
    remaining_correct = set(range(len(correct_analyses)))
    pairs = []
    for user_analysis in user_analyses:
        if not remaining_correct:
            pairs.append((user_analysis, None, set(user_analysis.get("_explicit_categories", set()))))
            continue
        ranked = []
        for index in remaining_correct:
            cost, mismatches = verb_recognition_pair_cost(
                user_analysis, correct_analyses[index], lexical_voice
            )
            ranked.append((cost, index, mismatches))
        _, best_index, mismatches = min(ranked, key=lambda item: (item[0], item[1]))
        remaining_correct.remove(best_index)
        pairs.append((user_analysis, correct_analyses[best_index], mismatches))

    # If the learner omitted an entire valid analysis, show that missing analysis
    # only in the correction row; the answer row stays empty for those cells.
    for index in sorted(remaining_correct):
        pairs.append((None, correct_analyses[index], set()))
    return pairs


def format_incorrect_verb_recognition_table_html(user_analyses, correct_analyses, lexical_voice):
    """Render a compact two-row comparison grid for an incorrect recognition answer."""
    pairs = pair_verb_recognition_analyses(
        user_analyses, correct_analyses, lexical_voice
    )
    if not pairs:
        return '<strong>Helytelen válasz.</strong>'

    explicit_template = set()
    for user_analysis in user_analyses:
        explicit_template.update(user_analysis.get("_explicit_categories", set()))
    # Keep canonical order and never invent parameters that were inferred.
    template_categories = [
        category for category in VERB_ANALYSIS_CATEGORY_ORDER
        if category in explicit_template
    ]

    answer_cells = []
    correction_cells = []
    spacer = '<td aria-hidden="true" style="width:0.8rem;padding:0;"></td>'

    for pair_index, (user_analysis, correct_analysis, mismatches) in enumerate(pairs):
        categories = template_categories
        if user_analysis is not None:
            categories = [
                category for category in VERB_ANALYSIS_CATEGORY_ORDER
                if category in user_analysis.get("_explicit_categories", set())
            ]
        if pair_index:
            answer_cells.append(spacer)
            correction_cells.append(spacer)

        for category in categories:
            cell_style = 'padding:0.08rem 0.28rem;text-align:center;white-space:nowrap;font-weight:800;'
            if user_analysis is None:
                answer_cells.append(f'<td style="{cell_style}">&nbsp;</td>')
                if correct_analysis is not None and category in correct_analysis:
                    correction = html.escape(
                        verb_recognition_parameter_label(correct_analysis, category, correction=True)
                    )
                else:
                    correction = '&mdash;'
                correction_cells.append(
                    f'<td style="{cell_style}color:inherit;">{correction}</td>'
                )
                continue

            if category not in user_analysis:
                answer_cells.append(f'<td style="{cell_style}">&nbsp;</td>')
                correction_cells.append(f'<td style="{cell_style}">&nbsp;</td>')
                continue

            user_text = html.escape(
                verb_recognition_parameter_label(user_analysis, category)
            )
            is_wrong = category in mismatches
            color = '#b3261e' if is_wrong else '#188038'
            answer_cells.append(
                f'<td style="{cell_style}color:{color};">{user_text}</td>'
            )

            if not is_wrong:
                correction_cells.append(f'<td style="{cell_style}">&nbsp;</td>')
            elif correct_analysis is not None and category in correct_analysis:
                correction = html.escape(
                    verb_recognition_parameter_label(correct_analysis, category, correction=True)
                )
                correction_cells.append(
                    f'<td style="{cell_style}color:inherit;">{correction}</td>'
                )
            else:
                correction_cells.append(
                    f'<td style="{cell_style}color:inherit;">&mdash;</td>'
                )

    label_style = 'padding:0.08rem 0.55rem 0.08rem 0;text-align:right;white-space:nowrap;font-weight:700;'
    return (
        '<div style="max-width:100%;overflow-x:auto;">'
        '<table role="presentation" style="border-collapse:collapse;border:0;background:transparent;line-height:1.55;">'
        '<tbody>'
        f'<tr><td style="{label_style}">Helytelen válasz:</td>{"".join(answer_cells)}</tr>'
        f'<tr><td style="{label_style}">Helyesen:</td>{"".join(correction_cells)}</tr>'
        '</tbody></table></div>'
    )
'''
text = text[:start] + new_block + text[end:]

old = '''                        if evaluation == "incorrect":
                            correct_text = ", ".join(
                                format_correct_verb_recognition_analysis_html(
                                    analysis,
                                    parsed_analyses["analyses"],
                                    lexical_voice,
                                )
                                for analysis in recognition_correct_analyses
                            )
                        else:
                            correct_text = ", ".join(
                                html.escape(format_correct_verb_recognition_analysis(analysis))
                                for analysis in recognition_correct_analyses
                            )
'''
new = '''                        if evaluation == "incorrect":
                            incorrect_feedback_html = format_incorrect_verb_recognition_table_html(
                                parsed_analyses["analyses"],
                                recognition_correct_analyses,
                                lexical_voice,
                            )
                        else:
                            correct_text = ", ".join(
                                html.escape(format_correct_verb_recognition_analysis(analysis))
                                for analysis in recognition_correct_analyses
                            )
'''
replace_once(old, new, 'build incorrect feedback grid')

old = '''                        else:
                            st.session_state.result_message = "**Incorrect. Better luck next time!**"
                            label = "A helyes válasz" if len(recognition_correct_analyses) == 1 else "A helyes válaszok"
                            st.session_state.answer_display_message = feedback_box(
                                f"<strong>Helytelen válasz. {label}:</strong> <span style='font-weight:900;'>{correct_text}</span>",
                                "incorrect",
                            )
'''
new = '''                        else:
                            st.session_state.result_message = "**Incorrect. Better luck next time!**"
                            st.session_state.answer_display_message = feedback_box(
                                incorrect_feedback_html,
                                "incorrect",
                            )
'''
replace_once(old, new, 'use incorrect feedback grid')

compile(text, 'verbs.py', 'exec')
path.write_text(text)
