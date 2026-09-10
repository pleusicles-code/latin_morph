from pathlib import Path

path = Path('verbs.py')
text = path.read_text()

repls = [
    (
        '    "exercise_type": choice_setting("inflect", ["inflect", "recognize"]),\n    "indicate_multiple_answers": bool_setting(False),\n',
        '    "exercise_type": choice_setting("inflect", ["inflect", "recognize"]),\n    "print_macrons": bool_setting(False),\n    "indicate_multiple_answers": bool_setting(False),\n'
    ),
    (
        '    indicate_multiple_answers = False\n    award_partial_credit = False\n',
        '    print_macrons = False\n    indicate_multiple_answers = False\n    award_partial_credit = False\n'
    ),
    (
        '    else:\n        indicate_multiple_answers = st.checkbox(\n',
        '    else:\n        print_macrons = st.checkbox(\n            "Hosszú magánhangzók jelölése?",\n            help="Ha be van kapcsolva, a kérdésben szereplő igealak jelöli a magánhangzók hosszúságát. Ez ritkán két, egyébként azonos írásképű alakot is megkülönböztethet.",\n            key=widget_key(page_id, "print_macrons"),\n        )\n        indicate_multiple_answers = st.checkbox(\n'
    ),
    (
        'current_exercise_settings = {\n    "exercise_type": exercise_type,\n    "indicate_multiple_answers": indicate_multiple_answers,\n',
        'current_exercise_settings = {\n    "exercise_type": exercise_type,\n    "print_macrons": print_macrons,\n    "indicate_multiple_answers": indicate_multiple_answers,\n'
    ),
    (
        '            displayed_form = verb_form[0] if isinstance(verb_form, list) else verb_form\n            form_article = hungarian_article(displayed_form)\n',
        '            displayed_form = verb_form[0] if isinstance(verb_form, list) else verb_form\n            if not print_macrons:\n                displayed_form = remove_macrons(displayed_form)\n            form_article = hungarian_article(displayed_form)\n'
    ),
]

for old, new in repls:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'Expected exactly one match, found {count}: {old[:100]!r}')
    text = text.replace(old, new)

compile(text, 'verbs.py', 'exec')
path.write_text(text)
