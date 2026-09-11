from pathlib import Path

path = Path('verbs.py')
text = path.read_text()

old = '''def parse_verb_morphology_analyses(text):
    """Return canonical verb analyses, expanding shared parameters.

    The number of analyses is the greatest number of occurrences of any
    grammatical category. A category supplied once is shared by all analyses;
    a category supplied once per analysis is paired positionally. This allows
    compact answers such as ``praes impf praes perf ind act sg 3`` to express
    two full analyses while sharing mood, voice, number, and person.
    """
    normalized = normalize_verb_morphology_tokens(text)
    if not normalized:
        return {"valid": False, "analyses": [], "error": "no recognized parameters"}

    by_category = {category: [] for category in VERB_ANALYSIS_CATEGORY_ORDER}
    for category, value in normalized:
        by_category[category].append(value)

    analysis_count = max((len(values) for values in by_category.values()), default=0)
    if analysis_count == 0:
        return {"valid": False, "analyses": [], "error": "no recognized parameters"}

    for category, values in by_category.items():
        if len(values) not in (0, 1, analysis_count):
            return {
                "valid": False,
                "analyses": [],
                "error": f"cannot distribute {category} parameters across analyses",
            }

    analyses = []
    for index in range(analysis_count):
        analysis = {}
        for category in VERB_ANALYSIS_CATEGORY_ORDER:
            values = by_category[category]
            if not values:
                continue
            analysis[category] = values[0] if len(values) == 1 else values[index]
        analyses.append(analysis)

    return {"valid": True, "analyses": analyses, "error": None}
'''

new = '''def parse_verb_morphology_analyses(
    text,
    *,
    selected_tenses=None,
    selected_voices=None,
    selected_moods=None,
    lexical_voice=None,
):
    """Parse, expand, infer, and validate verb analyses.

    Repeated categories create multiple analyses; categories supplied once are
    shared. Missing parameters are inferred only where the current exercise
    settings or Latin morphology make them pedagogically unambiguous.
    """
    raw_tokens = tokenize_morphology_answer(text)
    recognized = []
    for raw_token in raw_tokens:
        pieces = segment_verb_morphology_token(raw_token)
        if pieces is None:
            return {
                "valid": False,
                "analyses": [],
                "error": "unrecognized parameter",
                "invalid_token": raw_token,
            }
        recognized.extend(pieces)

    if not recognized:
        return {"valid": False, "analyses": [], "error": "no recognized parameters"}

    normalized = [VERB_MORPHOLOGY_ALIASES[token] for token in recognized]
    by_category = {category: [] for category in VERB_ANALYSIS_CATEGORY_ORDER}
    for category, value in normalized:
        by_category[category].append(value)

    analysis_count = max((len(values) for values in by_category.values()), default=0)
    if analysis_count == 0:
        return {"valid": False, "analyses": [], "error": "no recognized parameters"}

    for category, values in by_category.items():
        if len(values) not in (0, 1, analysis_count):
            return {
                "valid": False,
                "analyses": [],
                "error": f"cannot distribute {category} parameters across analyses",
            }

    analyses = []
    for index in range(analysis_count):
        analysis = {}
        for category in VERB_ANALYSIS_CATEGORY_ORDER:
            values = by_category[category]
            if not values:
                continue
            analysis[category] = values[0] if len(values) == 1 else values[index]
        analyses.append(analysis)

    selected_tenses = list(selected_tenses or [])
    selected_voices = list(selected_voices or [])
    selected_moods = list(selected_moods or [])

    tense_components = {
        "pres": ("pres", "impf"),
        "impf": ("past", "impf"),
        "fut": ("fut", "impf"),
        "perf": ("pres", "perf"),
        "plupf": ("past", "perf"),
        "fut_pf": ("fut", "perf"),
    }

    for analysis in analyses:
        # A single practised tense makes both tense components implicit. If
        # more than one tense is practised, both components remain compulsory.
        if len(selected_tenses) == 1:
            inferred_relative, inferred_aspect = tense_components[selected_tenses[0]]
            if "relative_tense" in analysis and analysis["relative_tense"] != inferred_relative:
                return {"valid": False, "analyses": [], "error": "tense contradicts exercise settings"}
            if "aspect" in analysis and analysis["aspect"] != inferred_aspect:
                return {"valid": False, "analyses": [], "error": "aspect contradicts exercise settings"}
            analysis.setdefault("relative_tense", inferred_relative)
            analysis.setdefault("aspect", inferred_aspect)
        elif "relative_tense" not in analysis or "aspect" not in analysis:
            return {"valid": False, "analyses": [], "error": "incomplete tense"}

        # Mood inference: one selected mood is implicit. If indicativus and
        # imperativus are the only practised moods, missing mood defaults to
        # indicativus. Future finite forms likewise cannot be subjunctive.
        if "mood" not in analysis:
            if len(selected_moods) == 1:
                analysis["mood"] = "impv" if selected_moods[0] in ["impv", "fut_impv"] else selected_moods[0]
            elif set(selected_moods) and set(selected_moods) <= {"ind", "impv", "fut_impv"} and "ind" in selected_moods:
                analysis["mood"] = "ind"
            elif analysis.get("relative_tense") == "fut":
                analysis["mood"] = "ind"

        # Voice inference. Deponents and semideponents never require a voice
        # token; pass. is accepted for deponent morphology, and semideponents
        # accept whichever visible voice matches the relevant system.
        if lexical_voice not in ["dep", "semidep"] and "voice" not in analysis:
            if len(selected_voices) == 1:
                analysis["voice"] = selected_voices[0]

        required = ["relative_tense", "aspect", "mood", "number", "person"]
        if lexical_voice not in ["dep", "semidep"]:
            required.append("voice")
        missing = [category for category in required if category not in analysis]
        if missing:
            return {
                "valid": False,
                "analyses": [],
                "error": "missing required parameter",
                "missing": missing,
            }

        # Morphologically impossible combinations are parse/analysis errors,
        # not merely wrong answers.
        if analysis["relative_tense"] == "fut" and analysis["mood"] == "subj":
            return {"valid": False, "analyses": [], "error": "future subjunctive does not exist"}
        if analysis["mood"] == "impv":
            if analysis["relative_tense"] == "past" or analysis["aspect"] == "perf":
                return {"valid": False, "analyses": [], "error": "invalid imperative tense"}
            if analysis["relative_tense"] == "pres" and analysis["person"] != "2":
                return {"valid": False, "analyses": [], "error": "invalid present imperative person"}
            if analysis["relative_tense"] == "fut" and analysis["person"] not in ["2", "3"]:
                return {"valid": False, "analyses": [], "error": "invalid future imperative person"}

        if lexical_voice == "dep":
            if analysis.get("voice") not in [None, "pass"]:
                return {"valid": False, "analyses": [], "error": "invalid deponent voice"}
        elif lexical_voice == "semidep":
            expected_voice = "act" if analysis["aspect"] == "impf" else "pass"
            if analysis.get("voice") not in [None, expected_voice]:
                return {"valid": False, "analyses": [], "error": "invalid semideponent voice"}

    return {"valid": True, "analyses": analyses, "error": None}
'''

if text.count(old) != 1:
    raise SystemExit(f'Expected parser block once, found {text.count(old)}')
text = text.replace(old, new)

old = '''            with st.form(key="verb_answer_form", clear_on_submit=True):
'''
new = '''            with st.form(key="verb_answer_form", clear_on_submit=(exercise_type != "recognize")):
'''
if text.count(old) != 1:
    raise SystemExit(f'Expected verb form declaration once, found {text.count(old)}')
text = text.replace(old, new)

old = '''                        parsed_analyses = parse_verb_morphology_analyses(user_answer)
                        if parsed_analyses["valid"]:
                            formatted_analyses = [
                                format_verb_morphology_analysis(analysis)
                                for analysis in parsed_analyses["analyses"]
                            ]
                            recognized_html = "<br>".join(
                                html.escape(analysis) for analysis in formatted_analyses
                            ) or "&nbsp;"
                        else:
                            recognized_tokens = recognized_verb_morphology_tokens(user_answer)
                            recognized_html = " ".join(
                                html.escape(token) for token in recognized_tokens
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
if text.count(old) != 1:
    raise SystemExit(f'Expected recognition submit block once, found {text.count(old)}')
text = text.replace(old, new)

compile(text, 'verbs.py', 'exec')
path.write_text(text)
