import streamlit as st
import random
import time
import pandas as pd
import ast
from utils import radio_change, reset, new_question, submit_and_check_answer, clear_page, send_setting, save_defaults, clear_defaults, auto_advance_delay, remove_macrons, tokenize_morphology_answer
from exercise_presets import (bool_setting, choice_setting, list_setting, resolve_exercise_settings,
                              initialize_widget_state, widget_key, url_preset_active, exercise_link_popover)
from vocab import import_nouns


st.set_page_config("BevLat Nouns", layout="centered")

# if st.session_state.question_list:
questions_asked = st.session_state.question_list
noun_vocab = import_nouns()

# if "nouns_enforce_macrons" not in st.session_state:
st.session_state.nouns_enforce_macrons = st.session_state.enforce_macrons["nouns_enforce_macrons"]

page_id = "nouns"
clear_page(page_id)

defaults = st.session_state.default_settings.get(f"{page_id}.py", {})

st.markdown("# Nouns")


declension_dict = {
    "1st": 1,
    "2nd":["2_us", "2_er", "2_neut"],
    "3rd": [3, "3_istem", "3_neut", "3_istem_neut"],
    "4th": [4, "4_neut"],
    "5th": ["5_vowel", "5_consonant"]
    }

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
    "show_stem": bool_setting(False),
    "declension": list_setting(list(declension_dict.keys()), list(declension_dict.keys())),
    "irregs_include": list_setting(["deus"] if "deus" in master_irregular_nouns_list else [], master_irregular_nouns_list),
    "irregs_only": choice_setting("No", ["No", "Yes"]),
}
exercise_settings = resolve_exercise_settings(page_id, exercise_schema, defaults)
initialize_widget_state(page_id, exercise_settings)
preset_active = url_preset_active(page_id)

## SET OPTIONS ##

option_expander = st.expander("Settings", expanded=True)

with option_expander:
    exercise_type = st.radio(
        "Exercise type:",
        options=["inflect", "recognize"],
        format_func=lambda value: {
            "inflect": "Inflect words",
            "recognize": "Recognize inflected forms",
        }[value],
        horizontal=True,
        key=widget_key(page_id, "exercise_type"),
        on_change=radio_change,
    )
    col_declension, col_options = st.columns([3,2])

with col_options:
    def switch_noun_macrons():
        st.session_state.enforce_macrons["nouns_enforce_macrons"] = st.session_state["nouns_enforce_macrons"]
        return
    st.markdown("Options:", help="You can adjust these options at any point.")
    if exercise_type == "inflect":
        st.checkbox("Enforce macrons?",
                    help="If this box is selected, macron mistakes will be considered incorrect. If not selected, macrons can be used but will not be evaluated.",
                    key="nouns_enforce_macrons",
                    # value=st.session_state.enforce_macrons["nouns_enforce_macrons"],
                    on_change=send_setting,
                    args=(switch_noun_macrons,),
                    kwargs={"streamlit_page":"nouns.py","setting_name":"nouns_enforce_macrons"},
                    )
        # st.session_state.enforce_macrons["nouns_enforce_macrons"] = st.session_state.nouns_enforce_macrons
        macrons = st.session_state.nouns_enforce_macrons

        if macrons:
            st.markdown("You can copy and paste letters from here:")
            st.code("āēīōū", language=None)
    else:
        print_macrons = st.checkbox(
            "Print macrons?",
            help="If enabled, inflected forms will be printed with macrons, and answers must be provided considering the given vowel length; if disabled, vowels might be either short or long, in same cases raising the number of correct answers.",
            key=widget_key(page_id, "print_macrons"),
        )
        indicate_multiple_answers = st.checkbox(
            "Indicate multiple correct answers?",
            help="If enabled, the question will contain a message that there are multiple correct answers.",
            key=widget_key(page_id, "indicate_multiple_answers"),
        )
        award_partial_credit = st.checkbox(
            "Award partial credit?",
            help="If enabled, partially correct answers receive half credit; otherwise, only fully correct answers receive credit.",
            key=widget_key(page_id, "award_partial_credit"),
        )

    st.html('<hr style="border-top: 1px dotted; border-bottom: none;">')

    show_dictionary_entry = st.checkbox(
        "Show dictionary entry?",
        help="Select this box to show the whole dictionary entry of the noun, which allows one to reconstruct the stem/base from the genitive form.",
        key=widget_key(page_id, "show_dictionary_entry"),
    )
    show_declension = st.checkbox("Show declension?",
                                  help="Select this box to show the noun's declension.",
                                  key=widget_key(page_id, "show_declension"))
    show_stem = st.checkbox("Show noun stem/base?",
                            help="Select this box to show the noun base. (The base is the stem without any of the trailing vowels that sometimes combine with endings.)",
                            key=widget_key(page_id, "show_stem"))

with col_declension:
    # radio_change() is defined in utils.py
    # declension = st.radio("Choose a declension to practice:",{"random":"random"} | declension_dict, on_change=radio_change)
    declension = st.multiselect("Choose which declensions to practice (they are all selected by default):",
                                options=list(declension_dict.keys()),
                                help="If the selected declension(s) include irregular nouns, an option will be shown to include or exclude them.",
                                key=widget_key(page_id, "declension"))


## DEFINE AVAILABLE NOUNS AND NOUN ENDINGS ##

# based on radio button 'declension' (which may still need its own key in session_state), filter noun_vocab.
active_vocab = {}
for noun_key, noun_val in noun_vocab.items():
    n_decl = noun_val["decl"]
    for decl_sel in declension:
        if isinstance(declension_dict[decl_sel], list) and n_decl in declension_dict[decl_sel]:
            active_vocab = active_vocab | {noun_key: noun_val}
        elif n_decl == declension_dict[decl_sel]:
            active_vocab = active_vocab | {noun_key: noun_val}
        else:
            continue

# deal with irregular nouns
avail_decl = []
for item in {k:v for k,v in declension_dict.items() if k in declension}.values():
    if isinstance(item, list):
        avail_decl += item
    else:
        avail_decl.append(item)

irreg_nouns = [noun for noun in active_vocab.keys() if noun_vocab[noun].get("irreg", {}).get("irreg") and noun_vocab[noun]["decl"] in avail_decl]

irregs_include = []
irregs_only = "No"

with col_declension:
    if len(irreg_nouns) > 0:
        irregs_key = widget_key(page_id, "irregs_include")
        st.session_state[irregs_key] = [noun for noun in st.session_state.get(irregs_key, []) if noun in irreg_nouns]
        # default_irreg_nouns = [noun for noun in irreg_nouns if noun in active_vocab]
        # if defaults.get("irre")
        irregs_include = st.multiselect("Choose which irregular nouns to include:",
                                        options=irreg_nouns,
                                        help="Only irregular nouns for the selected declension(s) are shown.",
                                        key=widget_key(page_id, "irregs_include"))
        if len(irregs_include) > 0:
            irregs_only = st.radio("Practice *only* the selected irregular nouns?",
                                   options=["No", "Yes"],

                                   horizontal=True,
                                   key=widget_key(page_id, "irregs_only"))

current_exercise_settings = {
    "exercise_type": exercise_type,
    "print_macrons": st.session_state[widget_key(page_id, "print_macrons")],
    "indicate_multiple_answers": st.session_state[widget_key(page_id, "indicate_multiple_answers")],
    "award_partial_credit": st.session_state[widget_key(page_id, "award_partial_credit")],
    "show_dictionary_entry": show_dictionary_entry,
    "show_declension": show_declension,
    "show_stem": show_stem,
    "declension": declension,
    "irregs_include": irregs_include,
    "irregs_only": irregs_only,
}

with col_options:
    if st.user.is_logged_in:
        set_defaults_col, clear_defaults_col, link_col = st.container(vertical_alignment="bottom", height="stretch").columns(3, vertical_alignment="center")
        with set_defaults_col:
            st.button("Save settings",
                        type="primary",
                        width="stretch",
                        help="Save your current noun settings (except macron enforcement) as your default.",
                        on_click=save_defaults,
                        args=(page_id, defaults,),
                        kwargs=current_exercise_settings,
                        disabled=preset_active
                        )
        with clear_defaults_col:
            generic_noun_settings = {
                "exercise_type": "inflect",
                "print_macrons": False,
                "indicate_multiple_answers": False,
                "award_partial_credit": False,
                "show_dictionary_entry": True,
                "show_declension": False,
                "show_stem": False,
                "declension": list(declension_dict.keys()),
                "irregs_include": ["deus"],
                "irregs_only": "No",
            }
            current_noun_settings = {
                "exercise_type": exercise_type,
                "print_macrons": st.session_state[widget_key(page_id, "print_macrons")],
                "indicate_multiple_answers": st.session_state[widget_key(page_id, "indicate_multiple_answers")],
                "award_partial_credit": st.session_state[widget_key(page_id, "award_partial_credit")],
                "show_dictionary_entry": show_dictionary_entry,
                "show_declension": show_declension,
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
                st.session_state.nouns_show_stem = False
                st.session_state.nouns_declension = list(declension_dict.keys())
                st.session_state.nouns_irregs_include = ["deus"]
                st.session_state.nouns_irregs_only = "No"

            st.button("Reset defaults",
                        type="primary",
                        width="stretch",
                        help="Restore the generic BevLat default settings for nouns.",
                        on_click=reset_noun_defaults,
                        disabled=preset_active or (not defaults and not noun_settings_changed)
                        )
        with link_col:
            exercise_link_popover(page_id, exercise_schema, current_exercise_settings)
    else:
        exercise_link_popover(page_id, exercise_schema, current_exercise_settings)


for noun in irreg_nouns:
    if noun not in irregs_include:
        if noun in active_vocab:
            active_vocab.pop(noun)

if irregs_only == "Yes":
    irreg_decl = []
    for noun in irregs_include:
        irreg_decl.append(noun_vocab[noun]["decl"])
    active_vocab = {k:v for k,v in active_vocab.items() if k in irregs_include}

noun_options = {"case": {"nom": "nominative",
                         "gen": "genitive",
                         "dat": "dative",
                         "acc": "accusative",
                         "abl": "ablative",
                         "voc": "vocative"},
                "number": {"sg": "singular",
                           "pl": "plural"}}


NOUN_ANALYSIS_TOKEN_ALIASES = {
    "sg": "sg",
    "sing": "sg",
    "singular": "sg",
    "singularis": "sg",
    "pl": "pl",
    "plur": "pl",
    "plural": "pl",
    "pluralis": "pl",
    "nom": "nom",
    "nominative": "nom",
    "nominativus": "nom",
    "voc": "voc",
    "vocative": "voc",
    "vocativus": "voc",
    "acc": "acc",
    "accusative": "acc",
    "accusativus": "acc",
    "gen": "gen",
    "genitive": "gen",
    "genitivus": "gen",
    "dat": "dat",
    "dative": "dat",
    "dativus": "dat",
    "abl": "abl",
    "ablative": "abl",
    "ablativus": "abl",
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

    # A distinctive noun vocative can only be singular, so allow the
    # pedagogically natural shorthand "voc" / "voc." and normalize it.
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

NOUN_ANALYSIS_CASE_ORDER = {case: index for index, case in enumerate(("nom", "voc", "acc", "gen", "dat", "abl"))}
NOUN_ANALYSIS_NUMBER_ORDER = {"sg": 0, "pl": 1}


def canonicalize_noun_analyses(analyses):
    """Return noun analyses in canonical singular-then-plural case order."""
    return sorted(
        analyses,
        key=lambda analysis: (
            NOUN_ANALYSIS_NUMBER_ORDER[analysis[0]],
            NOUN_ANALYSIS_CASE_ORDER[analysis[1]],
        ),
    )


def format_noun_analysis(analysis):
    """Format one canonical noun analysis for user-facing feedback."""
    number, case = analysis
    return f"{number}. {case}."


def format_noun_analysis_list(analyses):
    """Format noun analyses in canonical order."""
    return "; ".join(
        format_noun_analysis(analysis)
        for analysis in canonicalize_noun_analyses(analyses)
    )


def evaluate_noun_recognition_answer(user_analyses, possible_analyses):
    """Return correct / partial / incorrect using complete-analysis semantics."""
    user_analyses = set(user_analyses)
    possible_analyses = set(possible_analyses)
    correct_supplied = user_analyses & possible_analyses

    if user_analyses == possible_analyses:
        return "correct"
    if correct_supplied:
        return "partial"
    return "incorrect"


noun_endings = {1: {"sg": {"gen": "ae",
                           "dat": "ae",
                           "acc": "am",
                           "abl": "ā",
                           "voc": None},
                    "pl": {"nom": "ae",
                           "gen": "ārum",
                           "dat": "īs",
                           "acc": "ās",
                           "abl": "īs",
                           "voc": None}},
                "2_us": {"sg": {"gen": "ī",
                           "dat": "ō",
                           "acc": "um",
                           "abl": "ō",
                           "voc": "e"},
                    "pl": {"nom": "ī",
                           "gen": "ōrum",
                           "dat": "īs",
                           "acc": "ōs",
                           "abl": "īs",
                           "voc": None}},
                "2_er": {"sg": {"gen": "ī",
                           "dat": "ō",
                           "acc": "um",
                           "abl": "ō",
                           "voc": None},
                    "pl": {"nom": "ī",
                           "gen": "ōrum",
                           "dat": "īs",
                           "acc": "ōs",
                           "abl": "īs",
                           "voc": None}},
                "2_neut": {"sg": {"gen": "ī",
                           "dat": "ō",
                           "acc": "um",
                           "abl": "ō",
                           "voc": None},
                    "pl": {"nom": "a",
                           "gen": "ōrum",
                           "dat": "īs",
                           "acc": "a",
                           "abl": "īs",
                           "voc": None}},
                3: {"sg": {"gen": "is",
                           "dat": "ī",
                           "acc": "em",
                           "abl": "e",
                           "voc": None},
                    "pl": {"nom": "ēs",
                           "gen": "um",
                           "dat": "ibus",
                           "acc": "ēs",
                           "abl": "ibus",
                           "voc": None}},
                "3_neut": {"sg": {"gen": "is",
                           "dat": "ī",
                           "acc": None,
                           "abl": "e",
                           "voc": None},
                    "pl": {"nom": "a",
                           "gen": "um",
                           "dat": "ibus",
                           "acc": "a",
                           "abl": "ibus",
                           "voc": None}},
                "3_istem": {"sg": {"gen": "is",
                           "dat": "ī",
                           "acc": "em",
                           "abl": "e",
                           "voc": None},
                    "pl": {"nom": "ēs",
                           "gen": "ium",
                           "dat": "ibus",
                           "acc": ["īs","ēs"],
                           "abl": "ibus",
                           "voc": None}},
                "3_istem_neut": {"sg": {"gen": "is",
                           "dat": "ī",
                           "acc": None,
                           "abl": "ī",
                           "voc": None},
                    "pl": {"nom": "ia",
                           "gen": "ium",
                           "dat": "ibus",
                           "acc": "ia",
                           "abl": "ibus",
                           "voc": None}},
                4: {"sg": {"gen": "ūs",
                           "dat": "uī",
                           "acc": "um",
                           "abl": "ū",
                           "voc": None},
                    "pl": {"nom": "ūs",
                           "gen": "uum",
                           "dat": "ibus",
                           "acc": "ūs",
                           "abl": "ibus",
                           "voc": None}},
                "4_neut": {"sg": {"gen": "ūs",
                           "dat": "ū",
                           "acc": "ū",
                           "abl": "ū",
                           "voc": None},
                    "pl": {"nom": "ua",
                           "gen": "uum",
                           "dat": "ibus",
                           "acc": "ua",
                           "abl": "ibus",
                           "voc": None}},
                "5_vowel": {"sg": {"gen": "ēī",
                           "dat": "ēī",
                           "acc": "em",
                           "abl": "ē",
                           "voc": None},
                    "pl": {"nom": "ēs",
                           "gen": "ērum",
                           "dat": "ēbus",
                           "acc": "ēs",
                           "abl": "ēbus",
                           "voc": None}},
                "5_consonant": {"sg": {"gen": "eī",
                           "dat": "eī",
                           "acc": "em",
                           "abl": "ē",
                           "voc": None},
                    "pl": {"nom": "ēs",
                           "gen": "ērum",
                           "dat": "ēbus",
                           "acc": "ēs",
                           "abl": "ēbus",
                           "voc": None}},
                           }


# st.write(st.session_state.question_list)
## CREATE THE QUIZ ##
if len(declension) == 0 and not st.session_state.current_question:
    st.write("You need to choose at least one declension.")
else:
    def gen_question():
        if len(st.session_state.question_list) > 0:
            last_question = st.session_state.question_list[-1]
        else:
            last_question = {}
        decl_rand = random.choice(declension)
        decl_dict_subset = declension_dict.get(decl_rand)
        if irregs_only == "Yes":
            decl_dict_subset = random.choice(irreg_decl)
        # st.write(decl_dict_subset)

        if isinstance(decl_dict_subset, list):
            decl_rand_subset = random.choice(decl_dict_subset)
            vocab_subset = {k: v for k,v in active_vocab.items() if v["decl"] == decl_rand_subset}
        else:
            vocab_subset = {k: v for k,v in active_vocab.items() if v["decl"] == decl_dict_subset}
        noun = random.choice(list(vocab_subset.keys()))
        number = random.choice(list(noun_options["number"].keys()))
        if number == "sg":
            nom_weight = 1 if is_diagnostic_sg_nom(noun, st.session_state.nouns_enforce_macrons) else 9
            case_weights = [nom_weight,9,9,9,9]
            # if decl_rand == "2nd":
            if decl_rand == "2nd" and noun[-2:] == "us":
                case_weights.append(8)
            elif noun[-2:] == "us" or decl_rand == "2nd":
                case_weights.append(5)
            else:
                case_weights.append(1)
        else:
            case_weights = [9,9,9,9,9,1]
        case = ""
        # if last_question:
        #     if noun_vocab[noun]["decl"] == noun_vocab[last_question["word"]] and number == last_question["id"].get("num"):
        #         case = last_question["id"].get("case")
        while case == "":
            case = random.choices(list(noun_options["case"].keys()),case_weights)[0]
            if case in noun_vocab[noun].get("irreg", {}).get(number, {}) and noun_vocab[noun]["irreg"][number][case] is None:
                case = ""
            elif number == last_question.get("id", {}).get("num") and noun_vocab[noun]["decl"] == noun_vocab.get(last_question.get("word"),{}).get("decl"):
                if case == last_question.get("id", {}).get("case"):
                    case = ""

        # st.write(noun, case, number)
        return [noun, case, number]


    ## ADAPTIVE LEARNING ALGORITHM ##

    def adap_gen_question():
        avail_nouns = dict(active_vocab)
        if not avail_nouns:
            return
        noun_qs_answered = [{k:(v.copy() if isinstance(v,dict) else v) for k,v in q.copy().items()} for q in questions_asked if (q["pos"] == "noun" and "correct" in q and q["word"] in avail_nouns)]
        for i,q in enumerate(noun_qs_answered):
            noun_qs_answered[i]["id"]["decl"] = noun_vocab[q["word"]]["decl"]
        last_q = noun_qs_answered[-1] if noun_qs_answered else {}

        dfs = {}
        noun = case = number = decl = None

        if questions_asked and noun_qs_answered:

            noun_df = (
                pd.json_normalize(noun_qs_answered)
                    .reindex(columns=["pos","word","answer","correct","id.case","id.num","id.decl","id.irreg"])
                    .replace({None: "-", pd.NA: "-", "nan": "-", "None": "-"})
                    .drop("answer",axis=1)
                    .assign(**{"id.decl": lambda df: df["id.decl"].astype(str).replace({"5_consonant":"5","5_vowel":"5"})})
                    .assign(decl_mod = lambda df: df["id.decl"].apply(lambda x: x[0]))
                    .assign(decl_mod = lambda df: df["decl_mod"].where(~(df["id.irreg"] == "irreg"), df["word"]))
                    .drop("id.irreg",axis=1)
                )
            # st.write(noun_df)
            dfs["noun_df"] = noun_df

            def agg_df(gb):
                df = (
                    gb.agg(num_correct=("correct","sum"),total_q=("correct","count"))
                        .assign(pct_wrong = lambda df: (df["total_q"]-df["num_correct"])/df["total_q"])
                        .assign(weight = lambda df: ((df["total_q"]-df["num_correct"])/(df["num_correct"]+1))**0.5)
                        .query("pct_wrong > 0")
                )
                return df

            if not noun_df.empty and len(noun_df) > 5:
                noun_df_wrong_indiv = agg_df(
                    noun_df.copy()
                        .groupby(["decl_mod","id.decl","id.case","id.num"])
                    )
                if not noun_df_wrong_indiv.empty:
                    noun_df_wrong_agg_superset = agg_df(
                        noun_df.copy()
                            .groupby("decl_mod")
                        )
                    noun_df_wrong_agg = agg_df(
                        noun_df.copy()
                            .groupby(["decl_mod","id.decl"])
                    )
                    dfs["noun_df_wrong_indiv"] = noun_df_wrong_indiv
                    dfs["noun_df_wrong_agg_superset"] = noun_df_wrong_agg_superset
                    dfs["noun_df_wrong_agg"] = noun_df_wrong_agg

        if "noun_df_wrong_agg" in dfs and noun_df_wrong_agg["weight"].max() >= .58:
            repeat_chance = random.choices(["new","repeat"],[st.session_state["adap_learning_frequency"],1])[0]
            if repeat_chance == "repeat":
                noun_info = None
                noun_decl_cat = (
                    noun_df_wrong_agg_superset["weight"]
                        .sample(n=1, weights=noun_df_wrong_agg_superset["weight"])
                        .index[0]
                    )
                if noun_decl_cat not in noun_vocab:
                    if not noun_df_wrong_agg.xs(noun_decl_cat,level="decl_mod").query("weight >= .58").empty:
                        df_slice = noun_df_wrong_agg.xs(noun_decl_cat,level="decl_mod").query("weight >= .58")
                        decl = df_slice.sample(n=1,weights=df_slice["weight"]).index[0]
                if decl:
                    df_slice = noun_df_wrong_indiv.xs((noun_decl_cat,decl),level=["decl_mod","id.decl"]).query("weight > 1.7")
                else:
                    df_slice = noun_df_wrong_indiv.xs(noun_decl_cat,level="decl_mod").query("weight > 1.7")
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
                    decl = next(val for key,val in declension_dict.items() if key.startswith(noun_decl_cat))
                if not noun:
                    if noun_decl_cat == "5":
                        avail_nouns = {k:v for k,v in avail_nouns.items() if v["decl"] in decl and not v.get("irreg", {}).get("irreg")}
                    else:
                        if isinstance(decl, list):
                            decl = random.choice(decl)
                        avail_nouns = {k:v for k,v in avail_nouns.items() if v["decl"] == decl and not v.get("irreg", {}).get("irreg")}
                    noun = random.choice(list(avail_nouns))
                if not noun_info:
                    number = random.choice(list(noun_options["number"].keys()))
                    if number == "sg" and noun != "deus":
                        nom_weight = 1 if is_diagnostic_sg_nom(noun, st.session_state.nouns_enforce_macrons) else 9
                        case_weights = [nom_weight,9,9,9,9]
                        if decl == "2_us":
                            case_weights.append(8)
                        elif noun[-2:] == "us" or (isinstance(decl, str) and decl.startswith("2")):
                            case_weights.append(5)
                        else:
                            case_weights.append(1)
                    else:
                        case_weights = [9,9,9,9,9,1]
                    case = ""
                    while case == "" or (case in noun_vocab[noun].get("irreg", {}).get(number, {}) and noun_vocab[noun]["irreg"][number][case] is None):
                        case = random.choices(list(noun_options["case"].keys()),case_weights)[0]
                        if (noun == last_q.get("word") or noun_vocab[noun]["decl"] == last_q.get("decl")) and case == last_q.get("id", {}).get("case") and number == last_q.get("id", {}).get("num"):
                            case = ""
        while not noun:
            noun, case, number = gen_question()
            if (noun == last_q.get("word") or noun_vocab[noun]["decl"] == noun_vocab.get(last_q.get("word"),{}).get("decl")) and case == last_q.get("id", {}).get("case") and number == last_q.get("id", {}).get("num"):
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
                            correct_ending = ["iī","ī"]
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
                        correct_answer = []
                        for ending in correct_ending:
                            correct_answer.append(noun_stem + ending)
                    else:
                        correct_answer = noun_stem + correct_ending
        return correct_answer

    def build_dictionary_entry(noun):
        genitive = build_noun([noun, "gen", "sg"])
        gender = noun_vocab[noun]["gender"]
        if isinstance(genitive, list):
            genitive = "/".join(genitive)
        if genitive:
            return f"{noun}, {genitive} {gender}."
        return f"{noun} {gender}."

    def recognition_cases_for_noun(noun, number):
        """Return cases used in noun recognition, with vocative only when distinctive."""
        cases = [case for case in noun_options["case"] if case != "voc"]
        if number != "sg":
            return cases

        noun_data = noun_vocab[noun]
        if not str(noun_data.get("decl", "")).startswith("2") or noun_data.get("gender") != "m":
            return cases

        nominative = build_noun([noun, "nom", "sg"])
        vocative = build_noun([noun, "voc", "sg"])
        if vocative is None:
            return cases

        nominative_forms = set(nominative if isinstance(nominative, list) else [nominative])
        vocative_forms = set(vocative if isinstance(vocative, list) else [vocative])
        if vocative_forms != nominative_forms:
            cases.append("voc")
        return cases

    def is_diagnostic_sg_nom(noun, preserve_macrons):
        """Whether the displayed sg. nom. has no other recognition-eligible analysis."""
        nominative = build_noun([noun, "nom", "sg"])
        nominative_forms = nominative if isinstance(nominative, list) else [nominative]
        displayed_nominatives = {
            form if preserve_macrons else remove_macrons(form)
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
                    displayed = form if preserve_macrons else remove_macrons(form)
                    if displayed in displayed_nominatives:
                        analyses.add((possible_number, possible_case))
                        break

        return analyses == {("sg", "nom")}

    def recognition_gen_question():
        # Use the ordinary random generator to choose the noun, but do not let
        # the sampled case/number determine which surface form is asked about.
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
                    displayed = form if print_macrons else remove_macrons(form)
                    form_analyses.setdefault(displayed, set()).add((possible_case, possible_number))

        displayed_forms = list(form_analyses)
        diagnostic_nom = is_diagnostic_sg_nom(noun, print_macrons)
        displayed_nom = noun if print_macrons else remove_macrons(noun)
        form_weights = [
            1 if diagnostic_nom and form == displayed_nom else 9
            for form in displayed_forms
        ]
        displayed_form = random.choices(displayed_forms, weights=form_weights, k=1)[0]
        case, number = random.choice(list(form_analyses[displayed_form]))
        st.session_state.nouns_recognition_displayed_form = displayed_form
        return [noun, case, number]

    st.session_state.gen_func = recognition_gen_question if exercise_type == "recognize" else adap_gen_question

    if st.session_state.current_question:
        noun, case, number = st.session_state.current_question
        st.session_state["correct_answer"] = correct_answer = build_noun(st.session_state.current_question)

        noun_prompt = build_dictionary_entry(noun) if show_dictionary_entry else noun
        noun_decl = noun_vocab.get(noun)["decl"]
        decl = ""
        third_logic = ""

        if show_declension:
            for key, val in declension_dict.items():
                if isinstance(val, list):
                    if noun_decl in val:
                        decl = key
                    if key == "3rd":
                        if noun_decl == "3_istem":
                            third_logic = "i-stem "
                        elif noun_decl == "3_neut":
                            third_logic = "neuter "
                        elif noun_decl == "3_istem_neut":
                            third_logic = "neuter i-stem "
                        else:
                            third_logic = ""
                elif noun_decl == val:
                    decl = key

        if exercise_type == "inflect":
            question = f'For *{noun_prompt}*, give the **{noun_options["case"][case]} {noun_options["number"][number]}**.'
            if show_declension:
                question += f" This is a {decl} declension {third_logic}noun."
            if show_stem:
                question += f' (The base is: {noun_vocab[noun]["stem"]}-)'
        else:
            displayed_form = st.session_state.get("nouns_recognition_displayed_form")
            if not displayed_form:
                # Fallback for any pre-existing session question created before
                # the recognition-specific generator was introduced.
                displayed_form = correct_answer
                if isinstance(displayed_form, list):
                    displayed_form = random.choice(displayed_form)
                if not st.session_state[widget_key(page_id, "print_macrons")]:
                    displayed_form = remove_macrons(displayed_form)

            question = f"Which number and case can *{displayed_form}* represent?"
            if show_dictionary_entry:
                question += f" The dictionary entry is *{build_dictionary_entry(noun)}*"
            if show_declension and show_stem:
                question += f' This is a {decl} declension {third_logic}noun and the base is: *{noun_vocab[noun]["stem"]}-*.'
            elif show_declension:
                question += f" This is a {decl} declension {third_logic}noun."
            elif show_stem:
                question += f' The base is: *{noun_vocab[noun]["stem"]}-*.'

            print_macrons = st.session_state[widget_key(page_id, "print_macrons")]
            comparable_displayed_form = displayed_form if print_macrons else remove_macrons(displayed_form)
            matching_analyses = set()
            for possible_number in noun_options["number"]:
                for possible_case in recognition_cases_for_noun(noun, possible_number):
                    possible_form = build_noun([noun, possible_case, possible_number])
                    if possible_form is None:
                        continue
                    possible_forms = possible_form if isinstance(possible_form, list) else [possible_form]
                    for form in possible_forms:
                        comparable_form = form if print_macrons else remove_macrons(form)
                        if comparable_form == comparable_displayed_form:
                            matching_analyses.add((possible_number, possible_case))
                            break

            vowel_phrase = "are" if print_macrons else "are not"
            question += f"  \nVowel lengths {vowel_phrase} indicated"
            if st.session_state[widget_key(page_id, "indicate_multiple_answers")]:
                if len(matching_analyses) > 1:
                    question += " and multiple correct answers are possible."
                else:
                    question += "."
            else:
                question += " and multiple correct answers might be possible."

        st.markdown("### Current question")

        with st.form(key="noun_form", clear_on_submit=True):
            current_answer = st.text_input(question, key="answer_input")
            submit_button_col, user_answer_col = st.columns([1,2])
            with submit_button_col:
                def disable_button():
                        st.session_state.button_disable = True

                def submit_noun_answer():
                    recognition_answer = None
                    parsed_answer = None
                    evaluation = None

                    if exercise_type == "recognize" and st.session_state.get("answer_input"):
                        recognition_answer = st.session_state.answer_input
                        parsed_answer = parse_noun_analysis_answer(recognition_answer)

                        if parsed_answer["valid"]:
                            evaluation = evaluate_noun_recognition_answer(
                                parsed_answer["analyses"],
                                matching_analyses,
                            )
                            # Let the shared checker perform score/history/logging. It only
                            # understands binary correctness, so partial answers are logged
                            # as not correct for adaptive-learning purposes.
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
                            # Use the temporary self-match only so the shared function can
                            # execute safely; all of its submission effects are rolled back below.
                            st.session_state.correct_answer = recognition_answer

                    submit_and_check_answer()

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
                                f"Please check your answer and try again. "
                                f"tokens={parsed_answer['tokens']}; parser error: {parsed_answer['error']}"
                            )
                            return

                        user_analyses = set(parsed_answer["analyses"])
                        possible_analyses = set(matching_analyses)
                        correct_supplied = user_analyses & possible_analyses
                        incorrect_supplied = user_analyses - possible_analyses
                        missing_analyses = possible_analyses - user_analyses
                        all_possible_text = format_noun_analysis_list(possible_analyses)
                        st.session_state.nouns_recognition_extra_delay = 0

                        if evaluation == "correct":
                            st.session_state.result_message = "**Good job!**"
                            st.session_state.answer_display_message = (
                                ":green-background[**Correct answer!**]"
                            )
                        elif evaluation == "partial":
                            st.session_state.result_message = "**Partially correct.**"
                            feedback_parts = []
                            if correct_supplied:
                                feedback_parts.append(
                                    '<div style="background:#d9f2df;padding:0.15rem 0.35rem;border-radius:0.25rem;">'
                                    f'Correct: {format_noun_analysis_list(correct_supplied)}</div>'
                                )
                            if incorrect_supplied:
                                feedback_parts.append(
                                    '<div style="background:#f7d7d9;padding:0.15rem 0.35rem;border-radius:0.25rem;">'
                                    f'Incorrect: {format_noun_analysis_list(incorrect_supplied)}</div>'
                                )
                            if missing_analyses:
                                feedback_parts.append(
                                    '<div style="background:#dbeafe;padding:0.15rem 0.35rem;border-radius:0.25rem;">'
                                    f'Missing: {format_noun_analysis_list(missing_analyses)}</div>'
                                )
                            st.session_state.answer_display_message = (
                                '<table style="border-collapse:collapse;border:none;background:#fff3cd;width:100%;">'
                                '<tr>'
                                '<td style="border:none;vertical-align:middle;padding:0.45rem 0.6rem;white-space:nowrap;">'
                                '<strong>Partially correct answer:</strong>'
                                '</td>'
                                '<td style="border:none;vertical-align:middle;padding:0.45rem 0.6rem;">'
                                + ''.join(feedback_parts) +
                                '</td>'
                                '</tr></table>'
                            )
                        else:
                            st.session_state.result_message = "**Incorrect. Better luck next time!**"
                            incorrect_text = format_noun_analysis_list(user_analyses)
                            st.session_state.answer_display_message = (
                                f":red-background[Your answer: {incorrect_text}]  \n"
                                f":red-background[**Correct: {all_possible_text}**]"
                            )

                st.form_submit_button(
                    "Check Answer",
                    key="form_submission_button",
                    on_click=submit_noun_answer,
                    disabled=st.session_state.button_disable,
                )
            with user_answer_col:
                if st.session_state.answer_display_message.lstrip().startswith("<table"):
                    st.html(st.session_state.answer_display_message)
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
                    "irreg": "irreg" if noun_vocab[noun].get("irreg",{}).get("irreg") is True else None
                },
            }

        if st.session_state.append_answer is True:
            questions_asked.append(curr_question)
            st.session_state.append_answer = False

    new_question_col, results_col, score_col = st.columns(3)

    new_q_button_text = "New Question" if st.session_state.question_list else "Click here for your first question!"
    new_q_button_type = "secondary" if st.session_state.question_list else "primary"
    with new_question_col:
        st.button(new_q_button_text, on_click=new_question, args=(st.session_state.gen_func,), key="question_button", width="stretch",
                  disabled=True if len(declension) == 0 else False, type=new_q_button_type
                  )

    with results_col:
        st.markdown(st.session_state.result_message)

        if st.session_state.current_question and st.session_state.answer_checked and "Incorrect" in st.session_state.result_message:
            chart_popover = st.popover("View chart",type="primary")
            with chart_popover:
                st.caption("*N.B. This is a beta feature; please let me know if it appears to be buggy or if you would find other information helpful.*")
                st.caption("You can change your preferred case order in the navigation menu.")
                starting_form = list(st.session_state.current_question)
                next_form = list(starting_form)
                noun_table = {}
                table_index = []
                cs_order = st.session_state.case_order
                for num in ["sg","pl"]:
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
                        except:
                            form = None
                        noun_table[num].append(form if form is not None else "--")
                declension_table = pd.DataFrame(noun_table, index=table_index)
                st.table(declension_table)

    with score_col:
        st.button("Reset Score", "reset", on_click=reset, width="stretch")
        st.markdown(f"Current score: **{st.session_state.current_score}** out of **{st.session_state.total_questions}**")

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

    #st.write(questions_asked)
