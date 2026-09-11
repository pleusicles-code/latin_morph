from pathlib import Path

path = Path('verbs.py')
text = path.read_text()
old = '    "irreg_selector": list_setting(master_irregular_verbs_list, master_irregular_verbs_list),\n'
new = '    "irreg_selector": list_setting(["sum"], master_irregular_verbs_list),\n'
if text.count(old) != 1:
    raise SystemExit(f'Expected irreg selector schema once, found {text.count(old)}')
text = text.replace(old, new)
compile(text, 'verbs.py', 'exec')
path.write_text(text)
