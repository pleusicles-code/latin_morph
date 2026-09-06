from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path, old, new):
    p = ROOT / path
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one match, found {count}: {old[:100]!r}")
    p.write_text(text.replace(old, new, 1))


def clean(path):
    p = ROOT / path
    p.write_text("\n".join(line.rstrip() for line in p.read_text().splitlines()) + "\n")


def patch_verbs():
    path = "verbs.py"
    if "exercise_schema = {" in (ROOT / path).read_text():
        return
    replace_once(path,
        "from utils import radio_change, reset, new_question, remove_macrons, submit_and_check_answer, clear_page, send_setting, save_defaults, clear_defaults\n",
        "from utils import radio_change, reset, new_question, remove_macrons, submit_and_check_answer, clear_page, send_setting, save_defaults, clear_defaults\n"
        "from exercise_presets import (bool_setting, list_setting, resolve_exercise_settings, initialize_widget_state,\n"
        "                              widget_key, url_preset_active, exercise_link_popover)\n")
    replace_once(path,
'''conjugation_dict = {1: "1st (-āre)", \n                    2: "2nd (-ēre)", \n                    3: "3rd (-ere)", \n                    "3io": '3rd "io" (-ere)', \n                    4: "4th (-īre)"}\n''',
'''conjugation_dict = {1: "1st (-āre)",\n                    2: "2nd (-ēre)",\n                    3: "3rd (-ere)",\n                    "3io": '3rd "io" (-ere)',\n                    4: "4th (-īre)"}\n\nmaster_tense_list = ["pres","impf","fut","perf","plupf","fut_pf"]\nmaster_voice_list = ["act", "pass", "dep", "semidep"]\nmaster_mood_list = ["ind", "subj", "inf", "impv"]\nmaster_irregular_verbs_list = [key for key in complete_verb_vocab.keys() if complete_verb_vocab[key].get("irreg",{}).get("irreg") is True]\nexercise_schema = {\n    "show_principal_parts": bool_setting(False),\n    "conjugation_selector": list_setting(list(conjugation_dict.keys()), list(conjugation_dict.keys())),\n    "tense_selector": list_setting(master_tense_list, master_tense_list),\n    "voice_selector": list_setting(master_voice_list, master_voice_list),\n    "mood_selector": list_setting(master_mood_list, master_mood_list),\n    "irreg_selector": list_setting(master_irregular_verbs_list, master_irregular_verbs_list),\n    "irreg_only": bool_setting(False),\n    "fut_impv": bool_setting(False),\n}\nexercise_settings = resolve_exercise_settings(page_id, exercise_schema, defaults)\ninitialize_widget_state(page_id, exercise_settings)\npreset_active = url_preset_active(page_id)\n''')
    for old in [
        '    master_tense_list = ["pres","impf","fut","perf","plupf","fut_pf"]\n',
        '    master_voice_list = ["act", "pass", "dep", "semidep"]\n',
        '    master_mood_list = ["ind", "subj", "inf", "impv"]\n',
        '    master_irregular_verbs_list = [key for key in complete_verb_vocab.keys() if complete_verb_vocab[key].get("irreg",{}).get("irreg") is True]\n',
    ]:
        replace_once(path, old, "")
    replacements = [
        ('                                        value=defaults.get("show_principal_parts") if defaults.get("show_principal_parts") is not None else False)', '                                        key=widget_key(page_id, "show_principal_parts"))'),
        ('        default = defaults.get("conjugation_selector") if defaults.get("conjugation_selector") is not None else conjugation_dict.keys(),\n', '        key=widget_key(page_id, "conjugation_selector"),\n'),
        ('        default=defaults.get("tense_selector") if defaults.get("tense_selector") is not None else master_tense_list\n', '        key=widget_key(page_id, "tense_selector")\n'),
        ('                                    default = defaults.get("voice_selector") if defaults.get("voice_selector") is not None else master_voice_list,\n', '                                    key=widget_key(page_id, "voice_selector"),\n'),
        ('                                default=defaults.get("mood_selector") if defaults.get("mood_selector") is not None else master_mood_list)', '                                key=widget_key(page_id, "mood_selector"))'),
        ('                                    default=defaults.get("irreg_selector") if defaults.get("irreg_selector") is not None else master_irregular_verbs_list,\n', '                                    key=widget_key(page_id, "irreg_selector"),\n'),
        ('                                    value=defaults.get("irreg_only") if defaults.get("irreg_only") is not None else False,\n', '                                    key=widget_key(page_id, "irreg_only"),\n'),
        ('                                value=defaults.get("fut_impv") if defaults.get("fut_impv") is not None else False,\n', '                                key=widget_key(page_id, "fut_impv"),\n'),
    ]
    for old, new in replacements:
        replace_once(path, old, new)
    replace_once(path,
'''with options_col:\n    if st.user.is_logged_in:\n        set_defaults_col, clear_defaults_col = st.container(vertical_alignment="bottom", height="stretch").columns(2, vertical_alignment="center")\n''',
'''current_exercise_settings = {\n    "show_principal_parts": show_principal_parts,\n    "conjugation_selector": conjugation_selector,\n    "tense_selector": tense_selector,\n    "voice_selector": voice_selector,\n    "mood_selector": mood_selector,\n    "irreg_selector": irreg_selector,\n    "irreg_only": irreg_only,\n    "fut_impv": fut_impv,\n}\n\nwith options_col:\n    if st.user.is_logged_in:\n        set_defaults_col, clear_defaults_col, link_col = st.container(vertical_alignment="bottom", height="stretch").columns(3, vertical_alignment="center")\n''')
    replace_once(path,
'''                        kwargs={\n                            "show_principal_parts": show_principal_parts,\n                            "conjugation_selector": conjugation_selector,\n                            "tense_selector": tense_selector,\n                            "voice_selector": voice_selector,\n                            "mood_selector": mood_selector,\n                            "irreg_selector": irreg_selector,\n                            "irreg_only": irreg_only,\n                            "fut_impv": fut_impv\n                        },\n                        )\n''',
'''                        kwargs=current_exercise_settings,\n                        disabled=preset_active,\n                        )\n''')
    replace_once(path,
'''                        disabled=True if not defaults else False\n                        )\n\n\n## DEFINE AVAILABLE VERBS AND VERB ENDINGS ##\n''',
'''                        disabled=preset_active or not defaults\n                        )\n        with link_col:\n            exercise_link_popover(page_id, exercise_schema, current_exercise_settings)\n    else:\n        exercise_link_popover(page_id, exercise_schema, current_exercise_settings)\n\n\n## DEFINE AVAILABLE VERBS AND VERB ENDINGS ##\n''')
    clean(path)


def patch_adjectives():
    path = "adjectives.py"
    if "exercise_schema = {" in (ROOT / path).read_text():
        return
    replace_once(path,
        "from utils import reset, new_question, submit_and_check_answer, clear_page, remove_macrons, send_setting, save_defaults, clear_defaults\n",
        "from utils import reset, new_question, submit_and_check_answer, clear_page, remove_macrons, send_setting, save_defaults, clear_defaults\n"
        "from exercise_presets import (bool_setting, choice_setting, list_setting, resolve_exercise_settings,\n"
        "                              initialize_widget_state, widget_key, url_preset_active, exercise_link_popover)\n")
    marker = '''}\n\noption_expander = st.expander("Settings", expanded=True)\n'''
    insert = '''}\n\nmaster_decl_list = [(1,2), 3]\nmaster_degree_list = list(adj_abbrevs["degree"].keys())\nmaster_cardinal_list = list({k:v for k,v in adj_vocab.items() if v.get("cardinal")}.keys())\nexercise_schema = {\n    "declension": choice_setting("random", {"random": "random", "1-2": (1,2), "3": 3}),\n    "degree_list": list_setting(master_degree_list, master_degree_list),\n    "incl_cardinals": bool_setting(True),\n    "cardinal_radio": choice_setting("No", ["No", "Yes"]),\n    "cardinal_select": list_setting(master_cardinal_list, master_cardinal_list),\n    "incl_pronominals": bool_setting(True),\n    "incl_cons_stems": bool_setting(True),\n    "incl_adv": bool_setting(True),\n    "dictionary_entry": bool_setting(False),\n    "irreg_alert": bool_setting(False),\n}\nexercise_settings = resolve_exercise_settings(page_id, exercise_schema, defaults)\ninitialize_widget_state(page_id, exercise_settings)\npreset_active = url_preset_active(page_id)\n\noption_expander = st.expander("Settings", expanded=True)\n'''
    replace_once(path, marker, insert)
    replace_once(path, '    master_decl_list = [(1,2), 3]\n', '')
    replace_once(path, '    master_degree_list = list(adj_abbrevs["degree"].keys())\n', '')
    replacements = [
        ('                        index=(["random"]+[decl for decl in master_decl_list]).index(defaults.get("declension")) if defaults.get("declension") is not None else 0,\n', '                        key=widget_key(page_id, "declension"),\n'),
        ('        default=defaults.get("degree_list") if defaults.get("degree_list") is not None else [deg for deg in master_degree_list],\n', '        key=widget_key(page_id, "degree_list"),\n'),
        ('                                    value=defaults.get("incl_cardinals") if defaults.get("incl_cardinals") is not None else True, \n', '                                    key=widget_key(page_id, "incl_cardinals"),\n'),
        ('                                    index=["No","Yes"].index(defaults.get("cardinal_radio")) if defaults.get("cardinal_radio") is not None else 0,\n', '                                    key=widget_key(page_id, "cardinal_radio"),\n'),
        ('                                            default=defaults.get("cardinal_select") if defaults.get("cardinal_select") is not None else {k:v for k,v in adj_vocab.items() if v.get("cardinal")}.keys(),\n', '                                            key=widget_key(page_id, "cardinal_select"),\n'),
        ('                        value=defaults.get("incl_pronominals") if defaults.get("incl_pronominals") is not None else True, \n', '                        key=widget_key(page_id, "incl_pronominals"),\n'),
        ('                                    value=defaults.get("incl_cons_stems") if defaults.get("incl_cons_stems") is not None else True, \n', '                                    key=widget_key(page_id, "incl_cons_stems"),\n'),
        ('                        value=defaults.get("incl_adv") if defaults.get("incl_adv") is not None else True, \n', '                        key=widget_key(page_id, "incl_adv"),\n'),
        ('                                    value=defaults.get("dictionary_entry") if defaults.get("dictionary_entry") is not None else False,\n', '                                    key=widget_key(page_id, "dictionary_entry"),\n'),
        ('                                value=defaults.get("irreg_alert") if defaults.get("irreg_alert") is not None else False,\n', '                                key=widget_key(page_id, "irreg_alert"),\n'),
    ]
    for old, new in replacements:
        replace_once(path, old, new)
    replace_once(path,
'''    if st.user.is_logged_in:\n        set_defaults_col, clear_defaults_col = st.container(vertical_alignment="bottom", height="stretch").columns(2, vertical_alignment="center")\n''',
'''    current_exercise_settings = {\n        "declension": declension,\n        "degree_list": degree_list,\n        "incl_cardinals": incl_cardinals,\n        "cardinal_radio": cardinal_radio,\n        "cardinal_select": cardinal_select,\n        "incl_pronominals": incl_pronominals,\n        "incl_cons_stems": incl_cons_stems,\n        "incl_adv": incl_adv,\n        "dictionary_entry": dictionary_entry,\n        "irreg_alert": irreg_alert,\n    }\n    if st.user.is_logged_in:\n        set_defaults_col, clear_defaults_col, link_col = st.container(vertical_alignment="bottom", height="stretch").columns(3, vertical_alignment="center")\n''')
    replace_once(path,
'''                        kwargs={\n                            "declension": declension,\n                            "degree_list": degree_list,\n                            "incl_cardinals": incl_cardinals,\n                            "cardinal_radio": cardinal_radio,\n                            "cardinal_select": cardinal_select,\n                            "incl_pronominals": incl_pronominals,\n                            "incl_cons_stems": incl_cons_stems,\n                            "incl_adv": incl_adv,\n                            "dictionary_entry": dictionary_entry,\n                            "irreg_alert": irreg_alert,\n                            }\n                        )\n''',
'''                        kwargs=current_exercise_settings,\n                        disabled=preset_active\n                        )\n''')
    replace_once(path,
'''                        disabled=True if not defaults else False\n                        )\n\n\n## DEFINE AVAILABLE ADJECTIVES AND ADJ/ADV ENDINGS ##\n''',
'''                        disabled=preset_active or not defaults\n                        )\n        with link_col:\n            exercise_link_popover(page_id, exercise_schema, current_exercise_settings)\n    else:\n        exercise_link_popover(page_id, exercise_schema, current_exercise_settings)\n\n\n## DEFINE AVAILABLE ADJECTIVES AND ADJ/ADV ENDINGS ##\n''')
    clean(path)


def patch_verbal_adj():
    path = "verbal_adj.py"
    if "exercise_schema = {" in (ROOT / path).read_text():
        return
    replace_once(path,
        "from utils import reset, new_question, submit_and_check_answer, clear_page, remove_macrons, send_setting, save_defaults, clear_defaults\n",
        "from utils import reset, new_question, submit_and_check_answer, clear_page, remove_macrons, send_setting, save_defaults, clear_defaults\n"
        "from exercise_presets import (bool_setting, list_setting, resolve_exercise_settings, initialize_widget_state,\n"
        "                              widget_key, url_preset_active, exercise_link_popover)\n")
    replace_once(path,
'''conjugation_dict = {1: "1st (-āre)", \n                    2: "2nd (-ēre)", \n                    3: "3rd (-ere)", \n                    "3io": '3rd "io" (-ere)', \n                    4: "4th (-īre)"}\n''',
'''conjugation_dict = {1: "1st (-āre)",\n                    2: "2nd (-ēre)",\n                    3: "3rd (-ere)",\n                    "3io": '3rd "io" (-ere)',\n                    4: "4th (-īre)"}\n\nmaster_ptc_list = ["pap", "ppp", "fap", "gdv"]\nmaster_voice_list = ["act", "dep", "semidep"]\nmaster_irregular_verbs_list = [key for key in complete_verb_vocab.keys() if complete_verb_vocab[key].get("irreg",{}).get("irreg") is True]\nif "mālō" in master_irregular_verbs_list:\n    master_irregular_verbs_list.remove("mālō")\nexercise_schema = {\n    "show_principal_parts": bool_setting(False),\n    "conjugation_selector": list_setting(list(conjugation_dict.keys()), list(conjugation_dict.keys())),\n    "ptc_selector": list_setting(master_ptc_list, master_ptc_list),\n    "voice_selector": list_setting(master_voice_list, master_voice_list),\n    "irreg_selector": list_setting(master_irregular_verbs_list, master_irregular_verbs_list),\n}\nexercise_settings = resolve_exercise_settings(page_id, exercise_schema, defaults)\ninitialize_widget_state(page_id, exercise_settings)\npreset_active = url_preset_active(page_id)\n''')
    for old in [
        '    master_ptc_list = ["pap", "ppp", "fap", "gdv"]\n',
        '    master_voice_list = ["act", "dep", "semidep"]\n',
        '    master_irregular_verbs_list = [key for key in complete_verb_vocab.keys() if complete_verb_vocab[key].get("irreg",{}).get("irreg") is True]\n    master_irregular_verbs_list.remove("mālō")\n',
    ]:
        replace_once(path, old, "")
    replacements = [
        ('                                       value=defaults.get("show_principal_parts") if defaults.get("show_principal_parts") is not None else False,\n', '                                       key=widget_key(page_id, "show_principal_parts"),\n'),
        ('        default = defaults.get("conjugation_selector") if defaults.get("conjugation_selector") is not None else conjugation_dict.keys(),\n', '        key=widget_key(page_id, "conjugation_selector"),\n'),
        ('        default=defaults.get("ptc_selector") if defaults.get("ptc_selector") is not None else master_ptc_list,\n', '        key=widget_key(page_id, "ptc_selector"),\n'),
        ('                                    default = defaults.get("voice_selector") if defaults.get("voice_selector") is not None else master_voice_list,\n', '                                    key=widget_key(page_id, "voice_selector"),\n'),
        ('                                    default=defaults.get("irreg_selector") if defaults.get("irreg_selector") is not None else master_irregular_verbs_list,\n', '                                    key=widget_key(page_id, "irreg_selector"),\n'),
    ]
    for old, new in replacements:
        replace_once(path, old, new)
    replace_once(path,
'''with options_col:\n    if st.user.is_logged_in:\n        set_defaults_col, clear_defaults_col = st.container(vertical_alignment="bottom", height="stretch").columns(2, vertical_alignment="center")\n''',
'''current_exercise_settings = {\n    "show_principal_parts": show_principal_parts,\n    "conjugation_selector": conjugation_selector,\n    "ptc_selector": ptc_selector,\n    "voice_selector": voice_selector,\n    "irreg_selector": irreg_selector,\n}\n\nwith options_col:\n    if st.user.is_logged_in:\n        set_defaults_col, clear_defaults_col, link_col = st.container(vertical_alignment="bottom", height="stretch").columns(3, vertical_alignment="center")\n''')
    replace_once(path,
'''                        kwargs={\n                            "show_principal_parts": show_principal_parts,\n                            "conjugation_selector": conjugation_selector,\n                            "ptc_selector": ptc_selector,\n                            "voice_selector": voice_selector,\n                            "irreg_selector": irreg_selector\n                            },\n                        )\n''',
'''                        kwargs=current_exercise_settings,\n                        disabled=preset_active,\n                        )\n''')
    replace_once(path,
'''                        disabled=True if not defaults else False\n                        )\n\nverb_vocab = {key: val for key, val in complete_verb_vocab.items()''',
'''                        disabled=preset_active or not defaults\n                        )\n        with link_col:\n            exercise_link_popover(page_id, exercise_schema, current_exercise_settings)\n    else:\n        exercise_link_popover(page_id, exercise_schema, current_exercise_settings)\n\nverb_vocab = {key: val for key, val in complete_verb_vocab.items()''')
    clean(path)


def patch_pronouns():
    path = "pronouns.py"
    if "exercise_schema = {" in (ROOT / path).read_text():
        return
    replace_once(path,
        "from utils import radio_change, reset, new_question, submit_and_check_answer, clear_page, send_setting, save_defaults, clear_defaults\n",
        "from utils import radio_change, reset, new_question, submit_and_check_answer, clear_page, send_setting, save_defaults, clear_defaults\n"
        "from exercise_presets import (bool_setting, list_setting, resolve_exercise_settings, initialize_widget_state,\n"
        "                              widget_key, url_preset_active, exercise_link_popover)\n")
    replace_once(path,
'''pronoun_vocab = import_pronouns()\n\n\n## SET OPTIONS ##\n''',
'''pronoun_vocab = import_pronouns()\n\ndemonstrative_options = [k for k,v in pronoun_vocab.items() if v.get("type") == "demonstrative"]\npersonal_options = [k for k,v in pronoun_vocab.items() if v.get("type") == "pers_pron"]\nrel_interr_options = [k for k,v in pronoun_vocab.items() if v.get("type") == "rel_interrog"]\nindefinite_options = [k for k,v in pronoun_vocab.items() if v.get("type") == "indefinite"]\nexercise_schema = {\n    "demonstratives": list_setting(demonstrative_options, demonstrative_options),\n    "personal_pron": list_setting(personal_options, personal_options),\n    "rel_interr": list_setting(rel_interr_options, rel_interr_options),\n    "indefinites": list_setting(indefinite_options, indefinite_options),\n    "gen_forms_diff": bool_setting(False),\n}\nexercise_settings = resolve_exercise_settings(page_id, exercise_schema, defaults)\ninitialize_widget_state(page_id, exercise_settings)\npreset_active = url_preset_active(page_id)\n\n## SET OPTIONS ##\n''')
    replace_once(path, 'gen_forms_diff = None\n', 'gen_forms_diff = False\n')
    replacements = [
        ('                                    options=[k for k,v in pronoun_vocab.items() if v.get("type") == "demonstrative"],\n                                    default=defaults.get("demonstratives") if defaults.get("demonstratives") is not None else [k for k,v in pronoun_vocab.items() if v.get("type") == "demonstrative"])', '                                    options=demonstrative_options,\n                                    key=widget_key(page_id, "demonstratives"))'),
        ('                                    options=[k for k,v in pronoun_vocab.items() if v.get("type") == "pers_pron"],\n                                    default=defaults.get("personal_pron") if defaults.get("personal_pron") is not None else [k for k,v in pronoun_vocab.items() if v.get("type") == "pers_pron"])', '                                    options=personal_options,\n                                    key=widget_key(page_id, "personal_pron"))'),
        ('                                    options=[k for k,v in pronoun_vocab.items() if v.get("type") == "rel_interrog"],\n                                    default=defaults.get("rel_interr") if defaults.get("rel_interr") is not None else [k for k,v in pronoun_vocab.items() if v.get("type") == "rel_interrog"])', '                                    options=rel_interr_options,\n                                    key=widget_key(page_id, "rel_interr"))'),
        ('                                    options=[k for k,v in pronoun_vocab.items() if v.get("type") == "indefinite"],\n                                    default=defaults.get("indefinites") if defaults.get("indefinites") is not None else [k for k,v in pronoun_vocab.items() if v.get("type") == "indefinite"])', '                                    options=indefinite_options,\n                                    key=widget_key(page_id, "indefinites"))'),
        ('                                        value=defaults.get("gen_forms_diff") if defaults.get("gen_forms_diff") is not None else False)', '                                        key=widget_key(page_id, "gen_forms_diff"))'),
    ]
    for old, new in replacements:
        replace_once(path, old, new)
    replace_once(path,
'''    if st.user.is_logged_in:\n        set_defaults_col, clear_defaults_col = st.container(vertical_alignment="bottom", height="stretch").columns(2, vertical_alignment="center")\n''',
'''    current_exercise_settings = {\n        "demonstratives": demonstratives,\n        "personal_pron": personal_pron,\n        "rel_interr": rel_interr,\n        "indefinites": indefinites,\n        "gen_forms_diff": gen_forms_diff,\n    }\n    if st.user.is_logged_in:\n        set_defaults_col, clear_defaults_col, link_col = st.container(vertical_alignment="bottom", height="stretch").columns(3, vertical_alignment="center")\n''')
    replace_once(path,
'''                        kwargs={\n                            "demonstratives": demonstratives,\n                            "personal_pron": personal_pron,\n                            "rel_interr": rel_interr,\n                            "indefinites": indefinites,\n                            "gen_forms_diff": gen_forms_diff\n                        },\n                        )\n''',
'''                        kwargs=current_exercise_settings,\n                        disabled=preset_active,\n                        )\n''')
    replace_once(path,
'''                        disabled=True if not defaults else False\n                        )\n\npron_list = demonstratives+personal_pron+rel_interr+indefinites\n''',
'''                        disabled=preset_active or not defaults\n                        )\n        with link_col:\n            exercise_link_popover(page_id, exercise_schema, current_exercise_settings)\n    else:\n        exercise_link_popover(page_id, exercise_schema, current_exercise_settings)\n\npron_list = demonstratives+personal_pron+rel_interr+indefinites\n''')
    clean(path)


if __name__ == "__main__":
    patch_verbs()
    patch_adjectives()
    patch_verbal_adj()
    patch_pronouns()
