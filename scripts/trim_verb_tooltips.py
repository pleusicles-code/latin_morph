from pathlib import Path

path = Path('verbs.py')
text = path.read_text()
replacements = {
    'Az ige szótári alakjának (főalakjainak) megjelenítése.': 'Az ige szótári alakjának megjelenítése.',
    'A jelenlegi ige töveinek megjelenítése a kérdés alatt.': 'Az ige töveinek megjelenítése a kérdés alatt.',
}
for old, new in replacements.items():
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'Expected 1 occurrence of {old!r}, found {count}')
    text = text.replace(old, new)
compile(text, 'verbs.py', 'exec')
path.write_text(text)
