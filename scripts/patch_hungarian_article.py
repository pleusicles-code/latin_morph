from pathlib import Path

path = Path('verbs.py')
text = path.read_text()
old = '''        verb_label = verb_dictionary_entry(verb) if show_principal_parts else verb\n        question_html = (\n            f'Add meg a <strong><em>{html.escape(verb_label)}</em></strong> ige '\n            f'<strong>{html.escape(form_label)}</strong> alakját!'\n        )\n'''
new = '''        verb_label = verb_dictionary_entry(verb) if show_principal_parts else verb\n        article = "az" if verb_label and verb_label[0].casefold() in "aáeéiíoóöőuúüű" else "a"\n        question_html = (\n            f'Add meg {article} <strong><em>{html.escape(verb_label)}</em></strong> ige '\n            f'<strong>{html.escape(form_label)}</strong> alakját!'\n        )\n'''
if text.count(old) != 1:
    raise SystemExit(f'Expected exactly one question block, found {text.count(old)}')
text = text.replace(old, new)
compile(text, 'verbs.py', 'exec')
path.write_text(text)
