from pathlib import Path

path = Path('verbs.py')
text = path.read_text()

def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 occurrence, found {count}')
    text = text.replace(old, new)

# Preserve which grammatical categories were actually typed by the learner,
# before any setting-based or morphology-based inference fills gaps.
old = '''    analyses = []
    for index in range(analysis_count):
        analysis = {}
        for category in VERB_ANALYSIS_CATEGORY_ORDER:
            values = by_category[category]
            if not values:
                continue
            analysis[category] = values[0] if len(values) == 1 else values[index]
        analyses.append(analysis)
'''
new = '''    analyses = []
    explicit_categories = {
        category for category, values in by_category.items() if values
    }
    for index in range(analysis_count):
        analysis = {"_explicit_categories": set(explicit_categories)}
        for category in VERB_ANALYSIS_CATEGORY_ORDER:
            values = by_category[category]
            if not values:
                continue
            analysis[category] = values[0] if len(values) == 1 else values[index]
        analyses.append(analysis)
'''
replace_once(old, new, 'explicit category tracking')

old = '''def format_correct_verb_recognition_analysis_html(correct_analysis, user_analyses, lexical_voice):
    """Format a correct analysis and underline parameters the learner got wrong."""
    mismatches = closest_verb_recognition_mismatches(
        correct_analysis, user_analyses, lexical_voice
    )

    def render(category, text):
        escaped = html.escape(str(text))
        if category in mismatches:
            return f"<u>{escaped}</u>"
        return escaped

    if correct_analysis.get("mood") == "impv":
        mood_text = (
            "2. imperativus"
            if correct_analysis.get("relative_tense") == "fut"
            else "imperativus"
        )
        parts = [render("mood", mood_text)]
        if "voice" in correct_analysis:
            parts.append(render("voice", VERB_ANALYSIS_CANONICAL_LABELS[("voice", correct_analysis["voice"])]))
        if "number" in correct_analysis:
            parts.append(render("number", VERB_ANALYSIS_CANONICAL_LABELS[("number", correct_analysis["number"])]))
        if "person" in correct_analysis:
            parts.append(render("person", correct_analysis["person"]))
        return " ".join(parts)

    parts = []
    for category in VERB_ANALYSIS_CATEGORY_ORDER:
        if category == "gender" or category not in correct_analysis:
            continue
        parts.append(
            render(category, VERB_ANALYSIS_CANONICAL_LABELS[(category, correct_analysis[category])])
        )
    return " ".join(parts)
'''
new = '''def format_correct_verb_recognition_analysis_html(correct_analysis, user_analyses, lexical_voice):
    """Color supplied parameters green/red and omit parameters inferred for the learner."""
    if not user_analyses:
        return html.escape(format_correct_verb_recognition_analysis(correct_analysis))

    comparisons = []
    for user_analysis in user_analyses:
        mismatches = verb_recognition_mismatch_categories(
            user_analysis, correct_analysis, lexical_voice
        )
        comparisons.append((len(mismatches), user_analysis, mismatches))
    _, closest_user, mismatches = min(comparisons, key=lambda item: item[0])
    explicit_categories = set(closest_user.get("_explicit_categories", set()))

    def render(category, text):
        if category not in explicit_categories:
            return None
        escaped = html.escape(str(text))
        color = "#b3261e" if category in mismatches else "#188038"
        return f'<span style="color:{color};">{escaped}</span>'

    if correct_analysis.get("mood") == "impv":
        mood_text = (
            "2. imperativus"
            if correct_analysis.get("relative_tense") == "fut"
            else "imperativus"
        )
        candidates = [("mood", mood_text)]
        if "voice" in correct_analysis:
            candidates.append(("voice", VERB_ANALYSIS_CANONICAL_LABELS[("voice", correct_analysis["voice"])]))
        if "number" in correct_analysis:
            candidates.append(("number", VERB_ANALYSIS_CANONICAL_LABELS[("number", correct_analysis["number"])]))
        if "person" in correct_analysis:
            candidates.append(("person", correct_analysis["person"]))
        return " ".join(
            rendered for category, value in candidates
            if (rendered := render(category, value)) is not None
        )

    parts = []
    for category in VERB_ANALYSIS_CATEGORY_ORDER:
        if category == "gender" or category not in correct_analysis:
            continue
        rendered = render(
            category,
            VERB_ANALYSIS_CANONICAL_LABELS[(category, correct_analysis[category])],
        )
        if rendered is not None:
            parts.append(rendered)
    return " ".join(parts)
'''
replace_once(old, new, 'color feedback formatter')

compile(text, 'verbs.py', 'exec')
path.write_text(text)
