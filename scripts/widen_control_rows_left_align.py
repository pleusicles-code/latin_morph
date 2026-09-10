from pathlib import Path

# 1. Left-align the global 1300px main content area.
path = Path('streamlit_app.py')
text = path.read_text()
old = '''            .block-container {
                max-width: 1300px !important;
                padding-top: 2rem !important;
                margin-top: 0 !important;
            }
'''
new = '''            .block-container {
                max-width: 1300px !important;
                padding-top: 2rem !important;
                margin-top: 0 !important;
                margin-left: 0 !important;
                margin-right: auto !important;
            }
'''
if text.count(old) != 1:
    raise SystemExit(f'Expected one global block-container rule, found {text.count(old)}')
text = text.replace(old, new)
compile(text, 'streamlit_app.py', 'exec')
path.write_text(text)

# 2. Widen the New question / results / Reset score control rows everywhere
#    the common three-column pattern is used.
old_cols = 'new_question_col, results_col, score_col = st.columns(3, gap="medium", vertical_alignment="top")'
new_cols = 'new_question_col, results_col, score_col = st.columns([5, 2, 5], gap="large", vertical_alignment="top")'
changed = []
for file_path in sorted(Path('.').glob('*.py')):
    source = file_path.read_text()
    count = source.count(old_cols)
    if count:
        source = source.replace(old_cols, new_cols)
        compile(source, str(file_path), 'exec')
        file_path.write_text(source)
        changed.append((str(file_path), count))

if not changed:
    raise SystemExit('No common exercise control-row patterns found')
print('Changed control rows:', changed)
