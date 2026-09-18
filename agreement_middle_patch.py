from itertools import permutations
import textwrap


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


def apply_recognition_base(source):
    old_generator = r'''    def recognition_gen_question():
        noun, _, _ = adap_gen_question()
        print_macrons = st.session_state[widget_key(page_id, "print_macrons")]
        form_analyses = {}

        for possible_number in noun_options["number"]:
            for possible_case in recognition_cases_for_noun(noun, possible_number):
                possible_form = build_noun([noun, possible_case, possible_number])
                if possible_form is None:
                    continue
                possible_forms = possible_form if isinstance(possible_form, list) else [possible_form]
                for form in possible_forms:
                    displayed = normalize_noun_surface(form, print_macrons)
                    form_analyses.setdefault(displayed, set()).add((possible_case, possible_number))

        displayed_forms = list(form_analyses)
        diagnostic_nom = is_diagnostic_sg_nom(noun, print_macrons)
        displayed_nom = normalize_noun_surface(noun, print_macrons)
        form_weights = [1 if diagnostic_nom and form == displayed_nom else 9 for form in displayed_forms]
        displayed_form = random.choices(displayed_forms, weights=form_weights, k=1)[0]
        displayed_analyses = set(form_analyses[displayed_form])
        if (
            noun == "deus"
            and normalize_noun_surface(displayed_form, print_macrons)
            == normalize_noun_surface("deum", print_macrons)
            and ("acc", "sg") in displayed_analyses
        ):
            case, number = ("acc", "sg")
        else:
            case, number = random.choice(list(displayed_analyses))
        st.session_state.agreement_recognition_displayed_form = displayed_form
        return [noun, case, number]
'''
    old_generator = textwrap.indent(old_generator, "    ")
    new_generator = r'''    def _ar_adjective_group(adj):
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
        if _ar_adjective_group(adj) in adjective_declension
        and not info.get("no_sg")
        and info.get("decl") in ((1, 2), 3)
    }

    def _ar_gendered_form(form, gender):
        if not isinstance(form, (tuple, list)):
            return form
        if not form:
            return None
        if gender == "n":
            return form[-1]
        if len(form) in (1, 2):
            return form[0]
        return form[0] if gender == "m" else form[1]

    def _ar_adjective_nom_sg(adj, gender):
        info = adj_vocab[adj]
        noms = info.get("noms")
        if noms:
            return _ar_gendered_form(noms, gender)
        if info.get("decl") == (1, 2):
            if gender == "m":
                return adj
            return info["stem"] + ("a" if gender == "f" else "um")
        return adj if gender != "n" else _ar_gendered_form(info.get("noms", (adj,)), gender)

    def _ar_adjective_form(adj, case, gender, number):
        info = adj_vocab[adj]
        if number == "sg" and case in ("nom", "voc"):
            nom = _ar_adjective_nom_sg(adj, gender)
            if case == "voc" and info.get("decl") == (1, 2) and gender == "m" and adj.endswith("us"):
                if adj.endswith("ius"):
                    return info["stem"][:-1] + "ī"
                if adj == "meus":
                    return "mī"
                return info["stem"] + "e"
            return nom

        stem = info["stem"]
        if info.get("decl") == (1, 2):
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
            return stem + endings[number][gender][case]

        if number == "pl":
            cons = bool(info.get("cons_stem"))
            if case == "gen":
                return stem + ("um" if cons else "ium")
            if case in ("dat", "abl"):
                return stem + "ibus"
            if gender == "n" and case in ("nom", "acc", "voc"):
                return stem + ("a" if cons else "ia")
            if gender != "n":
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
                return _ar_adjective_nom_sg(adj, gender)
            return stem + "em"
        return _ar_adjective_nom_sg(adj, gender)

    def _ar_adjective_dictionary_entry(adj):
        info = adj_vocab[adj]
        noms = info.get("noms")
        forms = list(noms) if isinstance(noms, (tuple, list)) else ([noms] if noms else [])
        group = _ar_adjective_group(adj)
        if group == "3_1":
            return f"{adj} ({info.get('stem', '')}is)"
        if abbreviate_adjective_dictionary:
            if info.get("decl") == (1, 2) and adj.endswith("er"):
                if not forms:
                    forms = [adj, info["stem"] + "a", info["stem"] + "um"]
                return ", ".join(str(form) for form in forms)
            return f"{adj} {3 if info.get('decl') == (1, 2) else max(1, len(forms))}"
        if not forms and info.get("decl") == (1, 2):
            forms = [adj, info["stem"] + "a", info["stem"] + "um"]
        return ", ".join(str(form) for form in forms) if forms else adj

    def _ar_pair_category(noun, adjective):
        noun_decl = noun_vocab[noun].get("decl")
        adj_decl = adj_vocab[adjective].get("decl")
        if noun_decl == 1:
            noun_family = "1"
        elif str(noun_decl).startswith("2"):
            noun_family = "2"
        elif str(noun_decl).startswith("3") or noun_decl == 3:
            noun_family = "3"
        elif str(noun_decl).startswith("4") or noun_decl == 4:
            noun_family = "4"
        elif str(noun_decl).startswith("5"):
            noun_family = "5"
        else:
            noun_family = str(noun_decl)
        same_family = (
            noun_family in ("1", "2") if adj_decl == (1, 2)
            else noun_family == "3" if adj_decl == 3
            else False
        )
        if not same_family:
            return "different"
        if adj_decl == 3 and noun_family == "3":
            strong_i_stem = (
                noun_decl == "3_istem_neut"
                or noun_vocab[noun].get("true_i_stem") is True
            )
            if not strong_i_stem:
                return "third_mixed"
        return "same"

    def _ar_weighted_pair():
        pools = {"different": [], "third_mixed": [], "same": []}
        for noun in active_vocab:
            for adjective in active_adj_vocab:
                pools[_ar_pair_category(noun, adjective)].append((noun, adjective))
        available = [category for category, pairs in pools.items() if pairs]
        if not available:
            return None, None
        weights = {"different": 0.60, "third_mixed": 0.25, "same": 0.15}
        category = random.choices(
            available, weights=[weights[item] for item in available], k=1
        )[0]
        return random.choice(pools[category])

    def _ar_allowed_numbers(noun, adjective):
        restriction = noun_vocab[noun].get("number")
        if restriction == "singular":
            numbers = ["sg"]
        elif restriction == "plural":
            numbers = ["pl"]
        else:
            numbers = ["sg", "pl"]
        if adj_vocab[adjective].get("no_pl"):
            numbers = [number for number in numbers if number != "pl"]
        return numbers

    def _ar_cases(noun, adjective, number, gender):
        cases = [case for case in noun_options["case"] if case != "voc"]
        if include_vocative:
            noun_voc = build_noun([noun, "voc", number])
            noun_nom = build_noun([noun, "nom", number])
            adj_voc = _ar_adjective_form(adjective, "voc", gender, number)
            adj_nom = _ar_adjective_form(adjective, "nom", gender, number)
            if noun_voc != noun_nom or adj_voc != adj_nom:
                cases.append("voc")
        return cases

    def _ar_forms(value):
        if value is None:
            return []
        return value if isinstance(value, list) else [value]

    def _ar_surface(value, preserve_macrons):
        value = unicodedata.normalize("NFC", str(value))
        return value if preserve_macrons else remove_macrons(value)

    def recognition_gen_question():
        noun, adjective = _ar_weighted_pair()
        if not noun or not adjective:
            return None
        raw_gender = noun_vocab[noun]["gender"]
        gender = random.choice(["m", "f"]) if raw_gender == "m/f" else raw_gender
        print_macrons = st.session_state[widget_key(page_id, "print_macrons")]

        candidates = []
        for number in _ar_allowed_numbers(noun, adjective):
            for case in _ar_cases(noun, adjective, number, gender):
                noun_forms = _ar_forms(build_noun([noun, case, number]))
                adjective_forms = _ar_forms(_ar_adjective_form(adjective, case, gender, number))
                for noun_form in noun_forms:
                    for adjective_form in adjective_forms:
                        if noun_form is None or adjective_form is None:
                            continue
                        phrase = (
                            f"{_ar_surface(noun_form, print_macrons)} "
                            f"{_ar_surface(adjective_form, print_macrons)}"
                        )
                        weight = 0.7 if number == "sg" and case == "nom" else 1.0
                        candidates.append((phrase, case, number, weight))

        if not candidates:
            return None
        phrase, case, number, _ = random.choices(
            candidates, weights=[item[3] for item in candidates], k=1
        )[0]
        st.session_state.agreement_recognition_adjective = adjective
        st.session_state.agreement_recognition_gender = gender
        st.session_state.agreement_recognition_displayed_phrase = phrase
        return [noun, case, number]
'''
    new_generator = textwrap.indent(new_generator, "    ")
    if old_generator not in source:
        raise RuntimeError("Could not locate noun recognition generator for agreement recognition")
    source = source.replace(old_generator, new_generator, 1)

    old_intro = r'''        st.session_state["correct_answer"] = correct_answer = build_noun(st.session_state.current_question)

        noun_prompt = build_dictionary_entry(noun) if show_dictionary_entry else noun
        noun_decl = noun_vocab.get(noun)["decl"]
'''
    old_intro = textwrap.indent(old_intro, "    ")
    new_intro = r'''        adjective = st.session_state.get("agreement_recognition_adjective")
        gender = st.session_state.get("agreement_recognition_gender")
        displayed_phrase = st.session_state.get("agreement_recognition_displayed_phrase", "")
        st.session_state["correct_answer"] = correct_answer = displayed_phrase

        noun_prompt = build_dictionary_entry(noun) if show_dictionary_entry else noun
        adjective_prompt = _ar_adjective_dictionary_entry(adjective) if show_dictionary_entry else adjective
        noun_decl = noun_vocab.get(noun)["decl"]
'''
    new_intro = textwrap.indent(new_intro, "    ")
    if old_intro not in source:
        raise RuntimeError("Could not locate recognition question introduction")
    source = source.replace(old_intro, new_intro, 1)

    old_recognition = r'''        else:
            displayed_form = st.session_state.get("agreement_recognition_displayed_form")
            if not displayed_form:
                displayed_form = correct_answer
                if isinstance(displayed_form, list):
                    displayed_form = random.choice(displayed_form)
                if not st.session_state[widget_key(page_id, "print_macrons")]:
                    displayed_form = remove_macrons(displayed_form)

            article = hungarian_article(displayed_form)
            question_html = (
                f'Milyen alak lehet {article} '
                f'<strong><em>{html.escape(displayed_form)}</em></strong>?'
            )
            if show_dictionary_entry:
                question_html += f' <em>({html.escape(build_dictionary_entry(noun))})</em>'
            if show_declension and show_stem:
                decl_text = f"Ez egy {DECLENSION_NUMBER_LABELS[decl]} declinatiós"
                if third_group:
                    decl_text += f" {third_group}"
                supplementary.append(f"{decl_text} szó, a töve {stem_html}")
            elif show_declension:
                decl_text = f"Ez egy {DECLENSION_NUMBER_LABELS[decl]} declinatiós"
                if third_group:
                    decl_text += f" {third_group} szó."
                else:
                    decl_text += " szó."
                supplementary.append(decl_text)
            elif show_stem:
                supplementary.append(f"A szó töve {stem_html}")

            print_macrons = st.session_state[widget_key(page_id, "print_macrons")]
            comparable_displayed_form = normalize_noun_surface(displayed_form, print_macrons)
            matching_analyses = set()
            for possible_number in noun_options["number"]:
                for possible_case in recognition_cases_for_noun(noun, possible_number):
                    possible_form = build_noun([noun, possible_case, possible_number])
                    if possible_form is None:
                        continue
                    possible_forms = possible_form if isinstance(possible_form, list) else [possible_form]
                    for form in possible_forms:
                        comparable_form = normalize_noun_surface(form, print_macrons)
                        if comparable_form == comparable_displayed_form:
                            matching_analyses.add((possible_number, possible_case))
                            break

            optional_analyses = (
                optional_noun_recognition_analyses(noun, displayed_form, print_macrons)
                & matching_analyses
            )
            required_analyses = matching_analyses - optional_analyses

            supplementary.append(
                "A magánhangzók hosszúsága jelölve van."
                if print_macrons
                else "A magánhangzók hosszúsága nincs jelölve."
            )
            multiple_answer_message = None
            if st.session_state[widget_key(page_id, "indicate_multiple_answers")]:
                if len(required_analyses) > 1:
                    multiple_answer_message = '<span style="color:#7c3aed;">Több helyes válaszlehetőség van.</span>'
            else:
                multiple_answer_message = "Több helyes válaszlehetőség is lehet."
            if multiple_answer_message:
                if show_dictionary_entry and show_declension and show_stem:
                    supplementary.append(f"<br>{multiple_answer_message}")
                else:
                    supplementary.append(multiple_answer_message)
'''
    old_recognition = textwrap.indent(old_recognition, "    ")
    new_recognition = r'''        else:
            print_macrons = st.session_state[widget_key(page_id, "print_macrons")]
            question_html = (
                f'Milyen alakban állhat a <strong><em>{html.escape(displayed_phrase)}</em></strong> '
                f'jelzős kifejezés?'
            )
            if show_dictionary_entry:
                question_html += (
                    f' <em>({html.escape(build_dictionary_entry(noun))} · '
                    f'{html.escape(_ar_adjective_dictionary_entry(adjective))})</em>'
                )

            noun_parts = []
            adjective_parts = []
            if show_declension:
                noun_parts.append(f"{DECLENSION_NUMBER_LABELS[decl]} declinatiós")
                adjective_group = _ar_adjective_group(adjective)
                if adjective_group == "1_2":
                    adjective_parts.append("1–2. declinatiós")
                elif adjective_group and adjective_group.startswith("3_"):
                    adjective_parts.append("3. declinatiós")
            if show_third_group:
                if third_group:
                    noun_parts.append(third_group)
                adjective_group = _ar_adjective_group(adjective)
                if adjective_group and adjective_group.startswith("3_"):
                    adjective_parts.append(
                        {"3_1": "1 végű", "3_2": "2 végű", "3_3": "3 végű"}[adjective_group]
                    )
            if show_stem:
                noun_parts.append(f'a töve <em>{html.escape(display_noun_stem(noun))}-</em>')
                adjective_parts.append(
                    f'a töve <em>{html.escape(str(adj_vocab[adjective].get("stem", "")))}-</em>'
                )
            if noun_parts:
                supplementary.append("<strong>Főnév:</strong> " + ", ".join(noun_parts))
            if adjective_parts:
                supplementary.append("<strong>Melléknév:</strong> " + ", ".join(adjective_parts))

            matching_analyses = set()
            for possible_number in _ar_allowed_numbers(noun, adjective):
                for possible_case in _ar_cases(noun, adjective, possible_number, gender):
                    noun_forms = _ar_forms(build_noun([noun, possible_case, possible_number]))
                    adjective_forms = _ar_forms(
                        _ar_adjective_form(adjective, possible_case, gender, possible_number)
                    )
                    for noun_form in noun_forms:
                        for adjective_form in adjective_forms:
                            possible_phrase = (
                                f"{_ar_surface(noun_form, print_macrons)} "
                                f"{_ar_surface(adjective_form, print_macrons)}"
                            )
                            if possible_phrase == displayed_phrase:
                                matching_analyses.add((possible_number, possible_case))

            optional_analyses = set()
            required_analyses = matching_analyses

            supplementary.append(
                "A magánhangzók hosszúsága jelölve van."
                if print_macrons
                else "A magánhangzók hosszúsága nincs jelölve."
            )
            multiple_answer_message = None
            if st.session_state[widget_key(page_id, "indicate_multiple_answers")]:
                if len(required_analyses) > 1:
                    multiple_answer_message = '<span style="color:#7c3aed;">Több helyes válaszlehetőség van.</span>'
            else:
                multiple_answer_message = "Több helyes válaszlehetőség is lehet."
            if multiple_answer_message:
                supplementary.append(multiple_answer_message)
'''
    new_recognition = textwrap.indent(new_recognition, "    ")
    if old_recognition not in source:
        raise RuntimeError("Could not locate noun recognition display block")
    source = source.replace(old_recognition, new_recognition, 1)

    old_curr = r'''        curr_question = {
            "pos": "noun",
            "word": noun,
'''
    old_curr = textwrap.indent(old_curr, "    ")
    new_curr = r'''        curr_question = {
            "pos": "agreement_recognize" if exercise_type == "recognize" else "noun",
            "word": [noun, adjective] if exercise_type == "recognize" else noun,
'''
    new_curr = textwrap.indent(new_curr, "    ")
    if old_curr not in source:
        raise RuntimeError("Could not locate recognition logging block")
    source = source.replace(old_curr, new_curr, 1)

    return source


def apply_recognition_mode(source):
    needle = 'exec(compile(source, str(Path(__file__).with_name("agreement_base.py")), "exec"))'
    replacement = (
        'from agreement_middle_patch import apply_recognition_base\n'
        'source = apply_recognition_base(source)\n'
        + needle
    )
    if needle not in source:
        raise RuntimeError("Could not locate agreement base execution point for recognition mode")
    return source.replace(needle, replacement, 1)
