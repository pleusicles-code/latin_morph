from pathlib import Path

path = Path('verbs.py')
text = path.read_text()


def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 occurrence, found {count}')
    text = text.replace(old, new)

# Add semantic helpers after formatter.
old = '''def format_verb_morphology_analysis(analysis):
    """Format one analysis in BevLat's fixed canonical order and abbreviations."""
    return " ".join(
        VERB_ANALYSIS_CANONICAL_LABELS[(category, analysis[category])]
        for category in VERB_ANALYSIS_CATEGORY_ORDER
        if category in analysis
    )


def participial_answer_variants(answers):
'''
new = '''def format_verb_morphology_analysis(analysis):
    """Format one analysis in BevLat's fixed canonical order and abbreviations."""
    return " ".join(
        VERB_ANALYSIS_CANONICAL_LABELS[(category, analysis[category])]
        for category in VERB_ANALYSIS_CATEGORY_ORDER
        if category in analysis
    )


def canonical_verb_analysis(analysis, lexical_voice):
    """Return a hashable semantic analysis for comparison.

    Voice is intentionally ignored for deponents and semideponents: learners
    need not supply it, although the parser accepts the correct visible voice.
    """
    normalized = dict(analysis)
    if lexical_voice in ["dep", "semidep"]:
        normalized.pop("voice", None)
    return tuple((category, normalized[category]) for category in VERB_ANALYSIS_CATEGORY_ORDER if category in normalized)


def verb_id_to_analysis(verb_id, lexical_voice):
    tense_components = {
        "pres": ("pres", "impf"),
        "impf": ("past", "impf"),
        "fut": ("fut", "impf"),
        "perf": ("pres", "perf"),
        "plupf": ("past", "perf"),
        "fut_pf": ("fut", "perf"),
    }
    relative_tense, aspect = tense_components[verb_id["tense"]]
    analysis = {
        "relative_tense": relative_tense,
        "aspect": aspect,
        "mood": verb_id["mood"],
        "number": verb_id["num"],
        "person": str(verb_id["pers"]),
    }
    if lexical_voice not in ["dep", "semidep"]:
        analysis["voice"] = verb_id["voice"]
    return analysis


def evaluate_verb_recognition_answer(user_analyses, correct_analyses, lexical_voice):
    user_set = {canonical_verb_analysis(analysis, lexical_voice) for analysis in user_analyses}
    correct_set = {canonical_verb_analysis(analysis, lexical_voice) for analysis in correct_analyses}
    if user_set == correct_set:
        return "correct"
    if user_set and user_set < correct_set:
        return "partial"
    return "incorrect"


def participial_answer_variants(answers):
'''
replace_once(old, new, 'analysis helpers')

# Add enumerator immediately after build_verb is complete, before gen_func assignment.
old = '''        return [verb_form, verb_id, verb_principal_parts]

    st.session_state.gen_func = build_verb
'''
new = '''        return [verb_form, verb_id, verb_principal_parts]

    def matching_verb_recognition_analyses(verb, displayed_form, preserve_macrons):
        """Enumerate all enabled finite analyses producing the displayed form."""
        lexical_voice = verb_vocab[verb]["voice"]
        target_surface = displayed_form if preserve_macrons else remove_macrons(displayed_form)
        target_surface = str(target_surface).casefold()
        analyses = {}

        if lexical_voice == "dep":
            candidate_voices = ["dep"] if "pass" in voice_selector else []
        elif lexical_voice == "semidep":
            candidate_voices = []  # chosen per tense below
        else:
            candidate_voices = []
            if "act" in voice_selector:
                candidate_voices.append("act")
            if "pass" in voice_selector and not verb_vocab[verb].get("no_pass"):
                candidate_voices.append("pass")

        saved_append_answer = st.session_state.append_answer
        st.session_state.append_answer = False
        try:
            for possible_tense in tense_selector:
                possible_moods = []
                if "ind" in mood_selector:
                    possible_moods.append("ind")
                if "subj" in mood_selector and possible_tense not in ["fut", "fut_pf"]:
                    possible_moods.append("subj")
                if possible_tense == "pres" and "impv" in mood_selector:
                    possible_moods.append("impv")
                if possible_tense == "fut" and "fut_impv" in mood_selector:
                    possible_moods.append("impv")

                if lexical_voice == "semidep":
                    if possible_tense in pres_sys:
                        voices_for_tense = ["act"] if "act" in voice_selector else []
                    else:
                        voices_for_tense = ["dep"] if "pass" in voice_selector else []
                else:
                    voices_for_tense = candidate_voices

                for possible_mood in possible_moods:
                    if possible_mood == "impv":
                        persons = [2] if possible_tense == "pres" else [2, 3]
                    else:
                        persons = [1, 2, 3]
                    for possible_voice in voices_for_tense:
                        for possible_number in ["sg", "pl"]:
                            for possible_person in persons:
                                if (
                                    possible_mood == "impv"
                                    and possible_tense == "fut"
                                    and possible_voice in ["pass", "dep"]
                                    and possible_number == "pl"
                                    and possible_person == 2
                                ):
                                    continue
                                candidate_id = {
                                    "verb": verb,
                                    "pers": possible_person,
                                    "num": possible_number,
                                    "tense": possible_tense,
                                    "voice": possible_voice,
                                    "mood": possible_mood,
                                }
                                try:
                                    built = build_verb(candidate_id)
                                except Exception:
                                    continue
                                if not built:
                                    continue
                                candidate_form = built[0]
                                candidate_forms = candidate_form if isinstance(candidate_form, list) else [candidate_form]
                                matched = False
                                for form in candidate_forms:
                                    surface = form if preserve_macrons else remove_macrons(form)
                                    if str(surface).casefold() == target_surface:
                                        matched = True
                                        break
                                if matched:
                                    analysis = verb_id_to_analysis(candidate_id, lexical_voice)
                                    key = canonical_verb_analysis(analysis, lexical_voice)
                                    analyses[key] = analysis
        finally:
            st.session_state.append_answer = saved_append_answer
        return list(analyses.values())

    st.session_state.gen_func = build_verb
'''
replace_once(old, new, 'recognition enumerator')

# Compute correct analyses when rendering recognition prompt.
old = '''        if exercise_type == "recognize":
            displayed_form = verb_form[0] if isinstance(verb_form, list) else verb_form
            if not print_macrons:
                displayed_form = remove_macrons(displayed_form)
            form_article = hungarian_article(displayed_form)
            question_html = (
                f'Milyen alak lehet {form_article} <strong><em>{html.escape(displayed_form)}</em></strong>?'
            )
            if show_principal_parts:
                question_html += f' <em>({html.escape(verb_dictionary_entry(verb))})</em>'
        else:
'''
new = '''        recognition_correct_analyses = []
        if exercise_type == "recognize":
            displayed_form = verb_form[0] if isinstance(verb_form, list) else verb_form
            if not print_macrons:
                displayed_form = remove_macrons(displayed_form)
            recognition_correct_analyses = matching_verb_recognition_analyses(
                verb, displayed_form, print_macrons
            )
            form_article = hungarian_article(displayed_form)
            question_html = (
                f'Milyen alak lehet {form_article} <strong><em>{html.escape(displayed_form)}</em></strong>?'
            )
            if show_principal_parts:
                question_html += f' <em>({html.escape(verb_dictionary_entry(verb))})</em>'
        else:
'''
replace_once(old, new, 'correct analyses computation')

# Replace recognition submit branch with actual scoring, preserving parse-error retry.
old = '''                        parsed_analyses = parse_verb_morphology_analyses(
                            user_answer,
                            selected_tenses=tense_selector,
                            selected_voices=voice_selector,
                            selected_moods=mood_selector,
                            lexical_voice=verb_vocab[verb]["voice"],
                        )
                        if not parsed_analyses["valid"]:
                            st.session_state.button_disable = False
                            st.session_state.answer_checked = False
                            st.session_state.result_message = ""
                            st.session_state.auto_advance_trigger = False
                            st.session_state.answer_display_message = (
                                "Ellenőrizd a válasz paramétereit, majd próbáld újra. "
                                "A válaszod nincs még értékelve."
                            )
                            return

                        formatted_analyses = [
                            format_verb_morphology_analysis(analysis)
                            for analysis in parsed_analyses["analyses"]
                        ]
                        recognized_html = "<br>".join(
                            html.escape(analysis) for analysis in formatted_analyses
                        ) or "&nbsp;"
                        st.session_state.button_disable = True
                        st.session_state.answer_checked = True
                        st.session_state.result_message = "**Good job!**"
                        st.session_state.answer_display_message = feedback_box(
                            recognized_html, "correct"
                        )
                        st.session_state.auto_advance_trigger = bool(st.session_state.auto_advance)
                        return
'''
new = '''                        parsed_analyses = parse_verb_morphology_analyses(
                            user_answer,
                            selected_tenses=tense_selector,
                            selected_voices=voice_selector,
                            selected_moods=mood_selector,
                            lexical_voice=verb_vocab[verb]["voice"],
                        )
                        if not parsed_analyses["valid"]:
                            st.session_state.button_disable = False
                            st.session_state.answer_checked = False
                            st.session_state.result_message = ""
                            st.session_state.auto_advance_trigger = False
                            st.session_state.answer_display_message = (
                                "Ellenőrizd a válasz paramétereit, majd próbáld újra. "
                                "A válaszod nincs még értékelve."
                            )
                            return

                        lexical_voice = verb_vocab[verb]["voice"]
                        evaluation = evaluate_verb_recognition_answer(
                            parsed_analyses["analyses"],
                            recognition_correct_analyses,
                            lexical_voice,
                        )
                        original_correct_answer = st.session_state.correct_answer
                        st.session_state.correct_answer = (
                            user_answer if evaluation == "correct" else "__verb_recognition_incorrect__"
                        )
                        if evaluation == "partial":
                            st.session_state.answer_credit_override = 0.5 if award_partial_credit else 0

                        submit_and_check_answer()
                        st.session_state.correct_answer = original_correct_answer

                        correct_text = "<br>".join(
                            html.escape(format_verb_morphology_analysis(analysis))
                            for analysis in recognition_correct_analyses
                        )
                        if evaluation == "correct":
                            st.session_state.result_message = "**Good job!**"
                            st.session_state.answer_display_message = feedback_box(
                                "<strong>Helyes válasz!</strong>", "correct"
                            )
                        elif evaluation == "partial":
                            st.session_state.result_message = "**Partially correct.**"
                            st.session_state.answer_display_message = feedback_box(
                                "<strong>Részben helyes válasz.</strong> "
                                f"<strong>A helyes válaszok:<br>{correct_text}</strong>",
                                "partial",
                            )
                        else:
                            st.session_state.result_message = "**Incorrect. Better luck next time!**"
                            label = "A helyes válasz" if len(recognition_correct_analyses) == 1 else "A helyes válaszok"
                            st.session_state.answer_display_message = feedback_box(
                                f"<strong>Helytelen válasz. {label}:<br>{correct_text}</strong>",
                                "incorrect",
                            )
                        return
'''
replace_once(old, new, 'recognition scoring')

compile(text, 'verbs.py', 'exec')
path.write_text(text)
