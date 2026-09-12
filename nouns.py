import streamlit as st
import random
import time
import pandas as pd
import ast
import unicodedata
import html
from utils import radio_change, reset, new_question, submit_and_check_answer, clear_page, send_setting, save_defaults, clear_defaults, auto_advance_delay, remove_macrons, tokenize_morphology_answer
from exercise_presets import (bool_setting, choice_setting, list_setting, resolve_exercise_settings,
                              initialize_widget_state, widget_key, url_preset_active, exercise_link_popover)
from vocab import import_nouns


st.set_page_config("BevLat – Főnevek", layout="centered")

questions_asked = st.session_state.question_list
noun_vocab = import_nouns()
st.session_state.nouns_enforce_macrons = st.session_state.enforce_macrons["nouns_enforce_macrons"]

page_id = "nouns"
clear_page(page_id)
defaults = st.session_state.default_settings.get(f"{page_id}.py", {})

st.markdown("# Főnevek")


declension_dict = {
    "1st": 1,
    "2nd": ["2_us", "2_er", "2_neut"],
    "3rd_cons": [3, "3_neut"],
    "3rd_i": ["3_istem", "3_istem_neut"],
    "4th": [4, "4_neut"],
    "5th": ["5_vowel", "5_consonant"],
}

DECLENSION_LABELS = {
    "1st": "1.",
    "2nd": "2.",
    "3rd_cons": "3. (msh)",
    "3rd_i": "3. (i)",
    "4th": "4.",
    "5th": "5.",
}

DECLENSION_NUMBER_LABELS = {
    "1st": "1.",
    "2nd": "2.",
    "3rd_cons": "3.",
    "3rd_i": "3.",
    "4th": "4.",
    "5th": "5.",
}

DEFAULT_DECLENSIONS = list(declension_dict.keys())
DECLENSION_URL_CHOICES = {
    "1st": "1st",
    "2nd": "2nd",
    "3rd_cons": "3rd_cons",
    "3rd_i": "3rd_i",
    "3rd": "3rd",
    "4th": "4th",
    "5th": "5th",
}


def normalize_declension_selection(values):
    normalized = []
    for value in values:
        expanded = ["3rd_cons", "3rd_i"] if value == "3rd" else [value]
        for item in expanded:
            if item in declension_dict and item not in normalized:
                normalized.append(item)
    return normalized


LATIN_VOWELS = set("aeiouy")
LATIN_DIPHTHONGS = {"ae", "au", "oe", "ei", "eu", "ui"}


def hungarian_article(word):
    normalized = "".join(
        char for char in unicodedata.normalize("NFD", word.lower())
        if unicodedata.category(char) != "Mn"
    )
    if not normalized or normalized[0] not in LATIN_VOWELS:
        return "a"
    if len(normalized) > 1 and normalized[1] in LATIN_VOWELS:
        return "az" if normalized[:2] in LATIN_DIPHTHONGS else "a"
    return "az"


def feedback_box(content, state):
    colors = {
        "correct": ("#e3f3e7", "#7aa682"),
        "incorrect": ("#f7dddd", "#c48282"),
        "partial": ("#fff4d6", "#e2c66d"),
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


master_irregular_nouns_list = [
    noun for noun, data in noun_vocab.items() if data.get("irreg", {}).get("irreg")
]
exercise_schema = {
    "exercise_type": choice_setting("inflect", ["inflect", "recognize"]),
    "print_macrons": bool_setting(False),
    "indicate_multiple_answers": bool_setting(False),
    "award_partial_credit": bool_setting(False),
    "show_dictionary_entry": bool_setting(True),
    "show_declension": bool_setting(False),
    "show_third_group": bool_setting(False),
    "show_stem": bool_setting(False),
    "declension": list_setting(DEFAULT_DECLENSIONS, DECLENSION_URL_CHOICES),
    "irregs_include": list_setting(["deus"] if "deus" in master_irregular_nouns_list else [], master_irregular_nouns_list),
    "irregs_only": choice_setting("No", ["No", "Yes"]),
}
exercise_settings = resolve_exercise_settings(page_id, exercise_schema, defaults)
exercise_settings["declension"] = normalize_declension_selection(exercise_settings["declension"])
declension_widget_key = widget_key(page_id, "declension")
if declension_widget_key in st.session_state:
    st.session_state[declension_widget_key] = normalize_declension_selection(
        st.session_state[declension_widget_key]
    )
initialize_widget_state(page_id, exercise_settings)
preset_active = url_preset_active(page_id)


option_expander = st.expander("Beállítások", expanded=True)

with option_expander:
    col_declension, col_options = st.columns([3, 2])

with col_declension:
    exercise_type_label_col, exercise_type_radio_col = st.columns(
        [1, 4], vertical_alignment="center"
    )
    with exercise_type_label_col:
        st.markdown("Feladattípus:")
    with exercise_type_radio_col:
        exercise_type = st.radio(
            "Feladattípus:",
            options=["inflect", "recognize"],
            format_func=lambda value: {
                "inflect": "Ragozás",
                "recognize": "Alakfelismerés",
            }[value],
            horizontal=True,
            label_visibility="collapsed",
            key=widget_key(page_id, "exercise_type"),
            on_change=radio_change,
        )

with col_options:
    def switch_noun_macrons():
        st.session_state.enforce_macrons["nouns_enforce_macrons"] = st.session_state["nouns_enforce_macrons"]
        return

    st.markdown("Opciók:", help="Ezeket a beállításokat gyakorlás közben is bármikor módosíthatod.")
    if exercise_type == "inflect":
        st.checkbox(
            "Hosszú magánhangzók ellenőrzése?",
            help="Ha be van jelölve, a hosszú magánhangzók hibás jelölése hibás válasznak számít. Ha nincs bejelölve, a hosszúságjelek használhatók, de a program nem értékeli őket.",
            key="nouns_enforce_macrons",
            on_change=send_setting,
            args=(switch_noun_macrons,),
            kwargs={"streamlit_page": "nouns.py", "setting_name": "nouns_enforce_macrons"},
        )
        macrons = st.session_state.nouns_enforce_macrons

        if macrons:
            st.markdown("A hosszú magánhangzók innen másolhatók:")
            st.code("āēīōū", language=None)
    else:
        print_macrons = st.checkbox(
            "Hosszú magánhangzók jelölése?",
            help="Ha be van kapcsolva, a kérdésben szereplő alakok jelölik a magánhangzók hosszúságát, és a választ ennek figyelembevételével kell megadni. Ha ki van kapcsolva, ugyanaz az írott alak rövid és hosszú magánhangzóval képzett alakokat is jelölhet, ezért több helyes elemzés is lehetséges.",
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

    show_dictionary_entry = st.checkbox(
        "Szótári alak megjelenítése?",
        help="A teljes szótári alak megjelenítése; ennek genitivusából a tő is meghatározható.",
        key=widget_key(page_id, "show_dictionary_entry"),
    )
    show_declension = st.checkbox(
        "Declinatio megjelenítése?",
        help="A főnév declinatiójának megjelenítése.",
        key=widget_key(page_id, "show_declension"),
    )
    show_third_group = st.checkbox(
        "3. decl. csoport megjelenítése?",
        help="A 3. declinatiós főneveknél megjeleníti, hogy a szó msh.-tövű, gyenge i-tövű vagy erős i-tövű.",
        key=widget_key(page_id, "show_third_group"),
        disabled=not show_declension,
    )
    show_stem = st.checkbox(
        "Tő megjelenítése?",
        help="A főnév tövének megjelenítése.",
        key=widget_key(page_id, "show_stem"),
    )

with col_declension:
    declension = st.multiselect(
        "Válaszd ki, mely declinatiókat szeretnéd gyakorolni (alapértelmezés szerint mindegyik ki van választva):",
        options=DEFAULT_DECLENSIONS,
        format_func=lambda x: DECLENSION_LABELS[x],
        help="Ha a kiválasztott declinatiók között rendhagyó főnevek is vannak, külön megadhatod, melyeket szeretnéd bevonni a gyakorlásba.",
        key=widget_key(page_id, "declension"),
    )


active_vocab = {}
for noun_key, noun_val in noun_vocab.items():
    n_decl = noun_val["decl"]
    for decl_sel in declension:
        if isinstance(declension_dict[decl_sel], list) and n_decl in declension_dict[decl_sel]:
            active_vocab = active_vocab | {noun_key: noun_val}
        elif n_decl == declension_dict[decl_sel]:
            active_vocab = active_vocab | {noun_key: noun_val}

avail_decl = []
for item in {k: v for k, v in declension_dict.items() if k in declension}.values():
    if isinstance(item, list):
        avail_decl += item
    else:
        avail_decl.append(item)

irreg_nouns = [
    noun for noun in active_vocab.keys()
    if noun_vocab[noun].get("irreg", {}).get("irreg") and noun_vocab[noun]["decl"] in avail_decl
]

irregs_include = []
irregs_only = "No"

with col_declension:
    if len(irreg_nouns) > 0:
        irregs_key = widget_key(page_id, "irregs_include")
        st.session_state[irregs_key] = [
            noun for noun in st.session_state.get(irregs_key, []) if noun in irreg_nouns
        ]
        irregs_include = st.multiselect(
            "Válaszd ki, mely rendhagyó főneveket szeretnéd gyakorolni:",
            options=irreg_nouns,
            help="Csak a kiválasztott declinatiókhoz tartozó rendhagyó főnevek jelennek meg.",
            key=widget_key(page_id, "irregs_include"),
        )
        if len(irregs_include) > 0:
            irregs_only = st.radio(
                "Csak a kiválasztott rendhagyó főnevek gyakorlása?",
                options=["No", "Yes"],
                format_func=lambda value: "Nem" if value == "No" else "Igen",
                horizontal=True,
                key=widget_key(page_id, "irregs_only"),
            )

current_exercise_settings = {
    "exercise_type": exercise_type,
    "print_macrons": st.session_state[widget_key(page_id, "print_macrons")],
    "indicate_multiple_answers": st.session_state[widget_key(page_id, "indicate_multiple_answers")],
    "award_partial_credit": st.session_state[widget_key(page_id, "award_partial_credit")],
    "show_dictionary_entry": show_dictionary_entry,
    "show_declension": show_declension,
    "show_third_group": show_third_group,
    "show_stem": show_stem,
    "declension": declension,
    "irregs_include": irregs_include,
    "irregs_only": irregs_only,
}

if st.user.is_logged_in:
    generic_noun_settings = {
        "exercise_type": "inflect",
        "print_macrons": False,
        "indicate_multiple_answers": False,
        "award_partial_credit": False,
        "show_dictionary_entry": True,
        "show_declension": False,
        "show_third_group": False,
        "show_stem": False,
        "declension": DEFAULT_DECLENSIONS,
        "irregs_include": [],
        "irregs_only": "No",
    }
    current_noun_settings = {
        "exercise_type": exercise_type,
        "print_macrons": st.session_state[widget_key(page_id, "print_macrons")],
        "indicate_multiple_answers": st.session_state[widget_key(page_id, "indicate_multiple_answers")],
        "award_partial_credit": st.session_state[widget_key(page_id, "award_partial_credit")],
        "show_dictionary_entry": show_dictionary_entry,
        "show_declension": show_declension,
        "show_third_group": show_third_group,
        "show_stem": show_stem,
        "declension": declension,
        "irregs_include": irregs_include,
        "irregs_only": irregs_only,
    }
    noun_settings_changed = current_noun_settings != generic_noun_settings

    def reset_noun_defaults():
        clear_defaults(page_id)
        st.session_state.nouns_exercise_type = "inflect"
        st.session_state.nouns_print_macrons = False
        st.session_state.nouns_indicate_multiple_answers = False
        st.session_state.nouns_award_partial_credit = False
        st.session_state.nouns_show_dictionary_entry = True
        st.session_state.nouns_show_declension = False
        st.session_state.nouns_show_third_group = False
        st.session_state.nouns_show_stem = False
        st.session_state.nouns_declension = DEFAULT_DECLENSIONS
        st.session_state.nouns_irregs_include = []
        st.session_state.nouns_irregs_only = "No"

with option_expander:
    if st.user.is_logged_in:
        set_defaults_col, clear_defaults_col, link_col = st.columns(3)
        with set_defaults_col:
            st.button(
                "Beállítások mentése",
                type="primary",
                width="stretch",
                help="A jelenlegi főnévi beállítások mentése alapértelmezettként (a hosszú magánhangzók ellenőrzésének kivételével).",
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
                help="A BevLat általános alapértelmezett főnévi beállításainak visszaállítása.",
                on_click=reset_noun_defaults,
                disabled=preset_active or (not defaults and not noun_settings_changed),
            )
        with link_col:
            exercise_link_popover(page_id, exercise_schema, current_exercise_settings)
    else:
        exercise_link_popover(page_id, exercise_schema, current_exercise_settings)


for noun in irreg_nouns:
    if noun not in irregs_include and noun in active_vocab:
        active_vocab.pop(noun)

if irregs_only == "Yes":
    irreg_decl = []
    for noun in irregs_include:
        irreg_decl.append(noun_vocab[noun]["decl"])
    active_vocab = {k: v for k, v in active_vocab.items() if k in irregs_include}

noun_options = {
    "case": {
        "nom": "nominativus",
        "gen": "genitivus",
        "dat": "dativus",
        "acc": "accusativus",
        "abl": "ablativus",
        "voc": "vocativus",
    },
    "number": {
        "sg": "singularis",
        "pl": "pluralis",
    },
}


NOUN_ANALYSIS_TOKEN_ALIASES = {
    "sg": "sg", "sing": "sg", "singular": "sg", "singularis": "sg",
    "pl": "pl", "plur": "pl", "plural": "pl", "pluralis": "pl",
    "nom": "nom", "nominative": "nom", "nominativus": "nom",
    "voc": "voc", "vocative": "voc", "vocativus": "voc",
    "acc": "acc", "accusative": "acc", "accusativus": "acc",
    "gen": "gen", "genitive": "gen", "genitivus": "gen",
    "dat": "dat", "dative": "dat", "dativus": "dat",
    "abl": "abl", "ablative": "abl", "ablativus": "abl",
}
NOUN_ANALYSIS_SOURCE_TOKENS = tuple(
    sorted(NOUN_ANALYSIS_TOKEN_ALIASES, key=len, reverse=True)
)


def segment_noun_analysis_token(token):
    """Fully segment one tokenizer token into known noun-analysis abbreviations."""
    memo = {}

    def segment_from(index):
        if index == len(token):
            return []
        if index in memo:
            return memo[index]
        for candidate in NOUN_ANALYSIS_SOURCE_TOKENS:
            if token.startswith(candidate, index):
                remainder = segment_from(index + len(candidate))
                if remainder is not None:
                    memo[index] = [candidate] + remainder
                    return memo[index]
        memo[index] = None
        return None

    return segment_from(0)


def parse_noun_analysis_answer(text):
    """Parse NUMBER CASE+ (NUMBER CASE+)* from free-form noun analysis input."""
    raw_tokens = tokenize_morphology_answer(text)
    normalized_tokens = []

    for raw_token in raw_tokens:
        pieces = segment_noun_analysis_token(raw_token)
        if pieces is None:
            return {
                "valid": False,
                "tokens": normalized_tokens,
                "analyses": set(),
                "error": f"unrecognized token: {raw_token}",
            }
        normalized_tokens.extend(NOUN_ANALYSIS_TOKEN_ALIASES[piece] for piece in pieces)

    if not normalized_tokens:
        return {
            "valid": False,
            "tokens": [],
            "analyses": set(),
            "error": "no grammatical tokens found",
        }

    if normalized_tokens == ["voc"]:
        normalized_tokens = ["sg", "voc"]

    analyses = set()
    current_number = None
    current_number_has_case = False

    for token in normalized_tokens:
        if token in noun_options["number"]:
            if current_number is not None and not current_number_has_case:
                return {
                    "valid": False,
                    "tokens": normalized_tokens,
                    "analyses": analyses,
                    "error": f"number {current_number} has no case",
                }
            current_number = token
            current_number_has_case = False
        elif token in noun_options["case"]:
            if current_number is None:
                return {
                    "valid": False,
                    "tokens": normalized_tokens,
                    "analyses": analyses,
                    "error": f"case {token} appears before any number",
                }
            analyses.add((current_number, token))
            current_number_has_case = True

    if current_number is not None and not current_number_has_case:
        return {
            "valid": False,
            "tokens": normalized_tokens,
            "analyses": analyses,
            "error": f"number {current_number} has no case",
        }

    return {
        "valid": True,
        "tokens": normalized_tokens,
        "analyses": analyses,
        "error": None,
    }


NOUN_ANALYSIS_CASE_ORDER = {
    case: index for index, case in enumerate(("nom", "voc", "acc", "gen", "dat", "abl"))
}
NOUN_ANALYSIS_NUMBER_ORDER = {"sg": 0, "pl": 1}


def canonicalize_noun_analyses(analyses):
    return sorted(
        analyses,
        key=lambda analysis: (
            NOUN_ANALYSIS_NUMBER_ORDER[analysis[0]],
            NOUN_ANALYSIS_CASE_ORDER[analysis[1]],
        ),
    )


def format_noun_analysis(analysis):
    number, case = analysis
    return f"{number}. {case}."


def format_noun_analysis_list(analyses):
    return "; ".join(
        format_noun_analysis(analysis)
        for analysis in canonicalize_noun_analyses(analyses)
    )


def evaluate_noun_recognition_answer(user_analyses, required_analyses, optional_analyses=None):
    user_analyses = set(user_analyses)
    required_analyses = set(required_analyses)
    optional_analyses = set(optional_analyses or ())
    valid_analyses = required_analyses | optional_analyses

    if required_analyses.issubset(user_analyses) and user_analyses.issubset(valid_analyses):
        return "correct"
    if user_analyses & valid_analyses:
        return "partial"
    return "incorrect"


noun_endings = {
    1: {"sg": {"gen": "ae", "dat": "ae", "acc": "am", "abl": "ā", "voc": None},
        "pl": {"nom": "ae", "gen": "ārum", "dat": "īs", "acc": "ās", "abl": "īs", "voc": None}},
    "2_us": {"sg": {"gen": "ī", "dat": "ō", "acc": "um", "abl": "ō", "voc": "e"},
             "pl": {"nom": "ī", "gen": "ōrum", "dat": "īs", "acc": "ōs", "abl": "īs", "voc": None}},
    "2_er": {"sg": {"gen": "ī", "dat": "ō", "acc": "um", "abl": "ō", "voc": None},
             "pl": {"nom": "ī", "gen": "ōrum", "dat": "īs", "acc": "ōs", "abl": "īs", "voc": None}},
    "2_neut": {"sg": {"gen": "ī", "dat": "ō", "acc": "um", "abl": "ō", "voc": None},
               "pl": {"nom": "a", "gen": "ōrum", "dat": "īs", "acc": "a", "abl": "īs", "voc": None}},
    3: {"sg": {"gen": "is", "dat": "ī", "acc": "em", "abl": "e", "voc": None},
        "pl": {"nom": "ēs", "gen": "um", "dat": "ibus", "acc": "ēs", "abl": "ibus", "voc": None}},
    "3_neut": {"sg": {"gen": "is", "dat": "ī", "acc": None, "abl": "e", "voc": None},
               "pl": {"nom": "a", "gen": "um", "dat": "ibus", "acc": "a", "abl": "ibus", "voc": None}},
    "3_istem": {"sg": {"gen": "is", "dat": "ī", "acc": "em", "abl": "e", "voc": None},
                "pl": {"nom": "ēs", "gen": "ium", "dat": "ibus", "acc": ["īs", "ēs"], "abl": "ibus", "voc": None}},
    "3_istem_neut": {"sg": {"gen": "is", "dat": "ī", "acc": None, "abl": "ī", "voc": None},
                     "pl": {"nom": "ia", "gen": "ium", "dat": "ibus", "acc": "ia", "abl": "ibus", "voc": None}},
    4: {"sg": {"gen": "ūs", "dat": "uī", "acc": "um", "abl": "ū", "voc": None},
        "pl": {"nom": "ūs", "gen": "uum", "dat": "ibus", "acc": "ūs", "abl": "ibus", "voc": None}},
    "4_neut": {"sg": {"gen": "ūs", "dat": "ū", "acc": "ū", "abl": "ū", "voc": None},
               "pl": {"nom": "ua", "gen": "uum", "dat": "ibus", "acc": "ua", "abl": "ibus", "voc": None}},
    "5_vowel": {"sg": {"gen": "ēī", "dat": "ēī", "acc": "em", "abl": "ē", "voc": None},
                "pl": {"nom": "ēs", "gen": "ērum", "dat": "ēbus", "acc": "ēs", "abl": "ēbus", "voc": None}},
    "5_consonant": {"sg": {"gen": "eī", "dat": "eī", "acc": "em", "abl": "ē", "voc": None},
                    "pl": {"nom": "ēs", "gen": "ērum", "dat": "ēbus", "acc": "ēs", "abl": "ēbus", "voc": None}},
}


if len(declension) == 0 and not st.session_state.current_question:
    st.write("Legalább egy declinatiót ki kell választanod.")
else:
    def noun_has_distinct_sg_vocative(noun):
        nominative = build_noun([noun, "nom", "sg"])
        vocative = build_noun([noun, "voc", "sg"])
        if vocative is None:
            return False
        nominative_forms = set(nominative if isinstance(nominative, list) else [nominative])
        vocative_forms = set(vocative if isinstance(vocative, list) else [vocative])
        return vocative_forms != nominative_forms


    def inflection_cases_for_noun(noun, number):
        cases = [case for case in noun_options["case"] if case != "voc"]
        if number == "sg" and noun_has_distinct_sg_vocative(noun):
            cases.append("voc")
        return cases


    def inflection_case_weights(noun, number):
        cases = inflection_cases_for_noun(noun, number)
        nom_weight = 9
        if number == "sg":
            nom_weight = 1 if is_diagnostic_sg_nom(noun, st.session_state.nouns_enforce_macrons) else 9
        weights = {
            "nom": nom_weight,
            "gen": 9,
            "dat": 9,
            "acc": 9,
            "abl": 9,
            "voc": 8,
        }
        return cases, [weights[case] for case in cases]


    def gen_question():
        last_question = st.session_state.question_list[-1] if st.session_state.question_list else {}
        decl_rand = random.choice(declension)
        decl_dict_subset = declension_dict.get(decl_rand)
        if irregs_only == "Yes":
            decl_dict_subset = random.choice(irreg_decl)

        if isinstance(decl_dict_subset, list):
            decl_rand_subset = random.choice(decl_dict_subset)
            vocab_subset = {k: v for k, v in active_vocab.items() if v["decl"] == decl_rand_subset}
        else:
            vocab_subset = {k: v for k, v in active_vocab.items() if v["decl"] == decl_dict_subset}
        noun = random.choice(list(vocab_subset.keys()))
        number_restriction = noun_vocab[noun].get("number")
        if number_restriction == "singular":
            number = "sg"
        elif number_restriction == "plural":
            number = "pl"
        else:
            number = random.choice(list(noun_options["number"].keys()))
        available_cases, case_weights = inflection_case_weights(noun, number)
        case = ""
        while case == "":
            case = random.choices(available_cases, case_weights)[0]
            if case in noun_vocab[noun].get("irreg", {}).get(number, {}) and noun_vocab[noun]["irreg"][number][case] is None:
                case = ""
            elif number == last_question.get("id", {}).get("num") and noun_vocab[noun]["decl"] == noun_vocab.get(last_question.get("word"), {}).get("decl"):
                if case == last_question.get("id", {}).get("case"):
                    case = ""
        return [noun, case, number]


    def adap_gen_question():
        avail_nouns = dict(active_vocab)
        if not avail_nouns:
            return
        noun_qs_answered = [
            {k: (v.copy() if isinstance(v, dict) else v) for k, v in q.copy().items()}
            for q in questions_asked
            if (q["pos"] == "noun" and "correct" in q and q["word"] in avail_nouns)
        ]
        for i, q in enumerate(noun_qs_answered):
            noun_qs_answered[i]["id"]["decl"] = noun_vocab[q["word"]]["decl"]
        last_q = noun_qs_answered[-1] if noun_qs_answered else {}

        dfs = {}
        noun = case = number = decl = None

        if questions_asked and noun_qs_answered:
            noun_df = (
                pd.json_normalize(noun_qs_answered)
                .reindex(columns=["pos", "word", "answer", "correct", "id.case", "id.num", "id.decl", "id.irreg"])
                .replace({None: "-", pd.NA: "-", "nan": "-", "None": "-"})
                .drop("answer", axis=1)
                .assign(**{"id.decl": lambda df: df["id.decl"].astype(str).replace({"5_consonant": "5", "5_vowel": "5"})})
                .assign(decl_mod=lambda df: df["id.decl"].apply(lambda x: x[0]))
                .assign(decl_mod=lambda df: df["decl_mod"].where(~(df["id.irreg"] == "irreg"), df["word"]))
                .drop("id.irreg", axis=1)
            )
            dfs["noun_df"] = noun_df

            def agg_df(gb):
                return (
                    gb.agg(num_correct=("correct", "sum"), total_q=("correct", "count"))
                    .assign(pct_wrong=lambda df: (df["total_q"] - df["num_correct"]) / df["total_q"])
                    .assign(weight=lambda df: ((df["total_q"] - df["num_correct"]) / (df["num_correct"] + 1)) ** 0.5)
                    .query("pct_wrong > 0")
                )

            if not noun_df.empty and len(noun_df) > 5:
                noun_df_wrong_indiv = agg_df(noun_df.copy().groupby(["decl_mod", "id.decl", "id.case", "id.num"]))
                if not noun_df_wrong_indiv.empty:
                    noun_df_wrong_agg_superset = agg_df(noun_df.copy().groupby("decl_mod"))
                    noun_df_wrong_agg = agg_df(noun_df.copy().groupby(["decl_mod", "id.decl"]))
                    dfs["noun_df_wrong_indiv"] = noun_df_wrong_indiv
                    dfs["noun_df_wrong_agg_superset"] = noun_df_wrong_agg_superset
                    dfs["noun_df_wrong_agg"] = noun_df_wrong_agg

        if "noun_df_wrong_agg" in dfs and noun_df_wrong_agg["weight"].max() >= .58:
            repeat_chance = random.choices(["new", "repeat"], [st.session_state["adap_learning_frequency"], 1])[0]
            if repeat_chance == "repeat":
                noun_info = None
                noun_decl_cat = noun_df_wrong_agg_superset["weight"].sample(
                    n=1, weights=noun_df_wrong_agg_superset["weight"]
                ).index[0]
                if noun_decl_cat not in noun_vocab:
                    if not noun_df_wrong_agg.xs(noun_decl_cat, level="decl_mod").query("weight >= .58").empty:
                        df_slice = noun_df_wrong_agg.xs(noun_decl_cat, level="decl_mod").query("weight >= .58")
                        decl = df_slice.sample(n=1, weights=df_slice["weight"]).index[0]
                if decl:
                    df_slice = noun_df_wrong_indiv.xs((noun_decl_cat, decl), level=["decl_mod", "id.decl"]).query("weight > 1.7")
                else:
                    df_slice = noun_df_wrong_indiv.xs(noun_decl_cat, level="decl_mod").query("weight > 1.7")
                if not df_slice.empty:
                    noun_info = df_slice.sample(n=1, weights=df_slice["weight"]).index[0]
                    if len(noun_info) == 2:
                        case, number = noun_info
                    else:
                        if noun_decl_cat in noun_vocab:
                            case, number = noun_info[1:]
                            noun = noun_decl_cat
                        else:
                            decl, case, number = noun_info
                if decl and decl != "5":
                    decl = int(decl) if decl.isdigit() else decl
                elif noun_decl_cat in noun_vocab:
                    noun = noun_decl_cat
                else:
                    decl = []
                    for selected_decl in declension:
                        selected_values = declension_dict[selected_decl]
                        if not isinstance(selected_values, list):
                            selected_values = [selected_values]
                        decl.extend(
                            value for value in selected_values
                            if str(value).startswith(noun_decl_cat)
                        )
                if not noun:
                    if noun_decl_cat == "5":
                        avail_nouns = {
                            k: v for k, v in avail_nouns.items()
                            if v["decl"] in decl and not v.get("irreg", {}).get("irreg")
                        }
                    else:
                        if isinstance(decl, list):
                            decl = random.choice(decl)
                        avail_nouns = {
                            k: v for k, v in avail_nouns.items()
                            if v["decl"] == decl and not v.get("irreg", {}).get("irreg")
                        }
                    noun = random.choice(list(avail_nouns))
                if noun_info and case not in inflection_cases_for_noun(noun, number):
                    noun_info = None
                    case = None
                if not noun_info:
                    number = random.choice(list(noun_options["number"].keys()))
                    available_cases, case_weights = inflection_case_weights(noun, number)
                    case = ""
                    while case == "" or (
                        case in noun_vocab[noun].get("irreg", {}).get(number, {})
                        and noun_vocab[noun]["irreg"][number][case] is None
                    ):
                        case = random.choices(available_cases, case_weights)[0]
                        if (
                            (noun == last_q.get("word") or noun_vocab[noun]["decl"] == last_q.get("decl"))
                            and case == last_q.get("id", {}).get("case")
                            and number == last_q.get("id", {}).get("num")
                        ):
                            case = ""
        while not noun:
            noun, case, number = gen_question()
            if (
                (noun == last_q.get("word") or noun_vocab[noun]["decl"] == noun_vocab.get(last_q.get("word"), {}).get("decl"))
                and case == last_q.get("id", {}).get("case")
                and number == last_q.get("id", {}).get("num")
            ):
                noun = None
        return [noun, case, number]


    def build_noun(noun_id=None):
        if noun_id:
            pass
        else:
            noun_id = adap_gen_question()
        noun, case, number = noun_id
        noun_decl = noun_vocab.get(noun, {}).get("decl")
        noun_stem = noun_vocab.get(noun, {}).get("stem")
        correct_answer = ""
        if case == "nom" and number == "sg":
            correct_answer = noun
        else:
            if "irreg" in noun_vocab[noun]:
                irreg_form = noun_vocab[noun]["irreg"].get(number, {}).get(case, "")
                if irreg_form:
                    correct_answer = irreg_form
                elif irreg_form is None:
                    return None
            if not correct_answer:
                correct_ending = noun_endings[noun_decl][number][case]
                if ((noun[-3:] == "ius" and noun_decl == "2_us") or (noun[-3:] == "ium" and noun_decl == "2_neut")) and number == "sg":
                    if case in ["voc", "gen"]:
                        if case == "voc" and noun_decl == "2_us":
                            noun_stem = noun_stem[:-1]
                            correct_ending = "ī"
                        if case == "gen":
                            noun_stem = noun_stem[:-1]
                            correct_ending = ["iī", "ī"]
                if noun_vocab[noun].get("true_i_stem") is True and number == "sg":
                    if case == "acc":
                        correct_ending = ["im", "em"]
                    if case == "abl":
                        correct_ending = ["ī", "e"]
                if correct_ending is None and number == "sg":
                    correct_answer = noun
                else:
                    if correct_ending is None and number == "pl":
                        correct_ending = noun_endings[noun_decl][number]["nom"]
                        correct_answer = noun_stem + correct_ending
                    elif isinstance(correct_ending, list):
                        correct_answer = [noun_stem + ending for ending in correct_ending]
                    else:
                        correct_answer = noun_stem + correct_ending
        return correct_answer


    def build_dictionary_entry(noun):
        genitive = build_noun([noun, "gen", "sg"])
        gender = noun_vocab[noun]["gender"]
        if isinstance(genitive, list):
            if str(noun_vocab[noun].get("decl", "")).startswith("2") and noun.endswith(("ius", "ium")):
                genitive = genitive[0]
            else:
                genitive = "/".join(genitive)
        if genitive:
            return f"{noun}, {genitive} {gender}."
        return f"{noun} {gender}."


    def display_noun_stem(noun):
        stem = noun_vocab[noun]["stem"]
        if str(noun_vocab[noun].get("decl", "")).startswith("5"):
            stem += "e"
        return stem


    def third_declension_group(noun):
        noun_decl = noun_vocab[noun]["decl"]
        if noun_decl in (3, "3_neut"):
            return "msh.-tövű"
        if noun_decl == "3_istem_neut" or noun_vocab[noun].get("true_i_stem") is True:
            return "erős i-tövű"
        if noun_decl == "3_istem":
            return "gyenge i-tövű"
        return ""


    def normalize_noun_surface(form, preserve_macrons):
        normalized = unicodedata.normalize("NFC", form)
        return normalized if preserve_macrons else remove_macrons(normalized)


    def optional_noun_recognition_analyses(noun, displayed_form, preserve_macrons):
        if (
            noun == "deus"
            and normalize_noun_surface(displayed_form, preserve_macrons)
            == normalize_noun_surface("deum", preserve_macrons)
        ):
            return {("pl", "gen")}
        return set()


    def recognition_cases_for_noun(noun, number):
        cases = [case for case in noun_options["case"] if case != "voc"]
        if number == "sg" and noun_has_distinct_sg_vocative(noun):
            cases.append("voc")
        return cases


    def is_diagnostic_sg_nom(noun, preserve_macrons):
        nominative = build_noun([noun, "nom", "sg"])
        nominative_forms = nominative if isinstance(nominative, list) else [nominative]
        displayed_nominatives = {
            normalize_noun_surface(form, preserve_macrons)
            for form in nominative_forms
            if form is not None
        }

        analyses = set()
        for possible_number in noun_options["number"]:
            for possible_case in recognition_cases_for_noun(noun, possible_number):
                possible_form = build_noun([noun, possible_case, possible_number])
                if possible_form is None:
                    continue
                possible_forms = possible_form if isinstance(possible_form, list) else [possible_form]
                for form in possible_forms:
                    displayed = normalize_noun_surface(form, preserve_macrons)
                    if displayed in displayed_nominatives:
                        analyses.add((possible_number, possible_case))
                        break
        return analyses == {("sg", "nom")}


    def recognition_gen_question():
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
        st.session_state.nouns_recognition_displayed_form = displayed_form
        return [noun, case, number]


    st.session_state.gen_func = recognition_gen_question if exercise_type == "recognize" else adap_gen_question

    if st.session_state.current_question:
        noun, case, number = st.session_state.current_question
        st.session_state["correct_answer"] = correct_answer = build_noun(st.session_state.current_question)

        noun_prompt = build_dictionary_entry(noun) if show_dictionary_entry else noun
        noun_decl = noun_vocab.get(noun)["decl"]
        decl = ""
        third_group = ""

        if show_declension:
            for key, val in declension_dict.items():
                if isinstance(val, list):
                    if noun_decl in val:
                        decl = key
                elif noun_decl == val:
                    decl = key
            if show_third_group:
                third_group = third_declension_group(noun)

        supplementary = []
        stem_html = f'<strong><em>{html.escape(display_noun_stem(noun))}-</em></strong>'

        if exercise_type == "inflect":
            question_html = (
                f'Add meg a <strong><em>{html.escape(noun_prompt)}</em></strong> szó '
                f'<strong>{noun_options["number"][number]} {noun_options["case"][case]}</strong>át!'
            )
            if show_declension and show_stem:
                decl_text = f"Ez egy {DECLENSION_NUMBER_LABELS[decl]} declinatiós"
                if third_group:
                    decl_text += f" {third_group}"
                supplementary.append(f"{decl_text} szó, a töve {stem_html}")
            elif show_declension:
                decl_text = f"Ez egy {DECLENSION_NUMBER_LABELS[decl]} declinatiós"
                if third_group:
                    decl_text += f" {third_group}"
                supplementary.append(f"{decl_text} szó.")
            elif show_stem:
                supplementary.append(f"A szó töve {stem_html}")
        else:
            displayed_form = st.session_state.get("nouns_recognition_displayed_form")
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

        prompt_height = 104 if supplementary else 72
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

        with st.form(key="noun_form", clear_on_submit=True):
            current_answer = st.text_input("Válaszod:", key="answer_input")

            def submit_noun_answer():
                recognition_answer = None
                parsed_answer = None
                evaluation = None

                if exercise_type == "recognize" and st.session_state.get("answer_input"):
                    recognition_answer = st.session_state.answer_input
                    parsed_answer = parse_noun_analysis_answer(recognition_answer)

                    if parsed_answer["valid"]:
                        evaluation = evaluate_noun_recognition_answer(
                            parsed_answer["analyses"], required_analyses, optional_analyses
                        )
                        st.session_state.correct_answer = (
                            recognition_answer
                            if evaluation == "correct"
                            else "__noun_recognition_incorrect__"
                        )
                        if evaluation == "partial":
                            st.session_state.answer_credit_override = (
                                0.5
                                if st.session_state[widget_key(page_id, "award_partial_credit")]
                                else 0
                            )
                    else:
                        st.session_state.correct_answer = recognition_answer

                submit_and_check_answer()

                if exercise_type == "inflect":
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
                            if not isinstance(answers, list):
                                answers = [answers]
                            correct_html = " <span style=\"font-weight:700;\">vagy</span> ".join(
                                heavy(answer, italic=True) for answer in answers
                            )
                            label = "A helyes válasz" if len(answers) == 1 else "A helyes válaszok"
                            st.session_state.answer_display_message = feedback_box(
                                f"<strong>Helytelen válasz. {label}:</strong> {correct_html}.",
                                "incorrect",
                            )
                    return

                if recognition_answer and parsed_answer:
                    if not parsed_answer["valid"]:
                        st.session_state.button_disable = False
                        st.session_state.answer_checked = False
                        st.session_state.total_questions = max(0, st.session_state.total_questions - 1)
                        st.session_state.append_answer = True
                        st.session_state.result_message = ""
                        st.session_state.auto_advance_trigger = False
                        st.session_state.nouns_recognition_extra_delay = 0
                        st.session_state.answer_display_message = (
                            "Ellenőrizd a válasz formátumát, majd próbáld újra. "
                            "Használhatsz például ilyen alakokat: **sg. nom.**, **pl. dat. abl.**"
                        )
                        return

                    user_analyses = set(parsed_answer["analyses"])
                    required_analyses_set = set(required_analyses)
                    optional_analyses_set = set(optional_analyses)
                    valid_analyses = required_analyses_set | optional_analyses_set
                    correct_supplied = user_analyses & valid_analyses
                    incorrect_supplied = user_analyses - valid_analyses
                    all_possible_text = format_noun_analysis_list(required_analyses_set)
                    st.session_state.nouns_recognition_extra_delay = 0

                    if evaluation == "correct":
                        st.session_state.result_message = "**Good job!**"
                        st.session_state.answer_display_message = feedback_box(
                            "<strong>Helyes válasz!</strong>", "correct"
                        )
                    elif evaluation == "partial":
                        st.session_state.result_message = "**Partially correct.**"
                        display_parts = []
                        for analysis in canonicalize_noun_analyses(user_analyses):
                            text = format_noun_analysis(analysis)
                            if analysis in correct_supplied:
                                background, border = "#d7f2df", "#7aa682"
                            else:
                                background, border = "#f7dddd", "#c48282"
                            display_parts.append(
                                '<span style="display:inline-block;background:{background};border:1px solid {border};'
                                'border-radius:0.3rem;padding:0.08rem 0.35rem;margin-right:0.25rem;font-weight:700;">'
                                '{text}</span>'.format(
                                    background=background,
                                    border=border,
                                    text=html.escape(text),
                                )
                            )
                        st.session_state.answer_display_message = feedback_box(
                            '<strong>Részben helyes válasz.</strong> '
                            '<span>Válaszod: {user}</span> '
                            '<strong>A helyes válasz: {correct}</strong>'.format(
                                user="".join(display_parts),
                                correct=heavy(all_possible_text),
                            ),
                            "partial",
                        )
                    else:
                        st.session_state.result_message = "**Incorrect. Better luck next time!**"
                        st.session_state.answer_display_message = feedback_box(
                            f"<strong>Helytelen válasz. A helyes válasz:</strong> {heavy(all_possible_text)}",
                            "incorrect",
                        )

            st.form_submit_button(
                "Válasz ellenőrzése",
                key="form_submission_button",
                on_click=submit_noun_answer,
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
            "pos": "noun",
            "word": noun,
            "id": {
                "case": case,
                "num": number,
                "decl": (
                    "1st" if str(noun_decl)[0] == "1"
                    else "2nd" if str(noun_decl)[0] == "2"
                    else "3rd (i-stem)" if "istem" in str(noun_decl)
                    else "3rd" if str(noun_decl)[0] == "3"
                    else "4th" if str(noun_decl)[0] == "4"
                    else "5th"
                ),
                "irreg": "irreg" if noun_vocab[noun].get("irreg", {}).get("irreg") is True else None,
            },
        }

        if st.session_state.append_answer is True:
            questions_asked.append(curr_question)
            st.session_state.append_answer = False

    control_row = st.container(height=110, border=False)
    with control_row:
        new_question_col, results_col, score_col = st.columns([1, 1, 1], gap="medium", vertical_alignment="top")

        new_q_button_text = "Új kérdés" if st.session_state.question_list else "Kattints ide az első kérdéshez!"
        new_q_button_type = "secondary" if st.session_state.question_list else "primary"
        with new_question_col:
            st.button(
                new_q_button_text,
                on_click=new_question,
                args=(st.session_state.gen_func,),
                key="question_button",
                width="stretch",
                disabled=len(declension) == 0,
                type=new_q_button_type,
            )

        with results_col:
            if (
                st.session_state.current_question
                and st.session_state.answer_checked
                and "Incorrect" in st.session_state.result_message
            ):
                chart_popover = st.popover("Ragozási táblázat", type="primary")
                with chart_popover:
                    st.caption("Ez a funkció még fejlesztés alatt áll.")
                    st.caption("Az esetek sorrendjét a navigációs menüben állíthatod be.")
                    starting_form = list(st.session_state.current_question)
                    next_form = list(starting_form)
                    noun_table = {}
                    table_index = []
                    cs_order = [
                        cs for cs in st.session_state.case_order
                        if cs != "voc" or noun_has_distinct_sg_vocative(starting_form[0])
                    ]
                    for num in ["sg", "pl"]:
                        noun_table[num] = []
                        for cs in cs_order:
                            if cs not in table_index:
                                table_index.append(cs)
                            next_form[2] = num
                            next_form[1] = cs
                            try:
                                form = build_noun(next_form)
                                if isinstance(form, list):
                                    form = "/".join(form)
                                if next_form == starting_form:
                                    form = f":green-background[{form}]"
                            except Exception:
                                form = None
                            noun_table[num].append(form if form is not None else "--")
                    declension_table = pd.DataFrame(noun_table, index=table_index)
                    st.table(declension_table)

        with score_col:
            st.button("Pontszám nullázása", "reset", on_click=reset, width="stretch")
            st.markdown(
                f'<div style="text-align:right;">Jelenlegi pontszám: <strong>{st.session_state.current_score}</strong> / <strong>{st.session_state.total_questions}</strong></div>',
                unsafe_allow_html=True,
            )

    if st.session_state.auto_advance_trigger and st.session_state.answer_checked:
        advance_delay = auto_advance_delay()
        if exercise_type == "recognize":
            advance_delay = min(
                60,
                advance_delay + st.session_state.get("nouns_recognition_extra_delay", 0),
            )
        time.sleep(advance_delay)
        new_question(st.session_state.gen_func)
        st.rerun()
