from pathlib import Path

path = Path('verbs.py')
text = path.read_text()

def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 occurrence, found {count}')
    text = text.replace(old, new)

replace_once('import html\nimport unicodedata\n', 'import html\nimport re\nimport unicodedata\n', 'import re')

old = '''    raw_tokens = tokenize_morphology_answer(text)
    recognized = []
'''
new = '''    # ``2. imper...`` is the only special marker for the future/second
    # imperative. The dot is compulsory so ordinary person ``2`` remains
    # unambiguous (e.g. ``imper act sg 2``).
    second_imperative_pattern = re.compile(
        r"(?<!\\w)2\\.\\s*(imperativus|imper)(?=\\W|$)",
        flags=re.IGNORECASE,
    )
    explicit_second_imperative = bool(second_imperative_pattern.search(text))
    parse_text = second_imperative_pattern.sub(lambda match: match.group(1), text)

    raw_tokens = tokenize_morphology_answer(parse_text)
    recognized = []
'''
replace_once(old, new, 'special second imperative marker')

old = '''    for analysis in analyses:
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
'''
new = '''    for analysis in analyses:
        # The explicit ``2. imper...`` marker itself supplies the mood and
        # constrains the analysis to the future/second imperative.
        if explicit_second_imperative:
            analysis["mood"] = "impv"
            analysis["second_imperative"] = True
            analysis.setdefault("relative_tense", "fut")
            analysis.setdefault("aspect", "impf")

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

        # Imperatives do not require a tense/aspect answer. Plain ``imper`` is
        # accepted for both the ordinary and second imperative; ``2. imper``
        # is the optional explicit distinction for the latter. Other moods
        # retain the normal tense/aspect requirements and inference rules.
        if analysis.get("mood") != "impv":
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
'''
replace_once(old, new, 'imperative tense inference')

old = '''        required = ["relative_tense", "aspect", "mood", "number", "person"]
        if lexical_voice not in ["dep", "semidep"]:
            required.append("voice")
'''
new = '''        required = ["mood", "number", "person"]
        if analysis.get("mood") != "impv":
            required = ["relative_tense", "aspect"] + required
        if lexical_voice not in ["dep", "semidep"]:
            required.append("voice")
'''
replace_once(old, new, 'imperative required categories')

old = '''        if analysis["relative_tense"] == "fut" and analysis["mood"] == "subj":
            return {"valid": False, "analyses": [], "error": "future subjunctive does not exist"}
        if analysis["mood"] == "impv":
            if analysis["relative_tense"] == "past" or analysis["aspect"] == "perf":
                return {"valid": False, "analyses": [], "error": "invalid imperative tense"}
            if analysis["relative_tense"] == "pres" and analysis["person"] != "2":
                return {"valid": False, "analyses": [], "error": "invalid present imperative person"}
            if analysis["relative_tense"] == "fut" and analysis["person"] not in ["2", "3"]:
                return {"valid": False, "analyses": [], "error": "invalid future imperative person"}
'''
new = '''        if analysis.get("relative_tense") == "fut" and analysis["mood"] == "subj":
            return {"valid": False, "analyses": [], "error": "future subjunctive does not exist"}
        if analysis["mood"] == "impv":
            if analysis.get("relative_tense") == "past" or analysis.get("aspect") == "perf":
                return {"valid": False, "analyses": [], "error": "invalid imperative tense"}
            if analysis.get("relative_tense") == "pres" and analysis["person"] != "2":
                return {"valid": False, "analyses": [], "error": "invalid present imperative person"}
            if analysis.get("relative_tense") == "fut" and analysis["person"] not in ["2", "3"]:
                return {"valid": False, "analyses": [], "error": "invalid future imperative person"}
'''
replace_once(old, new, 'safe imperative validation')

old = '''def evaluate_verb_recognition_answer(user_analyses, correct_analyses, lexical_voice):
    user_set = {canonical_verb_analysis(analysis, lexical_voice) for analysis in user_analyses}
    correct_set = {canonical_verb_analysis(analysis, lexical_voice) for analysis in correct_analyses}
    if user_set == correct_set:
        return "correct"
    if user_set and user_set < correct_set:
        return "partial"
    return "incorrect"
'''
new = '''def verb_recognition_analysis_matches(user_analysis, correct_analysis, lexical_voice):
    """Match one supplied analysis against one genuinely possible analysis.

    Plain ``imper.`` deliberately ignores the present/future imperative
    distinction. Explicit ``2. imper.`` matches future imperatives only.
    """
    user = dict(user_analysis)
    correct = dict(correct_analysis)
    if lexical_voice in ["dep", "semidep"]:
        user.pop("voice", None)
        correct.pop("voice", None)

    if user.get("mood") == "impv" and correct.get("mood") == "impv":
        if user.get("second_imperative") and correct.get("relative_tense") != "fut":
            return False
        for category in ["mood", "voice", "number", "person"]:
            if category in user and user.get(category) != correct.get(category):
                return False
        # If the learner voluntarily supplied tense/aspect, respect it.
        for category in ["relative_tense", "aspect"]:
            if category in user and user.get(category) != correct.get(category):
                return False
        return True

    return canonical_verb_analysis(user, lexical_voice) == canonical_verb_analysis(correct, lexical_voice)


def evaluate_verb_recognition_answer(user_analyses, correct_analyses, lexical_voice):
    if not user_analyses or not correct_analyses:
        return "incorrect"

    matched_correct = set()
    for user_analysis in user_analyses:
        matches = {
            index for index, correct_analysis in enumerate(correct_analyses)
            if verb_recognition_analysis_matches(user_analysis, correct_analysis, lexical_voice)
        }
        if not matches:
            return "incorrect"
        matched_correct.update(matches)

    if len(matched_correct) == len(correct_analyses):
        return "correct"
    return "partial"
'''
replace_once(old, new, 'imperative wildcard evaluation')

old = '''def format_verb_morphology_analysis(analysis):
    """Format one analysis in BevLat's fixed canonical order and abbreviations."""
    return " ".join(
        VERB_ANALYSIS_CANONICAL_LABELS[(category, analysis[category])]
        for category in VERB_ANALYSIS_CATEGORY_ORDER
        if category in analysis
    )
'''
new = '''def format_verb_morphology_analysis(analysis):
    """Format one analysis in BevLat's fixed canonical order and abbreviations."""
    return " ".join(
        VERB_ANALYSIS_CANONICAL_LABELS[(category, analysis[category])]
        for category in VERB_ANALYSIS_CATEGORY_ORDER
        if category in analysis
    )


def format_correct_verb_recognition_analysis(analysis):
    """Format feedback, naming the second imperative explicitly when needed."""
    if analysis.get("mood") == "impv":
        mood_text = "2. imperativus" if analysis.get("relative_tense") == "fut" else "imperativus"
        parts = [mood_text]
        if "voice" in analysis:
            parts.append(VERB_ANALYSIS_CANONICAL_LABELS[("voice", analysis["voice"])])
        if "number" in analysis:
            parts.append(VERB_ANALYSIS_CANONICAL_LABELS[("number", analysis["number"])])
        if "person" in analysis:
            parts.append(str(analysis["person"]))
        return " ".join(parts)
    return format_verb_morphology_analysis(analysis)
'''
replace_once(old, new, 'imperative correct feedback formatter')

old = '''        form_label = " ".join(
            part for part in [tense_labels[tense], mood_label, voice_label, number_label, str(person)]
            if part and part != "None"
        )
'''
new = '''        form_label = " ".join(
            part for part in [
                None if mood == "impv" else tense_labels[tense],
                mood_label,
                voice_label,
                number_label,
                str(person),
            ]
            if part and part != "None"
        )
'''
replace_once(old, new, 'inflection imperative prompt')

old = '''                        correct_text = "<br>".join(
                            html.escape(format_verb_morphology_analysis(analysis))
                            for analysis in recognition_correct_analyses
                        )
'''
new = '''                        correct_text = "<br>".join(
                            html.escape(format_correct_verb_recognition_analysis(analysis))
                            for analysis in recognition_correct_analyses
                        )
'''
replace_once(old, new, 'recognition correct feedback format')

compile(text, 'verbs.py', 'exec')
path.write_text(text)
