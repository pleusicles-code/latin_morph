from pathlib import Path

path = Path('streamlit_app.py')
text = path.read_text()
old = '''            [data-testid="stMainBlockContainer"],
            .stMainBlockContainer,
            .block-container {
                max-width: 950px !important;
                padding-top: 0.5rem !important;
            }
'''
new = '''            [data-testid="stMainBlockContainer"],
            .stMainBlockContainer {
                max-width: 950px !important;
                padding-top: 0 !important;
            }

            .block-container {
                max-width: 950px !important;
                padding-top: 0 !important;
                margin-top: 0 !important;
            }
'''
if text.count(old) != 1:
    raise SystemExit(f'Expected exactly one global layout CSS block, found {text.count(old)}')
text = text.replace(old, new)
compile(text, 'streamlit_app.py', 'exec')
path.write_text(text)
