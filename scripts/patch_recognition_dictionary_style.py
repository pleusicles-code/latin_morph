from pathlib import Path

path = Path('verbs.py')
text = path.read_text()
old = "                question_html += f' <strong><em>{html.escape(verb_dictionary_entry(verb))}</em></strong>'\n"
new = "                question_html += f' <em>({html.escape(verb_dictionary_entry(verb))})</em>'\n"
if text.count(old) != 1:
    raise SystemExit(f'Expected exactly one recognition dictionary style line, found {text.count(old)}')
text = text.replace(old, new)
compile(text, 'verbs.py', 'exec')
path.write_text(text)
