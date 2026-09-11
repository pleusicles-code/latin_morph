from pathlib import Path

# 1. Always clear the shared answer field when generating a new question.
utils = Path('utils.py')
text = utils.read_text()
old = '''    st.session_state.answer_checked = False
    st.session_state.answer_to_check = ""
    st.session_state.result_message = ""
'''
new = '''    st.session_state.answer_checked = False
    st.session_state.answer_to_check = ""
    st.session_state.answer_input = ""
    st.session_state.result_message = ""
'''
if text.count(old) != 1:
    raise SystemExit(f'utils new_question block: expected 1, found {text.count(old)}')
utils.write_text(text.replace(old, new))

# 2. Equal-width three-slot bottom control rows in every current exercise page.
exercise_files = [
    'identify_stems.py',
    'nouns.py',
    'recognize_declension.py',
    'recognize_pos.py',
    'verbs.py',
]
for filename in exercise_files:
    path = Path(filename)
    text = path.read_text()
    count = text.count('st.columns([6, 1, 6], gap="medium", vertical_alignment="top")')
    if count != 1:
        raise SystemExit(f'{filename}: expected one [6,1,6] control row, found {count}')
    text = text.replace(
        'st.columns([6, 1, 6], gap="medium", vertical_alignment="top")',
        'st.columns([1, 1, 1], gap="medium", vertical_alignment="top")',
    )
    path.write_text(text)

# 3. Verb recognition / feedback refinements.
path = Path('verbs.py')
text = path.read_text()

# Imperatives never require an explicit voice marker; supplied voice is still checked.
old = '''        if lexical_voice not in ["dep", "semidep"]:
            required.append("voice")
'''
new = '''        if lexical_voice not in ["dep", "semidep"] and analysis.get("mood") != "impv":
            required.append("voice")
'''
if text.count(old) != 1:
    raise SystemExit(f'verb required voice block: expected 1, found {text.count(old)}')
text = text.replace(old, new)

# Multiple correct recognition analyses should be inline and comma-delimited.
old = '''                        correct_text = "<br>".join(
                            html.escape(format_correct_verb_recognition_analysis(analysis))
                            for analysis in recognition_correct_analyses
                        )
'''
new = '''                        correct_text = ", ".join(
                            html.escape(format_correct_verb_recognition_analysis(analysis))
                            for analysis in recognition_correct_analyses
                        )
'''
if text.count(old) != 1:
    raise SystemExit(f'verb correct_text join: expected 1, found {text.count(old)}')
text = text.replace(old, new)

# Recognition: message bold, correct form heavier.
old = '''                            st.session_state.answer_display_message = feedback_box(
                                f"<strong>Helytelen válasz. {label}: {correct_text}</strong>",
                                "incorrect",
                            )
'''
new = '''                            st.session_state.answer_display_message = feedback_box(
                                f"<strong>Helytelen válasz. {label}:</strong> <span style='font-weight:900;'>{correct_text}</span>",
                                "incorrect",
                            )
'''
if text.count(old) != 1:
    raise SystemExit(f'verb recognition incorrect block: expected 1, found {text.count(old)}')
text = text.replace(old, new)

# Inflection: don't wrap the already-heavy correct forms in the same <strong> as the message.
old = '''                            st.session_state.answer_display_message = feedback_box(
                                f"<strong>Helytelen válasz. {label}: {correct_html}.</strong>",
                                "incorrect",
                            )
'''
new = '''                            st.session_state.answer_display_message = feedback_box(
                                f"<strong>Helytelen válasz. {label}:</strong> {correct_html}.",
                                "incorrect",
                            )
'''
if text.count(old) != 1:
    raise SystemExit(f'verb inflection incorrect block: expected 1, found {text.count(old)}')
text = text.replace(old, new)

# Make the middle conjugation-table control fill its equal-width slot.
old = 'chart_popover = st.popover("Ragozási táblázat", type="primary", help=help_text)'
new = 'chart_popover = st.popover("Ragozási táblázat", type="primary", help=help_text, width="stretch")'
if text.count(old) != 1:
    raise SystemExit(f'verb chart popover: expected 1, found {text.count(old)}')
text = text.replace(old, new)

path.write_text(text)

# 4. In the other translated exercises, separate message weight from heavy correct forms.
# Guarded literal replacements cover their current incorrect-answer templates.
for filename in ['nouns.py', 'identify_stems.py', 'recognize_pos.py', 'recognize_declension.py']:
    path = Path(filename)
    text = path.read_text()
    text = text.replace(
        'f"<strong>Helytelen válasz. {label}: {correct_html}.</strong>"',
        'f"<strong>Helytelen válasz. {label}:</strong> {correct_html}."',
    )
    text = text.replace(
        'f"<strong>Helytelen válasz. A helyes válasz: {heavy(all_possible_text)}</strong>"',
        'f"<strong>Helytelen válasz. A helyes válasz:</strong> {heavy(all_possible_text)}"',
    )
    path.write_text(text)

# Syntax-check every modified file.
for filename in ['utils.py'] + exercise_files:
    compile(Path(filename).read_text(), filename, 'exec')
