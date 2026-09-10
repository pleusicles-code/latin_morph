from pathlib import Path

path = Path('verbs.py')
text = path.read_text()

repls = []
repls.append((
'''import ast\nimport html\n''',
'''import ast\nimport html\nimport unicodedata\n'''
))
repls.append((
'''from exercise_presets import (bool_setting, list_setting, resolve_exercise_settings, initialize_widget_state,\n                              widget_key, url_preset_active, exercise_link_popover)\n''',
'''from exercise_presets import (bool_setting, choice_setting, list_setting, resolve_exercise_settings, initialize_widget_state,\n                              widget_key, url_preset_active, exercise_link_popover)\n'''
))
repls.append((
'''def heavy(text, italic=False):\n    escaped = html.escape(str(text))\n    if italic:\n        escaped = f"<em>{escaped}</em>"\n    return f'<span style="font-weight:900;">{escaped}</span>'\n\n\n''',
'''def heavy(text, italic=False):\n    escaped = html.escape(str(text))\n    if italic:\n        escaped = f"<em>{escaped}</em>"\n    return f'<span style="font-weight:900;">{escaped}</span>'\n\n\nLATIN_VOWELS = set("aeiouy")\nLATIN_DIPHTHONGS = {"ae", "au", "oe", "ei", "eu", "ui"}\n\n\ndef hungarian_article(word):\n    normalized = "".join(\n        char for char in unicodedata.normalize("NFD", str(word).lower())\n        if unicodedata.category(char) != "Mn"\n    )\n    if not normalized or normalized[0] not in LATIN_VOWELS:\n        return "a"\n    if len(normalized) > 1 and normalized[1] in LATIN_VOWELS:\n        return "az" if normalized[:2] in LATIN_DIPHTHONGS else "a"\n    return "az"\n\n\n'''
))
repls.append((
'''exercise_schema = {\n    "show_principal_parts": bool_setting(False),\n    "show_stems": bool_setting(False),\n''',
'''exercise_schema = {\n    "exercise_type": choice_setting("inflect", ["inflect", "recognize"]),\n    "indicate_multiple_answers": bool_setting(False),\n    "award_partial_credit": bool_setting(False),\n    "show_principal_parts": bool_setting(False),\n    "show_stems": bool_setting(False),\n'''
))
repls.append((
'''with option_expander:\n    verb_options_col,options_col = st.columns([3,2])\n\nwith options_col:\n''',
'''with option_expander:\n    verb_options_col,options_col = st.columns([3,2])\n\nwith verb_options_col:\n    exercise_type = st.radio(\n        "Feladattípus:",\n        options=["inflect", "recognize"],\n        format_func=lambda value: {\n            "inflect": "Ragozás",\n            "recognize": "Alakfelismerés",\n        }[value],\n        horizontal=True,\n        key=widget_key(page_id, "exercise_type"),\n        on_change=radio_change,\n    )\n\nwith options_col:\n'''
))
old_options = '''    st.markdown("Opciók:", help="Ezeket a beállításokat gyakorlás közben is bármikor módosíthatod.")\n    st.checkbox("Hosszú magánhangzók ellenőrzése?",\n                help="Ha be van jelölve, a hosszú magánhangzók hibás jelölése hibás válasznak számít. Ha nincs bejelölve, a hosszúságjelek használhatók, de a program nem értékeli őket.",\n                key="verbs_enforce_macrons",\n                on_change=send_setting,\n                args=(switch_verb_macrons,),\n                kwargs={"streamlit_page":"verbs.py","setting_name":"verbs_enforce_macrons"},\n                # value=st.session_state.enforce_macrons["verbs_enforce_macrons"]\n                )\n    macrons = st.session_state.verbs_enforce_macrons\n    if macrons:\n        st.markdown("A hosszú magánhangzók innen másolhatók:")\n        st.code("āēīōū", language=None)\n\n    st.html('<hr style="border-top: 1px dotted; border-bottom: none;">')\n\n    show_principal_parts = st.checkbox("Szótári alak megjelenítése?",\n'''
new_options = '''    st.markdown("Opciók:", help="Ezeket a beállításokat gyakorlás közben is bármikor módosíthatod.")\n    indicate_multiple_answers = False\n    award_partial_credit = False\n    if exercise_type == "inflect":\n        st.checkbox("Hosszú magánhangzók ellenőrzése?",\n                    help="Ha be van jelölve, a hosszú magánhangzók hibás jelölése hibás válasznak számít. Ha nincs bejelölve, a hosszúságjelek használhatók, de a program nem értékeli őket.",\n                    key="verbs_enforce_macrons",\n                    on_change=send_setting,\n                    args=(switch_verb_macrons,),\n                    kwargs={"streamlit_page":"verbs.py","setting_name":"verbs_enforce_macrons"},\n                    )\n        macrons = st.session_state.verbs_enforce_macrons\n        if macrons:\n            st.markdown("A hosszú magánhangzók innen másolhatók:")\n            st.code("āēīōū", language=None)\n    else:\n        indicate_multiple_answers = st.checkbox(\n            "Több helyes válaszlehetőség jelzése?",\n            help="Ha be van kapcsolva, a kérdés külön jelzi, ha az adott alaknak több helyes elemzése van.",\n            key=widget_key(page_id, "indicate_multiple_answers"),\n        )\n        award_partial_credit = st.checkbox(\n            "Részpont adása?",\n            help="Ha be van kapcsolva, a részben helyes válasz fél pontot ér; különben csak a teljesen helyes válaszért jár pont.",\n            key=widget_key(page_id, "award_partial_credit"),\n        )\n\n    st.html('<hr style="border-top: 1px dotted; border-bottom: none;">')\n\n    show_principal_parts = st.checkbox("Szótári alak megjelenítése?",\n'''
repls.append((old_options, new_options))
repls.append((
'''current_exercise_settings = {\n    "show_principal_parts": show_principal_parts,\n    "show_stems": show_stems,\n''',
'''current_exercise_settings = {\n    "exercise_type": exercise_type,\n    "indicate_multiple_answers": indicate_multiple_answers,\n    "award_partial_credit": award_partial_credit,\n    "show_principal_parts": show_principal_parts,\n    "show_stems": show_stems,\n'''
))
old_prompt = '''        verb_label = verb_dictionary_entry(verb) if show_principal_parts else verb\n        article = "az" if verb_label and verb_label[0].casefold() in "aáeéiíoóöőuúüű" else "a"\n        question_html = (\n            f'Add meg {article} <strong><em>{html.escape(verb_label)}</em></strong> ige '\n            f'<strong>{html.escape(form_label)}</strong> alakját!'\n        )\n\n        stems = verb_stem_display(verb) if show_stems else []\n'''
new_prompt = '''        verb_label = verb_dictionary_entry(verb) if show_principal_parts else verb\n        if exercise_type == "recognize":\n            displayed_form = verb_form[0] if isinstance(verb_form, list) else verb_form\n            form_article = hungarian_article(displayed_form)\n            question_html = (\n                f'Milyen alak lehet {form_article} <strong><em>{html.escape(displayed_form)}</em></strong>?'\n            )\n            if show_principal_parts:\n                question_html += f' <strong><em>{html.escape(verb_dictionary_entry(verb))}</em></strong>'\n        else:\n            article = hungarian_article(verb_label)\n            question_html = (\n                f'Add meg {article} <strong><em>{html.escape(verb_label)}</em></strong> ige '\n                f'<strong>{html.escape(form_label)}</strong> alakját!'\n            )\n\n        stems = verb_stem_display(verb) if show_stems else []\n'''
repls.append((old_prompt, new_prompt))

for old, new in repls:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'Expected exactly one match, found {count}: {old[:80]!r}')
    text = text.replace(old, new)

compile(text, 'verbs.py', 'exec')
path.write_text(text)
