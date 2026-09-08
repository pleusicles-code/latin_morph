from pathlib import Path

root = Path(__file__).resolve().parents[1]
nouns_path = root / "nouns.py"
vocab_path = root / "vocab.py"

nouns = nouns_path.read_text()
vocab = vocab_path.read_text()

# Deus keeps its alternative-form data but is no longer classified as an irregular noun.
old = '''        "deus": {"gender": "m", \n            "decl": "2_us",\n            "stem": "de",\n            "irreg": {\n                "irreg": True,\n                "sg": {\n'''
new = '''        "deus": {"gender": "m", \n            "decl": "2_us",\n            "stem": "de",\n            "irreg": {\n                "sg": {\n'''
if vocab.count(old) != 1:
    raise RuntimeError(f"Expected deus irregular flag once, found {vocab.count(old)}")
vocab = vocab.replace(old, new, 1)

# Clean generic/reset defaults now that deus is not in the irregular selector.
nouns = nouns.replace('"irregs_include": ["deus"],', '"irregs_include": [],')
nouns = nouns.replace('st.session_state.nouns_irregs_include = ["deus"]', 'st.session_state.nouns_irregs_include = []')

# Generalize recognition evaluation to support accepted-but-optional analyses.
old_eval = '''def evaluate_noun_recognition_answer(user_analyses, possible_analyses):
    """Return correct / partial / incorrect using complete-analysis semantics."""
    user_analyses = set(user_analyses)
    possible_analyses = set(possible_analyses)
    correct_supplied = user_analyses & possible_analyses

    if user_analyses == possible_analyses:
        return "correct"
    if correct_supplied:
        return "partial"
    return "incorrect"
'''
new_eval = '''def evaluate_noun_recognition_answer(user_analyses, required_analyses, optional_analyses=None):
    """Return correct / partial / incorrect, allowing accepted optional analyses."""
    user_analyses = set(user_analyses)
    required_analyses = set(required_analyses)
    optional_analyses = set(optional_analyses or ())
    valid_analyses = required_analyses | optional_analyses

    if required_analyses.issubset(user_analyses) and user_analyses.issubset(valid_analyses):
        return "correct"
    if user_analyses & valid_analyses:
        return "partial"
    return "incorrect"
'''
if nouns.count(old_eval) != 1:
    raise RuntimeError(f"Expected evaluator once, found {nouns.count(old_eval)}")
nouns = nouns.replace(old_eval, new_eval, 1)

# Add the recognition-only optional-analysis rule for deus/deum.
anchor = '''    def recognition_cases_for_noun(noun, number):
        """Return cases used in noun recognition, with vocative only when distinctive."""
'''
helper = '''    def optional_noun_recognition_analyses(noun, displayed_form, preserve_macrons):
        """Return valid analyses accepted in recognition but never required."""
        if (
            noun == "deus"
            and normalize_noun_surface(displayed_form, preserve_macrons)
            == normalize_noun_surface("deum", preserve_macrons)
        ):
            return {("pl", "gen")}
        return set()

    def recognition_cases_for_noun(noun, number):
        """Return cases used in noun recognition, with vocative only when distinctive."""
'''
if nouns.count(anchor) != 1:
    raise RuntimeError(f"Expected recognition helper anchor once, found {nouns.count(anchor)}")
nouns = nouns.replace(anchor, helper, 1)

# Make sg. acc. the representative internal target when the selected surface is deus/deum.
old_rep = '''        displayed_form = random.choices(displayed_forms, weights=form_weights, k=1)[0]
        case, number = random.choice(list(form_analyses[displayed_form]))
        st.session_state.nouns_recognition_displayed_form = displayed_form
'''
new_rep = '''        displayed_form = random.choices(displayed_forms, weights=form_weights, k=1)[0]
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
        st.session_state.nouns_recognition_displayed_form = displayed_form
'''
if nouns.count(old_rep) != 1:
    raise RuntimeError(f"Expected representative selection once, found {nouns.count(old_rep)}")
nouns = nouns.replace(old_rep, new_rep, 1)

# Split matching analyses into required and optional sets; ambiguity messaging uses required only.
old_match_tail = '''                        if comparable_form == comparable_displayed_form:
                            matching_analyses.add((possible_number, possible_case))
                            break

            vowel_phrase = "are" if print_macrons else "are not"
            question += f"  \\nVowel lengths {vowel_phrase} indicated"
            if st.session_state[widget_key(page_id, "indicate_multiple_answers")]:
                if len(matching_analyses) > 1:
'''
new_match_tail = '''                        if comparable_form == comparable_displayed_form:
                            matching_analyses.add((possible_number, possible_case))
                            break

            optional_analyses = (
                optional_noun_recognition_analyses(noun, displayed_form, print_macrons)
                & matching_analyses
            )
            required_analyses = matching_analyses - optional_analyses

            vowel_phrase = "are" if print_macrons else "are not"
            question += f"  \\nVowel lengths {vowel_phrase} indicated"
            if st.session_state[widget_key(page_id, "indicate_multiple_answers")]:
                if len(required_analyses) > 1:
'''
if nouns.count(old_match_tail) != 1:
    raise RuntimeError(f"Expected matching/ambiguity block once, found {nouns.count(old_match_tail)}")
nouns = nouns.replace(old_match_tail, new_match_tail, 1)

# Evaluate against required + optional analyses.
old_call = '''                            evaluation = evaluate_noun_recognition_answer(
                                parsed_answer["analyses"],
                                matching_analyses,
                            )
'''
new_call = '''                            evaluation = evaluate_noun_recognition_answer(
                                parsed_answer["analyses"],
                                required_analyses,
                                optional_analyses,
                            )
'''
if nouns.count(old_call) != 1:
    raise RuntimeError(f"Expected evaluator call once, found {nouns.count(old_call)}")
nouns = nouns.replace(old_call, new_call, 1)

# Feedback: optional analyses count as correct when supplied, but are never shown as missing/required.
old_feedback_setup = '''                        user_analyses = set(parsed_answer["analyses"])
                        possible_analyses = set(matching_analyses)
                        correct_supplied = user_analyses & possible_analyses
                        incorrect_supplied = user_analyses - possible_analyses
                        missing_analyses = possible_analyses - user_analyses
                        all_possible_text = format_noun_analysis_list(possible_analyses)
'''
new_feedback_setup = '''                        user_analyses = set(parsed_answer["analyses"])
                        required_analyses_set = set(required_analyses)
                        optional_analyses_set = set(optional_analyses)
                        valid_analyses = required_analyses_set | optional_analyses_set
                        correct_supplied = user_analyses & valid_analyses
                        incorrect_supplied = user_analyses - valid_analyses
                        missing_analyses = required_analyses_set - user_analyses
                        all_possible_text = format_noun_analysis_list(required_analyses_set)
'''
if nouns.count(old_feedback_setup) != 1:
    raise RuntimeError(f"Expected feedback setup once, found {nouns.count(old_feedback_setup)}")
nouns = nouns.replace(old_feedback_setup, new_feedback_setup, 1)

nouns_path.write_text(nouns)
vocab_path.write_text(vocab)
