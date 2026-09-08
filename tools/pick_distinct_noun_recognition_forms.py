from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()

old = '''    def build_dictionary_entry(noun):
        genitive = build_noun([noun, "gen", "sg"])
        gender = noun_vocab[noun]["gender"]
        if isinstance(genitive, list):
            genitive = "/".join(genitive)
        if genitive:
            return f"{noun}, {genitive} {gender}."
        return f"{noun} {gender}."

    st.session_state.gen_func = adap_gen_question
'''

new = '''    def build_dictionary_entry(noun):
        genitive = build_noun([noun, "gen", "sg"])
        gender = noun_vocab[noun]["gender"]
        if isinstance(genitive, list):
            genitive = "/".join(genitive)
        if genitive:
            return f"{noun}, {genitive} {gender}."
        return f"{noun} {gender}."

    def recognition_gen_question():
        # Use the ordinary random generator to choose the noun, but do not let
        # the sampled case/number determine which surface form is asked about.
        noun, _, _ = gen_question()
        print_macrons = st.session_state[widget_key(page_id, "print_macrons")]
        form_analyses = {}

        for possible_number in noun_options["number"]:
            for possible_case in noun_options["case"]:
                possible_form = build_noun([noun, possible_case, possible_number])
                if possible_form is None:
                    continue
                possible_forms = possible_form if isinstance(possible_form, list) else [possible_form]
                for form in possible_forms:
                    displayed = form if print_macrons else remove_macrons(form)
                    form_analyses.setdefault(displayed, set()).add((possible_case, possible_number))

        displayed_form = random.choice(list(form_analyses))
        case, number = random.choice(list(form_analyses[displayed_form]))
        st.session_state.nouns_recognition_displayed_form = displayed_form
        return [noun, case, number]

    st.session_state.gen_func = recognition_gen_question if exercise_type == "recognize" else adap_gen_question
'''

if text.count(old) != 1:
    raise RuntimeError(f"Expected dictionary-entry/generator anchor once, found {text.count(old)}")
text = text.replace(old, new, 1)

old_display = '''        else:
            displayed_form = correct_answer
            if isinstance(displayed_form, list):
                displayed_form = random.choice(displayed_form)
            if not st.session_state[widget_key(page_id, "print_macrons")]:
                displayed_form = remove_macrons(displayed_form)

            question = f"Which number and case can *{displayed_form}* represent?"
'''
new_display = '''        else:
            displayed_form = st.session_state.get("nouns_recognition_displayed_form")
            if not displayed_form:
                # Fallback for any pre-existing session question created before
                # the recognition-specific generator was introduced.
                displayed_form = correct_answer
                if isinstance(displayed_form, list):
                    displayed_form = random.choice(displayed_form)
                if not st.session_state[widget_key(page_id, "print_macrons")]:
                    displayed_form = remove_macrons(displayed_form)

            question = f"Which number and case can *{displayed_form}* represent?"
'''
if text.count(old_display) != 1:
    raise RuntimeError(f"Expected recognition display block once, found {text.count(old_display)}")
text = text.replace(old_display, new_display, 1)

old_button = '''        st.button(new_q_button_text, on_click=new_question, args=(adap_gen_question,), key="question_button", width="stretch",
'''
new_button = '''        st.button(new_q_button_text, on_click=new_question, args=(st.session_state.gen_func,), key="question_button", width="stretch",
'''
if text.count(old_button) != 1:
    raise RuntimeError(f"Expected New Question button generator once, found {text.count(old_button)}")
text = text.replace(old_button, new_button, 1)

path.write_text(text)
