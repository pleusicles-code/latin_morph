from pathlib import Path

path = Path('verbs.py')
text = path.read_text()
start = text.index('def format_incorrect_verb_recognition_table_html(')
end = text.index('\n\ndef canonical_verb_analysis(', start)
old = text[start:end]
new = '''def format_incorrect_verb_recognition_table_html(user_analyses, correct_analyses, lexical_voice):
    """Render a compact two-row comparison grid for an incorrect recognition answer."""
    pairs = pair_verb_recognition_analyses(
        user_analyses, correct_analyses, lexical_voice
    )
    if not pairs:
        return '<strong>Helytelen válasz.</strong>'

    explicit_template = set()
    for user_analysis in user_analyses:
        explicit_template.update(user_analysis.get("_explicit_categories", set()))
    template_categories = [
        category for category in VERB_ANALYSIS_CATEGORY_ORDER
        if category in explicit_template
    ]

    answer_cells = []
    correction_cells = []
    column_count = 1  # label column

    def cell(content, *, color=None, extra=''):
        style = (
            'padding:0 0.14rem;text-align:center;white-space:nowrap;'
            'font-weight:800;background:transparent;min-width:max-content;'
        )
        if color:
            style += f'color:{color};'
        style += extra
        return f'<div style="{style}">{content}</div>'

    def spacer():
        return '<div aria-hidden="true" style="width:0.35rem;min-width:0.35rem;"></div>'

    for pair_index, (user_analysis, correct_analysis, mismatches) in enumerate(pairs):
        categories = template_categories
        if user_analysis is not None:
            categories = [
                category for category in VERB_ANALYSIS_CATEGORY_ORDER
                if category in user_analysis.get("_explicit_categories", set())
            ]

        if pair_index:
            answer_cells.append(spacer())
            correction_cells.append(spacer())
            column_count += 1

        for category in categories:
            column_count += 1
            if user_analysis is None:
                answer_cells.append(cell('&nbsp;'))
                if correct_analysis is not None and category in correct_analysis:
                    correction = html.escape(
                        verb_recognition_parameter_label(correct_analysis, category, correction=True)
                    )
                else:
                    correction = '&mdash;'
                correction_cells.append(cell(correction, color='#111'))
                continue

            if category not in user_analysis:
                answer_cells.append(cell('&nbsp;'))
                correction_cells.append(cell('&nbsp;'))
                continue

            user_text = html.escape(
                verb_recognition_parameter_label(user_analysis, category)
            )
            is_wrong = category in mismatches
            answer_cells.append(
                cell(user_text, color='#b3261e' if is_wrong else '#188038')
            )

            if not is_wrong:
                correction_cells.append(cell('&nbsp;'))
            elif correct_analysis is not None and category in correct_analysis:
                correction = html.escape(
                    verb_recognition_parameter_label(correct_analysis, category, correction=True)
                )
                correction_cells.append(cell(correction, color='#111'))
            else:
                correction_cells.append(cell('&mdash;', color='#111'))

    grid_columns = 'max-content ' + ' '.join('max-content' for _ in range(column_count - 1))
    label_style = (
        'padding:0 0.34rem 0 0;text-align:right;white-space:nowrap;'
        'font-weight:700;background:transparent;'
    )
    return (
        '<div style="max-width:100%;overflow-x:auto;">'
        f'<div role="presentation" style="display:grid;grid-template-columns:{grid_columns};'
        'grid-auto-rows:min-content;align-items:baseline;line-height:1.4;background:transparent;">'
        f'<div style="{label_style}">Helytelen válasz:</div>{"".join(answer_cells)}'
        f'<div style="{label_style}">Helyesen:</div>{"".join(correction_cells)}'
        '</div></div>'
    )
'''
text = text[:start] + new + text[end:]
compile(text, 'verbs.py', 'exec')
path.write_text(text)
