from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()

old_import = "from utils import radio_change, reset, new_question, submit_and_check_answer, clear_page, send_setting, save_defaults, clear_defaults, auto_advance_delay\n"
new_import = "from utils import radio_change, reset, new_question, submit_and_check_answer, clear_page, send_setting, save_defaults, clear_defaults, auto_advance_delay, remove_macrons\n"
if text.count(old_import) != 1:
    raise RuntimeError(f"Expected one utils import anchor, found {text.count(old_import)}")
text = text.replace(old_import, new_import, 1)

old_block = '''        noun_prompt = build_dictionary_entry(noun) if show_dictionary_entry else noun
        question = f'For *{noun_prompt}*, give the **{noun_options["case"][case]} {noun_options["number"][number]}**.'
        noun_decl = noun_vocab.get(noun)["decl"]

        if show_declension:
            for key, val in declension_dict.items():
                if isinstance(val, list):
                    if noun_decl in val:
                        decl = key
                    if key == "3rd":
                        if noun_decl == "3_istem":
                            third_logic = "i-stem "
                        elif noun_decl == "3_neut":
                            third_logic = "neuter "
                        elif noun_decl == "3_istem_neut":
                            third_logic = "neuter i-stem "
                        else:
                            third_logic = ""
                    else:
                        pass
                else:
                    if noun_decl == val:
                        decl = key
                    else:
                        pass
            question += f" This is a {decl} declension {third_logic}noun."

        if show_stem:
            question += f' (The base is: {noun_vocab[noun]["stem"]}-)'

        st.markdown("### Current question")

        with st.form(key="noun_form", clear_on_submit=True):
            current_answer = st.text_input(question, key="answer_input")
            submit_button_col, user_answer_col = st.columns([1,2])
            with submit_button_col:
                def disable_button():
                        st.session_state.button_disable = True
                st.form_submit_button(
                    "Check Answer",
                    key="form_submission_button",
                    on_click=submit_and_check_answer,
                    disabled=st.session_state.button_disable,
                )
'''

new_block = '''        noun_prompt = build_dictionary_entry(noun) if show_dictionary_entry else noun
        noun_decl = noun_vocab.get(noun)["decl"]
        decl = ""
        third_logic = ""

        if show_declension:
            for key, val in declension_dict.items():
                if isinstance(val, list):
                    if noun_decl in val:
                        decl = key
                    if key == "3rd":
                        if noun_decl == "3_istem":
                            third_logic = "i-stem "
                        elif noun_decl == "3_neut":
                            third_logic = "neuter "
                        elif noun_decl == "3_istem_neut":
                            third_logic = "neuter i-stem "
                        else:
                            third_logic = ""
                elif noun_decl == val:
                    decl = key

        if exercise_type == "inflect":
            question = f'For *{noun_prompt}*, give the **{noun_options["case"][case]} {noun_options["number"][number]}**.'
            if show_declension:
                question += f" This is a {decl} declension {third_logic}noun."
            if show_stem:
                question += f' (The base is: {noun_vocab[noun]["stem"]}-)'
        else:
            displayed_form = correct_answer
            if isinstance(displayed_form, list):
                displayed_form = random.choice(displayed_form)
            if not st.session_state[widget_key(page_id, "print_macrons")]:
                displayed_form = remove_macrons(displayed_form)

            question = f"Which number and case can *{displayed_form}* represent?"
            if show_dictionary_entry:
                question += f" The dictionary entry is *{build_dictionary_entry(noun)}*."
            if show_declension and show_stem:
                question += f' This is a {decl} declension {third_logic}noun and the base is: *{noun_vocab[noun]["stem"]}-*.'
            elif show_declension:
                question += f" This is a {decl} declension {third_logic}noun."
            elif show_stem:
                question += f' The base is: *{noun_vocab[noun]["stem"]}-*.'

            vowel_phrase = "are" if st.session_state[widget_key(page_id, "print_macrons")] else "are not"
            multiple_phrase = "are" if st.session_state[widget_key(page_id, "indicate_multiple_answers")] else "might be"
            question += (
                f" Take into account that vowel lengths {vowel_phrase} indicated and that "
                f"multiple correct answers {multiple_phrase} possible."
            )

        st.markdown("### Current question")

        with st.form(key="noun_form", clear_on_submit=True):
            current_answer = st.text_input(question, key="answer_input")
            submit_button_col, user_answer_col = st.columns([1,2])
            with submit_button_col:
                def disable_button():
                        st.session_state.button_disable = True

                def submit_noun_answer():
                    if exercise_type == "recognize" and st.session_state.get("answer_input"):
                        st.session_state.correct_answer = st.session_state.answer_input
                    submit_and_check_answer()

                st.form_submit_button(
                    "Check Answer",
                    key="form_submission_button",
                    on_click=submit_noun_answer,
                    disabled=st.session_state.button_disable,
                )
'''

if text.count(old_block) != 1:
    raise RuntimeError(f"Expected one question/form block, found {text.count(old_block)}")
text = text.replace(old_block, new_block, 1)
path.write_text(text)
