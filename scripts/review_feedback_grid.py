from pathlib import Path

path = Path('verbs.py')
text = path.read_text()
old = 'color:inherit;'
count = text.count(old)
if count != 3:
    raise SystemExit(f'Expected 3 correction color declarations, found {count}')
text = text.replace(old, 'color:#111;')
compile(text, 'verbs.py', 'exec')
path.write_text(text)
