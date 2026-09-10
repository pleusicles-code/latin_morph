from pathlib import Path

path = Path('streamlit_app.py')
text = path.read_text()
old = '''            [data-testid="stMainBlockContainer"],
            .stMainBlockContainer,
            .block-container {
                max-width: 950px !important;
            }
'''
new = '''            [data-testid="stMainBlockContainer"],
            .stMainBlockContainer,
            .block-container {
                max-width: 950px !important;
                padding-top: 1.5rem !important;
            }
'''
if text.count(old) != 1:
    raise SystemExit(f'Expected exactly one global layout CSS block, found {text.count(old)}')
text = text.replace(old, new)
compile(text, 'streamlit_app.py', 'exec')
path.write_text(text)
