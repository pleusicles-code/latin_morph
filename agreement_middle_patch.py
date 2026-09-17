from itertools import permutations


def apply_middle_mode(source):
    # The middle mode uses the same right-column option set as recognition.
    source = source.replace(
        "source = source.replace('if exercise_type == \"inflect\":', 'if exercise_type in (\"inflect\", \"agreement\"):')",
        "# Agreement uses the same option controls as recognition."
    )

    marker = '''    if st.session_state.auto_advance_trigger and st.session_state.answer_checked:
        time.sleep(auto_advance_delay())
        new_question(st.session_state.gen_func)
        st.rerun()
else:
'''

    if marker not in source:
        raise RuntimeError("Could not locate agreement-mode insertion point")

    agreement_branch = r'''    if st.session_state.auto_advance_trigger and st.session_state.answer_checked:
        time.sleep(auto_advance_delay())
        new_question(st.session_state.gen_func)
        st.rerun()
elif exercise_type == "agreement":
    def _am_adjective_group(adj):
        info = adj_vocab[adj]
        if info.get("decl") == (1, 2):
            return "1_2"
        if info.get("decl") != 3:
            return None
        noms = info.get("noms")
        endings = len(noms) if isinstance(noms, (tuple, list)) else 1
        return {1: "3_1", 2: "3_2", 3: "3_3"}.get(endings, "3_1")

    active_adj_vocab = {
        adj: info for adj, info in adj_vocab.items()
        if _am_adjective_group(adj) in adjective_declension
        and not info.get("no_sg")
        and info.get("decl") in ((1, 2), 3)
    }

    def _am_forms_list(form):
        if form is None:
            return []
        return form if isinstance(form, list) else [form]

    def _am_gendered_form(form, gender):
        if not isinstance(form, (tuple, list)):
            return form
        if not form:
            return None
        if gender == "n":
            return form[-1]
        if len(form) in (1, 2):
            return form[0]
        return form[0] if gender == "m" else form[1]

    def _am_noun_form(noun, case, number):
        info = noun_vocab[noun]
        if number == "sg" and case == "nom":
            return noun
        irreg_form = info.get("irreg", {}).get(number, {}).get(case, "")
        if irreg_form:
            return irreg_form
        if irreg_form is None:
            return None
        decl = info["decl"]
        stem = info["stem"]
        ending = noun_endings[decl][number][case]
        if (number == "sg" and
                ((noun.endswith("ius") and decl == "2_us") or
                 (noun.endswith("ium") and decl == "2_neut")) and
                case in ("voc", "gen")):
            stem = stem[:-1]
            ending = "ī" if case == "voc" else ["iī", "ī"]
        if number == "sg" and info.get("true_i_stem") is True:
            if case == "acc":
                ending = ["im", "em"]
            elif case == "abl":
                ending = ["ī", "e"]
        if ending is None:
            if number == "sg":
                return noun
            ending = noun_endings[decl][number]["nom"]
        if isinstance(ending, list):
            return [stem + item for item in ending]
        return stem + ending

    def _am_adjective_nom_sg(adj, gender):
        info = adj_vocab[adj]
        noms = info.get("irreg", {}).get("forms", {}).get("sg", {}).get("nom")
        if not noms:
            noms = info.get("noms")
        if noms:
            return _am_gendered_form(noms, gender)
        if info.get("decl") == (1, 2):
            if gender == "m":
                return adj
            return info["stem"] + ("a" if gender == "f" else "um")
        return adj if gender != "n" else _am_gendered_form(info.get("noms", (adj,)), gender)

    def _am_adjective_form(adj, case, gender, number):
        info = adj_vocab[adj]
        irreg_forms = info.get("irreg", {}).get("forms", {})
        raw_irregular = irreg_forms.get(number, {}).get(case)
        if raw_irregular:
            return _am_gendered_form(raw_irregular, gender)

        if number == "sg" and case in ("nom", "voc"):
            nom = _am_adjective_nom_sg(adj, gender)
            if case == "voc" and info.get("decl") == (1, 2) and gender == "m" and adj.endswith("us"):
                if adj.endswith("ius"):
                    return info["stem"][:-1] + "ī"
                if adj == "meus":
                    return "mī"
                return info["stem"] + "e"
            return nom

        stem = info.get("irreg", {}).get("stems", {}).get("pos") or info["stem"]
        if info.get("decl") == (1, 2):
            if number == "sg" and info.get("pronominal") is True and case == "gen":
                ending = "īus"
            elif number == "sg" and info.get("pronominal") is True and case == "dat":
                ending = "ī"
            else:
                endings = {
                    "sg": {
                        "f": {"gen": "ae", "dat": "ae", "acc": "am", "abl": "ā"},
                        "m": {"gen": "ī", "dat": "ō", "acc": "um", "abl": "ō"},
                        "n": {"gen": "ī", "dat": "ō", "acc": "um", "abl": "ō"},
                    },
                    "pl": {
                        "f": {"nom": "ae", "gen": "ārum", "dat": "īs", "acc": "ās", "abl": "īs", "voc": "ae"},
                        "m": {"nom": "ī", "gen": "ōrum", "dat": "īs", "acc": "ōs", "abl": "īs", "voc": "ī"},
                        "n": {"nom": "a", "gen": "ōrum", "dat": "īs", "acc": "a", "abl": "īs", "voc": "a"},
                    },
                }
                ending = endings[number][gender][case]
            return stem + ending

        if number == "pl":
            cons = bool(info.get("cons_stem"))
            if case == "gen":
                return stem + ("um" if cons else "ium")
            if case in ("dat", "abl"):
                return stem + "ibus"
            if gender == "n":
                if case in ("nom", "acc", "voc"):
                    return stem + ("a" if cons else "ia")
            else:
                if case in ("nom", "voc"):
                    return stem + "ēs"
                if case == "acc":
                    return stem + "ēs" if cons else [stem + "īs", stem + "ēs"]

        if case == "gen":
            return stem + "is"
        if case == "dat":
            return stem + "ī"
        if case == "abl":
            return stem + ("e" if info.get("cons_stem") else "ī")
        if case == "acc":
            if gender == "n":
                return _am_adjective_nom_sg(adj, gender)
            return stem + "em"
        return _am_adjective_nom_sg(adj, gender)

    def _am_noun_dictionary_entry(noun):
        genitive = _am_noun_form(noun, "gen", "sg")
        if isinstance(genitive, list):
            if str(noun_vocab[noun].get("decl", "")).startswith("2") and noun.endswith(("ius", "ium")):
                genitive = genitive[0]
            else:
                genitive = "/".join(genitive)
        gender = noun_vocab[noun]["gender"]
        return f"{noun}, {genitive} {gender}." if genitive else f"{noun} {gender}."

    def _am_adjective_nominatives(adj):
        info = adj_vocab[adj]
        noms = info.get("irreg", {}).get("forms", {}).get("sg", {}).get("nom") or info.get("noms")
        if noms:
            if not isinstance(noms, (tuple, list)):
                noms = [noms]
            forms = list(noms)
            if info.get("decl") == 3 and len(forms) == 1 and forms[0] != adj:
                forms.insert(0, adj)
            return forms
        if info.get("decl") == (1, 2):
            return [adj, info["stem"] + "a", info["stem"] + "um"]
        return [adj]

    def _am_adjective_dictionary_entry(adj):
        info = adj_vocab[adj]
        forms = _am_adjective_nominatives(adj)
        group = _am_adjective_group(adj)
        if group == "3_1":
            return f"{adj} ({info.get('stem', '')}is)"
        if abbreviate_adjective_dictionary:
            if info.get("decl") == (1, 2) and adj.endswith("er"):
                return ", ".join(str(form) for form in forms)
            return f"{adj} {3 if info.get('decl') == (1, 2) else len(forms)}"
        return ", ".join(str(form) for form in forms)

    def _am_allowed_numbers(noun, adjective):
        restriction = noun_vocab[noun].get("number")
        if restriction == "singular":
            numbers = ["sg"]
        elif restriction == "plural":
            numbers = ["pl"]
        else:
            numbers = ["sg", "pl"]
        if adj_vocab[adjective].get("no_pl"):
            numbers = [n for n in numbers if n != "pl"]
        return numbers

    def _am_vocative_eligible(noun, adjective, number, gender):
        if not include_vocative:
            return False
        noun_voc = _am_noun_form(noun, "voc", number)
        noun_nom = _am_noun_form(noun, "nom", number)
        adj_voc = _am_adjective_form(adjective, "voc", gender, number)
        adj_nom = _am_adjective_form(adjective, "nom", gender, number)
        return noun_voc != noun_nom or adj_voc != adj_nom

    def _am_cases(noun, adjective, number, gender):
        cases = [case for case in noun_options["case"] if case != "voc"]
        if _am_vocative_eligible(noun, adjective, number, gender):
            cases.append("voc")
        return cases

    def _am_surface(text, preserve_macrons):
        text = unicodedata.normalize("NFC", str(text))
        return text if preserve_macrons else remove_macrons(text)

    def _am_question():
        if not active_vocab or not active_adj_vocab:
            return None
        noun = random.choice(list(active_vocab))
        adjective = random.choice(list(active_adj_vocab))
        gender = noun_vocab[noun]["gender"]
        numbers = _am_allowed_numbers(noun, adjective)
        if not numbers:
            return None
        number = random.choice(numbers)
        case = random.choice(_am_cases(noun, adjective, number, gender))
        noun_forms = _am_forms_list(_am_noun_form(noun, case, number))
        if not noun_forms:
            return None
        noun_form = random.choice(noun_forms)
        return {
            "noun": noun,
            "adjective": adjective,
            "gender": gender,
            "noun_form": noun_form,
        }

    st.session_state.gen_func = _am_question

    if not declension:
        st.write("Legalább egy főnévi declinatiót ki kell választanod.")
    elif not adjective_declension:
        st.write("Legalább egy melléknévi declinatiót ki kell választanod.")
    elif not active_vocab:
        st.write("A kiválasztott főnévi beállításokhoz nincs használható szó.")
    elif not active_adj_vocab:
        st.write("A kiválasztott melléknévi beállításokhoz nincs használható szó.")

    if st.session_state.current_question:
        q = st.session_state.current_question
        noun = q["noun"]
        adjective = q["adjective"]
        gender = q["gender"]
        noun_form = q["noun_form"]
        print_macrons = st.session_state[widget_key(page_id, "print_macrons")]
        displayed_noun_form = _am_surface(noun_form, print_macrons)

        matching_analyses = set()
        for possible_number in _am_allowed_numbers(noun, adjective):
            for possible_case in _am_cases(noun, adjective, possible_number, gender):
                possible_form = _am_noun_form(noun, possible_case, possible_number)
                for form in _am_forms_list(possible_form):
                    if _am_surface(form, print_macrons) == displayed_noun_form:
                        matching_analyses.add((possible_number, possible_case))
                        break

        adjective_forms = []
        seen_forms = set()
        for possible_number, possible_case in matching_analyses:
            form = _am_adjective_form(adjective, possible_case, gender, possible_number)
            for adj_form in _am_forms_list(form):
                rendered = _am_surface(adj_form, print_macrons)
                key = rendered.casefold()
                if key not in seen_forms:
                    seen_forms.add(key)
                    adjective_forms.append(rendered)

        adjective_forms.sort(key=lambda value: value.casefold())
        answer_options = [" ".join(items) for items in permutations(adjective_forms)] if adjective_forms else []
        st.session_state.correct_answer = answer_options

        noun_prompt = _am_noun_dictionary_entry(noun) if show_dictionary_entry else noun
        adjective_prompt = _am_adjective_dictionary_entry(adjective) if show_dictionary_entry else adjective
        noun_article = hungarian_article(noun)
        adjective_article = hungarian_article(adjective)
        question_html = (
            f'Egyeztesd {noun_article} <strong>{html.escape(noun_prompt)}</strong> főnév '
            f'<strong>{html.escape(displayed_noun_form)}</strong> alakjával '
            f'{adjective_article} <strong>{html.escape(adjective_prompt)}</strong> melléknevet!'
        )

        supplementary = []
        noun_decl_key = ""
        noun_decl_value = noun_vocab[noun].get("decl")
        for key, value in declension_dict.items():
            if isinstance(value, list):
                if noun_decl_value in value:
                    noun_decl_key = key
                    break
            elif noun_decl_value == value:
                noun_decl_key = key
                break

        noun_parts = []
        adjective_parts = []
        if show_declension:
            if noun_decl_key:
                noun_parts.append(f"{DECLENSION_NUMBER_LABELS[noun_decl_key]} declinatiós")
            adjective_group = _am_adjective_group(adjective)
            if adjective_group == "1_2":
                adjective_parts.append("1–2. declinatiós")
            elif adjective_group and adjective_group.startswith("3_"):
                adjective_parts.append("3. declinatiós")

        if show_third_group:
            if noun_decl_value in (3, "3_neut"):
                noun_parts.append("msh.-tövű")
            elif noun_decl_value == "3_istem_neut" or noun_vocab[noun].get("true_i_stem") is True:
                noun_parts.append("erős i-tövű")
            elif noun_decl_value == "3_istem":
                noun_parts.append("gyenge i-tövű")
            adjective_group = _am_adjective_group(adjective)
            if adjective_group and adjective_group.startswith("3_"):
                adjective_parts.append({"3_1": "1 végű", "3_2": "2 végű", "3_3": "3 végű"}[adjective_group])

        if show_stem:
            noun_stem_raw = str(noun_vocab[noun].get("stem", ""))
            if str(noun_vocab[noun].get("decl", "")).startswith("5"):
                noun_stem_raw += "e"
            noun_parts.append(f'a töve <em>{html.escape(noun_stem_raw)}-</em>')
            adjective_parts.append(f'a töve <em>{html.escape(str(adj_vocab[adjective].get("stem", "")))}-</em>')

        if noun_parts:
            supplementary.append("<strong>Főnév:</strong> " + ", ".join(noun_parts))
        if adjective_parts:
            supplementary.append("<strong>Melléknév:</strong> " + ", ".join(adjective_parts))

        if len(adjective_forms) > 1:
            if st.session_state[widget_key(page_id, "indicate_multiple_answers")]:
                supplementary.append('<span style="color:#7c3aed;">Több helyes válaszlehetőség van.</span>')
            else:
                supplementary.append("Több helyes válaszlehetőség is lehet.")

        prompt_height = 112 if supplementary else 82
        prompt_space = st.container(height=prompt_height, border=False)
        with prompt_space:
            st.markdown(
                f'<div style="margin-top:0.75rem;font-size:1.75rem;line-height:1.25;">{question_html}</div>',
                unsafe_allow_html=True,
            )
            if supplementary:
                st.markdown(
                    '<div style="font-size:1.15rem;line-height:1.35;margin-top:0.35rem;">'
                    + " &nbsp;·&nbsp; ".join(supplementary)
                    + "</div>",
                    unsafe_allow_html=True,
                )

        with st.form(key="agreement_match_form", clear_on_submit=True):
            st.text_input("Válaszod:", key="answer_input")

            def submit_agreement_answer():
                raw_answer = st.session_state.get("answer_input") or ""
                answer_tokens = tokenize_morphology_answer(raw_answer)
                if answer_tokens:
                    st.session_state.answer_input = " ".join(answer_tokens)

                required = {form.casefold() for form in adjective_forms}
                supplied = {
                    _am_surface(token, print_macrons).casefold()
                    for token in answer_tokens
                }
                partial = bool(supplied & required) and supplied != required
                if partial:
                    st.session_state.answer_credit_override = (
                        0.5 if st.session_state[widget_key(page_id, "award_partial_credit")] else 0
                    )

                old_macron_setting = st.session_state.enforce_macrons.get("agreement_enforce_macrons", False)
                st.session_state.enforce_macrons["agreement_enforce_macrons"] = bool(print_macrons)
                submit_and_check_answer()
                st.session_state.enforce_macrons["agreement_enforce_macrons"] = old_macron_setting

                if not raw_answer:
                    st.session_state.answer_display_message = (
                        "A válaszmező üres. Írd be a megfelelő melléknévi alakot vagy alakokat."
                    )
                elif st.session_state.answer_checked:
                    if supplied == required:
                        st.session_state.answer_display_message = feedback_box(
                            "<strong>Helyes válasz!</strong>", "correct"
                        )
                    elif partial:
                        correct_text = " ".join(adjective_forms)
                        st.session_state.answer_display_message = feedback_box(
                            f"<strong>Részben helyes. A teljes válasz:</strong> {heavy(correct_text, italic=True)}.",
                            "incorrect",
                        )
                    else:
                        correct_text = " ".join(adjective_forms)
                        st.session_state.answer_display_message = feedback_box(
                            f"<strong>Helytelen válasz. A helyes válasz:</strong> {heavy(correct_text, italic=True)}.",
                            "incorrect",
                        )

            st.form_submit_button(
                "Válasz ellenőrzése",
                key="form_submission_button",
                on_click=submit_agreement_answer,
                disabled=st.session_state.button_disable,
                width="stretch",
            )

        feedback_space = st.container(height=90, border=False)
        with feedback_space:
            if st.session_state.answer_display_message.lstrip().startswith("<div"):
                st.markdown(st.session_state.answer_display_message, unsafe_allow_html=True)
            else:
                st.markdown(st.session_state.answer_display_message)

        curr_question = {
            "pos": "agreement_match",
            "word": [noun, adjective],
            "id": {
                "analyses": sorted([f"{num}:{case}" for num, case in matching_analyses]),
                "gender": gender,
                "noun_decl": str(noun_vocab[noun].get("decl")),
                "adj_decl": str(adj_vocab[adjective].get("decl")),
            },
        }
        if st.session_state.append_answer is True:
            questions_asked.append(curr_question)
            st.session_state.append_answer = False

    control_row = st.container(height=110, border=False)
    with control_row:
        new_question_col, _, score_col = st.columns([1, 1, 1], gap="medium", vertical_alignment="top")
        with new_question_col:
            st.button(
                "Új kérdés" if st.session_state.question_list else "Kattints ide az első kérdéshez!",
                on_click=new_question,
                args=(st.session_state.gen_func,),
                key="question_button",
                width="stretch",
                disabled=not declension or not adjective_declension or not active_vocab or not active_adj_vocab,
                type="secondary" if st.session_state.question_list else "primary",
            )
        with score_col:
            st.button("Pontszám nullázása", "reset", on_click=reset, width="stretch")
            st.markdown(
                f'<div style="text-align:right;">Jelenlegi pontszám: <strong>{st.session_state.current_score}</strong> / <strong>{st.session_state.total_questions}</strong></div>',
                unsafe_allow_html=True,
            )

    if st.session_state.auto_advance_trigger and st.session_state.answer_checked:
        time.sleep(auto_advance_delay())
        new_question(st.session_state.gen_func)
        st.rerun()
else:
'''

    source = source.replace(marker, agreement_branch, 1)
    return source
