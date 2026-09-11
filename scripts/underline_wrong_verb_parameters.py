from pathlib import Path

path = Path('verbs.py')
text = path.read_text()

def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 occurrence, found {count}')
    text = text.replace(old, new)

# Always use the pedagogically familiar full dictionary entry for sum.
old = '''def verb_dictionary_entry(verb):
    """Use the same compact verb-entry format as the identify-stems exercise."""
    data = complete_verb_vocab[verb]
'''
new = '''def verb_dictionary_entry(verb):
    """Use the same compact verb-entry format as the identify-stems exercise."""
    if verb == "sum":
        return "sum, esse, fui"

    data = complete_verb_vocab[verb]
'''
replace_once(old, new, 'sum dictionary entry')

# Add HTML feedback formatting that underlines only incorrect parameters.
anchor = '''def canonical_verb_analysis(analysis, lexical_voice):
'''
insert = '''def verb_recognition_mismatch_categories(user_analysis, correct_analysis, lexical_voice):
    """Return displayed categories that are wrong in one supplied analysis."""
    user = dict(user_analysis)
    correct = dict(correct_analysis)

    if lexical_voice in ["dep", "semidep"]:
        user.pop("voice", None)
        correct.pop("voice", None)

    mismatches = set()

    if correct.get("mood") == "impv":
        # Plain imper. is intentionally sufficient for both imperative types.
        # Explicit 2. imper. is wrong only for an ordinary/present imperative.
        if user.get("mood") != "impv" or (
            user.get("second_imperative") and correct.get("relative_tense") != "fut"
        ):
            mismatches.add("mood")

        # Voice is optional for imperatives. If supplied, however, it must agree.
        if "voice" in user and "voice" in correct and user.get("voice") != correct.get("voice"):
            mismatches.add("voice")
        for category in ["number", "person"]:
            if user.get(category) != correct.get(category):
                mismatches.add(category)
        return mismatches

    for category in ["relative_tense", "aspect", "mood", "voice", "number", "person"]:
        if category in correct and user.get(category) != correct.get(category):
            mismatches.add(category)
    return mismatches


def closest_verb_recognition_mismatches(correct_analysis, user_analyses, lexical_voice):
    """Compare a correct analysis with the learner analysis nearest to it."""
    if not user_analyses:
        return set()
    candidates = [
        verb_recognition_mismatch_categories(user_analysis, correct_analysis, lexical_voice)
        for user_analysis in user_analyses
    ]
    return min(candidates, key=len)


def format_correct_verb_recognition_analysis_html(correct_analysis, user_analyses, lexical_voice):
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
if text.count(anchor) != 1:
    raise SystemExit(f'feedback formatter anchor: expected 1, found {text.count(anchor)}')
text = text.replace(anchor, insert + anchor)

old = '''                        correct_text = ", ".join(
                            html.escape(format_correct_verb_recognition_analysis(analysis))
                            for analysis in recognition_correct_analyses
                        )
'''
new = '''                        if evaluation == "incorrect":
                            correct_text = ", ".join(
                                format_correct_verb_recognition_analysis_html(
                                    analysis,
                                    parsed_analyses["analyses"],
                                    lexical_voice,
                                )
                                for analysis in recognition_correct_analyses
                            )
                        else:
                            correct_text = ", ".join(
                                html.escape(format_correct_verb_recognition_analysis(analysis))
                                for analysis in recognition_correct_analyses
                            )
'''
replace_once(old, new, 'incorrect recognition highlighting')

compile(text, 'verbs.py', 'exec')
path.write_text(text)
