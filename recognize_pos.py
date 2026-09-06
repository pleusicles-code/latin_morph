import random
import time
from datetime import datetime as dt, timezone

import streamlit as st

from utils import clear_page, new_question, reset, save_defaults, clear_defaults
from vocab import import_nouns, import_adjectives, import_verbs


st.set_page_config("Latin Morph! Recognize Part of Speech", layout="centered")

page_id = "recognize_pos"
clear_page(page_id)
questions_asked = st.session_state.question_list
defaults = st.session_state.default_settings.get(f"{page_id}.py", {})

noun_vocab = import_nouns()
adjective_vocab = import_adjectives()
verb_vocab = import_verbs()

PARTS_OF_SPEECH = ["noun", "adjective", "verb"]

st.markdown("# Recognize Part of Speech")


# --- Dictionary-entry builders -------------------------------------------------

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

    # -er adjectives need their full nominative set to reveal the stem.
    # 1st/2nd-declension entries store only lemma + stem in vocab.py.
    if decl == (1, 2) and adjective.endswith("er") and adjective != "pauper":
        stem = data["stem"]
        return f"{adjective}, {stem}a, {stem}um"

    # 3rd-declension -er adjectives already store all three nominatives.
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

    # Defensive fallback for any future adjective subtype.
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

    # Regular first-conjugation active verbs are deliberately abbreviated.
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
    # Exclude nouns whose singular genitive is explicitly unavailable
    # (e.g. vīs), since this exercise teaches the standard dictionary-entry pattern.
    return data.get("irreg", {}).get("sg", {}).get("gen", "__regular__") is not None


def adjective_has_beginner_dictionary_entry(data):
    # Exclude one-termination 3rd-declension adjectives (e.g. vetus, ingēns).
    # This beginner exercise uses only adjective entries that visibly distinguish
    # at least the neuter nominative from the masculine/feminine form.
    if data.get("decl") == 3:
        noms = data.get("noms")
        return bool(noms and len(noms) >= 2)
    return True


def verb_has_beginner_dictionary_entry(data):
    # Exclude genuinely irregular verbs such as sum, possum, ferō, etc.
    # Verbs with only isolated irregular forms (e.g. dīcō, dūcō) remain eligible.
    return data.get("irreg", {}).get("irreg") is not True


VOCABULARIES = {
    "noun": {word: data for word, data in noun_vocab.items() if noun_has_beginner_dictionary_entry(data)},
    "adjective": {word: data for word, data in adjective_vocab.items() if adjective_has_beginner_dictionary_entry(data)},
    "verb": {word: data for word, data in verb_vocab.items() if verb_has_beginner_dictionary_entry(data)},
}


# --- Settings ------------------------------------------------------------------

option_expander = st.expander("Settings", expanded=True)
with option_expander:
    selected_pos = st.multiselect(
        "Choose which parts of speech to practice (they are all selected by default):",
        options=PARTS_OF_SPEECH,
        default=defaults.get("selected_pos") if defaults.get("selected_pos") is not None else PARTS_OF_SPEECH,
        key="recognize_pos_selected_pos",
    )

    if st.user.is_logged_in:
        set_defaults_col, clear_defaults_col = st.columns(2)
        with set_defaults_col:
            st.button(
                "Save settings",
                type="primary",
                width="stretch",
                help="Save your current part-of-speech selection as your default.",
                on_click=save_defaults,
                args=(page_id, defaults),
                kwargs={"selected_pos": selected_pos},
            )

        with clear_defaults_col:
            generic_settings = {"selected_pos": PARTS_OF_SPEECH}
            current_settings = {"selected_pos": selected_pos}
            settings_changed = current_settings != generic_settings

            def reset_recognition_defaults():
                clear_defaults(page_id)
                st.session_state.recognize_pos_selected_pos = list(PARTS_OF_SPEECH)

            st.button(
                "Reset defaults",
                type="primary",
                width="stretch",
                help="Restore the generic Latin Morph! default settings for this exercise.",
                on_click=reset_recognition_defaults,
                disabled=not defaults and not settings_changed,
            )


# --- Question generation and checking -----------------------------------------

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

    return {
        "pos": pos,
        "word": word,
        "entry": ENTRY_BUILDERS[pos](word),
        "qid": random.getrandbits(64),
    }


def start_new_question():
    new_question(gen_question)


def check_recognition_answer(answer_key):
    answer = st.session_state.get(answer_key)
    if not answer or st.session_state.answer_checked:
        return

    correct_answer = st.session_state.current_question["pos"]
    correct = answer == correct_answer

    st.session_state.answer_checked = True
    st.session_state.button_disable = True
    st.session_state.total_questions += 1
    if correct:
        st.session_state.current_score += 1
        st.session_state.result_message = "**Good job!**"
    else:
        st.session_state.result_message = "**Incorrect. Better luck next time!**"

    feedback_color = "green" if correct else "red"
    st.session_state.answer_display_message = (
        f":{feedback_color}-background[Your answer is: {answer}]  \n"
        f":{feedback_color}-background[The correct answer is: {correct_answer}]"
    )

    record = {
        "pos": "recognize_pos",
        "word": st.session_state.current_question["word"],
        "answer": answer,
        "correct": correct,
        "id": {"target_pos": correct_answer},
    }
    questions_asked.append(record)

    if st.user.is_logged_in:
        insert_dict = {
            "user_id": str(st.session_state.user_id),
            "time_answered": dt.now(timezone.utc).isoformat(),
            "answer": record,
        }
        st.session_state.supabase_connection.table("answer").insert(insert_dict).execute()

    st.session_state.auto_advance_trigger = bool(st.session_state.auto_advance)


def choose_recognition_answer(answer_key):
    # Give the learner one second to register the selected radio option visually,
    # then evaluate it automatically.
    time.sleep(1)
    check_recognition_answer(answer_key)


st.session_state.gen_func = gen_question

if not selected_pos and not st.session_state.current_question:
    st.write("You need to choose at least one part of speech.")

if st.session_state.current_question:
    question = st.session_state.current_question
    answer_key = f"recognize_pos_answer_{question['qid']}"

    st.markdown("### Current question")
    st.markdown(f"Which part of speech is *{question['entry']}*?")

    st.radio(
        "Choose one:",
        options=PARTS_OF_SPEECH,
        index=None,
        key=answer_key,
        horizontal=True,
        disabled=st.session_state.answer_checked,
        on_change=choose_recognition_answer,
        args=(answer_key,),
    )
    st.markdown(st.session_state.answer_display_message)

new_question_col, results_col, score_col = st.columns(3)

with new_question_col:
    button_text = "New Question" if st.session_state.question_list else "Click here for your first question!"
    button_type = "secondary" if st.session_state.question_list else "primary"
    st.button(
        button_text,
        on_click=start_new_question,
        key="recognize_pos_question_button",
        width="stretch",
        disabled=not selected_pos,
        type=button_type,
    )

with results_col:
    st.markdown(st.session_state.result_message)

with score_col:
    st.button("Reset Score", "recognize_pos_reset", on_click=reset, width="stretch")
    st.markdown(f"Current score: **{st.session_state.current_score}** out of **{st.session_state.total_questions}**")

if st.session_state.auto_advance_trigger and st.session_state.answer_checked:
    time.sleep(st.session_state.auto_advance)
    new_question(gen_question)
    st.rerun()
