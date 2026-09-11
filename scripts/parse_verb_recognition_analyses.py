from pathlib import Path

path = Path('verbs.py')
text = path.read_text()

old = '''def normalize_verb_morphology_tokens(text):
    """Normalize recognized verb-analysis tokens, including concatenated forms.

    Longest-first segmentation ensures ``imper`` is tried before the imperfect
    alias ``imp``. Future/second imperatives are not distinguished yet.
    """
    return [
        VERB_MORPHOLOGY_ALIASES[token]
        for token in recognized_verb_morphology_tokens(text)
    ]


def participial_answer_variants(answers):
'''

new = '''def normalize_verb_morphology_tokens(text):
    """Normalize recognized verb-analysis tokens, including concatenated forms.

    Longest-first segmentation ensures ``imper`` is tried before the imperfect
    alias ``imp``. Future/second imperatives are not distinguished yet.
    """
    return [
        VERB_MORPHOLOGY_ALIASES[token]
        for token in recognized_verb_morphology_tokens(text)
    ]


VERB_ANALYSIS_CATEGORY_ORDER = (
    "relative_tense",
    "aspect",
    "mood",
    "voice",
    "number",
    "person",
)

VERB_ANALYSIS_CANONICAL_LABELS = {
    ("relative_tense", "pres"): "praes.",
    ("relative_tense", "past"): "praet.",
    ("relative_tense", "fut"): "fut.",
    ("aspect", "impf"): "impf.",
    ("aspect", "perf"): "perf.",
    ("mood", "ind"): "ind.",
    ("mood", "subj"): "coni.",
    ("mood", "impv"): "imper.",
    ("voice", "act"): "act.",
    ("voice", "pass"): "pass.",
    ("number", "sg"): "sg.",
    ("number", "pl"): "pl.",
    ("person", "1"): "1",
    ("person", "2"): "2",
    ("person", "3"): "3",
}


def parse_verb_morphology_analyses(text):
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


def format_verb_morphology_analysis(analysis):
    """Format one analysis in BevLat's fixed canonical order and abbreviations."""
    return " ".join(
        VERB_ANALYSIS_CANONICAL_LABELS[(category, analysis[category])]
        for category in VERB_ANALYSIS_CATEGORY_ORDER
        if category in analysis
    )


def participial_answer_variants(answers):
'''

if text.count(old) != 1:
    raise SystemExit(f'Expected parser insertion point once, found {text.count(old)}')
text = text.replace(old, new)

old_feedback = '''                        recognized_tokens = recognized_verb_morphology_tokens(user_answer)
                        recognized_html = " ".join(html.escape(token) for token in recognized_tokens) or "&nbsp;"
                        st.session_state.button_disable = True
                        st.session_state.answer_checked = True
                        st.session_state.result_message = "**Good job!**"
                        st.session_state.answer_display_message = feedback_box(
                            recognized_html, "correct"
                        )
'''

new_feedback = '''                        parsed_analyses = parse_verb_morphology_analyses(user_answer)
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
'''

if text.count(old_feedback) != 1:
    raise SystemExit(f'Expected recognition feedback block once, found {text.count(old_feedback)}')
text = text.replace(old_feedback, new_feedback)

compile(text, 'verbs.py', 'exec')
path.write_text(text)
