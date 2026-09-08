import random
import time
import unicodedata
from datetime import datetime as dt, timezone

import streamlit as st

from utils import clear_page, new_question, reset, save_defaults, clear_defaults, auto_advance_delay
from exercise_presets import (list_setting, resolve_exercise_settings, initialize_widget_state,
                              widget_key, url_preset_active, exercise_link_popover)
from vocab import import_nouns, import_adjectives, import_verbs


st.set_page_config("BevLat – Szófaj felismerése", layout="centered")

page_id = "recognize_pos"
new_run = st.session_state.curr_page_id != page_id
clear_page(page_id)
if new_run or "recognize_pos_selected_answer" not in st.session_state:
    st.session_state.recognize_pos_selected_answer = None
questions_asked = st.session_state.question_list
defaults = st.session_state.default_settings.get(f"{page_id}.py", {})

noun_vocab = import_nouns()
adjective_vocab = import_adjectives()
verb_vocab = import_verbs()

PARTS_OF_SPEECH = ["noun", "adjective", "verb"]
POS_LABELS = {
    "noun": "főnév",
    "adjective": "melléknév",
    "verb": "ige",
}
ANSWER_CHECK_DELAY = 0.0

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


exercise_schema = {
    "selected_pos": list_setting(PARTS_OF_SPEECH, PARTS_OF_SPEECH),
}
exercise_settings = resolve_exercise_settings(page_id, exercise_schema, defaults)
initialize_widget_state(page_id, exercise_settings)
preset_active = url_preset_active(page_id)

st.markdown("# Szófaj felismerése")


def noun_dictionary_entry(noun):
    data = noun_vocab[noun]
    irreg_gen = data.get("irreg", {}).get("sg", {}).get("gen", "__regular__")
    if irreg_gen == "__regular__":
        decl = data["decl"]
        stem = data["stem"]
        if decl == 1:
            genitive = stem + "ae"
        elif str(decl).startswith("2"):
            genitive = stem + "ī"
        elif str(decl).startswith("3"):
            genitive = stem + "is"
        elif str(decl).startswith("4"):
            genitive = stem + "ūs"
        elif decl == "5_vowel":
            genitive = stem + "ēī"
        elif decl == "5_consonant":
            genitive = stem + "eī"
        else:
            genitive = None
    else:
        genitive = irreg_gen
    if isinstance(genitive, list):
        genitive = "/".join(genitive)
    if genitive:
        return f"{noun}, {genitive} {data['gender']}."
    return f"{noun} {data['gender']}."


def adjective_dictionary_entry(adjective):
    data = adjective_vocab[adjective]
    decl = data.get("decl")
    noms = data.get("noms")
    if decl == (1, 2) and adjective.endswith("er") and adjective != "pauper":
        stem = data["stem"]
        return f"{adjective}, {stem}a, {stem}um"
    if noms and len(noms) == 3 and str(noms[0]).endswith("er"):
        return ", ".join(noms)
    if decl == (1, 2):
        return f"{adjective} 3"
    if decl == 3:
        if noms:
            if len(noms) == 3:
                return ", ".join(noms)
            if len(noms) == 2:
                return f"{adjective} 2"
            if len(noms) == 1:
                return f"{adjective} 1"
        return f"{adjective} 1"
    return adjective


def regular_present_infinitive(verb, data):
    conj = data.get("conj")
    stem = data.get("pres")
    voice = data.get("voice")
    if not stem or conj is None:
        return None
    if voice == "dep":
        if conj == 1:
            return stem + "ārī"
        if conj == 2:
            return stem + "ērī"
        if conj in [3, "3io"]:
            return stem + "ī"
        if conj == 4:
            return stem + "īrī"
    else:
        if conj == 1:
            return stem + "āre"
        if conj == 2:
            return stem + "ēre"
        if conj in [3, "3io"]:
            return stem + "ere"
        if conj == 4:
            return stem + "īre"
    return None


def irregular_present_infinitive(data):
    pres_forms = data.get("irreg", {}).get("forms", {}).get("pres", {})
    for voice in ["act", "dep", "pass"]:
        infinitive = pres_forms.get(voice, {}).get("inf")
        if infinitive:
            if isinstance(infinitive, list):
                return "/".join(infinitive)
            return infinitive
    return None


def verb_dictionary_entry(verb):
    data = verb_vocab[verb]
    conj = data.get("conj")
    conj_label = 3 if conj == "3io" else conj
    genuinely_irregular = data.get("irreg", {}).get("irreg") is True
    voice = data.get("voice")
    if genuinely_irregular:
        infinitive = irregular_present_infinitive(data) or regular_present_infinitive(verb, data)
        parts = [verb]
        if infinitive:
            parts.append(infinitive)
        if voice == "act":
            if data.get("perf"):
                parts.append(data["perf"] + "ī")
            if data.get("ppp"):
                parts.append(data["ppp"] + "um")
        elif data.get("ppp"):
            parts.append(data["ppp"] + "us sum")
        return ", ".join(parts)
    if conj == 1 and voice == "act":
        return f"{verb} 1"
    if voice == "act":
        parts = [f"{verb} {conj_label}"]
        if data.get("perf"):
            parts.append(data["perf"] + "ī")
        if data.get("ppp"):
            parts.append(data["ppp"] + "um")
        return parts[0] + (" " + ", ".join(parts[1:]) if len(parts) > 1 else "")
    if data.get("ppp"):
        return f"{verb} {conj_label} {data['ppp']}us sum"
    return f"{verb} {conj_label}"


ENTRY_BUILDERS = {
    "noun": noun_dictionary_entry,
    "adjective": adjective_dictionary_entry,
    "verb": verb_dictionary_entry,
}


def noun_has_beginner_dictionary_entry(data):
    return data.get("irreg", {}).get("sg", {}).get("gen", "__regular__") is not None


def adjective_has_beginner_dictionary_entry(data):
    if data.get("cardinal") is True:
        return False
    if data.get("decl") == 3:
        noms = data.get("noms")
        return bool(noms and len(noms) >= 2)
    return True


def verb_has_beginner_dictionary_entry(data):
    if data.get("irreg", {}).get("irreg") is True:
        return False
    return data.get("voice") not in ["dep", "semidep"]


VOCABULARIES = {
    "noun": {word: data for word, data in noun_vocab.items() if noun_has_beginner_dictionary_entry(data)},
    "adjective": {word: data for word, data in adjective_vocab.items() if adjective_has_beginner_dictionary_entry(data)},
    "verb": {word: data for word, data in verb_vocab.items() if verb_has_beginner_dictionary_entry(data)},
}


option_expander = st.expander("Beállítások", expanded=True)
with option_expander:
    selected_pos = st.multiselect(
        "Válaszd ki, mely szófajokat szeretnéd gyakorolni (alapértelmezés szerint mindegyik ki van választva):",
        options=PARTS_OF_SPEECH,
        format_func=lambda x: POS_LABELS[x],
        key=widget_key(page_id, "selected_pos"),
    )
    current_settings = {"selected_pos": selected_pos}
    if st.user.is_logged_in:
        set_defaults_col, clear_defaults_col, link_col = st.columns(3)
        with set_defaults_col:
            st.button(
                "Beállítások mentése", type="primary", width="stretch",
                help="A jelenlegi szófajválasztás mentése alapértelmezett beállításként.",
                on_click=save_defaults, args=(page_id, defaults), kwargs=current_settings,
                disabled=preset_active,
            )
        with clear_defaults_col:
            generic_settings = {"selected_pos": PARTS_OF_SPEECH}
            settings_changed = current_settings != generic_settings
            def reset_recognition_defaults():
                clear_defaults(page_id)
                st.session_state.recognize_pos_selected_pos = list(PARTS_OF_SPEECH)
            st.button(
                "Alapbeállítások", type="primary", width="stretch",
                help="A BevLat általános alapértelmezett beállításainak visszaállítása ehhez a feladathoz.",
                on_click=reset_recognition_defaults,
                disabled=preset_active or (not defaults and not settings_changed),
            )
        with link_col:
            exercise_link_popover(page_id, exercise_schema, current_settings)
    else:
        exercise_link_popover(page_id, exercise_schema, current_settings)


def gen_question():
    if not selected_pos:
        return None
    pos = random.choice(selected_pos)
    word = random.choice(list(VOCABULARIES[pos].keys()))
    if st.session_state.current_question:
        previous = st.session_state.current_question
        attempts = 0
        while previous and previous.get("pos") == pos and previous.get("word") == word and attempts < 20:
            word = random.choice(list(VOCABULARIES[pos].keys()))
            attempts += 1
    return {"pos": pos, "word": word, "entry": ENTRY_BUILDERS[pos](word), "qid": random.getrandbits(64)}


def start_new_question():
    st.session_state.recognize_pos_selected_answer = None
    new_question(gen_question)


def check_recognition_answer(answer_key):
    answer = st.session_state.get(answer_key)
    if not answer or st.session_state.answer_checked:
        return
    st.session_state.pop("recognize_pos_pending_answer_key", None)
    st.session_state.pop("recognize_pos_check_after", None)
    correct_answer = st.session_state.current_question["pos"]
    correct = answer == correct_answer
    correct_answer_label = POS_LABELS[correct_answer]
    st.session_state.answer_checked = True
    st.session_state.button_disable = True
    st.session_state.total_questions += 1
    if correct:
        st.session_state.current_score += 1
        st.session_state.result_message = "**Helyes!**"
        st.session_state.answer_display_message = feedback_box("<strong>Helyes válasz!</strong>", "correct")
    else:
        st.session_state.result_message = "**Helytelen. Próbáld meg a következőt!**"
        st.session_state.answer_display_message = feedback_box(
            f"<strong>Helytelen válasz. A helyes válasz: {correct_answer_label}.</strong>",
            "incorrect",
        )
    record = {
        "pos": "recognize_pos", "word": st.session_state.current_question["word"],
        "answer": answer, "correct": correct, "id": {"target_pos": correct_answer},
    }
    questions_asked.append(record)
    if st.user.is_logged_in:
        insert_dict = {
            "user_id": str(st.session_state.user_id),
            "time_answered": dt.now(timezone.utc).isoformat(), "answer": record,
        }
        st.session_state.supabase_connection.table("answer").insert(insert_dict).execute()
    st.session_state.auto_advance_trigger = bool(st.session_state.auto_advance)


def choose_recognition_answer(answer_key, answer, answer_index):
    if st.session_state.answer_checked:
        return
    st.session_state[answer_key] = answer
    st.session_state.recognize_pos_selected_answer = answer_index
    st.session_state.recognize_pos_pending_answer_key = answer_key
    st.session_state.recognize_pos_check_after = time.monotonic() + ANSWER_CHECK_DELAY
    if ANSWER_CHECK_DELAY <= 0:
        check_recognition_answer(answer_key)


st.session_state.gen_func = gen_question

if not selected_pos and not st.session_state.current_question:
    st.write("Legalább egy szófajt ki kell választanod.")

if st.session_state.current_question:
    question = st.session_state.current_question
    answer_key = f"recognize_pos_answer_{question['qid']}"
    selected_answer_index = st.session_state.recognize_pos_selected_answer
    st.markdown("### Aktuális kérdés")
    prompt_space = st.container(height=52, border=False)
    with prompt_space:
        article = hungarian_article(question["word"])
        st.markdown(f"Milyen szófajú szó {article} ***{question['entry']}***?")
    if selected_answer_index is not None:
        st.html(f"""
            <style>
            .st-key-{answer_key}_option_{selected_answer_index} button {{
                background-color: rgba(128, 128, 128, 0.25) !important;
            }}
            </style>
            """)
    answer_columns = st.columns(len(PARTS_OF_SPEECH), gap="small")
    for answer_index, (answer_column, answer_option) in enumerate(zip(answer_columns, PARTS_OF_SPEECH)):
        with answer_column:
            st.button(
                POS_LABELS[answer_option], key=f"{answer_key}_option_{answer_index}",
                on_click=choose_recognition_answer, args=(answer_key, answer_option, answer_index),
                disabled=st.session_state.answer_checked, width="stretch",
            )
    feedback_space = st.container(height=90, border=False)
    with feedback_space:
        st.markdown(st.session_state.answer_display_message, unsafe_allow_html=True)

pending_answer_key = st.session_state.get("recognize_pos_pending_answer_key")
check_after = st.session_state.get("recognize_pos_check_after")
recognition_timer_interval = 0.2 if (
    ANSWER_CHECK_DELAY > 0 and pending_answer_key and not st.session_state.answer_checked
) else None

@st.fragment(run_every=recognition_timer_interval)
def recognition_check_timer():
    pending_key = st.session_state.get("recognize_pos_pending_answer_key")
    pending_time = st.session_state.get("recognize_pos_check_after")
    if pending_key and pending_time and not st.session_state.answer_checked and time.monotonic() >= pending_time:
        check_recognition_answer(pending_key)
        st.rerun()

recognition_check_timer()

control_row = st.container(height=92, border=False)
with control_row:
    new_question_col, results_col, score_col = st.columns(3, gap="medium", vertical_alignment="top")
    with new_question_col:
        button_text = "Új kérdés" if st.session_state.question_list else "Kattints ide az első kérdéshez!"
        button_type = "secondary" if st.session_state.question_list else "primary"
        st.button(
            button_text, on_click=start_new_question, key="recognize_pos_question_button",
            width="stretch", disabled=not selected_pos, type=button_type,
        )
    with results_col:
        st.container(height=48, border=False)
    with score_col:
        st.button("Pontszám nullázása", "recognize_pos_reset", on_click=reset, width="stretch")
        st.markdown(f"Jelenlegi pontszám: **{st.session_state.current_score}** / **{st.session_state.total_questions}**")

if not st.session_state.auto_advance:
    st.session_state.auto_advance_trigger = False

if st.session_state.auto_advance and st.session_state.auto_advance_trigger and st.session_state.answer_checked:
    time.sleep(auto_advance_delay())
    start_new_question()
    st.rerun()