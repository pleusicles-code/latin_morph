from pathlib import Path

path = Path('verbs.py')
text = path.read_text()
old = '''    def spacer():
        return '<div aria-hidden="true" style="padding:0 0.16rem;color:#111;font-weight:700;white-space:nowrap;">/</div>'
'''
new = '''    def spacer(show_slash=True):
        content = "/" if show_slash else "&nbsp;"
        return f'<div aria-hidden="true" style="padding:0 0.16rem;color:#111;font-weight:700;white-space:nowrap;">{content}</div>'
'''
if text.count(old) != 1:
    raise SystemExit(f'Expected spacer definition once, found {text.count(old)}')
text = text.replace(old, new)
old = '''        if pair_index:
            answer_cells.append(spacer())
            correction_cells.append(spacer())
            column_count += 1
'''
new = '''        if pair_index:
            answer_cells.append(spacer(True))
            correction_cells.append(spacer(False))
            column_count += 1
'''
if text.count(old) != 1:
    raise SystemExit(f'Expected spacer calls once, found {text.count(old)}')
text = text.replace(old, new)
compile(text, 'verbs.py', 'exec')
path.write_text(text)
