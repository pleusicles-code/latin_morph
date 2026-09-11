import streamlit as st
import random
import time
import pandas as pd
import ast
import html
import re
import unicodedata
from utils import radio_change, reset, new_question, remove_macrons, submit_and_check_answer, clear_page, send_setting, save_defaults, clear_defaults, auto_advance_delay, tokenize_morphology_answer
from exercise_presets import (bool_setting, choice_setting, list_setting, resolve_exercise_settings, initialize_widget_state,
                              widget_key, url_preset_active, exercise_link_popover)
from vocab import import_verbs

st.set_page_config("BevLat – Igék", layout="centered")

st.session_state.verbs_enforce_macrons = st.session_state.enforce_macrons["verbs_enforce_macrons"]

# if st.session_state.question_list:
questions_asked = st.session_state.question_list

page_id = "verbs"
clear_page(page_id)

defaults = st.session_state.default_settings.get(f"{page_id}.py", {})

complete_verb_vocab = import_verbs()
pres_sys = ["pres","fut","impf"]
perf_sys = ["perf", "plupf", "fut_pf"]


st.markdown("# Igék")


## SET OPTIONS ##

verb_abbrevs = {"ind": "indicativus",
               "subj": "coniunctivus",
               "impv": "imperativus",
               "inf": "infinitivus",
               "sg": "singularis",
               "pl": "pluralis",
               "pres": "praes. impf.",
               "impf": "praet. impf.",
               "fut": "fut. impf.",
               "perf": "praes. perf.",
               "plupf": "praet. perf.",
               "fut_pf": "fut. perf.",
               "act": "activum",
               "dep": "deponens",
               "semidep": "semideponens",
               "pass": "passivum",
                1: "1.",
                2: "2.",
                3: "3.",}


def feedback_box(content, state):
    colors = {
        "correct": ("#e3f3e7", "#7aa682"),
        "incorrect": ("#f7dddd", "#c48282"),
    }
    background, border = colors[state]
    return (
        f'<div style="background:{background};border:1px solid {border};border-radius:0.5rem;'
        f'padding:0.55rem 0.75rem;line-height:1.7;">{content}</div>'
    )


def heavy(text, italic=False):
    escaped = html.escape(str(text))
    if italic:
        escaped = f"<em>{escaped}</em>"
    return f'<span style="font-weight:900;">{escaped}</span>'


LATIN_VOWELS = set("aeiouy")
LATIN_DIPHTHONGS = {"ae", "au", "oe", "ei", "eu", "ui"}


def hungarian_article(word):
    normalized = "".join(
        char for char in unicodedata.normalize("NFD", str(word).lower())
        if unicodedata.category(char) != "Mn"
    )
    if not normalized or normalized[0] not in LATIN_VOWELS:
        return "a"
    if len(normalized) > 1 and normalized[1] in LATIN_VOWELS:
        return "az" if normalized[:2] in LATIN_DIPHTHONGS else "a"
    return "az"


VERB_MORPHOLOGY_ALIASES = {
    # relative tense
    "praesens": ("relative_tense", "pres"),
    "praes": ("relative_tense", "pres"),
    "praeteritum": ("relative_tense", "past"),
    "praet": ("relative_tense", "past"),
    "futurum": ("relative_tense", "fut"),
    "fut": ("relative_tense", "fut"),
    # aspect
    "imperfectum": ("aspect", "impf"),
    "impf": ("aspect", "impf"),
    "imp": ("aspect", "impf"),
    "perfectum": ("aspect", "perf"),
    "perf": ("aspect", "perf"),
    # voice
    "activum": ("voice", "act"),
    "activi": ("voice", "act"),
    "act": ("voice", "act"),
    "passivum": ("voice", "pass"),
    "passivi": ("voice", "pass"),
    "pass": ("voice", "pass"),
    # mood
    "indicativus": ("mood", "ind"),
    "ind": ("mood", "ind"),
    "coniunctivus": ("mood", "subj"),
    "coni": ("mood", "subj"),
    "imperativus": ("mood", "impv"),
    "imper": ("mood", "impv"),
    # number
    "singularis": ("number", "sg"),
    "sing": ("number", "sg"),
    "sg": ("number", "sg"),
    "pluralis": ("number", "pl"),
    "plur": ("number", "pl"),
    "pl": ("number", "pl"),
    # person
    "1": ("person", "1"),
    "2": ("person", "2"),
    "3": ("person", "3"),
    # optional participial gender for passive/deponent perfect-system forms
    "m": ("gender", "m"),
    "f": ("gender", "f"),
    "n": ("gender", "n"),
}


VERB_MORPHOLOGY_SOURCE_TOKENS = tuple(
    sorted(VERB_MORPHOLOGY_ALIASES, key=len, reverse=True)
)


def segment_verb_morphology_token(token):
    """Fully segment one tokenizer token into known verb-analysis tokens."""
    memo = {}

    def segment_from(index):
        if index == len(token):
            return []
        if index in memo:
            return memo[index]
        for candidate in VERB_MORPHOLOGY_SOURCE_TOKENS:
            if token.startswith(candidate, index):
                remainder = segment_from(index + len(candidate))
                if remainder is not None:
                    memo[index] = [candidate] + remainder
                    return memo[index]
        memo[index] = None
        return None

    return segment_from(0)


def recognized_verb_morphology_tokens(text):
    """Return recognized source tokens in input order, including concatenated forms."""
    recognized = []
    for raw_token in tokenize_morphology_answer(text):
        pieces = segment_verb_morphology_token(raw_token)
        if pieces is not None:
            recognized.extend(pieces)
    return recognized


def normalize_verb_morphology_tokens(text):
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
    "gender",
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
    ("gender", "m"): "m.",
    ("gender", "f"): "f.",
    ("gender", "n"): "n.",
    ("number", "sg"): "sg.",
    ("number", "pl"): "pl.",
    ("person", "1"): "1",
    ("person", "2"): "2",
    ("person", "3"): "3",
}


def parse_verb_morphology_analyses(
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
    # ``2. imper...`` is the only special marker for the future/second
    # imperative. The dot is compulsory so ordinary person ``2`` remains
    # unambiguous (e.g. ``imper act sg 2``).
    second_imperative_pattern = re.compile(
        r"(?<!\w)2\.\s*(imperativus|imper)(?=\W|$)",
        flags=re.IGNORECASE,
    )
    explicit_second_imperative = bool(second_imperative_pattern.search(text))
    parse_text = second_imperative_pattern.sub(lambda match: match.group(1), text)

    raw_tokens = tokenize_morphology_answer(parse_text)
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
    explicit_categories = {
        category for category, values in by_category.items() if values
    }
    for index in range(analysis_count):
        analysis = {
            "_explicit_categories": set(explicit_categories),
            "_explicit_second_imperative": explicit_second_imperative,
        }
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

        # Voice inference. Deponents and semideponents never require a voice
        # token; pass. is accepted for deponent morphology, and semideponents
        # accept whichever visible voice matches the relevant system.
        if lexical_voice not in ["dep", "semidep"] and "voice" not in analysis:
            if len(selected_voices) == 1:
                analysis["voice"] = selected_voices[0]

        required = ["mood", "number", "person"]
        if analysis.get("mood") != "impv":
            required = ["relative_tense", "aspect"] + required
        if lexical_voice not in ["dep", "semidep"] and analysis.get("mood") != "impv":
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
        if analysis.get("relative_tense") == "fut" and analysis["mood"] == "subj":
            return {"valid": False, "analyses": [], "error": "future subjunctive does not exist"}
        if analysis["mood"] == "impv":
            if analysis.get("relative_tense") == "past" or analysis.get("aspect") == "perf":
                return {"valid": False, "analyses": [], "error": "invalid imperative tense"}
            if analysis.get("relative_tense") == "pres" and analysis["person"] != "2":
                return {"valid": False, "analyses": [], "error": "invalid present imperative person"}
            if analysis.get("relative_tense") == "fut" and analysis["person"] not in ["2", "3"]:
                return {"valid": False, "analyses": [], "error": "invalid future imperative person"}

        if "gender" in analysis:
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
        elif lexical_voice == "semidep":
            if analysis.get("mood") == "impv":
                expected_voice = "act"
            else:
                expected_voice = "act" if analysis.get("aspect") == "impf" else "pass"
            if analysis.get("voice") not in [None, expected_voice]:
                return {"valid": False, "analyses": [], "error": "invalid semideponent voice"}

    return {"valid": True, "analyses": analyses, "error": None}


def format_verb_morphology_analysis(analysis):
    """Format one analysis in BevLat's fixed canonical order and abbreviations."""
    return " ".join(
        VERB_ANALYSIS_CANONICAL_LABELS[(category, analysis[category])]
        for category in VERB_ANALYSIS_CATEGORY_ORDER
        if category in analysis and category != "gender"
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


def verb_recognition_mismatch_categories(user_analysis, correct_analysis, lexical_voice):
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


def verb_recognition_parameter_label(analysis, category, *, correction=False):
    """Return the compact feedback label for one verb-analysis parameter."""
    if category == "mood" and analysis.get("mood") == "impv":
        if correction:
            return "2. imperativus" if analysis.get("relative_tense") == "fut" else "imperativus"
        if analysis.get("_explicit_second_imperative"):
            return "2. imper."
    return VERB_ANALYSIS_CANONICAL_LABELS[(category, analysis[category])]


def verb_recognition_pair_cost(user_analysis, correct_analysis, lexical_voice):
    """Score how closely one supplied analysis resembles one correct analysis."""
    mismatches = verb_recognition_mismatch_categories(
        user_analysis, correct_analysis, lexical_voice
    )
    explicit = set(user_analysis.get("_explicit_categories", set()))
    # Gender is optional but, when supplied, participates in pairing/feedback.
    if "gender" in explicit and user_analysis.get("gender") != correct_analysis.get("gender"):
        mismatches = set(mismatches) | {"gender"}
    return len(mismatches), mismatches


def pair_verb_recognition_analyses(user_analyses, correct_analyses, lexical_voice):
    """Greedily pair supplied analyses with the nearest unused correct analyses."""
    remaining_correct = set(range(len(correct_analyses)))
    pairs = []
    for user_analysis in user_analyses:
        if not remaining_correct:
            pairs.append((user_analysis, None, set(user_analysis.get("_explicit_categories", set()))))
            continue
        ranked = []
        for index in remaining_correct:
            cost, mismatches = verb_recognition_pair_cost(
                user_analysis, correct_analyses[index], lexical_voice
            )
            ranked.append((cost, index, mismatches))
        _, best_index, mismatches = min(ranked, key=lambda item: (item[0], item[1]))
        remaining_correct.remove(best_index)
        pairs.append((user_analysis, correct_analyses[best_index], mismatches))

    # If the learner omitted an entire valid analysis, show that missing analysis
    # only in the correction row; the answer row stays empty for those cells.
    for index in sorted(remaining_correct):
        pairs.append((None, correct_analyses[index], set()))
    return pairs


def format_incorrect_verb_recognition_table_html(user_analyses, correct_analyses, lexical_voice):
    """Render a compact two-row comparison grid for an incorrect recognition answer."""
    pairs = pair_verb_recognition_analyses(
        user_analyses, correct_analyses, lexical_voice
    )
    if not pairs:
        return '<strong>Helytelen válasz.</strong>'

    explicit_template = set()
    for user_analysis in user_analyses:
        explicit_template.update(user_analysis.get("_explicit_categories", set()))
    # Keep canonical order and never invent parameters that were inferred.
    template_categories = [
        category for category in VERB_ANALYSIS_CATEGORY_ORDER
        if category in explicit_template
    ]

    answer_cells = []
    correction_cells = []
    spacer = '<td aria-hidden="true" style="width:0.8rem;padding:0;"></td>'

    for pair_index, (user_analysis, correct_analysis, mismatches) in enumerate(pairs):
        categories = template_categories
        if user_analysis is not None:
            categories = [
                category for category in VERB_ANALYSIS_CATEGORY_ORDER
                if category in user_analysis.get("_explicit_categories", set())
            ]
        if pair_index:
            answer_cells.append(spacer)
            correction_cells.append(spacer)

        for category in categories:
            cell_style = 'padding:0.08rem 0.28rem;text-align:center;white-space:nowrap;font-weight:800;'
            if user_analysis is None:
                answer_cells.append(f'<td style="{cell_style}">&nbsp;</td>')
                if correct_analysis is not None and category in correct_analysis:
                    correction = html.escape(
                        verb_recognition_parameter_label(correct_analysis, category, correction=True)
                    )
                else:
                    correction = '&mdash;'
                correction_cells.append(
                    f'<td style="{cell_style}color:inherit;">{correction}</td>'
                )
                continue

            if category not in user_analysis:
                answer_cells.append(f'<td style="{cell_style}">&nbsp;</td>')
                correction_cells.append(f'<td style="{cell_style}">&nbsp;</td>')
                continue

            user_text = html.escape(
                verb_recognition_parameter_label(user_analysis, category)
            )
            is_wrong = category in mismatches
            color = '#b3261e' if is_wrong else '#188038'
            answer_cells.append(
                f'<td style="{cell_style}color:{color};">{user_text}</td>'
            )

            if not is_wrong:
                correction_cells.append(f'<td style="{cell_style}">&nbsp;</td>')
            elif correct_analysis is not None and category in correct_analysis:
                correction = html.escape(
                    verb_recognition_parameter_label(correct_analysis, category, correction=True)
                )
                correction_cells.append(
                    f'<td style="{cell_style}color:inherit;">{correction}</td>'
                )
            else:
                correction_cells.append(
                    f'<td style="{cell_style}color:inherit;">&mdash;</td>'
                )

    label_style = 'padding:0.08rem 0.55rem 0.08rem 0;text-align:right;white-space:nowrap;font-weight:700;'
    return (
        '<div style="max-width:100%;overflow-x:auto;">'
        '<table role="presentation" style="border-collapse:collapse;border:0;background:transparent;line-height:1.55;">'
        '<tbody>'
        f'<tr><td style="{label_style}">Helytelen válasz:</td>{"".join(answer_cells)}</tr>'
        f'<tr><td style="{label_style}">Helyesen:</td>{"".join(correction_cells)}</tr>'
        '</tbody></table></div>'
    )


def canonical_verb_analysis(analysis, lexical_voice):
    """Return a hashable semantic analysis for comparison.

    Voice is intentionally ignored for deponents and semideponents: learners
    need not supply it, although the parser accepts the correct visible voice.
    """
    normalized = dict(analysis)
    if lexical_voice in ["dep", "semidep"]:
        normalized.pop("voice", None)
    # Gender is an optional refinement of participial perfect forms and is
    # never required for correctness.
    normalized.pop("gender", None)
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


def verb_recognition_analysis_matches(user_analysis, correct_analysis, lexical_voice):
    """Match one supplied analysis against one genuinely possible analysis.

    Plain ``imper.`` deliberately ignores the present/future imperative
    distinction. Explicit ``2. imper.`` matches future imperatives only.
    """
    user = dict(user_analysis)
    correct = dict(correct_analysis)
    if lexical_voice in ["dep", "semidep"]:
        user.pop("voice", None)
        correct.pop("voice", None)

    supplied_gender = user.pop("gender", None)
    correct_gender = correct.pop("gender", None)
    if supplied_gender is not None and supplied_gender != correct_gender:
        return False

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


def participial_answer_variants(answers):
    """Add compact `3` variants when three gender forms share the same auxiliary."""
    answer_list = list(answers) if isinstance(answers, list) else [answers]
    split_answers = [answer.split(maxsplit=1) for answer in answer_list if isinstance(answer, str)]
    if len(answer_list) != 3 or len(split_answers) != 3 or any(len(parts) != 2 for parts in split_answers):
        return answer_list
    remainders = {parts[1] for parts in split_answers}
    if len(remainders) != 1:
        return answer_list

    remainder = split_answers[0][1]
    expanded = list(answer_list)
    for participle, _ in split_answers:
        expanded.append(f"{participle} 3 {remainder}")
        expanded.append(f"{participle}3 {remainder}")
    return expanded


def compact_participial_answer(answers):
    """Display a three-gender participial paradigm as e.g. `gestus 3 est`."""
    answer_list = list(answers) if isinstance(answers, list) else [answers]
    split_answers = [answer.split(maxsplit=1) for answer in answer_list if isinstance(answer, str)]
    if len(answer_list) == 3 and len(split_answers) == 3 and all(len(parts) == 2 for parts in split_answers):
        remainders = {parts[1] for parts in split_answers}
        if len(remainders) == 1:
            return f"{split_answers[0][0]} 3 {split_answers[0][1]}"
    return None


def verb_dictionary_entry(verb):
    """Use the same compact verb-entry format as the identify-stems exercise."""
    if verb == "sum":
        return "sum, esse, fui"

    data = complete_verb_vocab[verb]
    conj = data.get("conj")
    conj_label = 3 if conj == "3io" else conj
    head = f"{verb} {conj_label}" if conj_label is not None else verb

    # For regular 1st-conjugation verbs, the compact dictionary entry is just lemma + conjugation.
    if conj == 1 and not data.get("irreg"):
        return head

    # The identify-stems exercise uses perfect + supine for ordinary active verbs.
    if data.get("voice") == "act":
        parts = []
        if data.get("perf"):
            parts.append(data["perf"] + "ī")
        if data.get("ppp"):
            parts.append(data["ppp"] + "um")
        elif data.get("fap"):
            parts.append("[" + data["fap"] + "us]")
        return head + ((" " + ", ".join(parts)) if parts else "")

    # For deponent / semideponent verbs, retain the dictionary information
    # available in this exercise rather than inventing an active perfect.
    parts = []
    if data.get("ppp"):
        parts.append(data["ppp"] + "us sum")
    return head + ((" " + ", ".join(parts)) if parts else "")


def learner_present_stem(data):
    stem = data.get("pres")
    if not stem:
        return None
    conj = data.get("conj")
    if conj == 1:
        stem += "ā"
    elif conj == 2:
        stem += "ē"
    elif conj == "3io":
        stem += "i"
    elif conj == 4:
        stem += "ī"
    return stem


def verb_stem_display(verb):
    data = complete_verb_vocab[verb]
    stems = [learner_present_stem(data), data.get("perf"), data.get("ppp")]
    return [stem for stem in stems if stem]

conjugation_dict = {1: "1.",
                    2: "2.",
                    3: "3.",
                    4: "4."}

master_tense_list = ["pres","impf","fut","perf","plupf","fut_pf"]
master_voice_list = ["act", "pass"]
master_mood_list = ["ind", "subj", "impv", "fut_impv"]
default_mood_list = ["ind", "subj", "impv"]
master_irregular_verbs_list = [key for key in complete_verb_vocab.keys() if complete_verb_vocab[key].get("irreg",{}).get("irreg") is True]

# Migrate saved verb settings from the previous selector structure.
defaults = dict(defaults)
if isinstance(defaults.get("conjugation_selector"), list):
    migrated_conjugations = []
    for conj in defaults["conjugation_selector"]:
        visible_conj = 3 if conj == "3io" else conj
        if visible_conj in conjugation_dict and visible_conj not in migrated_conjugations:
            migrated_conjugations.append(visible_conj)
    defaults["conjugation_selector"] = migrated_conjugations
if isinstance(defaults.get("mood_selector"), list):
    migrated_moods = [mood for mood in defaults["mood_selector"] if mood in default_mood_list]
    if defaults.get("fut_impv") and "fut_impv" not in migrated_moods:
        migrated_moods.append("fut_impv")
    defaults["mood_selector"] = migrated_moods or default_mood_list
if isinstance(defaults.get("voice_selector"), list):
    migrated_voices = []
    for voice in defaults["voice_selector"]:
        visible_voice = "pass" if voice in ["pass", "dep", "semidep"] else voice
        if visible_voice in master_voice_list and visible_voice not in migrated_voices:
            migrated_voices.append(visible_voice)
    defaults["voice_selector"] = migrated_voices or master_voice_list
defaults.pop("fut_impv", None)
exercise_schema = {
    "exercise_type": choice_setting("inflect", ["inflect", "recognize"]),
    "print_macrons": bool_setting(False),
    "indicate_multiple_answers": bool_setting(False),
    "award_partial_credit": bool_setting(False),
    "show_principal_parts": bool_setting(True),
    "show_stems": bool_setting(False),
    "conjugation_selector": list_setting(list(conjugation_dict.keys()), list(conjugation_dict.keys())),
    "tense_selector": list_setting(master_tense_list, master_tense_list),
    "voice_selector": list_setting(master_voice_list, master_voice_list),
    "mood_selector": list_setting(default_mood_list, master_mood_list),
    "irreg_selector": list_setting(["sum"], master_irregular_verbs_list),
    "irreg_only": bool_setting(False),
}
exercise_settings = resolve_exercise_settings(page_id, exercise_schema, defaults)
initialize_widget_state(page_id, exercise_settings)
preset_active = url_preset_active(page_id)

#col_options, col_verb_options = st.columns(2)

# options_container = st.container()

# with options_container:
# options_col, conjugation_col = st.columns(2)
# tense_col, voice_col = st.columns(2)
# mood_col, irreg_col = st.columns(2)

option_expander = st.expander("Beállítások", expanded=True)

with option_expander:
    verb_options_col,options_col = st.columns([3,2])

with verb_options_col:
    exercise_type = st.radio(
        "Feladattípus:",
        options=["inflect", "recognize"],
        format_func=lambda value: {
            "inflect": "Ragozás",
            "recognize": "Alakfelismerés",
        }[value],
        horizontal=True,
        key=widget_key(page_id, "exercise_type"),
        on_change=radio_change,
    )

with options_col:
    def switch_verb_macrons():
        st.session_state.enforce_macrons["verbs_enforce_macrons"] = st.session_state["verbs_enforce_macrons"]
        return
    st.markdown("Opciók:", help="Ezeket a beállításokat gyakorlás közben is bármikor módosíthatod.")
    print_macrons = False
    indicate_multiple_answers = False
    award_partial_credit = False
    if exercise_type == "inflect":
        st.checkbox("Hosszú magánhangzók ellenőrzése?",
                    help="Ha be van jelölve, a hosszú magánhangzók hibás jelölése hibás válasznak számít. Ha nincs bejelölve, a hosszúságjelek használhatók, de a program nem értékeli őket.",
                    key="verbs_enforce_macrons",
                    on_change=send_setting,
                    args=(switch_verb_macrons,),
                    kwargs={"streamlit_page":"verbs.py","setting_name":"verbs_enforce_macrons"},
                    )
        macrons = st.session_state.verbs_enforce_macrons
        if macrons:
            st.markdown("A hosszú magánhangzók innen másolhatók:")
            st.code("āēīōū", language=None)
    else:
        print_macrons = st.checkbox(
            "Hosszú magánhangzók jelölése?",
            help="Ha be van kapcsolva, a kérdésben szereplő igealak jelöli a magánhangzók hosszúságát. Ez ritkán két, egyébként azonos írásképű alakot is megkülönböztethet.",
            key=widget_key(page_id, "print_macrons"),
        )
        indicate_multiple_answers = st.checkbox(
            "Több helyes válaszlehetőség jelzése?",
            help="Ha be van kapcsolva, a kérdés külön jelzi, ha az adott alaknak több helyes elemzése van.",
            key=widget_key(page_id, "indicate_multiple_answers"),
        )
        award_partial_credit = st.checkbox(
            "Részpont adása?",
            help="Ha be van kapcsolva, a részben helyes válasz fél pontot ér; különben csak a teljesen helyes válaszért jár pont.",
            key=widget_key(page_id, "award_partial_credit"),
        )

    show_principal_parts = st.checkbox("Szótári alak megjelenítése?",
                                        help="Az ige szótári alakjának (főalakjainak) megjelenítése.",
                                        key=widget_key(page_id, "show_principal_parts"))
    show_stems = st.checkbox("Tövek megjelenítése?",
                             help="A jelenlegi ige töveinek megjelenítése a kérdés alatt.",
                             key=widget_key(page_id, "show_stems"))

# with conjugation_col:
with verb_options_col:
    # st.write("Important note: If you only want to practice irregular verbs, you must deselect all of the conjugations.")

    conjugation_selector = st.multiselect(
        "Válaszd ki, mely coniugatiókat szeretnéd gyakorolni (alapértelmezés szerint mindegyik ki van választva):",
        conjugation_dict.keys(),
        format_func = lambda x: conjugation_dict.get(x),
        key=widget_key(page_id, "conjugation_selector"),
        help = "Ha egy coniugatiót sem választasz ki, csak a kiválasztott rendhagyó igékből kaphatsz kérdést."
        )

# with tense_col:
    tense_dict = {"pres": "praes. impf.",
                  "impf": "praet. impf.",
                  "fut": "fut. impf.",
                  "perf": "praes. perf.",
                  "plupf": "praet. perf.",
                  "fut_pf": "fut. perf."}

    tense_selector = st.multiselect(
        "Válaszd ki, mely igeidőket szeretnéd gyakorolni:",
        master_tense_list,
        format_func = lambda x: tense_dict[x],
        key=widget_key(page_id, "tense_selector")
    )

# with voice_col:
    voice_dict = {"act": "act.",
                  "pass": "pass."}

    voice_selector = st.multiselect(
        "Válaszd ki, mely igenemeket szeretnéd gyakorolni:",
        master_voice_list,
        format_func=lambda x: voice_dict[x],
        key=widget_key(page_id, "voice_selector"),
        help=(
            "A pass. beállítás a deponens igéket is magában foglalja. "
            "Semideponens igék csak akkor szerepelnek, ha a pass. ki van választva: "
            "csak pass. esetén kizárólag a deponens (perfectum-rendszerű) alakjaik, "
            "act. + pass. esetén az activum alakjaik is előfordulhatnak."
        ),
    )

# with mood_col:
    mood_dict = {"ind": "indicativus",
                 "subj": "coniunctivus",
                 "impv": "imperativus",
                 "fut_impv": "2. imperativus"}

    mood_selector = st.multiselect("Válaszd ki, mely módokat szeretnéd gyakorolni:",
                                master_mood_list,
                                format_func=lambda x: mood_dict[x],
                                key=widget_key(page_id, "mood_selector"))


# with irreg_col:
    #master_irregular_verbs_list = ["sum", "possum", "eō", "ferō", "fīō", "volō", "nōlō", "mālō"]
    # if "dō" in master_irregular_verbs_list:
    #     master_irregular_verbs_list.remove("dō")
    irreg_selector = st.multiselect("Válaszd ki, mely rendhagyó igéket szeretnéd gyakorolni:",
                                    master_irregular_verbs_list,
                                    key=widget_key(page_id, "irreg_selector"),
                                    help="A kiválasztott rendhagyó igék a fenti coniugatio-beállításoktól függetlenül előfordulhatnak. Ha csak rendhagyó igéket szeretnél gyakorolni, ne válassz ki egyetlen coniugatiót sem.")

    irreg_only = False
    if irreg_selector:
        irreg_only = st.checkbox("Csak a kiválasztott rendhagyó igék gyakorlása?",
                                    key=widget_key(page_id, "irreg_only"),
                                    help="Ha bejelölöd, csak a kiválasztott rendhagyó igékből kapsz kérdést; ugyanezt érheted el azzal is, ha fent minden coniugatiót kikapcsolsz.")

    fut_impv = "fut_impv" in mood_selector
    if st.session_state.question_generation_error_message:
        st.write(st.session_state.question_generation_error_message)

current_exercise_settings = {
    "exercise_type": exercise_type,
    "print_macrons": print_macrons,
    "indicate_multiple_answers": indicate_multiple_answers,
    "award_partial_credit": award_partial_credit,
    "show_principal_parts": show_principal_parts,
    "show_stems": show_stems,
    "conjugation_selector": conjugation_selector,
    "tense_selector": tense_selector,
    "voice_selector": voice_selector,
    "mood_selector": mood_selector,
    "irreg_selector": irreg_selector,
    "irreg_only": irreg_only,
}

with option_expander:
    if st.user.is_logged_in:
        set_defaults_col, clear_defaults_col, link_col = st.columns(3)
        with set_defaults_col:
            st.button(
                "Beállítások mentése",
                type="primary",
                width="stretch",
                help="A jelenlegi igebeállítások mentése alapértelmezettként (a hosszú magánhangzók ellenőrzésének kivételével).",
                on_click=save_defaults,
                args=(page_id, defaults,),
                kwargs=current_exercise_settings,
                disabled=preset_active,
            )
        with clear_defaults_col:
            st.button(
                "Alapbeállítások",
                type="primary",
                width="stretch",
                help="A BevLat általános alapértelmezett igebeállításainak visszaállítása.",
                on_click=clear_defaults,
                args=(page_id,),
                disabled=preset_active or not defaults,
            )
        with link_col:
            exercise_link_popover(page_id, exercise_schema, current_exercise_settings)
    else:
        exercise_link_popover(page_id, exercise_schema, current_exercise_settings)


## DEFINE AVAILABLE VERBS AND VERB ENDINGS ##

tense_list = list(tense_selector)
# Visible voice settings describe the morphology the learner wants to practise.
# Deponent forms are internally represented as ``dep`` but belong to visible ``pass.``.
internal_voice_selector = list(voice_selector)
if "pass" in voice_selector and "dep" not in internal_voice_selector:
    internal_voice_selector.append("dep")
present_impv = "impv" in mood_selector
fut_impv = "fut_impv" in mood_selector
internal_mood_selector = [mood for mood in mood_selector if mood != "fut_impv"]
if fut_impv and "impv" not in internal_mood_selector:
    internal_mood_selector.append("impv")

internal_conjugation_selector = []
for conj in conjugation_selector:
    if conj == 3:
        internal_conjugation_selector.extend([3, "3io"])
    else:
        internal_conjugation_selector.append(conj)

mood_list = {"ind": 70, "subj": 70, "impv": 10}
moods = list(mood_list.keys())
for md in moods:
    if md not in internal_mood_selector:
        mood_list.pop(md)
if "impv" in mood_list and not ((present_impv and "pres" in tense_list) or (fut_impv and "fut" in tense_list)):
    mood_list.pop("impv")
if all(tns not in tense_list for tns in ["pres","impf","plupf","perf"]) and "subj" in mood_list:
    mood_list.pop("subj")

verb_endings = {
    "pres": {
        "act": {
            "sg": {
                1: "m",
                2: "s",
                3: "t"
                },
            "pl": {
                1: "mus",
                2: "tis",
                3: "nt"
            }
        },
        "pass": {
            "sg": {
                1: "r",
                2: ["ris", "re"],
                3: "tur"
            },
            "pl": {
                1: "mur",
                2: "minī",
                3: "ntur"
            }
        }
    },
    "impf": {
        "act": {
            "ind": {
                "sg": {
                    1: "bam",
                    2: "bās",
                    3: "bat"
                    },
                "pl": {
                    1: "bāmus",
                    2: "bātis",
                    3: "bant"
                }
            }
        },
        "pass": {
            "ind": {
                "sg": {
                    1: "bar",
                    2: ["bāris","bāre"],
                    3: "bātur"
                    },
                "pl": {
                    1: "bāmur",
                    2: "bāminī",
                    3: "bantur"
                }
            }
        },
    },
    "fut": {
        "act": {
            "ind": {
                "sg": {
                    1: "bō",
                    2: "bis",
                    3: "bit"
                    },
                "pl": {
                    1: "bimus",
                    2: "bitis",
                    3: "bunt"
                }
            },
            "impv": {
                "sg": {
                    2: "tō",
                    3: "tō"
                },
                "pl": {
                    2: "tōte",
                    3: "ntō"
                }
            }
        },
        "pass": {
            "ind": {
                "sg": {
                    1: "bor",
                    2: ["beris","bere"],
                    3: "bitur"
                    },
                "pl": {
                    1: "bimur",
                    2: "biminī",
                    3: "buntur"
                }
            },
            "impv": {
                "sg": {
                    2: "tor",
                    3: "tor"
                },
                "pl": {
                    3: "ntor"
                }
            }
        },
    },
    "perf": {
        "act": {
            "ind": {
                "sg": {
                    1: "ī",
                    2: "istī",
                    3: "it"
                },
                "pl": {
                    1: "imus",
                    2: "istis",
                    3: ["ērunt","ēre"]
                },
            },
            "subj": {
                "sg": {
                    1: "erim",
                    2: ["eris","erīs"],
                    3: "erit"
                },
                "pl": {
                    1: ["erimus", "erīmus"],
                    2: ["eritis", "erītis"],
                    3: "erint"
                }
            }
        }
    },
    "plupf": {
        "act": {
            "ind":
                complete_verb_vocab["sum"]["irreg"]["forms"]["impf"]["act"]["ind"]
        }
    },
    "fut_pf": {
        "act": {
            "ind": {
                "sg": {
                    1: "erō",
                    2: ["eris","erīs"],
                    3: "erit"
                },
                "pl": {
                    1: ["erimus", "erīmus"],
                    2: ["eritis", "erītis"],
                    3: "erint"
                }
            }
        }
    }
}

verb_vowels = {
    "pres": {
        "ind": {
            1: "ā",
            2: "ē",
            3: "i",
            "3io": "i",
            4: "ī"
        },
        "subj": {
            1: "ē",
            2: "eā",
            3: "ā",
            "3io": "iā",
            4: "iā"
        },
        "inf": {
            1: "ā",
            2: "ē",
            3: "e",
            "3io": "e",
            4: "ī"
        }
    },
    "impf_fut": {
        1: "ā",
        2: "ē",
        3: "ē",
        "3io": "iē",
        4: "iē"
    }
}


## CREATE QUESTIONS AND ANSWERS ##

# Limit available verbs based on selections of irregulars and voice
verb_vocab = {key: val for key, val in complete_verb_vocab.items()}
for vb in master_irregular_verbs_list:
    if vb not in irreg_selector:
        verb_vocab.pop(vb)
if irreg_only:
    verb_vocab = {key: val for key, val in verb_vocab.items() if key in irreg_selector}
# for feature, feature_list in zip(["voice","conj"],[voice_selector,conjugation_selector + [None]]):
#     verb_vocab = {key: val for key, val in verb_vocab.items() if (verb_vocab[key][feature] in feature_list) or (key in irreg_selector)}
def verb_allowed_by_voice_settings(data):
    lexical_voice = data["voice"]
    if lexical_voice == "act":
        return (
            "act" in voice_selector
            or ("pass" in voice_selector and "no_pass" not in data)
        )
    if lexical_voice == "dep":
        return "pass" in voice_selector
    if lexical_voice == "semidep":
        if "pass" not in voice_selector:
            return False
        # With pass. only, semideponents can contribute only perfect-system
        # (deponent) forms; if no such tense is selected, exclude them entirely.
        return "act" in voice_selector or any(tense in perf_sys for tense in tense_list)
    return False

verb_vocab = {key: val for key, val in verb_vocab.items() if verb_allowed_by_voice_settings(val)}
verb_vocab = {key: val for key, val in verb_vocab.items() if verb_vocab[key]["conj"] in internal_conjugation_selector + [None] or key in irreg_selector}
# if "act" not in voice_selector:
#     verb_vocab = {key: val for key, val in verb_vocab.items() if not (verb_vocab[key].get("impers_pass_only") or verb_vocab[key].get("no_pass"))}
if set(internal_mood_selector) == {"impv"}:
    verb_vocab = {key: val for key, val in verb_vocab.items() if not val.get("no_impv")}
    if "act" not in voice_selector:
        verb_vocab = {key: val for key, val in verb_vocab.items() if not val.get("impers_pass_only")}
if (set(tense_list) <= {"fut","fut_pf"} and "ind" not in internal_mood_selector) or (("subj" not in internal_mood_selector and "ind" not in internal_mood_selector) and (set(tense_list) <= {"fut","fut_pf","impf","plupf"})):
    if not fut_impv:
        verb_vocab = {key:val for key, val in verb_vocab.items() if "ppp" in val or val.get("fap") is not None}
    else:
        if irreg_selector:
            for verb in irreg_selector:
                if not any(complete_verb_vocab[verb]["irreg"]["forms"].get("fut", {}).get(voice, {}).get("impv") for voice in ["act","pass","dep"]) and not all(["ppp" in complete_verb_vocab[verb] or complete_verb_vocab[verb].get("fap") is not None, "inf" in internal_mood_selector]):
                    if verb in verb_vocab:
                        verb_vocab.pop(verb)


#st.write(verb_vocab.keys())

if len(conjugation_selector) == 0 and len(irreg_selector) == 0:
    st.write("Legalább egy coniugatiót vagy rendhagyó igét ki kell választanod.")
elif len(tense_list) == 0:
    st.write("Legalább egy igeidőt ki kell választanod.")
elif len(voice_selector) == 0:
    st.write("Legalább egy igenemet vagy igetípust ki kell választanod.")
elif len(mood_selector) == 0:
    st.write("Legalább egy módot ki kell választanod.")
#    st.session_state.question_generation_error_message = ""
elif len(verb_vocab) == 0:
    st.write("A kiválasztott beállításokkal nincs olyan ige, amelyből kérdést lehetne generálni.")
# elif all([tense_list == ["fut"], mood_selector == ["subj"]]):
#     st.write("No forms exist that meet your selected criteria.")
# elif len(mood_list) == 0:
#     st.write("Based on your selections, it is not possible to generate any valid verb forms.")

# elif (list(mood_list.keys()) == ["inf"] and tense_list == ["fut"] and all([x is None for x in [item.get("ppp") for item in verb_vocab.values()]] + [x is None for x in [item.get("fap") for item in verb_vocab.values()]])):
#     st.write("Based on your selections, it is not possible to generate any valid verb forms.")

else:

    def gen_verb_id():
        avail_tenses = list(tense_list)
        avail_moods = dict(mood_list)
        st.session_state.question_generation_error_message = ""
        conj_random = random.choice(conjugation_selector + (["irreg"] if irreg_selector else []))
        # st.write(conj_random)
        if conj_random == "irreg":
            avail_verbs = [v for v in irreg_selector if v in verb_vocab]
        elif conj_random == 3:
            avail_verbs = [v for v, i in verb_vocab.items() if i["conj"] in [3, "3io"] and v not in irreg_selector]
        else:
            avail_verbs = [v for v, i in verb_vocab.items() if i["conj"] == conj_random and v not in irreg_selector]
        # st.write(avail_verbs)

        if len(avail_verbs) > 0:
            verb = random.choice(avail_verbs)
        else:
            verb = random.choice(list(verb_vocab.keys()))

        # With pass. only, semideponents contribute only their deponent
        # perfect-system forms. Their active present-system forms are hidden.
        if verb_vocab.get(verb, {}).get("voice") == "semidep" and "act" not in voice_selector:
            avail_tenses = [tense for tense in avail_tenses if tense in perf_sys]

     #    verb = "eō"    ## UNCOMMENT AND SET FOR TESTING

        # SET MOOD
        if verb_vocab[verb].get("no_impv") and "impv" in avail_moods:
            avail_moods.pop("impv")
        if verb_vocab[verb].get("impers_pass_only") and "impv" in avail_moods and "act" not in voice_selector:
            avail_moods.pop("impv")
        if set(avail_tenses) <= {"fut","fut_pf"}:
            if "subj" in avail_moods:
                avail_moods.pop("subj")
            if "impv" in avail_moods:
                if (fut_impv and verb == "fīō") or not fut_impv:
                    avail_moods.pop("impv")
        if not avail_moods:
            #st.session_state.question_generation_error_message = ":warning: Your selected options have resulted in an impossibility! Try selecting some different or additional options and hit 'New Question' again."
            return

        i = 0
        tense_list_copy = list(avail_tenses)
        inval_moods = []
        while i == 0 or not tense_list_copy:
            if not tense_list_copy:
                tense_list_copy = list(avail_tenses)
            # st.write(tense_list_copy)
            if inval_moods and set(avail_moods) <= set(inval_moods):
                tense_list_copy = list(avail_tenses)
                inval_moods = []
            while (mood := random.choices(list(avail_moods.keys()), list(avail_moods.values()))[0]) in inval_moods:
                # st.write(mood)
                pass

            # SET TENSE
            # limit tense options depending on mood
            if mood == "subj":
                for tns in ["fut", "fut_pf"]:
                    if tns in tense_list_copy:
                        tense_list_copy.remove(tns)
            elif mood == "inf":
                for tns in ["impf","plupf","fut_pf"]:
                    if tns in tense_list_copy:
                        tense_list_copy.remove(tns)
                if not (verb_vocab[verb].get("ppp") or verb_vocab[verb].get("fap")) and "fut" in tense_list_copy:
                    tense_list_copy.remove("fut")
            elif mood == "impv":
                allowed_impv_tenses = []
                if present_impv and "pres" in tense_list_copy:
                    allowed_impv_tenses.append("pres")
                if fut_impv and "fut" in tense_list_copy and verb != "fīō":
                    allowed_impv_tenses.append("fut")
                tense_list_copy = allowed_impv_tenses
            # st.write(i, verb,mood,tense_list_copy)
            if not tense_list_copy:
                inval_moods.append(mood)
            if i > 5 and not tense_list_copy:
                # st.write("problem!")
                # st.session_state.question_generation_error_message = ":warning: Your selected options have resulted in an impossibility! Try selecting some different options and hit 'New Question' again."
                return
            i+=1
        avail_tenses = list(tense_list_copy)

        if mood == "impv":
            # if verb == "fīō":
            #     tense = "pres"  # this forces a present tense even if only future imperatives are selected, since fīō has no future imperatives
            if "pres" in avail_tenses and "fut" in avail_tenses and fut_impv:
                tense = random.choices(["pres", "fut"], [25, 5])[0]
            elif "fut" in avail_tenses and fut_impv:
                tense = "fut"
            else:
                tense = "pres"
        else:
            tense = random.choice(avail_tenses)
     #    tense = "fut"    ## UNCOMMENT AND SET FOR TESTING

        # SET PERSON AND NUMBER
        ## only if mood isn't infinitive; limit for imperative
        if mood != "inf":
            if mood == "impv":
                if tense == "fut":
                    person = random.choice([2,3])
                else:
                    person = 2
            else:
                person = random.choice([1,2,3])
            number = random.choice(["sg","pl"])
        else:
            person = None
            number = None

        # SET VOICE
        act_pass_choice_dict = {"act": 90, "pass": 10}
        if mood == "inf" and tense == "fut":
            act_pass_choice_dict = {"act": 95, "pass": 5}
        for vc in ["act","pass"]:
            if vc not in voice_selector:
                act_pass_choice_dict.pop(vc)

        voice = None
        if verb_vocab[verb].get("impers_pass_only") and mood == "impv" and "act" in voice_selector:
            voice = "act"

        ## only if verb is active (or semidep?)
        if verb_vocab[verb]["voice"] == "act" and not voice:

            if verb in ["sum","possum","volō","nōlō","mālō"]:
                voice = "act"

            # may need to move impersonal passive logic elsewhere to accommodate semideponents:

            elif verb_vocab[verb].get("impers_pass_only") or (mood == "inf" and tense == "fut"):
                if len(act_pass_choice_dict) == 2:
                    voice = random.choices(list(act_pass_choice_dict.keys()), list(act_pass_choice_dict.values()))[0]
                elif act_pass_choice_dict:
                    voice = list(act_pass_choice_dict.keys())[0]
                if voice == "pass" and mood != "inf":
                    person = 3
                    number = "sg"
            elif verb in irreg_selector and not act_pass_choice_dict:
                voice = "act"
            else:
                voice = random.choice(list(act_pass_choice_dict.keys()))

        elif verb_vocab[verb]["voice"] == "semidep" and tense in pres_sys:
            # extend this logic later to include 3rd person singular passive
            voice = "act"
            if verb == "fīō" and mood == "inf":
                if tense in ["pres","perf"]:
                    voice = "dep"
                else:
                    voice = "pass"
        elif not voice:
            voice = "dep"

        # Make sure there are no 2nd person plural future passive imperatives
        if voice in ["pass","dep"] and tense == "fut" and mood == "impv" and number == "pl" and person == 2:
            person = 3

        return {"verb": verb, "pers": person, "num": number, "tense": tense, "voice": voice, "mood": mood}

    ## ADAPTIVE LEARNING ALGORITHM ##

    def adap_gen_verb_id():
        avail_verbs = list(verb_vocab.keys())

        dfs = {}
        verb = person = number = tense = voice = mood = None
        recent_words = []
        roll_again = False

        verb_qs_answered = [item for item in questions_asked if item["pos"] == "verb" and "correct" in item]

        if questions_asked and len(verb_qs_answered) > 0:

            verb_df = (
                pd.json_normalize(verb_qs_answered)
                    .reindex(columns=["pos","word","answer","correct","id.pers","id.num","id.tense","id.voice","id.mood","id.conj","id.irreg"])
                    .replace({None: "-", pd.NA: "-", "nan": "-", "None": "-"})
                    .assign(**{"id.conj": lambda df: df["id.conj"]
                            .where(~df["id.irreg"].isin(["irreg"]), df["word"])})
                    .assign(conj_adap = lambda df: df["id.conj"]
                            .where((~df["id.tense"].isin(["perf","plupf","fut_pf"])) | (df["id.irreg"] == "irreg"), "perf_sys"))
                    .assign(conj_adap = lambda df: df["conj_adap"]
                            .where((~((df["id.tense"] == "fut") & (df["id.mood"] == "inf"))) | (df["id.irreg"] == "irreg"), "fut_inf"))
                    .assign(conj_adap = lambda df: df["conj_adap"]
                            .where(~(df["conj_adap"] == "-"), df["word"]))
                    .assign(**{"id.conj": lambda df: df["id.conj"].where(~((df["word"] == "fīō") & (df["conj_adap"] == "perf_sys")), "3")}) # since fio is categorized as 3rd conj for word-construction purposes
                       )
            # st.write(verb_df)
            dfs["verb_df"] = verb_df

            # If any questions have been answered, check if some are incorrect thar match the current selections of conjugation, tense, voice, mood.
            if len(verb_df) > 0:
                verb_df_filtered = (
                    verb_df.copy()
                        .query("word in @avail_verbs")
                        .query(f"`id.conj` in {[str(conj) for conj in internal_conjugation_selector]} or word in @irreg_selector") # filter to only currently-selected categories
                        .query("`id.mood` in @internal_mood_selector")
                        .query("`id.voice` in @internal_voice_selector")
                        .query("`id.tense` in @tense_selector")
                    )
                if not present_impv:
                    verb_df_filtered = verb_df_filtered.query("not (`id.tense` == 'pres' and `id.mood` == 'impv')")
                if not fut_impv:
                    verb_df_filtered = verb_df_filtered.query("not (`id.tense` == 'fut' and `id.mood` == 'impv')")
                # st.write(verb_df_filtered)

                if not verb_df_filtered.empty:
                    verb_df_wrong_indiv = (
                        verb_df_filtered.copy()
                            .drop(["word","pos"], axis=1)
                            .groupby([col for col in verb_df.columns if col not in ["pos", "answer", "correct", "word"]])
                            .agg(num_correct=("correct","sum"),total_q=("correct","count"))
                            .assign(pct_wrong = lambda df: (df["total_q"]-df["num_correct"])/df["total_q"])
                            .assign(weight = lambda df: ((df["total_q"]-df["num_correct"])/(df["num_correct"]+1))**0.5)
                            .query("pct_wrong > 0")
                        )
                    if not verb_df_wrong_indiv.empty:
                        verb_df_wrong_agg = (
                            verb_df_filtered.copy()
                                # filter to only categories that the user has gotten *wrong*
                                .query(f"`conj_adap` in {list(verb_df_wrong_indiv.index.get_level_values("conj_adap"))}")
                                .query(f"`id.mood` in {list(verb_df_wrong_indiv.index.get_level_values("id.mood"))}")
                                .query(f"`id.voice` in {list(verb_df_wrong_indiv.index.get_level_values("id.voice"))}")
                                .query(f"`id.tense` in {list(verb_df_wrong_indiv.index.get_level_values("id.tense"))}")
                                .groupby(["conj_adap","id.irreg","id.tense","id.voice","id.mood"])
                                .agg(num_correct=("correct","sum"),total_q=("correct","count"))
                                .assign(pct_wrong = lambda df: (df["total_q"]-df["num_correct"])/df["total_q"])
                                .assign(weight = lambda df: ((df["total_q"]-df["num_correct"])/(df["num_correct"]+1))**0.5)
                                .query("pct_wrong > 0")
                            )

                    if len(verb_df_wrong_indiv) > 0:
                        dfs["verb_df_wrong_indiv"] = verb_df_wrong_indiv
                        dfs["verb_df_wrong_agg"] = verb_df_wrong_agg

                        # st.write("incorrect answers:",verb_df_wrong_indiv)
                        # st.write("aggregated incorrect answers:",verb_df_wrong_agg)

                recent = min(len(avail_verbs)-1,3)
                recent_words = list(verb_df.tail(recent)["word"].values) if recent > 0 else []

        # If there are incorrectly-answered verbs that match the current selections, decide whether to repeat a question.
        if "verb_df_wrong_agg" in dfs and verb_df_wrong_agg["weight"].max() >= .58:
            repeat_chance = random.choices(["new","repeat"],[st.session_state["adap_learning_frequency"],1])[0]   # 1 in 3 chance of repeated question
            # repeat_chance = "repeat"
            if repeat_chance == "repeat" and len(verb_df) > 5:
                roll_again = False
                # st.write("repeat!")
                verb_conj_id = (verb_df_wrong_agg
                                .query("weight >= .58")["weight"]
                                .sample(n=1, weights=verb_df_wrong_agg
                                        .query("weight >= .58")["weight"])
                                .index[0])
                # st.write(verb_conj_id)

                conj, vb_irreg, tense, voice, mood = [item if item != "-" else None for item in verb_conj_id]


                if conj == "perf_sys":
                    # verb is in perfect system
                    # st.write("perfect system:",tense)
                    conj = None
                    # conj = random.choices(conjugation_selector + ([None] if any([vb in irreg_selector for vb in ["sum","possum"]]) and voice == "act" else []), [len(conjugation_selector) for item in conjugation_selector] + ([1] if any([vb in irreg_selector for vb in ["sum","possum"]]) and voice == "act" else []))[0]
                elif conj == "fut_inf":
                    # verb is a future infinitive
                    # st.write("future infinitive:",voice)
                    conj = None
                    # conj = random.choices(conjugation_selector + ([None] if any([vb in irreg_selector for vb in ["sum","possum"]]) and voice == "act" else []), [len(conjugation_selector) for item in conjugation_selector] + ([1] if any([vb in irreg_selector for vb in ["sum","possum"]]) and voice == "act" else []))[0]
                elif conj in complete_verb_vocab:
                    # verb is an irregular form
                    # st.write("irregular:", conj)
                    verb = conj
                    conj = complete_verb_vocab.get(verb)["conj"]
                    # st.write("conj:",conj)
                # elif conj is None:
                #     st.write("I think this shouldn't happen, it's sum or possum")
                else:
                    if isinstance(conj,str) and conj.isdigit():
                        conj = int(conj)

                # st.write(verb_df_wrong_indiv.xs(verb_conj_id,level=("conj_adap","id.irreg","id.tense","id.voice","id.mood")))

                # st.write(verb, conj, tense, voice, mood)

                if verb is None:
                    # since we need to pick a verb, reduce available vocab to fit the current restrictions of voice, tense, mood
                    verb_vocab_filtered = {k:v for k,v in verb_vocab.items()}
                    if voice == "pass":
                        verb_vocab_filtered = {k:v for k,v in verb_vocab_filtered.items() if v.get("no_pass") is not True and v["voice"] not in ["dep","semidep"]}
                        if tense in perf_sys or (tense == "fut" and mood == "inf"):
                            verb_vocab_filtered = {k:v for k,v in verb_vocab_filtered.items() if v.get("ppp") is not None}
                    elif voice == "dep":
                        verb_vocab_filtered = {k:v for k,v in verb_vocab_filtered.items() if v["voice"] == "dep"}
                        if tense in perf_sys:
                            verb_vocab_filtered = verb_vocab_filtered | {k:v for k,v in verb_vocab.items() if v["voice"] == "semidep"}
                    else:
                        verb_vocab_filtered = {k:v for k,v in verb_vocab_filtered.items() if v["voice"] != "dep"}
                        if tense in perf_sys:
                            verb_vocab_filtered = {k:v for k,v in verb_vocab_filtered.items() if v["voice"] != "semidep"}
                    if mood == "impv":
                        verb_vocab_filtered = {k:v for k,v in verb_vocab_filtered.items() if not v.get("no_impv") is True}
                        if tense == "fut":
                            if not fut_impv:
                                st.write("This situation shouldn't happen.")
                            else:
                                verb_vocab_filtered = {k:v for k,v in verb_vocab_filtered.items() if k not in irreg_selector or any(v.get("irreg",{}).get("forms",{}).get("fut",{}).get(vc,{}).get("impv") for vc in ["act","pass"])}
                                # st.write(verb_vocab_filtered.keys())
                    if tense == "fut" and mood == "inf" and voice == "act":
                        verb_vocab_filtered = {k:v for k,v in verb_vocab_filtered.items() if v.get("ppp") is not None or ("fap" in v and v["fap"] is not None)}
                        st.write(verb_vocab_filtered.keys())

                    if len(verb_vocab_filtered) == 0:
                        return

                    ## KEEP FILTERING FOR OTHER NON-EXISTENT SITUATIONS

                    # st.write(verb_vocab_filtered.keys())
                    avail_conj = list(set([verb["conj"] for verb in verb_vocab_filtered.values()] + ([3, "3io"] if "fīō" in verb_vocab_filtered else []) + (["-"] if "sum" in verb_vocab_filtered or "possum" in verb_vocab_filtered else [])))
                    # st.write(avail_conj)

                    # if there's a matching form in verb_df_wrong_indiv that has a weight > 1.7, slice from there for person and number (and conjugation as relevant).
                    # st.write("to match:", tense,voice,mood,conj,verb)
                    df_slice = verb_df_wrong_indiv.query(f"weight > 1.7 and `id.tense` == @tense and `id.voice` == @voice and `id.mood` == @mood and `id.conj` in {[str(conj)] if conj else [str(item) for item in avail_conj+list(verb_vocab_filtered.keys())]}")
                    # st.write("possible verbs:",df_slice)
                    if not df_slice.empty:
                        vb_info_weights = df_slice.xs((tense,voice,mood),level=("id.tense","id.voice","id.mood"))["weight"]
                        vb_select = df_slice.reset_index(level=["id.tense","id.voice","id.mood"],drop=True).sample(n=1,weights=vb_info_weights).index[0]
                        person,number = vb_select[:2]
                        if conj is None:
                            conj = vb_select[2]
                        if isinstance(conj, str) and conj.isdigit():
                            conj = int(conj)
                        # try:
                        #     conj = ast.literal_eval(conj)
                        # except:
                        #     conj = conj
                        if conj == "-":
                            verb = random.choice(["sum","possum"])
                            conj = None
                            # st.write(verb)
                        person = None if person == "-" else int(person)
                        number = None if number == "-" else number

                    # st.write(conj, person, number)

                # Since we need to pick a conjugation and verb, pick a conjugation that exists in the current reduced verb set
                pick_sum_possum = False
                if conj is None and verb is None:
                    avail_conj = list(set([verb["conj"] for verb in verb_vocab_filtered.values()]))
                    conj = random.choice(avail_conj)
                    if conj is None:
                        pick_sum_possum = True

                if (verb is None and conj is not None) or pick_sum_possum is True:
                    # since we need to pick a verb, reduce available vocab to the selected conjugation
                    verb_vocab_filtered = {k:v for k,v in verb_vocab_filtered.items() if v["conj"] == conj}
                    if "fīō" in irreg_selector and conj in [3,"3io"]:
                        # since fio is classed under 3rd conj for forms but is really 3rd io and is listed as 3rd io, make sure it's there for both conjugations (regular forms only).
                        if (tense in ["fut", "impf"] and voice == "act" and not (tense == "fut" and mood == "inf")) or (tense in perf_sys and voice == "dep"):
                            verb_vocab_filtered["fīō"] = complete_verb_vocab["fīō"]
                    if number:
                        # if person/number is already chosen, make sure that
                        if voice == "pass":
                            if number != "sg" or person != 3:
                                verb_vocab_filtered = {k:v for k,v in verb_vocab_filtered.items() if v.get("impers_pass_only") is not True}
                    else:
                        if voice == "pass" and mood == "impv":
                            verb_vocab_filtered = {k:v for k,v in verb_vocab_filtered.items() if v.get("impers_pass_only") is not True}
                    if len(verb_vocab_filtered) == 0:
                        return
                    if not set(list(verb_vocab_filtered.keys())) <= set(recent_words):
                        roll_again = True
                    i = 0
                    while (roll_again is True or i < 1) and verb is None:
                        verb = random.choice(list(verb_vocab_filtered.keys()))
                        i += 1
                        if verb not in recent_words:
                            roll_again = False
                        elif roll_again is True:
                            verb = None
                # st.write(verb, conj)
                # need to assign person and number if not already assigned
                if mood != "inf" and not person:
                    # assign person and number within constraints
                    if voice == "pass" and complete_verb_vocab[verb].get("impers_pass_only") is True:
                        number = "sg"
                        person = 3
                    else:
                        if mood == "impv":
                            if tense == "fut":
                                if voice == "act":
                                    person = random.choice([2,3])
                                else:
                                    person = 3
                            else:
                                person = 2
                        else:
                            person = random.choice([1,2,3])
                        number = random.choice(["sg","pl"])


                # st.write("repeat:",verb, person, number, tense, voice, mood)
        #     else:
        #         st.write("There's stuff to choose from, but get new verb")
        # else:
        #     st.write("Nothing to choose from, get new verb")

        if not verb:
            if len(avail_verbs) > 5 and conjugation_selector and questions_asked and verb_qs_answered:
#                st.write("Generate a new verb question but not the most recent word")
                last_verb = verb_qs_answered[-1]["word"]
                roll_again = True
                i = 0
                while roll_again is True:
                    verb_id = gen_verb_id()
                    if verb_id:
                        verb = verb_id["verb"]
                        if verb != last_verb:
                            roll_again = False
                    if i > 5:
                        break
                    i += 1
            if not verb:
                # st.write("Generate a new verb question; it might overlap with recent words")
                verb_id = gen_verb_id()

            if not verb_id:
                # st.write("nothing chosen")
                return
            else:
                verb = verb_id["verb"]
                person = verb_id["pers"]
                number = verb_id["num"]
                tense = verb_id["tense"]
                voice = verb_id["voice"]
                mood = verb_id["mood"]

                # st.write("new:",verb_id)
        return {"verb": verb, "pers": person, "num": number, "tense": tense, "voice": voice, "mood": mood}

    # adap_gen_verb_id()

    def build_verb(verb_id=None):
        # logic for if verb is regular

        if verb_id:
            pass
        else:
            i = 0
            while verb_id is None and i < 5:
                verb_id = adap_gen_verb_id()
                i += 1

        if verb_id is None:
            st.session_state.question_generation_error_message = ":warning: A kiválasztott beállításokkal nem sikerült kérdést generálni. Módosíts néhány beállítást, majd kattints újra az 'Új kérdés' gombra."
            return

        verb = verb_id["verb"]
        person = verb_id["pers"]
        number = verb_id["num"]
        tense = verb_id["tense"]
        voice = verb_id["voice"]
        mood = verb_id["mood"]

        conj = verb_vocab[verb]["conj"]


        # st.write(verb_id)

        verb_principal_parts = {1: verb,
                                2: None,
                                3: None,
                                4: None}

        if verb_vocab[verb]["voice"] == "act":
            verb_principal_parts[3] = verb_vocab[verb]["perf"] + "ī"
            if verb_vocab[verb].get("ppp"):
                verb_principal_parts[4] = verb_vocab[verb]["ppp"] + "um"
            elif verb_vocab[verb].get("fap"):
                verb_principal_parts[4] = "[" + verb_vocab[verb]["fap"] + "us]"
        else:
            verb_principal_parts[3] = verb_vocab[verb]["ppp"] + "us sum"
            verb_principal_parts.pop(4)
        pres_inf = ""
        verb_form = ""
        irreg_form = False

        if verb_vocab[verb].get("irreg"):
            # If there's an irregular present active/deponent infinitive, grab it now.
            if verb_vocab[verb]["irreg"].get("forms", {}).get("pres"):
                for temp_voice in ["act","dep"]:
                    if verb_vocab[verb]["irreg"]["forms"]["pres"].get(temp_voice,{}).get("inf"):
                        pres_inf = verb_vocab[verb]["irreg"]["forms"]["pres"][temp_voice]["inf"]

            # If the verb has irregular forms for the specified tense, voice, and mood, grab that set and assign to `verb_form`.
            if verb_vocab[verb]["irreg"].get("forms",{}).get(tense):
                if verb_vocab[verb]["irreg"]["forms"][tense].get(voice):
                    verb_form = verb_vocab[verb]["irreg"]["forms"][tense][voice].get(mood)
            # If the previous step succeeded, then either:
            # the verb_form is now a list or string (in which case that's the correct form and we just need to finish filling in principal parts),
            # or it's a dictionary and we have to get the appropriate number and person.

            if verb_form:
                if not (isinstance(verb_form, str) or isinstance(verb_form, list)):
                    if verb_form.get(number):
                        verb_form = verb_form[number][person]

            if verb_form:
                irreg_form = True

        # If the pres. inf. isn't irregular, form it for the principal parts.
        pres_act_inf = ""
        if verb == "fīō":
            pres_act_inf = "fiere"

        if not pres_inf:
            pres_stem = verb_vocab[verb].get("pres")
            thematic_vowel = verb_vowels["pres"]["inf"].get(conj)
            pres_act_inf = pres_stem + thematic_vowel + "re"
            if verb_vocab[verb]["voice"] in ["act","semidep"]:
                pres_inf = pres_act_inf
            if verb_vocab[verb]["voice"] == "dep":
                if conj in [3,"3io"]:
                    pres_inf = pres_stem + "ī"
                else:
                    pres_inf = pres_stem + thematic_vowel + "rī"

        # If the pres. act. inf. *is* irregular, assign it to `pres_act_inf` for use in impf. subj.
        if not pres_act_inf:    # this may still not work for fio (needs fiere to exist for imperfect subj), so double-check it once fio is added
            pres_act_inf = pres_inf

        # Add pres. infinitive to principal parts
        verb_principal_parts[2] = pres_inf

        # If the requisite verb form isn't irregular, build it.
        if not verb_form or isinstance(verb_form, dict):
            if person == 1 and number == "sg" and tense == "pres" and mood == "ind" and voice in ["act", "dep"]:
                verb_form = verb
                # st.write("Used lemma form, mission accomplished.")
            else:
                if tense in pres_sys:
                    # deal with future act/pass infinitives
                    if tense == "fut" and mood == "inf":
                        if voice in ["act", "dep"]:
                            if verb_vocab[verb].get("fap"):
                                verb_form = verb_vocab[verb]["fap"] + "um esse"
                            else:
                                verb_form = verb_vocab[verb]["ppp"] + "ūrum esse"
                        elif verb == "fīō":
                            verb_form = verb_vocab[verb]["ppp"] + "um īrī"
                            irreg_form = True
                        else:
                            verb_form = verb_vocab[verb]["ppp"] + "um īrī"
                    else:
                        verb_stem = verb_vocab[verb].get("irreg",{}).get("stems",{}).get("pres", {}).get("subj")
                        irreg_form = True
                        if not verb_stem or not (mood == "subj" and tense == "pres"):
                            verb_stem = verb_vocab[verb].get("pres")
                            irreg_form = False

                        if mood == "inf":
                            if tense == "pres":
                                if voice in ["act","dep"]:
                                    verb_form = verb_principal_parts[2]
                                else:
                                    if conj in [3,"3io"]:
                                        verb_form = verb_stem + "ī"
                                    else:
                                        verb_form = verb_stem + thematic_vowel + "rī"

                        ## OTHER PRESENT SYSTEM MOODS AND TENSES
                        else:
                            verb_ending = verb_endings["pres"].get("act" if voice == "act" else "pass").get(number).get(person)
                            if tense == "pres" or (tense == "fut" and mood == "impv"): # all present forms and future imperatives
                                if mood != "impv" or tense == "fut":
                                    vowel = verb_vowels["pres"][mood if mood != "impv" else "ind"][conj]
                                    if mood == "ind" or tense == "fut":
                                        if person == 1 and number == "sg" and voice in ["pass", "dep"]:
                                            if conj in [1, 3]:
                                                vowel = "o"
                                            else:
                                                vowel = remove_macrons(vowel) + "o"
                                        elif person == 3 and number == "pl":
                                            if conj in ["3io", 4]:
                                                vowel += "u"
                                            elif conj == 3:
                                                vowel = "u"
                                        elif person == 2 and number == "sg" and voice in ["pass", "dep"] and conj in [3, "3io"] and tense != "fut":
                                            vowel = "e"

                                    if tense == "fut": # future imperatives
                                        verb_ending = verb_endings["fut"]["act" if voice == "act" else "pass"]["impv"][number].get(person)

                                    if verb_ending in ["r", "m", "t"] or verb_ending[:2] == "nt": # shorten vowels as needed
                                        vowel = remove_macrons(vowel)

                                    if isinstance(verb_ending, list):
                                        verb_form = [verb_stem + vowel + ending for ending in verb_ending]
                                    else:
                                        verb_form = verb_stem + vowel + verb_ending
                                else:   # present imperatives
                                    if number == "sg":
                                        if voice == "act":
                                            verb_form = pres_act_inf[:-2]
                                        else:
                                            verb_form = pres_act_inf
                                    if number == "pl":
                                        if voice == "act":
                                            if conj not in [3, "3io"]:
                                                verb_form = pres_act_inf[:-2] + "te"
                                            else:
                                                verb_form = pres_act_inf[:-3] + "ite"
                                        else:
                                            verb_form = pres_stem + verb_vowels["pres"]["ind"][conj] + "minī"
                            elif tense == "impf":
                                if mood == "ind":
                                    vowel = verb_vowels["impf_fut"][conj]
                                    if verb == "eō":
                                        vowel = ""
                                    verb_ending = verb_endings["impf"]["act" if voice == "act" else "pass"]["ind"][number][person]
                                    if isinstance(verb_ending, list):
                                        verb_form = [verb_stem + vowel + ending for ending in verb_ending]
                                    else:
                                        verb_form = verb_stem + vowel + verb_ending
                                else:   # imperfect subjunctives
                                    if person == 2 or (person == 1 and number == "pl") or (voice in ["pass","dep"] and person == 3 and number == "sg"):
                                        verb_stem = pres_act_inf[:-1] + "ē"
                                    else:
                                        verb_stem = pres_act_inf
                                    #verb_ending = verb_endings["pres"].get("act" if voice == "act" else "pass").get(number).get(person)
                                    if isinstance(verb_ending, list):
                                        verb_form = [verb_stem + ending for ending in verb_ending]
                                    else:
                                        verb_form = verb_stem + verb_ending

                            else:   # futures
                                if mood == "ind":
                                    vowel = verb_vowels["impf_fut"][conj]
                                    if conj in [1,2]:
                                        verb_ending = verb_endings["fut"]["act" if voice == "act" else "pass"]["ind"][number][person]
                                    else:   # 3rd, 3io and 4th conjugations
                                        verb_ending = verb_endings["pres"]["act" if voice == "act" else "pass"][number][person]
                                        if person == 1 and number == "sg":
                                            vowel = vowel[:-1] + "a"
                                        if verb_ending in ["r", "m", "t"] or verb_ending[:2] == "nt":
                                            vowel = remove_macrons(vowel)
                                    if isinstance(verb_ending, list):
                                        verb_form = [verb_stem + vowel + ending for ending in verb_ending]
                                    else:
                                        verb_form = verb_stem + vowel + verb_ending

                # deal with perfect system
                else:
                    # active voice
                    if voice == "act":
                        alt_form = ""
                        verb_stem = verb_vocab[verb].get("perf")
                        perf_act_inf = verb_form = verb_stem + "isse"
                        if mood != "inf":
                        #     verb_form = perf_act_inf
                        # else:
                            if mood == "subj" and tense == "plupf":
                                verb_form = perf_act_inf
                                if person == 2 or (person == 1 and number == "pl"):
                                    verb_form = verb_form[:-1] + "ē"
                                verb_form = verb_form + verb_endings["pres"]["act"].get(number).get(person)
                            # NEED TO ADD ENDINGS FOR OTHER ACTIVE TENSES
                            else:
                                verb_ending = verb_endings.get(tense,{}).get(voice,{}).get(mood, {}).get(number, {}).get(person)
                                if isinstance(verb_ending, list):
                                    verb_form = [verb_stem + ending for ending in verb_ending]
                                else:
                                    verb_form = verb_stem + verb_ending

                        # construct alternative 4th conj. perfect forms
                        if verb_stem[-2:] == "īv":
                            # if verb_stem[-2] in ["ā","ē","ō"]:
                            #     alt_stem = verb_stem[:-1]
                            # elif verb_stem[2] == "ī":
                            alt_stem = verb_stem[:-2] + "i"
                            if mood == "inf" or (mood == "subj" and tense == "plupf"):
                                alt_form = alt_stem + "isse"
                            if mood != "inf":
                                if alt_form:
                                    if person == 2 or (person == 1 and number == "pl"):
                                        alt_form = alt_form[:-1] + "ē"
                                    alt_form = alt_form + verb_endings["pres"]["act"].get(number).get(person)
                                else:
                                    verb_ending = verb_endings.get(tense,{}).get(voice,{}).get(mood, {}).get(number, {}).get(person)
                                    if isinstance(verb_ending, list):
                                        alt_form = [alt_stem + ending for ending in verb_ending]
                                    else:
                                        alt_form = alt_stem + verb_ending
                            if isinstance(alt_form, list):
                                for form in list(alt_form):
                                    if "iis" in form:
                                        alt_form.append(form.replace("iis", "īs"))
                            else:
                                if "iis" in alt_form:
                                    alt_form = [alt_form, alt_form.replace("iis", "īs")]

                        if alt_form:
                            if isinstance(verb_form, list):
                                if isinstance(alt_form, list):
                                    verb_form = verb_form + alt_form
                                else:
                                    verb_form.append(alt_form)
                            else:
                                if isinstance(alt_form, list):
                                    verb_form = [verb_form] + alt_form
                                else:
                                    verb_form = [verb_form, alt_form]

                    # passive or deponent voice
                    else:
                        verb_stem = verb_vocab[verb].get("ppp")

                        if mood == "inf":
                            verb_form = verb_stem + "um esse"

                        else:
                            if number == "sg":
                                ppp = [verb_stem + ending for ending in ["us", "a", "um"]]
                                if verb_vocab[verb].get("impers_pass_only") and voice == "pass":
                                    ppp = verb_stem + "um"
                            else:
                                ppp = [verb_stem + ending for ending in ["ī", "ae", "a"]]

                            tense_match = {"perf": "pres",
                                "plupf": "impf",
                                "fut_pf": "fut"}

                            to_be_form = ""

                            # make to-be impf subj for plupf subj

                            if mood == "subj" and tense == "plupf":
                                to_be_form = complete_verb_vocab["sum"]["irreg"]["forms"]["pres"]["act"]["inf"]
                                if person == 2 or (person == 1 and number == "pl"):
                                    to_be_form = to_be_form[:-1] + "ē"
                                to_be_form = to_be_form + verb_endings["pres"]["act"].get(number).get(person)

                            else:
                                for key, val in tense_match.items():
                                    if tense == key:
                                        to_be_form = complete_verb_vocab["sum"]["irreg"]["forms"][val]["act"][mood][number][person]

                            verb_form = [" ".join([ptc, to_be_form]) for ptc in ppp] if isinstance(ppp, list) else " ".join([ppp, to_be_form])

                # try:
                #     if isinstance(verb_stem, str):
                #         st.write("verb stem:", verb_stem)
                #     elif verb_stem is None:
                #         st.write("This verb may be defective, and/or may need to fix something in question generation logic.")
                # except:
                #     pass
                # # logic for if verb is irregular
                # else:
                #     st.write("This verb is irregular, figure out the best approach.")

        # st.write("Principal parts:", ", ".join([str(val) for val in list(verb_principal_parts.values())]))
        # st.write("Verb form:", verb_form)

        if verb == "sum" and tense == "impf" and mood == "subj":
            if number == "sg":
                verb_form = [verb_form] + ["forem" if person == 1 else "forēs" if person == 2 else "foret"]
            else:
                verb_form = [verb_form] + ["forēmus" if person == 1 else "forētis" if person == 2 else "forent"]
        if verb == "sum" and tense == "fut" and mood == "inf":
            verb_form = [verb_form] + ["fore"]

        curr_question = {
                "pos": "verb",
                "word": verb,
                "id": {k:str(v) if v is not None else v for k,v in verb_id.items() if k != "verb"} | {"conj": str(conj)} | {"irreg": "irreg" if irreg_form is True else None}
            }
        if verb in ["volō","nōlō","mālō"] and irreg_form is True:
            curr_question["id"]["conj"] = "-"
        elif verb == "fīō":
            curr_question["id"]["conj"] = "3io"

#        st.write(st.session_state.append_answer)
        if st.session_state.append_answer is True:
            questions_asked.append(
                curr_question
            )
#            st.write(curr_question)
            st.session_state.append_answer = False
#            st.write("Now it's", st.session_state.append_answer)

        return [verb_form, verb_id, verb_principal_parts]

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
        finally:
            st.session_state.append_answer = saved_append_answer
        return list(analyses.values())

    st.session_state.gen_func = build_verb

    # CREATE QUIZ

    # questions_asked = []

    if st.session_state.current_question:
        verb_form, verb_id, verb_pp = st.session_state.current_question
        verb, person, number, tense, voice, mood = verb_id.values()
        verb_pp = [val for val in verb_pp.values() if val]
        if verb == "eō":
            verb_pp[2] += "/iī"

        correct_answer = verb_form

        st.session_state["correct_answer"] = correct_answer

        # questions_asked.append(verb_id)

        tense_labels = {
            "pres": "praes. impf.",
            "impf": "praet. impf.",
            "fut": "fut. impf.",
            "perf": "praes. perf.",
            "plupf": "praet. perf.",
            "fut_pf": "fut. perf.",
        }
        mood_label = (
            "ind." if mood == "ind"
            else "coni." if mood == "subj"
            else "2. imperativus" if mood == "impv" and tense == "fut"
            else "imperativus"
        )
        voice_label = "" if voice in ["dep", "semidep"] else {
            "act": "act.",
            "pass": "pass.",
        }.get(voice, str(voice))
        number_label = {"sg": "sg.", "pl": "pl."}.get(number, "")
        form_label = " ".join(
            part for part in [
                None if mood == "impv" else tense_labels[tense],
                mood_label,
                voice_label,
                number_label,
                str(person),
            ]
            if part and part != "None"
        )

        verb_label = verb_dictionary_entry(verb) if show_principal_parts else verb
        recognition_correct_analyses = []
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
            article = hungarian_article(verb_label)
            question_html = (
                f'Add meg {article} <strong><em>{html.escape(verb_label)}</em></strong> ige '
                f'<strong>{html.escape(form_label)}</strong> alakját!'
            )

        stems = verb_stem_display(verb) if show_stems else []
        prompt_height = 114 if stems else 82
        prompt_space = st.container(height=prompt_height, border=False)
        with prompt_space:
            st.markdown(
                f'<div style="margin-top:0.75rem;font-size:1.75rem;line-height:1.25;">{question_html}</div>',
                unsafe_allow_html=True,
            )
            if stems:
                stems_html = ", ".join(f"<em>{html.escape(stem)}-</em>" for stem in stems)
                st.markdown(
                    f'<div style="font-size:1.05rem;line-height:1.35;margin-top:0.35rem;">A tövek: {stems_html}.</div>',
                    unsafe_allow_html=True,
                )

        if not st.session_state.question_generation_error_message:
            with st.form(key="verb_answer_form", clear_on_submit=(exercise_type != "recognize")):
                current_answer = st.text_input("Válaszod:", key="answer_input")

                def submit_verb_answer():
                    if exercise_type == "recognize":
                        user_answer = st.session_state.get("answer_input", "")
                        if not user_answer:
                            st.session_state.button_disable = False
                            st.session_state.answer_display_message = (
                                "A válaszmező üres. Írj be egy alakot, majd kattints a **Válasz ellenőrzése** gombra, "
                                "vagy az **Új kérdés** gombbal ugord át a kérdést."
                            )
                            return

                        parsed_analyses = parse_verb_morphology_analyses(
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
                            if parsed_analyses.get("error") in ["incomplete tense", "missing required parameter"]:
                                st.session_state.answer_display_message = feedback_box(
                                    "<strong>Hiányos válasz - pótold a hiányzó paramétereket!</strong>",
                                    "incorrect",
                                )
                            else:
                                st.session_state.answer_display_message = feedback_box(
                                    "<strong>Ellenőrizd a válasz paramétereit, majd próbáld újra. A válaszod nincs még értékelve.</strong>",
                                    "incorrect",
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

                        if evaluation == "incorrect":
                            incorrect_feedback_html = format_incorrect_verb_recognition_table_html(
                                parsed_analyses["analyses"],
                                recognition_correct_analyses,
                                lexical_voice,
                            )
                        else:
                            correct_text = ", ".join(
                                html.escape(format_correct_verb_recognition_analysis(analysis))
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
                            st.session_state.answer_display_message = feedback_box(
                                incorrect_feedback_html,
                                "incorrect",
                            )
                        # Recognition forms deliberately do not clear on submit so that
                        # parsing errors remain editable. Once parsing succeeds and the
                        # answer has actually been evaluated, clear the widget manually.
                        st.session_state.answer_input = ""
                        return

                    original_correct_answer = st.session_state.correct_answer
                    st.session_state.correct_answer = participial_answer_variants(original_correct_answer)
                    submit_and_check_answer()
                    st.session_state.correct_answer = original_correct_answer
                    if not st.session_state.get("answer_input"):
                        st.session_state.answer_display_message = (
                            "A válaszmező üres. Írj be egy alakot, majd kattints a **Válasz ellenőrzése** gombra, "
                            "vagy az **Új kérdés** gombbal ugord át a kérdést."
                        )
                    elif st.session_state.answer_checked:
                        if "Good job!" in st.session_state.result_message:
                            st.session_state.answer_display_message = feedback_box(
                                "<strong>Helyes válasz!</strong>", "correct"
                            )
                        else:
                            answers = st.session_state.correct_answer
                            compact_answer = compact_participial_answer(answers)
                            if compact_answer:
                                correct_html = heavy(compact_answer, italic=True)
                                label = "A helyes válasz"
                            else:
                                if not isinstance(answers, list):
                                    answers = [answers]
                                correct_html = " <span style='font-weight:700;'>vagy</span> ".join(
                                    heavy(answer, italic=True) for answer in answers
                                )
                                label = "A helyes válasz" if len(answers) == 1 else "A helyes válaszok"
                            st.session_state.answer_display_message = feedback_box(
                                f"<strong>Helytelen válasz. {label}:</strong> {correct_html}.",
                                "incorrect",
                            )

                st.form_submit_button(
                    "Válasz ellenőrzése",
                    key="form_submission_button",
                    on_click=submit_verb_answer,
                    disabled=st.session_state.button_disable,
                    width="stretch",
                )

            feedback_space = st.container(height=90, border=False)
            with feedback_space:
                if st.session_state.answer_display_message.lstrip().startswith("<div"):
                    st.markdown(st.session_state.answer_display_message, unsafe_allow_html=True)
                else:
                    st.markdown(st.session_state.answer_display_message)


    ## GENERATE NEW QUESTIONS AND CHECK ANSWERS ##

    control_row = st.container(height=110, border=False)
    with control_row:
        new_question_col, results_col, score_col = st.columns([1, 1, 1], gap="medium", vertical_alignment="top")

        new_q_button_text = "Új kérdés" if st.session_state.question_list else "Kattints ide az első kérdéshez!"
        new_q_button_type = "secondary" if st.session_state.question_list else "primary"
        with new_question_col:
            st.button(new_q_button_text, on_click=new_question, args=(build_verb,), key="question_button", width="stretch", type=new_q_button_type)

        with results_col:
            if st.session_state.current_question and st.session_state.answer_checked and "Incorrect" in st.session_state.result_message:
                starting_form = dict(st.session_state.current_question[1])
                next_form = dict(starting_form)
                help_text = "Ehhez az alakhoz nem jeleníthető meg ragozási táblázat." if (starting_form["voice"] == "pass" and complete_verb_vocab[starting_form["verb"]].get("impers_pass_only") is True) else None
                chart_popover = st.popover("Ragozási táblázat", type="primary", help=help_text, width="stretch")
                with chart_popover:
                    if not (starting_form["voice"] == "pass" and complete_verb_vocab[starting_form["verb"]].get("impers_pass_only") is True):
                        st.caption("Ez a funkció még fejlesztés alatt áll.")
                        conj_table = {}
                        table_index = []
                        for num in ["sg", "pl"]:
                            conj_table[num] = []
                            for pers in [1, 2, 3]:
                                if pers not in table_index:
                                    table_index.append(pers)
                                next_form["num"] = num
                                next_form["pers"] = pers
                                try:
                                    form = build_verb(next_form)[0]
                                    if isinstance(form, list):
                                        form = "/".join(form)
                                    if next_form == starting_form:
                                        form = f":green-background[{form}]"
                                except Exception:
                                    form = None
                                if starting_form["mood"] == "impv":
                                    if starting_form["tense"] == "pres" and pers != 2:
                                        form = None
                                    if starting_form["voice"] in ["pass", "dep"] and starting_form["tense"] == "fut" and num == "pl" and pers != 3:
                                        form = None
                                conj_table[num].append(form if isinstance(form, str) else "--")
                        conjugation_table = pd.DataFrame(conj_table, index=table_index)
                        st.table(conjugation_table)

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

# st.write(questions_asked)
