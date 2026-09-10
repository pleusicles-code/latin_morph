from pathlib import Path

path = Path('streamlit_app.py')
text = path.read_text()
old = 'max-width: 1200px !important;'
count = text.count(old)
if count != 2:
    raise SystemExit(f'Expected exactly two 1200px max-width rules, found {count}')
text = text.replace(old, 'max-width: 1300px !important;')
compile(text, 'streamlit_app.py', 'exec')
path.write_text(text)
