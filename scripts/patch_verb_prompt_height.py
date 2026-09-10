from pathlib import Path

path = Path('verbs.py')
text = path.read_text()
old = '        prompt_height = 104 if stems else 72\n'
new = '        prompt_height = 114 if stems else 82\n'
if text.count(old) != 1:
    raise SystemExit(f'Expected exactly one prompt height line, found {text.count(old)}')
text = text.replace(old, new)
compile(text, 'verbs.py', 'exec')
path.write_text(text)
