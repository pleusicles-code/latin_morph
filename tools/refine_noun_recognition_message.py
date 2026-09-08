from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()

old = '''            question = f"Which number and case can *{displayed_form}* represent?"
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
'''

new = '''            question = f"Which number and case can *{displayed_form}* represent?"
            if show_dictionary_entry:
                question += f" The dictionary entry is *{build_dictionary_entry(noun)}*"
            if show_declension and show_stem:
                question += f' This is a {decl} declension {third_logic}noun and the base is: *{noun_vocab[noun]["stem"]}-*.'
            elif show_declension:
                question += f" This is a {decl} declension {third_logic}noun."
            elif show_stem:
                question += f' The base is: *{noun_vocab[noun]["stem"]}-*.'

            print_macrons = st.session_state[widget_key(page_id, "print_macrons")]
            comparable_displayed_form = displayed_form if print_macrons else remove_macrons(displayed_form)
            matching_analyses = set()
            for possible_number in noun_options["number"]:
                for possible_case in noun_options["case"]:
                    possible_form = build_noun([noun, possible_case, possible_number])
                    if possible_form is None:
                        continue
                    possible_forms = possible_form if isinstance(possible_form, list) else [possible_form]
                    for form in possible_forms:
                        comparable_form = form if print_macrons else remove_macrons(form)
                        if comparable_form == comparable_displayed_form:
                            matching_analyses.add((possible_number, possible_case))
                            break

            vowel_phrase = "are" if print_macrons else "are not"
            question += f" Vowel lengths {vowel_phrase} indicated"
            if st.session_state[widget_key(page_id, "indicate_multiple_answers")]:
                if len(matching_analyses) > 1:
                    question += " and multiple correct answers are possible."
                else:
                    question += "."
            else:
                question += " and multiple correct answers might be possible."
'''

if text.count(old) != 1:
    raise RuntimeError(f"Expected one recognition message block, found {text.count(old)}")
text = text.replace(old, new, 1)
path.write_text(text)
