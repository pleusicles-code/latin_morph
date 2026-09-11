from pathlib import Path

for filename, container in [("verbs.py", "verb_options_col"), ("nouns.py", "col_declension")]:
    path = Path(filename)
    text = path.read_text()
    old = f'''with {container}:
    exercise_type = st.radio(
        "Feladattípus:",
        options=["inflect", "recognize"],
        format_func=lambda value: {{
            "inflect": "Ragozás",
            "recognize": "Alakfelismerés",
        }}[value],
        horizontal=True,
        key=widget_key(page_id, "exercise_type"),
        on_change=radio_change,
    )
'''
    new = f'''with {container}:
    exercise_type_label_col, exercise_type_radio_col = st.columns(
        [1, 4], vertical_alignment="center"
    )
    with exercise_type_label_col:
        st.markdown("Feladattípus:")
    with exercise_type_radio_col:
        exercise_type = st.radio(
            "Feladattípus:",
            options=["inflect", "recognize"],
            format_func=lambda value: {{
                "inflect": "Ragozás",
                "recognize": "Alakfelismerés",
            }}[value],
            horizontal=True,
            label_visibility="collapsed",
            key=widget_key(page_id, "exercise_type"),
            on_change=radio_change,
        )
'''
    if text.count(old) != 1:
        raise SystemExit(f"{{filename}}: expected radio block once, found {{text.count(old)}}")
    text = text.replace(old, new)
    compile(text, filename, "exec")
    path.write_text(text)
