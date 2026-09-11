from pathlib import Path

path = Path('verbs.py')
text = path.read_text()

def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 occurrence, found {count}')
    text = text.replace(old, new)

# Recognize compact gender labels as verb-analysis tokens.
old = '''    # person
    "1": ("person", "1"),
    "2": ("person", "2"),
    "3": ("person", "3"),
}'''
new = '''    # person
    "1": ("person", "1"),
    "2": ("person", "2"),
    "3": ("person", "3"),
    # optional participial gender for passive/deponent perfect-system forms
    "m": ("gender", "m"),
    "f": ("gender", "f"),
    "n": ("gender", "n"),
}'''
replace_once(old, new, 'gender aliases')

old = '''VERB_ANALYSIS_CATEGORY_ORDER = (
    "relative_tense",
    "aspect",
    "mood",
    "voice",
    "number",
    "person",
)'''
new = '''VERB_ANALYSIS_CATEGORY_ORDER = (
    "relative_tense",
    "aspect",
    "mood",
    "voice",
    "gender",
    "number",
    "person",
)'''
replace_once(old, new, 'analysis category order')

old = '''    ("voice", "act"): "act.",
    ("voice", "pass"): "pass.",
    ("number", "sg"): "sg.",'''
new = '''    ("voice", "act"): "act.",
    ("voice", "pass"): "pass.",
    ("gender", "m"): "m.",
    ("gender", "f"): "f.",
    ("gender", "n"): "n.",
    ("number", "sg"): "sg.",'''
replace_once(old, new, 'gender labels')

# Gender is optional, but if supplied it only makes sense with perfect-system
# passive/deponent morphology. Treat misuse as a parse/analysis error.
old = '''        if lexical_voice == "dep":
            if analysis.get("voice") not in [None, "pass"]:
                return {"valid": False, "analyses": [], "error": "invalid deponent voice"}
        elif lexical_voice == "semidep":'''
new = '''        if "gender" in analysis:
            participial_perfect = (
                analysis.get("aspect") == "perf"
                and (
                    lexical_voice in ["dep", "semidep"]
                    or analysis.get("voice") == "pass"
                )
            )
            if not participial_perfect:
                return {"valid": False, "analyses": [], "error": "invalid participial gender"}

        if lexical_voice == "dep":
            if analysis.get("voice") not in [None, "pass"]:
                return {"valid": False, "analyses": [], "error": "invalid deponent voice"}
        elif lexical_voice == "semidep":'''
replace_once(old, new, 'gender applicability validation')

# Gender remains optional and therefore does not appear in ordinary canonical
# answer display.
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
        if category in analysis and category != "gender"
    )
'''
replace_once(old, new, 'formatter ignores optional gender')

old = '''    normalized = dict(analysis)
    if lexical_voice in ["dep", "semidep"]:
        normalized.pop("voice", None)
    return tuple((category, normalized[category]) for category in VERB_ANALYSIS_CATEGORY_ORDER if category in normalized)
'''
new = '''    normalized = dict(analysis)
    if lexical_voice in ["dep", "semidep"]:
        normalized.pop("voice", None)
    # Gender is an optional refinement of participial perfect forms and is
    # never required for correctness.
    normalized.pop("gender", None)
    return tuple((category, normalized[category]) for category in VERB_ANALYSIS_CATEGORY_ORDER if category in normalized)
'''
replace_once(old, new, 'canonical comparison ignores optional gender')

# If the learner supplies a gender, validate it against the internally
# preserved gender of the displayed participial form.
old = '''    if lexical_voice in ["dep", "semidep"]:
        user.pop("voice", None)
        correct.pop("voice", None)

    if user.get("mood") == "impv" and correct.get("mood") == "impv":'''
new = '''    if lexical_voice in ["dep", "semidep"]:
        user.pop("voice", None)
        correct.pop("voice", None)

    supplied_gender = user.pop("gender", None)
    correct_gender = correct.pop("gender", None)
    if supplied_gender is not None and supplied_gender != correct_gender:
        return False

    if user.get("mood") == "impv" and correct.get("mood") == "impv":'''
replace_once(old, new, 'validate supplied gender')

# Preserve which member of a three-gender participial form list matched the
# displayed surface. This metadata is only used if the learner supplies m/f/n.
old = '''                                candidate_form = built[0]
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
'''
new = '''                                candidate_form = built[0]
                                candidate_forms = candidate_form if isinstance(candidate_form, list) else [candidate_form]
                                matched_index = None
                                for form_index, form in enumerate(candidate_forms):
                                    surface = form if preserve_macrons else remove_macrons(form)
                                    if str(surface).casefold() == target_surface:
                                        matched_index = form_index
                                        break
                                if matched_index is not None:
                                    analysis = verb_id_to_analysis(candidate_id, lexical_voice)
                                    if len(candidate_forms) == 3 and matched_index < 3:
                                        analysis["gender"] = ("m", "f", "n")[matched_index]
                                    key = canonical_verb_analysis(analysis, lexical_voice)
                                    analyses[key] = analysis
'''
replace_once(old, new, 'preserve matched participial gender')

compile(text, 'verbs.py', 'exec')
path.write_text(text)
