from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()

text = text.replace(
'''exercise_schema = {
    "show_dictionary_entry": bool_setting(True),
''',
'''exercise_schema = {
    "exercise_type": choice_setting("inflect", ["inflect", "recognize"]),
    "print_macrons": bool_setting(False),
    "indicate_multiple_answers": bool_setting(False),
    "expect_all_answers": bool_setting(False),
    "show_dictionary_entry": bool_setting(True),
''',
1,
)

text = text.replace(
'''with option_expander:
    col_declension, col_options = st.columns([3,2])

with col_options:
''',
'''with option_expander:
    exercise_type = st.radio(
        "Exercise type:",
        options=["inflect", "recognize"],
        format_func=lambda value: {
            "inflect": "Inflect words",
            "recognize": "Recognize inflected forms",
        }[value],
        horizontal=True,
        key=widget_key(page_id, "exercise_type"),
        on_change=radio_change,
    )
    col_declension, col_options = st.columns([3,2])

with col_options:
''',
1,
)

old_options = '''    st.markdown("Options:", help="You can adjust these options at any point.")
    st.checkbox("Enforce macrons?",
                help="If this box is selected, macron mistakes will be considered incorrect. If not selected, macrons can be used but will not be evaluated.",
                key="nouns_enforce_macrons",
                # value=st.session_state.enforce_macrons["nouns_enforce_macrons"],
                on_change=send_setting,
                args=(switch_noun_macrons,),
                kwargs={"streamlit_page":"nouns.py","setting_name":"nouns_enforce_macrons"},
                )
    # st.session_state.enforce_macrons["nouns_enforce_macrons"] = st.session_state.nouns_enforce_macrons
    macrons = st.session_state.nouns_enforce_macrons

    if macrons:
        st.markdown("You can copy and paste letters from here:")
        st.code("āēīōū", language=None)

    st.html('<hr style="border-top: 1px dotted; border-bottom: none;">')
'''

new_options = '''    st.markdown("Options:", help="You can adjust these options at any point.")
    if exercise_type == "inflect":
        st.checkbox("Enforce macrons?",
                    help="If this box is selected, macron mistakes will be considered incorrect. If not selected, macrons can be used but will not be evaluated.",
                    key="nouns_enforce_macrons",
                    # value=st.session_state.enforce_macrons["nouns_enforce_macrons"],
                    on_change=send_setting,
                    args=(switch_noun_macrons,),
                    kwargs={"streamlit_page":"nouns.py","setting_name":"nouns_enforce_macrons"},
                    )
        # st.session_state.enforce_macrons["nouns_enforce_macrons"] = st.session_state.nouns_enforce_macrons
        macrons = st.session_state.nouns_enforce_macrons

        if macrons:
            st.markdown("You can copy and paste letters from here:")
            st.code("āēīōū", language=None)
    else:
        print_macrons = st.checkbox(
            "Print macrons?",
            help="If enabled, inflected forms will be printed with macrons, and answers must be provided considering the given vowel length; if disabled, vowels might be either short or long, in same cases raising the number of correct answers.",
            key=widget_key(page_id, "print_macrons"),
        )
        indicate_multiple_answers = st.checkbox(
            "Indicate multiple correct answers?",
            help="If enabled, the question will contain a message that there are multiple correct answers.",
            key=widget_key(page_id, "indicate_multiple_answers"),
        )
        expect_all_answers = st.checkbox(
            "Expect all correct answers?",
            help="If checked, the answer will be deemed fully correct only if each possible analysis is given; otherwise, any possible analysis will be accepted as correct.",
            key=widget_key(page_id, "expect_all_answers"),
        )

    st.html('<hr style="border-top: 1px dotted; border-bottom: none;">')
'''

if text.count(old_options) != 1:
    raise RuntimeError(f"Expected one options block, found {text.count(old_options)}")
text = text.replace(old_options, new_options, 1)

text = text.replace(
'''current_exercise_settings = {
    "show_dictionary_entry": show_dictionary_entry,
''',
'''current_exercise_settings = {
    "exercise_type": exercise_type,
    "print_macrons": st.session_state[widget_key(page_id, "print_macrons")],
    "indicate_multiple_answers": st.session_state[widget_key(page_id, "indicate_multiple_answers")],
    "expect_all_answers": st.session_state[widget_key(page_id, "expect_all_answers")],
    "show_dictionary_entry": show_dictionary_entry,
''',
1,
)

text = text.replace(
'''            generic_noun_settings = {
                "show_dictionary_entry": True,
''',
'''            generic_noun_settings = {
                "exercise_type": "inflect",
                "print_macrons": False,
                "indicate_multiple_answers": False,
                "expect_all_answers": False,
                "show_dictionary_entry": True,
''',
1,
)

text = text.replace(
'''            current_noun_settings = {
                "show_dictionary_entry": show_dictionary_entry,
''',
'''            current_noun_settings = {
                "exercise_type": exercise_type,
                "print_macrons": st.session_state[widget_key(page_id, "print_macrons")],
                "indicate_multiple_answers": st.session_state[widget_key(page_id, "indicate_multiple_answers")],
                "expect_all_answers": st.session_state[widget_key(page_id, "expect_all_answers")],
                "show_dictionary_entry": show_dictionary_entry,
''',
1,
)

text = text.replace(
'''            def reset_noun_defaults():
                clear_defaults(page_id)
                st.session_state.nouns_show_dictionary_entry = True
''',
'''            def reset_noun_defaults():
                clear_defaults(page_id)
                st.session_state.nouns_exercise_type = "inflect"
                st.session_state.nouns_print_macrons = False
                st.session_state.nouns_indicate_multiple_answers = False
                st.session_state.nouns_expect_all_answers = False
                st.session_state.nouns_show_dictionary_entry = True
''',
1,
)

path.write_text(text)
