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


def patch_page(path, page_id, reset_function):
    replace_once(
        path,
        "from utils import clear_page, new_question, reset, save_defaults, clear_defaults\n",
        "from utils import clear_page, new_question, reset, save_defaults, clear_defaults\n"
        "from exercise_presets import (list_setting, resolve_exercise_settings, initialize_widget_state,\n"
        "                              widget_key, url_preset_active, exercise_link_popover)\n",
    )

    replace_once(
        path,
        'PARTS_OF_SPEECH = ["noun", "adjective", "verb"]\n',
        'PARTS_OF_SPEECH = ["noun", "adjective", "verb"]\n\n'
        'exercise_schema = {\n'
        '    "selected_pos": list_setting(PARTS_OF_SPEECH, PARTS_OF_SPEECH),\n'
        '}\n'
        'exercise_settings = resolve_exercise_settings(page_id, exercise_schema, defaults)\n'
        'initialize_widget_state(page_id, exercise_settings)\n'
        'preset_active = url_preset_active(page_id)\n',
    )

    replace_once(
        path,
        '        default=defaults.get("selected_pos") if defaults.get("selected_pos") is not None else PARTS_OF_SPEECH,\n'
        f'        key="{page_id}_selected_pos",\n',
        '        key=widget_key(page_id, "selected_pos"),\n',
    )

    replace_once(
        path,
        '    if st.user.is_logged_in:\n'
        '        set_defaults_col, clear_defaults_col = st.columns(2)\n',
        '    current_settings = {"selected_pos": selected_pos}\n\n'
        '    if st.user.is_logged_in:\n'
        '        set_defaults_col, clear_defaults_col, link_col = st.columns(3)\n',
    )

    replace_once(
        path,
        '                kwargs={"selected_pos": selected_pos},\n'
        '            )\n',
        '                kwargs=current_settings,\n'
        '                disabled=preset_active,\n'
        '            )\n',
    )

    replace_once(
        path,
        '            generic_settings = {"selected_pos": PARTS_OF_SPEECH}\n'
        '            current_settings = {"selected_pos": selected_pos}\n'
        '            settings_changed = current_settings != generic_settings\n',
        '            generic_settings = {"selected_pos": PARTS_OF_SPEECH}\n'
        '            settings_changed = current_settings != generic_settings\n',
    )

    replace_once(
        path,
        f'                disabled=not defaults and not settings_changed,\n'
        '            )\n\n\n# --- ',
        '                disabled=preset_active or (not defaults and not settings_changed),\n'
        '            )\n\n'
        '        with link_col:\n'
        '            exercise_link_popover(page_id, exercise_schema, current_settings)\n'
        '    else:\n'
        '        exercise_link_popover(page_id, exercise_schema, current_settings)\n\n\n# --- ',
    )

    clean(path)


patch_page("recognize_pos.py", "recognize_pos", "reset_recognition_defaults")
patch_page("identify_stems.py", "identify_stems", "reset_stem_defaults")
