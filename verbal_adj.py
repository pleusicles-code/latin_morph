import streamlit as st
import random
import time
import pandas as pd
import ast
import html
import unicodedata
from utils import reset, new_question, submit_and_check_answer, clear_page, remove_macrons, send_setting, save_defaults, clear_defaults, auto_advance_delay
from exercise_presets import (bool_setting, list_setting, resolve_exercise_settings, initialize_widget_state,
                              widget_key, url_preset_active, exercise_link_popover)
from vocab import import_verbs, filter_vocab_by_repo

st.set_page_config("BevLat – Igenevek", layout="centered")

st.session_state.verbal_adj_enforce_macrons = st.session_state.enforce_macrons["verbal_adj_enforce_macrons"]

# if st.session_state.question_list:
questions_asked = st.session_state.question_list

page_id = "verbal_adj"
clear_page(page_id)

defaults = st.session_state.default_settings.get(f"{page_id}.py", {})

complete_verb_vocab = {**filter_vocab_by_repo(import_verbs(), "alap1"), **filter_vocab_by_repo(import_verbs(), "alap2"), **filter_vocab_by_repo(import_verbs(), "alap3")}

st.markdown("# Igenevek")


## SET OPTIONS ##

adj_abbrevs = {
    "decl": {
        (1, 2): "1–2. declinatiós melléknevek",
        3: "3. declinatiós melléknevek",
    },
    "case": {
        "nom": "nom.",
        "gen": "gen.",
        "dat": "dat.",
        "acc": "acc.",
        "abl": "abl.",
        "voc": "voc.",
    },
    "number": {
        "sg": "sg.",
        "pl": "pl.",
    },
    "gender": {
        "m": "m.",
        "f": "f.",
        "n": "n.",
    },
}

abbrevs = {
    "ind": "indicativus",
    "subj": "coniunctivus",
    "impv": "imperativus",
    "inf": "infinitivus",
    "sg": "sg.",
    "pl": "pl.",
    "pres": "praesens",
    "fut": "futurum",
    "perf": "perfectum",
    "act": "activum",
    "dep": "deponens",
    "semidep": "semideponens",
    "pass": "passivum",
    1: "1.",
    2: "2.",
    3: "3.",
    "pap": "part. impf. act.",
    "ppp": "part. perf. pass.",
    "fap": "part. inst. act.",
    "gdv": "part. inst. pass.",
} | adj_abbrevs["gender"] | adj_abbrevs["case"]

adj_options = {"case": [case for case in adj_abbrevs["case"] if case != "voc"],
                "number": list(adj_abbrevs["number"].keys()),
                "gender": list(adj_abbrevs["gender"].keys()),
                }

verb_vowels = {
    "inf": {
        1: "ā",
        2: "ē",
        3: "e",
        "3io": "e",
        4: "ī"
    },
    "pap_gdv": {
        1: "ā",
        2: "ē",
        3: "ē",
        "3io": "iē",
        4: "iē"
    }
}

adj_endings = {
    1: {
        "sg": {
            "nom": "a",
            "gen": "ae",
            "dat": "ae",
            "acc": "am",
            "abl": "ā",
            "voc": "a"
        },
        "pl": {
            "nom": "ae",
            "gen": "ārum",
            "dat": "īs",
            "acc": "ās",
            "abl": "īs",
            "voc": "ae"
        }
    },
    "2_us": {
        "sg": {
            "nom": "us",
            "gen": "ī",
            "dat": "ō",
            "acc": "um",
            "abl": "ō",
            "voc": "e"
        },
        "pl": {
            "nom": "ī",
            "gen": "ōrum",
            "dat": "īs",
            "acc": "ōs",
            "abl": "īs",
            "voc": "ī"
        }
    },
    "2_neut": {
        "sg": {
            "nom": "um",
            "gen": "ī",
            "dat": "ō",
            "acc": "um",
            "abl": "ō",
            "voc": "um"
        },
        "pl": {
            "nom": "a",
            "gen": "ōrum",
            "dat": "īs",
            "acc": "a",
            "abl": "īs",
            "voc": "a"
        }
    },
    3: {
        "sg": {
            "nom": None,
            "gen": "is",
            "dat": "ī",
            "acc": "em",
            "abl": ["ī","e"],
            "voc": None
        },
        "pl": {
            "nom": "ēs",
            "gen": "ium",
            "dat": "ibus",
            "acc": ["īs","ēs"],
            "abl": "ibus",
            "voc": "ēs"
        }
    },
    "3_neut": {
        "sg": {
            "nom": None,
            "gen": "is",
            "dat": "ī",
            "acc": None,
            "abl": ["ī","e"],
            "voc": None
        },
        "pl": {
            "nom": "ia",
            "gen": "ium",
            "dat": "ibus",
            "acc": "ia",
            "abl": "ibus",
            "voc": "ia"
        }
    },
}

conjugation_dict = {1: "1.",
                    2: "2.",
                    3: "3.",
                    4: "4."}


def normalized_conjugations(selected):
    """Merge the old 3io option into 3 when restoring saved settings."""
    if not isinstance(selected, (list, tuple)):
        return selected
    result = []
    for conj in selected:
        visible = 3 if conj == "3io" else conj
        if visible in conjugation_dict and visible not in result:
            result.append(visible)
    return result


def verb_stem_display(verb):
    """Use the same stem convention as the Igék page."""
    data = complete_verb_vocab[verb]
    present = data.get("pres")
    if present:
        ending = {1: "ā", 2: "ē", "3io": "i", 4: "ī"}.get(data.get("conj"), "")
        present += ending
    return [stem for stem in (present, data.get("perf"), data.get("ppp")) if stem]


def hungarian_article(word):
    """Select a/az according to the Latin lemma's initial sound."""
    normalized = "".join(
        char for char in unicodedata.normalize("NFD", str(word).lower())
        if unicodedata.category(char) != "Mn"
    )
    if not normalized or normalized[0] not in "aeiouy":
        return "a"
    # Initial Latin i/u before another vowel may be consonantal (iaciō, uēnor).
    if len(normalized) > 1 and normalized[0] in "iu" and normalized[1] in "aeiouy":
        if normalized[:2] not in {"ui"}:
            return "a"
    return "az"


def verb_dictionary_entry(verb, principal_parts, show_full_regular_first=False):
    """Use BevLat's compact verb entries, retaining irregular infinitives."""
    data = complete_verb_vocab[verb]
    conj = data.get("conj")
    regular_first = (
        conj == 1
        and data.get("voice") == "act"
        and data.get("pres")
        and data.get("perf") == data.get("pres") + "āv"
        and data.get("ppp") == data.get("pres") + "āt"
        and data.get("irreg", {}).get("irreg") is not True
    )
    if regular_first:
        return f"{verb} 1, -āvī, -ātum" if show_full_regular_first else f"{verb} 1"

    irregular_forms = data.get("irreg", {}).get("forms", {}).get("pres", {})
    irregular_infinitive = next(
        (irregular_forms.get(voice, {}).get("inf") for voice in ("act", "dep")
         if irregular_forms.get(voice, {}).get("inf")),
        None,
    )
    infinitive = irregular_infinitive or principal_parts.get(2)
    if irregular_infinitive or conj is None:
        head = f"{verb}, {infinitive}" if infinitive else verb
        separator = ", "
    else:
        head = f"{verb} {3 if conj == '3io' else conj}"
        separator = " "

    parts = [principal_parts.get(3), principal_parts.get(4)]
    parts = [part for part in parts if part]
    return head + (separator + ", ".join(parts) if parts else "")

master_ptc_list = ["pap", "ppp", "fap", "gdv"]
master_voice_list = ["act", "dep", "semidep"]
master_irregular_verbs_list = [key for key in complete_verb_vocab.keys() if complete_verb_vocab[key].get("irreg",{}).get("irreg") is True]
if "mālō" in master_irregular_verbs_list:
    master_irregular_verbs_list.remove("mālō")
exercise_schema = {
    "show_principal_parts": bool_setting(False),
    "full_regular_first_entry": bool_setting(False),
    "show_stems": bool_setting(False),
    "conjugation_selector": list_setting(list(conjugation_dict.keys()), list(conjugation_dict.keys())),
    "ptc_selector": list_setting(master_ptc_list, master_ptc_list),
    "voice_selector": list_setting(master_voice_list, master_voice_list),
    "irreg_selector": list_setting([], master_irregular_verbs_list),
}
defaults = dict(defaults)
if "conjugation_selector" in defaults:
    defaults["conjugation_selector"] = normalized_conjugations(defaults["conjugation_selector"])
exercise_settings = resolve_exercise_settings(page_id, exercise_schema, defaults)
conjugation_key = widget_key(page_id, "conjugation_selector")
if conjugation_key in st.session_state:
    st.session_state[conjugation_key] = normalized_conjugations(st.session_state[conjugation_key])
exercise_settings["conjugation_selector"] = normalized_conjugations(exercise_settings["conjugation_selector"])
initialize_widget_state(page_id, exercise_settings)
preset_active = url_preset_active(page_id)


option_expander = st.expander("Beállítások", expanded=True)

with option_expander:
    ptc_options_col,options_col = st.columns([3,2])

with options_col:
    def switch_verbal_adj_macrons():
        st.session_state.enforce_macrons["verbal_adj_enforce_macrons"] = st.session_state["verbal_adj_enforce_macrons"]
        return
    st.markdown("Opciók:", help="Ezeket a beállításokat gyakorlás közben is bármikor módosíthatod.")
    st.checkbox("Hosszú magánhangzók ellenőrzése?",
                help="Ha be van jelölve, a hosszú magánhangzók hibás jelölése hibás válasznak számít. Ha nincs bejelölve, a hosszúságjelek használhatók, de a program nem értékeli őket.",
                key="verbal_adj_enforce_macrons",
                on_change=send_setting,
                kwargs={"streamlit_page":"verbal_adj.py","setting_name":"verbal_adj_enforce_macrons"},
                args=(switch_verbal_adj_macrons,),
                # value=st.session_state.enforce_macrons["verbal_adj_enforce_macrons"]
                )
    macrons = st.session_state.verbal_adj_enforce_macrons
    if macrons:
        st.markdown("A hosszú magánhangzók innen másolhatók:")
        st.code("āēīōū", language=None)

    st.html('<hr style="border-top: 1px dotted; border-bottom: none;">')

    show_principal_parts = st.checkbox("Szótári alak megjelenítése?",
                                       key=widget_key(page_id, "show_principal_parts"),
                                       help="Az ige szótári alakjának megjelenítése.")
    full_regular_first_entry = st.checkbox(
        "Szabályos 1. coniugatiós igék teljes szótári alakjának megjelenítése",
        key=widget_key(page_id, "full_regular_first_entry"),
        disabled=not show_principal_parts,
    )
    show_stems = st.checkbox(
        "Tövek megjelenítése?",
        help="Az ige töveinek megjelenítése a kérdés alatt.",
        key=widget_key(page_id, "show_stems"),
    )

# with conjugation_col:
with ptc_options_col:
    conjugation_selector = st.multiselect(
        "Válaszd ki, mely coniugatiókat szeretnéd gyakorolni (alapértelmezés szerint mindegyik ki van választva):",
        conjugation_dict.keys(),
        format_func = lambda x: conjugation_dict.get(x),
        key=widget_key(page_id, "conjugation_selector"),
        help = "Ha egy coniugatiót sem választasz ki, csak a kiválasztott rendhagyó igékből kaphatsz kérdést."
        )

    ptc_dict = {abbrev: name for abbrev, name in zip(master_ptc_list, [abbrevs[ptc] for ptc in master_ptc_list])}
    ptc_selector = st.multiselect(
        "Válaszd ki, mely igenévtípusokat szeretnéd gyakorolni:",
        master_ptc_list,
        format_func=lambda x: ptc_dict[x],
        key=widget_key(page_id, "ptc_selector"),
        help="A part. inst. pass. a gerundivum (más néven participium futuri passivi). A part. inst. act. kizárólag activum vagy deponens alakot jelent."
    )

# with voice_col:
    voice_dict = {abbrev: name for abbrev, name in zip(master_voice_list,[abbrevs[vc] for vc in master_voice_list])}

    voice_selector = st.multiselect("Válaszd ki, mely igetípusokat szeretnéd gyakorolni:",
                                    master_voice_list,
                                    format_func=lambda x: voice_dict[x],
                                    key=widget_key(page_id, "voice_selector"),
                                    help = "Az act. itt a nem deponens igéket jelenti; az adott igenévtípus határozza meg, hogy activum vagy passivum alakot kell-e képezni.")

    # if "dō" in master_irregular_verbs_list:
    #     master_irregular_verbs_list.remove("dō")
    irreg_selector = st.multiselect("Válaszd ki, mely rendhagyó igéket szeretnéd gyakorolni:",
                                    master_irregular_verbs_list,
                                    key=widget_key(page_id, "irreg_selector"),
                                    help="A kiválasztott rendhagyó igék a fenti coniugatio-beállításoktól függetlenül előfordulhatnak. Ha csak rendhagyó igéket szeretnél gyakorolni, ne válassz ki egyetlen coniugatiót sem.")

current_exercise_settings = {
    "show_principal_parts": show_principal_parts,
    "full_regular_first_entry": full_regular_first_entry,
    "show_stems": show_stems,
    "conjugation_selector": conjugation_selector,
    "ptc_selector": ptc_selector,
    "voice_selector": voice_selector,
    "irreg_selector": irreg_selector,
}

with options_col:
    if st.user.is_logged_in:
        set_defaults_col, clear_defaults_col, link_col = st.container(vertical_alignment="bottom", height="stretch").columns(3, vertical_alignment="center")
        with set_defaults_col:
            st.button("Beállítások mentése",
                        type="primary",
                        width="stretch",
                        help="A jelenlegi igenévbeállítások mentése alapértelmezettként (a hosszú magánhangzók ellenőrzésének kivételével).",
                        on_click=save_defaults,
                        args=(page_id, defaults,),
                        kwargs=current_exercise_settings,
                        disabled=preset_active,
                        )
        with clear_defaults_col:
            st.button("Alapbeállítások",
                        type="primary",
                        width="stretch",
                        help="A BevLat általános alapértelmezett igenévbeállításainak visszaállítása.",
                        on_click=clear_defaults,
                        args=(page_id,),
                        disabled=preset_active or not defaults
                        )
        with link_col:
            exercise_link_popover(page_id, exercise_schema, current_exercise_settings)
    else:
        exercise_link_popover(page_id, exercise_schema, current_exercise_settings)

verb_vocab = {key: val for key, val in complete_verb_vocab.items() if not (all(val.get(ptc) is None for ptc in ["pap","ppp","fap","gdv"]) and all(ptc in val for ptc in ["pap","gdv"]))}
for vb in master_irregular_verbs_list:
    if vb not in irreg_selector:
        verb_vocab.pop(vb)

verb_vocab = {key: val for key,val in verb_vocab.items() if verb_vocab[key]["voice"] in voice_selector}
selected_conjugations = conjugation_selector + (["3io"] if 3 in conjugation_selector else [])
verb_vocab = {key: val for key, val in verb_vocab.items() if verb_vocab[key]["conj"] in selected_conjugations + [None] or key in irreg_selector}


if ptc_selector == ["pap"]:
    verb_vocab = {key:val for key, val in verb_vocab.items() if not ("pap" in verb_vocab[key] and verb_vocab[key].get("pap") is None)}
elif ptc_selector == ["ppp"]:
    verb_vocab = {key: val for key, val in verb_vocab.items() if "ppp" in verb_vocab[key]}
elif ptc_selector == ["gdv"]:
    verb_vocab = {key:val for key, val in verb_vocab.items() if not ("gdv" in verb_vocab[key] and verb_vocab[key].get("gdv") is None)}
# If the selection is limited either to just fut.act.ptc or to those and PPPs, then keep the verbs that have either a PPP stem or special fut.act.ptc stem.
elif all(ptc not in ptc_selector for ptc in ["pap", "gdv"]) or ptc_selector == ["fap"]:
    verb_vocab = {key: val for key, val in verb_vocab.items() if any(ptc in verb_vocab[key] for ptc in ["fap","ppp"]) and not ("fap" in verb_vocab[key] and verb_vocab[key]["fap"] is None)}
elif "pap" not in ptc_selector:
    verb_vocab = {key: val for key, val in verb_vocab.items() if any(verb_vocab[key].get(ptc) for ptc in ["fap","ppp","gdv"])}
elif "gdv" not in ptc_selector:
    verb_vocab = {key: val for key, val in verb_vocab.items() if any(verb_vocab[key].get(ptc) for ptc in ["fap","ppp","pap"])}
else:
    verb_vocab = {key: val for key, val in verb_vocab.items() if not (all(val.get(ptc) is None for ptc in ptc_selector) and all(ptc in val for ptc in ptc_selector if ptc != "ppp"))}

#st.write(verb_vocab.keys())


def feedback_box(content, state):
    """Match the answer feedback boxes on the Igék page."""
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


def submit_ptc_answer():
    """Retain shared scoring, with the same feedback format as the verbs page."""
    submitted = st.session_state.get("answer_input") or ""
    submit_and_check_answer()
    if not submitted:
        st.session_state.answer_display_message = (
            "A válaszmező üres. Írj be egy alakot, majd kattints a "
            "**Válasz ellenőrzése** gombra, vagy az **Új kérdés** gombbal ugord át a kérdést."
        )
        return

    if st.session_state.answer_checked:
        if "Good job!" in st.session_state.result_message:
            st.session_state.answer_display_message = feedback_box(
                "<strong>Helyes válasz!</strong>", "correct"
            )
        else:
            answers = st.session_state.correct_answer
            if isinstance(answers, list):
                answer_list = [heavy(answer, italic=True) for answer in answers]
                correct_html = " vagy ".join(answer_list)
                label = "A helyes válasz" if len(answer_list) == 1 else "A helyes válaszok"
            else:
                correct_html = heavy(answers, italic=True)
                label = "A helyes válasz"
            st.session_state.answer_display_message = feedback_box(
                f"<strong>Helytelen válasz. {label}:</strong> {correct_html}.",
                "incorrect",
            )



if len(ptc_selector) == 0:
    st.write("Legalább egy igenévtípust ki kell választanod.")
elif len(voice_selector) == 0:
    st.write("Legalább egy igetípust ki kell választanod.")
elif len(irreg_selector) == 0 and len(conjugation_selector) == 0:
    st.write("Legalább egy coniugatiót vagy rendhagyó igét ki kell választanod.")
elif len(verb_vocab) == 0:
    st.write("A kiválasztott beállításokkal nincs olyan ige, amelyből kérdést lehetne generálni.")

else:

    def gen_ptc_id():
        conj_random = random.choice(conjugation_selector + (["irreg"] if irreg_selector else []))
        # st.write(conj_random)
        avail_verbs = [v for v,i in verb_vocab.items() if (i["conj"] == conj_random or (conj_random == 3 and i["conj"] == "3io")) and v not in irreg_selector] if conj_random != "irreg" else [v for v in irreg_selector if v in verb_vocab]
        # st.write(avail_verbs)

        if len(avail_verbs) > 0:
            verb = random.choice(avail_verbs)
        else:
            verb = random.choice(list(verb_vocab.keys()))
        avail_ptc = list(ptc_selector)

        # does the selected verb not have a PAP?
        if "pap" in verb_vocab[verb] and verb_vocab[verb].get("pap") is None:
            if "pap" in avail_ptc:
                avail_ptc.remove("pap")
        # Does the selected verb not have a PPP?
        if "ppp" not in verb_vocab[verb]:
            if "ppp" in avail_ptc:
                avail_ptc.remove("ppp")
        # Does the selected verb have neither a PPP nor a FAP form?
        if all(ptc not in verb_vocab[verb] for ptc in ["fap","ppp"]) or ("fap" in verb_vocab[verb] and verb_vocab[verb].get("fap") is None):
            if "fap" in avail_ptc:
                avail_ptc.remove("fap")
        # Does the selected verb have no gerundive?
        if "gdv" in verb_vocab[verb] and verb_vocab[verb].get("gdv") is None:
            if "gdv" in avail_ptc:
                avail_ptc.remove("gdv")
        # Does the selected verb not have passive forms?
        if verb_vocab[verb].get("no_pass"):
            if "ppp" in avail_ptc:
                avail_ptc.remove("ppp")
        # st.write(avail_ptc)
        # If there are no options left in the participle selector, we've got a problem.
        if len(avail_ptc) == 0:
            return

        ptc_type = random.choice(avail_ptc)

        if verb_vocab[verb].get("impers_pass_only") and ptc_type in ["ppp","gdv"]:
            gender = "n"
            number = "sg"
            case = "nom"
        else:
            gender = random.choice(adj_options["gender"])
            number = random.choice(adj_options["number"])
            case = random.choice(adj_options["case"])

        return [verb, ptc_type, gender, number, case]

    ## ADAPTIVE LEARNING ALGORITHM ##

    def adap_gen_ptc_id():
        avail_ptc = list(ptc_selector)
        avail_verbs = list(verb_vocab.keys())

        dfs = {}
        verb = ptc_type = case = number = gender = None
        recent_words = []
        roll_again = False

        if questions_asked and len([item for item in questions_asked if item["pos"] == "verbal adj." and "correct" in item]) > 0:

            ptc_df = pd.json_normalize([item for item in questions_asked if item["pos"] == "verbal adj." and "correct" in item]).replace({None: "-", pd.NA: "-", "nan": "-", "None": "-"})
            # Historical vocative answers must not enter adaptive sampling.
            ptc_df = ptc_df[ptc_df["id.case"].isin(adj_options["case"])]
#            st.write(ptc_df)
            dfs["ptc_df"] = ptc_df

            if len(ptc_df) > 0:
                ptc_df_wrong_indiv = ptc_df.copy().query("`id.ptc_type` in @avail_ptc") \
                    .assign(**{"id.conj": lambda df: df["id.conj"].where(~df["id.irreg"].isin(["irreg"]), df["word"])}) \
                    .query(f"`id.conj` in {[str(conj) for conj in selected_conjugations]} or word in @irreg_selector") \
                    .drop("word", axis=1) \
                    .groupby([col for col in ptc_df.columns if col not in ["pos", "answer", "correct", "word"]]) \
                    .agg(num_correct=("correct","sum"),total_q=("correct","count")) \
                    .assign(pct_wrong = lambda df: (df["total_q"]-df["num_correct"])/df["total_q"]) \
                    .assign(weight = lambda df: ((df["total_q"]-df["num_correct"])/(df["num_correct"]+1))**0.5) \
                    .query("pct_wrong > 0") #\
                    # .query("word in @avail_verbs")
                ptc_df_wrong_agg = ptc_df.copy().query("`id.ptc_type` in @avail_ptc") \
                    .assign(**{"id.conj": lambda df: df["id.conj"].where(~df["id.irreg"].isin(["irreg"]), df["word"])}) \
                    .query(f"`id.conj` in {[str(conj) for conj in selected_conjugations]} or word in @irreg_selector") \
                    .query(f"`id.conj` in {list(ptc_df_wrong_indiv.index.get_level_values("id.conj"))}") \
                    .groupby(["id.ptc_type","id.conj","id.irreg"]) \
                    .agg(num_correct=("correct","sum"),total_q=("correct","count")) \
                    .assign(pct_wrong = lambda df: (df["total_q"]-df["num_correct"])/df["total_q"]) \
                    .assign(weight = lambda df: ((df["total_q"]-df["num_correct"])/(df["num_correct"]+1))**0.5) \
                    .query("pct_wrong > 0")
                if len(ptc_df_wrong_indiv) > 0:
                    dfs["ptc_df_wrong_indiv"] = ptc_df_wrong_indiv
                    dfs["ptc_df_wrong_agg"] = ptc_df_wrong_agg

                # st.write("incorrect answers:",ptc_df_wrong_indiv)
                # st.write("aggregated incorrect answers:",ptc_df_wrong_agg)

                recent = min(len(avail_verbs)-1,3)
                recent_words = list(ptc_df.tail(recent)["word"].values) if recent > 0 else []
                # st.write(recent_words)
        if "ptc_df_wrong_agg" in dfs and ptc_df_wrong_agg["weight"].max() >= .58:
            repeat_chance = random.choices(["new","repeat"],[st.session_state["adap_learning_frequency"],1])[0]   # 1 in 3 chance of repeated question
            if repeat_chance == "repeat" and len(ptc_df) > 5:
                roll_again = False
                # st.write("repeat!")
                ptc_type_conj = ptc_df_wrong_agg.query("weight >= .58")["weight"].sample(n=1, weights=ptc_df_wrong_agg.query("weight >= .58")["weight"]).index[0]
                # st.write("ptc. type, conjugation/verb, irregular?",ptc_type_conj)

                conj = ptc_type_conj[1]
                ptc_type = ptc_type_conj[0]
                # st.write("Participle type:",ptc_type)
                if ptc_type in avail_ptc:
                    if conj == "-":
                        conj = None
                        verb = None
                    elif conj in avail_verbs:
                        verb = conj
                        conj = complete_verb_vocab[verb].get("conj")
                    else:
                        try:
                            conj = ast.literal_eval(conj)
                        except:
                            pass
                        verb = None

                    if verb and verb in avail_verbs: # specific irregular participial verb form that needs review

                        # st.write("verb:", verb)
                        pass
                        # have ptc type and verb; need to assign case/number/gender
                    else:
                        if (isinstance(conj, (int,str)) or conj is None) and conj in [ptc_info.get("conj") for ptc_info in verb_vocab.values()]:
                            # st.write("conjugation:",conj)

                            curr_avail_verbs = {k:v for k,v in verb_vocab.items() if v["conj"] == conj}
                            if "fīō" in irreg_selector and "semidep" in voice_selector and conj in [3,"3io"] and any(ptc in ptc_selector for ptc in ["gdv","ppp"]):
                                curr_avail_verbs["fīō"] = complete_verb_vocab["fīō"]
                            # st.write(curr_avail_verbs.keys())
                            # assign random new verb in conjugation
                        else:
                            # st.write("No matches to draw from, spin the conjugation wheel.")
                            curr_avail_verbs = {k:v for k,v in verb_vocab.items()}
                            # assign random new verb in ptc. type, unless only incompatible options selected
                        if ptc_type == "pap":
                            curr_avail_verbs = {v:i for v,i in curr_avail_verbs.items() if not ("pap" in i and i.get("pap") is None)}
                        elif ptc_type == "ppp":
                            curr_avail_verbs = {v:i for v,i in curr_avail_verbs.items() if "ppp" in i}
                        elif ptc_type == "fap":
                            curr_avail_verbs = {v:i for v,i in curr_avail_verbs.items() if not all(ptc not in i for ptc in ["fap","ppp"]) and not ("fap" in i and i.get("fap") is None)}
                        else: # ptc_type == "gdv"
                            curr_avail_verbs = {v:i for v,i in curr_avail_verbs.items() if not ("gdv" in i and i.get("gdv") is None)}

                        # st.write(curr_avail_verbs.keys())
                        if len(curr_avail_verbs) > 0:
                            verb = random.choice(list(curr_avail_verbs.keys()))
                            # st.write("verb:", verb)
                        else:
                            ptc_type = None

                    if ptc_type:
                        ptc_df_wrong_indiv_filtered = ptc_df_wrong_indiv.query(f"`id.ptc_type` == @ptc_type and `id.conj` in {[str(conj),verb]} and weight > 1.7")
                        # st.write(ptc_df_wrong_indiv_filtered)
                        if not ptc_df_wrong_indiv_filtered.empty:
                            ptc_weight = ptc_df_wrong_indiv_filtered.xs(ptc_type_conj,level=("id.ptc_type","id.conj","id.irreg"))["weight"]
                        else:
                            ptc_weight = None
                        # st.write("ptc_weight assigned:",ptc_weight)
                        if ptc_weight is not None:
                            ptc_id = ptc_weight.sample(n=1, weights=ptc_weight).index[0]
                            # st.write(ptc_id)
                            if ptc_id is not None:
                                gender, number, case = ptc_id
                        if not gender:
                            if verb_vocab[verb].get("impers_pass_only") and ptc_type in ["ppp","gdv"]:
                                gender = "n"
                                number = "sg"
                                case = "nom"
                            else:
                                gender = random.choice(adj_options["gender"])
                                number = random.choice(adj_options["number"])
                                case = random.choice(adj_options["case"])
                else:
                    ptc_type = None

                # Keep any recovered historical case within the current practice options.
                if case not in adj_options["case"] and case is not None:
                    case = random.choice(adj_options["case"])

                # st.write("repeat question:", verb, ptc_type, case, number, gender)
                last_q = [item for item in questions_asked if item["pos"] == "verbal adj." and "correct" in item][-1]
                if verb == last_q["word"] and ptc_type == last_q["id"]["ptc_type"] and case == last_q["id"]["case"] and number == last_q["id"]["number"] and gender == last_q["id"]["gender"]:
                    roll_again = True
                    # st.write("This is the same as last time.")

        if not ptc_type or roll_again is True:
            roll_again = True
            ptc_id = None
            while roll_again is True:
                while ptc_id is None:
                    ptc_id = gen_ptc_id()
                verb = ptc_id[0]
                # st.write("recent words:", recent_words)
                if set(recent_words) != set(avail_verbs) and not set(avail_verbs).issubset(set(recent_words)):
                    if verb not in recent_words:
                        # st.write("This is a new verb.")
                        roll_again = False
                    else:
                        # st.write("Resetting ID for next roll.")
                        ptc_id = None
                else:
                    roll_again = False
                    # st.write("This isn't a new word.")
            # st.write("new question:", verb, ptc_type, gender, number, case)

            verb, ptc_type, gender, number, case = ptc_id
            # st.write(ptc_id)
        return [verb, ptc_type, gender, number, case]

#    adap_gen_ptc_id()

    ## CREATE THE QUIZ ##

    def build_ptc(ptc_id=None):

        if ptc_id:
            pass
        else:
            i = 0
            while ptc_id is None and i < 5:
                ptc_id = adap_gen_ptc_id()
                i += 1

        if ptc_id is None:
            st.session_state.question_generation_error_message = ":warning: A megadott beállításokkal nem sikerült kérdést generálni. Módosítsd a beállításokat, majd kattints ismét az **Új kérdés** gombra."
            return

        verb, ptc_type, gender, number, case = ptc_id
        conj = complete_verb_vocab[verb]["conj"]

        verb_info = complete_verb_vocab[verb]
        ptc_form = ""
        irreg_form = False

        # Assign principal parts for use in question string.
        verb_principal_parts = {1: verb,
                                2: None,
                                3: None,
                                4: None}

        if verb_info["voice"] == "act":
            verb_principal_parts[3] = verb_info["perf"] + "ī"
            if verb_info.get("ppp"):
                verb_principal_parts[4] = verb_info["ppp"] + "um"
            elif verb_info.get("fap"):
                verb_principal_parts[4] = "[" + verb_info["fap"] + "us]"
        else:
            verb_principal_parts[3] = verb_info["ppp"] + "us sum"
            verb_principal_parts.pop(4)
        pres_inf = ""

        if verb_info.get("irreg"):
            # If there's an irregular present active/deponent infinitive, grab it now.
            if verb_info["irreg"].get("forms", {}).get("pres"):
                for temp_voice in ["act","dep"]:
                    if verb_info["irreg"]["forms"]["pres"].get(temp_voice,{}).get("inf"):
                        pres_inf = verb_info["irreg"]["forms"]["pres"][temp_voice]["inf"]

        if not pres_inf:
            pres_stem = verb_info.get("pres")
            thematic_vowel = verb_vowels["inf"].get(conj)
            pres_act_inf = pres_stem + thematic_vowel + "re"
            if verb_info["voice"] in ["act","semidep"]:
                pres_inf = pres_act_inf
            if verb_info["voice"] == "dep":
                if conj in [3,"3io"]:
                    pres_inf = pres_stem + "ī"
                else:
                    pres_inf = pres_stem + thematic_vowel + "rī"

        verb_principal_parts[2] = pres_inf
        if verb == "eō":
            verb_principal_parts[3] += "/iī"


        # Assign/create verbal adjective forms

        ptc_stem = ""
        ptc_nom = ""
        if ptc_type in ["pap", "gdv"]:
            if ptc_type == "pap" and "pap" in verb_info:
                irreg_form = True
                ptc_nom = verb_info["pap"][0]
                ptc_stem = verb_info["pap"][1]
            elif ptc_type == "gdv" and "gdv" in verb_info:
                irreg_form = True
                ptc_stem = verb_info["gdv"]
            ptc_vowel = verb_vowels["pap_gdv"].get(conj)
            if ptc_type == "pap" and not ptc_nom:
                ptc_nom = ptc_stem if ptc_stem else verb_info["pres"] + ptc_vowel + "ns"
            if not ptc_stem:
                ptc_stem = verb_info["pres"]
                if ptc_type == "gdv":
                    ptc_stem += remove_macrons(ptc_vowel) + "nd"
                else:
                    ptc_stem += remove_macrons(ptc_vowel) + "nt"

        else:
            if "ppp" in verb_info:
                ptc_stem = verb_info["ppp"]
            if ptc_type == "fap":
                if "fap" in verb_info:
                    ptc_stem = verb_info["fap"]
                else:
                    ptc_stem += "ūr"

        if ptc_type == "pap":
            if number == "sg" and (case in ["nom","voc"] or (case == "acc" and gender == "n")) :
                ptc_form = ptc_nom
            else:
                if gender in ["m","f"]:
                    ptc_ending = adj_endings[3][number][case]
                else:
                    ptc_ending = adj_endings["3_neut"][number][case]
                if isinstance(ptc_ending, list):
                    ptc_form = [ptc_stem + ending for ending in ptc_ending]
                else:
                    ptc_form = ptc_stem + ptc_ending

        else:
            if gender == "f":
                ptc_ending = adj_endings[1][number][case]
            elif gender == "m":
                ptc_ending = adj_endings["2_us"][number][case]
            else:
                ptc_ending = adj_endings["2_neut"][number][case]
            ptc_form = ptc_stem + ptc_ending


        curr_question = {
                "pos": "verbal adj.",
                "word": verb,
                "id": {
                    "ptc_type": ptc_type,
                    "gender": gender,
                    "number": number,
                    "case": case,
                    "conj": str(conj),
                    "irreg": "irreg" if irreg_form is True else None
                }
            }
        if verb == "fīō":
            curr_question["id"]["conj"] = "3io"
        elif verb == "eō" and ptc_type in ["pap","gdv"]:
            curr_question["id"]["conj"] = None

        if st.session_state.append_answer is True:
            questions_asked.append(
                curr_question
            )
            st.session_state.append_answer = False

        return [ptc_form, ptc_id, verb_principal_parts]

    st.session_state.gen_func = build_ptc

    ## CREATE QUIZ ##

    if st.session_state.current_question:
        correct_answer, ptc_id, verb_pp = st.session_state.current_question
        verb, ptc_type, gender, number, case = ptc_id

        st.session_state["correct_answer"] = correct_answer

        verb_label = verb
        if show_principal_parts:
            verb_label = verb_dictionary_entry(
                verb, verb_pp, show_full_regular_first=full_regular_first_entry
            )

        # Match the typography and placement of the question on the Igék page.
        form_label = (
            f"{abbrevs[ptc_type]}, {abbrevs[number]} "
            f"{abbrevs[case]} {abbrevs[gender]}"
        )
        question_html = (
            f'Képezd {hungarian_article(verb)} '
            f'<strong><em>{html.escape(verb_label)}</em></strong> ige következő alakját: '
            f'<strong>{html.escape(form_label)}</strong>!'
        )

        stems = verb_stem_display(verb) if show_stems else []
        prompt_space = st.container(height=114 if stems else 82, border=False)
        with prompt_space:
            st.markdown(
                f'<div style="margin-top:0.75rem;font-size:1.75rem;line-height:1.25;">{question_html}</div>',
                unsafe_allow_html=True,
            )
            if stems:
                stems_html = ", ".join(f"<em>{html.escape(stem)}-</em>" for stem in stems)
                irregular = bool(complete_verb_vocab[verb].get("irreg", {}).get("irreg"))
                stem_label = (
                    "Szabályos tő:" if len(stems) == 1 else "Szabályos tövek:"
                ) if irregular else "A tövek:"
                st.markdown(
                    f'<div style="font-size:1.05rem;line-height:1.35;margin-top:0.35rem;">{stem_label} {stems_html}.</div>',
                    unsafe_allow_html=True,
                )

        ## DISPLAY ANSWER FORM ##
        with st.form(key="ptc_form", clear_on_submit=True):
            current_answer = st.text_input("Válaszod:", key="answer_input")
            st.form_submit_button(
                "Válasz ellenőrzése",
                key="form_submission_button",
                on_click=submit_ptc_answer,
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
            st.button(new_q_button_text, on_click=new_question, args=(build_ptc,), key="question_button", width="stretch", type=new_q_button_type)

        with results_col:
            if st.session_state.current_question and st.session_state.answer_checked and "Incorrect" in st.session_state.result_message:
                starting_form = list(st.session_state.current_question[1])
                next_form = list(starting_form)
                help_text = "Ehhez az alakhoz nem jeleníthető meg ragozási táblázat." if (starting_form[1] in ["ppp","gdv"] and complete_verb_vocab[starting_form[0]].get("impers_pass_only") is True) else None

                chart_popover = st.popover("Ragozási táblázat", type="primary", help=help_text, width="stretch")
                with chart_popover:
                    if not (starting_form[1] in ["ppp","gdv"] and complete_verb_vocab[starting_form[0]].get("impers_pass_only") is True):
                        st.caption("Ez a funkció még fejlesztés alatt áll.")
                        st.caption("Az esetek sorrendjét a navigációs menüben állíthatod be.")

                        vb_adj_table = {}
                        table_index = []
                        cs_order = [case for case in st.session_state.case_order if case in adj_options["case"]]

                        for num in ["sg","pl"]:
                            for gd in ["m","f","n"]:
                                vb_adj_table[(num, gd)] = []
                                for cs in cs_order:
                                    if cs not in table_index:
                                        table_index.append(cs)
                                    next_form[-1] = cs
                                    next_form[-2] = num
                                    next_form[-3] = gd

                                    try:
                                        form = build_ptc(next_form)[0]
                                        if isinstance(form, list):
                                            form = "/".join(form)
                                        if next_form == starting_form:
                                            form = f":green-background[{form}]"
                                    except:
                                        form = None
                                    vb_adj_table[(num, gd)].append(form if form is not None else "--")

                        display_table = pd.DataFrame(vb_adj_table, table_index)
                        st.table(display_table)



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
