from pathlib import Path

path = Path('verbs.py')
text = path.read_text()
old = "    st.html('<hr style=\"border-top: 1px dotted; border-bottom: none;\">')\n\n"
if text.count(old) != 1:
    raise SystemExit(f'Expected exactly one separator, found {text.count(old)}')
text = text.replace(old, "")
compile(text, 'verbs.py', 'exec')
path.write_text(text)
