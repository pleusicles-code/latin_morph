from pathlib import Path

path = Path('streamlit_app.py')
text = path.read_text()
old = '                padding-top: 1.5rem !important;\n'
new = '                padding-top: 0.5rem !important;\n'
if text.count(old) != 1:
    raise SystemExit(f'Expected exactly one 1.5rem padding rule, found {text.count(old)}')
text = text.replace(old, new)
compile(text, 'streamlit_app.py', 'exec')
path.write_text(text)
