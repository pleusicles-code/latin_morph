from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path, old, new):
    file_path = ROOT / path
    text = file_path.read_text()
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected exactly one match, found {count}: {old[:80]!r}")
    file_path.write_text(text.replace(old, new, 1))


def patch_nouns():
    path = "nouns.py"

    replace_once(
        path,
        "from utils import radio_change, reset, new_question, submit_and_check_answer, clear_page, send_setting, save_defaults, clear_defaults\n",
        "from utils import radio_change, reset, new_question, submit_and_check_answer, clear_page, send_setting, save_defaults, clear_defaults\n"
        "from exercise_presets import (bool_setting, choice_setting, list_setting, resolve_exercise_settings,\n"
        "                              initialize_widget_state, widget_key, url_preset_active, exercise_link_popover)\n",
    )

    old = '''declension_dict = {\n    "1st": 1, \n    "2nd":["2_us", "2_er", "2_neut"], \n    "3rd": [3, "3_istem", "3_neut", "3_istem_neut"], \n    "4th": [4, "4_neut"], \n    "5th": ["5_vowel", "5_consonant"]\n    }\n\n## SET OPTIONS ##\n'''
    new = '''declension_dict = {\n    "1st": 1, \n    "2nd":["2_us", "2_er", "2_neut"], \n    "3rd": [3, "3_istem", "3_neut", "3_istem_neut"], \n    "4th": [4, "4_neut"], \n    "5th": ["5_vowel", "5_consonant"]\n    }\n\nmaster_irregular_nouns_list = [\n    noun for noun, data in noun_vocab.items() if data.get("irreg", {}).get("irreg")\n]\nexercise_schema = {\n    "show_dictionary_entry": bool_setting(True),\n    "show_declension": bool_setting(False),\n    "show_stem": bool_setting(False),\n    "declension": list_setting(list(declension_dict.keys()), list(declension_dict.keys())),\n    "irregs_include": list_setting(["deus"] if "deus" in master_irregular_nouns_list else [], master_irregular_nouns_list),\n    "irregs_only": choice_setting("No", ["No", "Yes"]),\n}\nexercise_settings = resolve_exercise_settings(page_id, exercise_schema, defaults)\ninitialize_widget_state(page_id, exercise_settings)\npreset_active = url_preset_active(page_id)\n\n## SET OPTIONS ##\n'''
    replace_once(path, old, new)

    replace_once(
        path,
        '''        value=defaults.get("show_dictionary_entry") if defaults.get("show_dictionary_entry") is not None else True,\n        key="nouns_show_dictionary_entry",\n''',
        '''        key=widget_key(page_id, "show_dictionary_entry"),\n''',
    )
    replace_once(
        path,
        '''                                  value=defaults.get("show_declension") if defaults.get("show_declension") is not None else False,\n                                  key="nouns_show_declension")\n''',
        '''                                  key=widget_key(page_id, "show_declension"))\n''',
    )
    replace_once(
        path,
        '''                            value=defaults.get("show_stem") if defaults.get("show_stem") is not None else False,\n                            key="nouns_show_stem")\n''',
        '''                            key=widget_key(page_id, "show_stem"))\n''',
    )
    replace_once(
        path,
        '''                                default=defaults.get("declension") if defaults.get("declension") is not None else list(declension_dict.keys()), \n                                help="If the selected declension(s) include irregular nouns, an option will be shown to include or exclude them.",\n                                key="nouns_declension")\n''',
        '''                                help="If the selected declension(s) include irregular nouns, an option will be shown to include or exclude them.",\n                                key=widget_key(page_id, "declension"))\n''',
    )

    replace_once(
        path,
        '''with col_declension:\n    if len(irreg_nouns) > 0:\n        # default_irreg_nouns = [noun for noun in irreg_nouns if noun in active_vocab]\n''',
        '''with col_declension:\n    if len(irreg_nouns) > 0:\n        irregs_key = widget_key(page_id, "irregs_include")\n        st.session_state[irregs_key] = [noun for noun in st.session_state.get(irregs_key, []) if noun in irreg_nouns]\n        # default_irreg_nouns = [noun for noun in irreg_nouns if noun in active_vocab]\n''',
    )
    replace_once(
        path,
        '''                                        default=[noun for noun in defaults.get("irregs_include") if noun in irreg_nouns] if defaults.get("irregs_include") is not None else (["deus"] if "deus" in irreg_nouns else []), \n                                        help="Only irregular nouns for the selected declension(s) are shown.",\n                                        key="nouns_irregs_include")\n''',
        '''                                        help="Only irregular nouns for the selected declension(s) are shown.",\n                                        key=widget_key(page_id, "irregs_include"))\n''',
    )
    replace_once(
        path,
        '                                   index=["No", "Yes"].index(defaults.get("irregs_only")) if defaults.get("irregs_only") is not None else 0,',
        '',
    )
    replace_once(
        path,
        '                                   key="nouns_irregs_only")',
        '                                   key=widget_key(page_id, "irregs_only"))',
    )

    replace_once(
        path,
        '''with col_options:\n    if st.user.is_logged_in:\n        set_defaults_col, clear_defaults_col = st.container(vertical_alignment="bottom", height="stretch").columns(2, vertical_alignment="center")\n''',
        '''current_exercise_settings = {\n    "show_dictionary_entry": show_dictionary_entry,\n    "show_declension": show_declension,\n    "show_stem": show_stem,\n    "declension": declension,\n    "irregs_include": irregs_include,\n    "irregs_only": irregs_only,\n}\n\nwith col_options:\n    if st.user.is_logged_in:\n        set_defaults_col, clear_defaults_col, link_col = st.container(vertical_alignment="bottom", height="stretch").columns(3, vertical_alignment="center")\n''',
    )
    replace_once(
        path,
        '''                        kwargs={\n                            "show_declension": show_declension,\n                            "show_stem": show_stem,\n                            "show_dictionary_entry": show_dictionary_entry,\n                            "irregs_include": irregs_include,\n                            "irregs_only": irregs_only,\n                            "declension": declension\n                            }\n                        )\n''',
        '''                        kwargs=current_exercise_settings,\n                        disabled=preset_active\n                        )\n''',
    )
    replace_once(
        path,
        '''                        disabled=not defaults and not noun_settings_changed\n                        )\n\n\nfor noun in irreg_nouns:\n''',
        '''                        disabled=preset_active or (not defaults and not noun_settings_changed)\n                        )\n        with link_col:\n            exercise_link_popover(page_id, exercise_schema, current_exercise_settings)\n    else:\n        exercise_link_popover(page_id, exercise_schema, current_exercise_settings)\n\n\nfor noun in irreg_nouns:\n''',
    )


if __name__ == "__main__":
    patch_nouns()
