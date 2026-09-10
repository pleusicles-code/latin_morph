from pathlib import Path
import re

files = [
    Path('nouns.py'),
    Path('verbs.py'),
    Path('identify_stems.py'),
    Path('recognize_declension.py'),
    Path('recognize_pos.py'),
]

old_cols = 'new_question_col, results_col, score_col = st.columns([5, 2, 5], gap="large", vertical_alignment="top")'
new_cols = 'new_question_col, results_col, score_col = st.columns([6, 1, 6], gap="medium", vertical_alignment="top")'

score_pattern = re.compile(
    r'''st\.markdown\(\s*f["']Jelenlegi pontszám: \*\*\{st\.session_state\.current_score\}\*\* / \*\*\{st\.session_state\.total_questions\}\*\*["']\s*\)''',
    re.MULTILINE,
)
score_replacement = '''st.markdown(
                f'<div style="text-align:right;">Jelenlegi pontszám: <strong>{st.session_state.current_score}</strong> / <strong>{st.session_state.total_questions}</strong></div>',
                unsafe_allow_html=True,
            )'''

col_changes = 0
score_changes = 0
for path in files:
    text = path.read_text()
    col_count = text.count(old_cols)
    if col_count:
        text = text.replace(old_cols, new_cols)
        col_changes += col_count

    text, count = score_pattern.subn(score_replacement, text)
    score_changes += count

    compile(text, str(path), 'exec')
    path.write_text(text)

if col_changes != len(files):
    raise SystemExit(f'Expected {len(files)} control-row changes, got {col_changes}')
if score_changes != len(files):
    raise SystemExit(f'Expected {len(files)} score alignment changes, got {score_changes}')

print(f'Updated {col_changes} control rows and {score_changes} score messages')
