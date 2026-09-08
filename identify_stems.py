import html
import random
import unicodedata
from datetime import datetime as dt, timezone

import streamlit as st
import streamlit.components.v1 as components

from utils import clear_page, new_question, remove_macrons, reset, save_defaults, clear_defaults
from exercise_presets import (list_setting, resolve_exercise_settings, initialize_widget_state,
                              widget_key, url_preset_active, exercise_link_popover)
from vocab import import_nouns, import_adjectives, import_verbs


st.set_page_config("Latin Morph! Identify Stems", layout="centered")

page_id = "identify_stems"
clear_page(page_id)
questions_asked = st.session_state.question_list
defaults = st.session_state.default_settings.get(f"{page_id}.py", {})

noun_vocab = import_nouns()
adjective_vocab = import_adjectives()
verb_vocab = import_verbs()

PARTS_OF_SPEECH = ["noun", "adjective", "verb"]

exercise_schema = {
    "selected_pos": list_setting(PARTS_OF_SPEECH, PARTS_OF_SPEECH),
}
exercise_settings = resolve_exercise_settings(page_id, exercise_schema, defaults)
initialize_widget_state(page_id, exercise_settings)
preset_active = url_preset_active(page_id)

st.markdown("# Identify Stems")


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


def verb_dictionary_entry(verb):
    data = verb_vocab[verb]
    conj = data.get("conj")
    conj_label = 3 if conj == "3io" else conj

    if conj == 1 and data.get("voice") == "act":
        return f"{verb} 1"

    parts = [f"{verb} {conj_label}"]
    if data.get("perf"):
        parts.append(data["perf"] + "ī")
    if data.get("ppp"):
        parts.append(data["ppp"] + "um")
    return parts[0] + (" " + ", ".join(parts[1:]) if len(parts) > 1 else "")


ENTRY_BUILDERS = {
    "noun": noun_dictionary_entry,
    "adjective": adjective_dictionary_entry,
    "verb": verb_dictionary_entry,
}


# --- Beginner-level vocabulary filters ----------------------------------------

def noun_has_beginner_dictionary_entry(word, data):
    # Keep deus, but otherwise exclude irregular nouns. Also exclude any noun
    # whose singular genitive is unavailable (e.g. vīs).
    if word != "deus" and data.get("irreg"):
        return False
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
    if data.get("voice") in ["dep", "semidep"]:
        return False
    # Every verb question requires all three stems.
    return bool(data.get("pres") and data.get("perf") and data.get("ppp"))


VOCABULARIES = {
    "noun": {word: data for word, data in noun_vocab.items() if noun_has_beginner_dictionary_entry(word, data)},
    "adjective": {word: data for word, data in adjective_vocab.items() if adjective_has_beginner_dictionary_entry(data)},
    "verb": {word: data for word, data in verb_vocab.items() if verb_has_beginner_dictionary_entry(data)},
}


# --- Settings ------------------------------------------------------------------

option_expander = st.expander("Settings", expanded=True)
with option_expander:
    selected_pos = st.multiselect(
        "Choose which parts of speech to practice (they are all selected by default):",
        options=PARTS_OF_SPEECH,
        key=widget_key(page_id, "selected_pos"),
    )

    current_settings = {"selected_pos": selected_pos}

    if st.user.is_logged_in:
        set_defaults_col, clear_defaults_col, link_col = st.columns(3)
        with set_defaults_col:
            st.button(
                "Save settings",
                type="primary",
                width="stretch",
                help="Save your current part-of-speech selection as your default.",
                on_click=save_defaults,
                args=(page_id, defaults),
                kwargs=current_settings,
                disabled=preset_active,
            )

        with clear_defaults_col:
            generic_settings = {"selected_pos": PARTS_OF_SPEECH}
            settings_changed = current_settings != generic_settings

            def reset_stem_defaults():
                clear_defaults(page_id)
                st.session_state.identify_stems_selected_pos = list(PARTS_OF_SPEECH)

            st.button(
                "Reset defaults",
                type="primary",
                width="stretch",
                help="Restore the generic Latin Morph! default settings for this exercise.",
                on_click=reset_stem_defaults,
                disabled=preset_active or (not defaults and not settings_changed),
            )

        with link_col:
            exercise_link_popover(page_id, exercise_schema, current_settings)
    else:
        exercise_link_popover(page_id, exercise_schema, current_settings)


# --- Answer normalization -------------------------------------------------------

def canonical_stem(stem):
    return unicodedata.normalize("NFC", stem.strip().rstrip("-.,").strip())


def parse_stem_answer(answer, expected_count):
    normalized = unicodedata.normalize("NFC", answer.strip())
    if expected_count == 1:
        return [canonical_stem(normalized)] if normalized else []

    # Commas and whitespace are both accepted as separators; trailing dashes
    # are optional. Canonical display always uses comma + space, without dashes.
    parts = [canonical_stem(part) for part in normalized.replace(",", " ").split()]
    return [part for part in parts if part]


def stems_equal(user_stem, correct_stem):
    user_check = remove_macrons(unicodedata.normalize("NFC", user_stem)).lower()
    correct_check = remove_macrons(unicodedata.normalize("NFC", correct_stem)).lower()
    if st.session_state.get("cons_u_normalize") is True:
        user_check = user_check.replace("v", "u")
        correct_check = correct_check.replace("v", "u")
    return user_check == correct_check


def canonical_display(parts):
    return ", ".join(parts)


def verb_feedback(user_parts, correct_parts, part_results, state):
    display_parts = list(user_parts[:len(correct_parts)])
    while len(display_parts) < len(correct_parts):
        display_parts.append("—")

    if state == "partial":
        background = "#fff4d6"
        border = "#e2c66d"
        label = "Your answers are partially correct:"
    else:
        background = "#f7dddd"
        border = "#d9a0a0"
        label = "Your answers are:"

    user_cells = []
    for i, part in enumerate(display_parts):
        if state == "partial":
            color = "#137333" if part_results[i] else "#b3261e"
        else:
            color = "#b3261e"
        user_cells.append(
            '<td style="padding:0 0.35rem;color:{color};font-weight:600;">{part}</td>'.format(
                color=color, part=html.escape(part)
            )
        )

    correct_cells = [
        '<td style="padding:0 0.35rem;">{}</td>'.format(html.escape(part))
        for part in correct_parts
    ]

    return (
        '<div style="background:{background};border:1px solid {border};border-radius:0.5rem;'
        'padding:0.55rem 0.75rem;line-height:1.6;">'
        '<table style="border-collapse:collapse;border:none;">'
        '<tr><td style="padding:0 0.6rem 0 0;white-space:nowrap;">{label}</td>{user}</tr>'
        '<tr><td style="padding:0 0.6rem 0 0;white-space:nowrap;">The correct answers are:</td>{correct}</tr>'
        '</table></div>'
    ).format(
        background=background,
        border=border,
        label=label,
        user="".join(user_cells),
        correct="".join(correct_cells),
    )


# --- Question generation and checking -----------------------------------------

def learner_present_stem(data):
    stem = data["pres"]
    conj = data.get("conj")
    if conj == 1:
        stem += "ā"
    elif conj == 2:
        stem += "ē"
    elif conj == "3io":
        stem += "i"
    elif conj == 4:
        stem += "ī"
    return canonical_stem(stem)


def correct_stems_for(pos, word):
    data = VOCABULARIES[pos][word]
    if pos in ["noun", "adjective"]:
        return [canonical_stem(data["stem"])]
    return [learner_present_stem(data), canonical_stem(data["perf"]), canonical_stem(data["ppp"])]


def gen_question():
    if not selected_pos:
        return None

    pos = random.choice(selected_pos)
    word = random.choice(list(VOCABULARIES[pos].keys()))

    if st.session_state.current_question:
        previous = st.session_state.current_question
        attempts = 0
        while previous and previous.get("target_pos") == pos and previous.get("word") == word and attempts < 20:
            word = random.choice(list(VOCABULARIES[pos].keys()))
            attempts += 1

    return {
        "target_pos": pos,
        "word": word,
        "entry": ENTRY_BUILDERS[pos](word),
        "correct_stems": correct_stems_for(pos, word),
        "qid": random.getrandbits(64),
    }


def start_new_question():
    new_question(gen_question)


def check_stem_answer(answer_key):
    raw_answer = st.session_state.get(answer_key, "")
    if not raw_answer.strip():
        st.session_state.answer_display_message = "Your answer was blank! Enter a stem and hit 'Check Answer', or click 'New Question' if you want to skip this one."
        st.session_state.button_disable = False
        return
    if st.session_state.answer_checked:
        return

    question = st.session_state.current_question
    target_pos = question["target_pos"]
    correct_parts = question["correct_stems"]
    user_parts = parse_stem_answer(raw_answer, len(correct_parts))

    part_results = []
    for i, correct_part in enumerate(correct_parts):
        part_results.append(i < len(user_parts) and stems_equal(user_parts[i], correct_part))

    fully_correct = len(user_parts) == len(correct_parts) and all(part_results)
    partially_correct = target_pos == "verb" and not fully_correct and any(part_results)

    st.session_state.answer_checked = True
    st.session_state.button_disable = True
    st.session_state.total_questions += 1
    if fully_correct:
        st.session_state.current_score += 1
        st.session_state.result_message = "**Good job!**"
    elif partially_correct:
        st.session_state.result_message = "**Partially correct.**"
    else:
        st.session_state.result_message = "**Incorrect. Better luck next time!**"

    normalized_user_display = canonical_display(user_parts)
    correct_display = canonical_display(correct_parts)

    if fully_correct:
        st.session_state.answer_display_message = (
            f":green-background[The correct answer is: {correct_display}]"
        )
    elif target_pos == "verb":
        feedback_state = "partial" if partially_correct else "incorrect"
        st.session_state.answer_display_message = verb_feedback(
            user_parts, correct_parts, part_results, feedback_state
        )
    else:
        st.session_state.answer_display_message = (
            f":red-background[Your answer is: {normalized_user_display}]  \n"
            f":red-background[The correct answer is: {correct_display}]"
        )

    answer_id = {"target_pos": target_pos}
    if target_pos == "verb":
        answer_id.update({
            "present_stem_correct": part_results[0],
            "perfect_stem_correct": part_results[1],
            "supine_stem_correct": part_results[2],
        })

    record = {
        "pos": "identify_stems",
        "word": question["word"],
        "answer": normalized_user_display,
        "correct": fully_correct,
        "id": answer_id,
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


st.session_state.gen_func = gen_question

if not selected_pos and not st.session_state.current_question:
    st.write("You need to choose at least one part of speech.")

if st.session_state.current_question:
    question = st.session_state.current_question
    answer_key = f"identify_stems_answer_{question['qid']}"

    st.markdown("### Current question")
    prompt_space = st.container(height=52, border=False)
    with prompt_space:
        if question["target_pos"] == "verb":
            st.markdown(f"What are the stems of *{question['entry']}*?")
        else:
            st.markdown(f"What is the stem of *{question['entry']}*?")

    with st.form(key=f"identify_stems_form_{question['qid']}"):
        st.text_input(
            "Your answer:",
            key=answer_key,
            disabled=st.session_state.answer_checked,
        )
        st.form_submit_button(
            "Check Answer",
            on_click=check_stem_answer,
            args=(answer_key,),
            disabled=st.session_state.answer_checked,
            width="stretch",
        )

    # Keep this zero-height component present both before and after checking so
    # its wrapper cannot subtly change the vertical position of the lower controls.
    components.html(
        f"""
        <span style="display:none">{question['qid']}</span>
        <script>
            setTimeout(() => {{
                const input = window.parent.document.querySelector('input[aria-label="Your answer:"]');
                if (input && !input.disabled) input.focus();
            }}, 50);
        </script>
        """,
        height=0,
    )

    feedback_space = st.container(height=90, border=False)
    with feedback_space:
        if st.session_state.answer_display_message.startswith("<div"):
            st.markdown(st.session_state.answer_display_message, unsafe_allow_html=True)
        else:
            st.markdown(st.session_state.answer_display_message)

control_row = st.container(height=92, border=False)
with control_row:
    new_question_col, results_col, score_col = st.columns(3, gap="medium", vertical_alignment="top")

    with new_question_col:
        button_text = "New Question" if st.session_state.question_list else "Click here for your first question!"
        button_type = "secondary" if st.session_state.question_list else "primary"
        st.button(
            button_text,
            on_click=start_new_question,
            key="identify_stems_question_button",
            width="stretch",
            disabled=not selected_pos,
            type=button_type,
        )

    with results_col:
        result_space = st.container(height=48, border=False)
        with result_space:
            st.markdown(st.session_state.result_message)

    with score_col:
        st.button("Reset Score", "identify_stems_reset", on_click=reset, width="stretch")
        st.markdown(f"Current score: **{st.session_state.current_score}** out of **{st.session_state.total_questions}**")

if not st.session_state.auto_advance:
    st.session_state.auto_advance_trigger = False

if st.session_state.auto_advance and st.session_state.auto_advance_trigger and st.session_state.answer_checked:
    import time
    time.sleep(st.session_state.auto_advance)
    start_new_question()
    st.rerun()
