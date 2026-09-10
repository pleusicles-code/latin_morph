from pathlib import Path

p = Path("verbs.py")
s = p.read_text()


def once(old, new):
    global s
    n = s.count(old)
    if n != 1:
        raise RuntimeError(f"Expected one match, got {n}: {old[:120]!r}")
    s = s.replace(old, new, 1)


# Shared presentation helpers, matching the translated noun exercise.
once("import ast\n", "import ast\nimport html\n")
once('st.set_page_config("BevLat Verbs", layout="centered")', 'st.set_page_config("BevLat – Igék", layout="centered")')
once('st.markdown("# Verbs")', 'st.markdown("# Igék")')

old_abbrevs = '''verb_abbrevs = {"ind": "indicative",
               "subj": "subjunctive",
               "impv": "imperative",
               "inf": "infinitive",
               "sg": "singular",
               "pl": "plural",
               "pres": "present",
               "impf": "imperfect",
               "fut": "future",
               "perf": "perfect",
               "plupf": "pluperfect",
               "fut_pf": "future perfect",
               "act": "active",
               "dep": "deponent",
               "semidep": "semi-deponent",
               "pass": "passive",
                1: "1st",
                2: "2nd",
                3: "3rd",}
'''
new_abbrevs = '''verb_abbrevs = {"ind": "indicativus",
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
'''
once(old_abbrevs, new_abbrevs)

# Settings translation.
replacements = {
    'option_expander = st.expander("Settings", expanded=True)': 'option_expander = st.expander("Beállítások", expanded=True)',
    'st.markdown("Options:", help="You can adjust these options at any point.")': 'st.markdown("Opciók:", help="Ezeket a beállításokat gyakorlás közben is bármikor módosíthatod.")',
    '"Enforce macrons?"': '"Hosszú magánhangzók ellenőrzése?"',
    'help="If this box is selected, macron mistakes will be considered incorrect. If not selected, macrons can be used but will not be evaluated."': 'help="Ha be van jelölve, a hosszú magánhangzók hibás jelölése hibás válasznak számít. Ha nincs bejelölve, a hosszúságjelek használhatók, de a program nem értékeli őket."',
    'st.markdown("You can copy and paste letters from here:")': 'st.markdown("A hosszú magánhangzók innen másolhatók:")',
    'st.checkbox("Show principal parts?",': 'st.checkbox("Szótári alak megjelenítése?",',
    'help="Select this box to show the verb\'s principal parts.",': 'help="Az ige szótári alakjának (főalakjainak) megjelenítése.",',
    '"Choose which conjugations to practice (they are all selected by default):"': '"Válaszd ki, mely coniugatiókat szeretnéd gyakorolni (alapértelmezés szerint mindegyik ki van választva):"',
    'help = "If no conjugations are chosen, only irregular verbs will be available."': 'help = "Ha egy coniugatiót sem választasz ki, csak a kiválasztott rendhagyó igékből kaphatsz kérdést."',
    '"Choose which tenses to practice:"': '"Válaszd ki, mely igeidőket szeretnéd gyakorolni:"',
    '"Choose which voices and types of verb to practice:"': '"Válaszd ki, mely igenemeket és igetípusokat szeretnéd gyakorolni:"',
    'help = "If semi-deponent is selected, those verbs\' active and deponent forms will be available, regardless of other voice selections."': 'help = "Ha a semideponens igéket kiválasztod, ezek activum és deponens alakjai a többi igenembeállítástól függetlenül előfordulhatnak."',
    '"Choose which moods to practice:"': '"Válaszd ki, mely módokat szeretnéd gyakorolni:"',
    '"Choose which irregular verbs to practice:"': '"Válaszd ki, mely rendhagyó igéket szeretnéd gyakorolni:"',
    'help="Selected irregular verbs will be available regardless of which conjugations are selected above. If you just want to practice irregular verbs, unselect all the conjugations."': 'help="A kiválasztott rendhagyó igék a fenti coniugatio-beállításoktól függetlenül előfordulhatnak. Ha csak rendhagyó igéket szeretnél gyakorolni, ne válassz ki egyetlen coniugatiót sem."',
    'st.checkbox("Practice *only* the selected irregular verbs?",': 'st.checkbox("Csak a kiválasztott rendhagyó igék gyakorlása?",',
    'help="Select this to practice *only* the selected irregular verbs; you can achieve the same effect by deselecting all of the conjugations above.")': 'help="Ha bejelölöd, csak a kiválasztott rendhagyó igékből kapsz kérdést; ugyanezt érheted el azzal is, ha fent minden coniugatiót kikapcsolsz.")',
}
for old, new in replacements.items():
    once(old, new)

# Move the three settings controls to a full-width row at the bottom of the expander.
old_buttons = '''with options_col:
    if st.user.is_logged_in:
        set_defaults_col, clear_defaults_col, link_col = st.container(vertical_alignment="bottom", height="stretch").columns(3, vertical_alignment="center")
        with set_defaults_col:
            st.button("Save settings",
                        type="primary",
                        width="stretch",
                        help="Save your current verb settings (except macron enforcement) as your default.",
                        on_click=save_defaults,
                        args=(page_id, defaults,),
                        kwargs=current_exercise_settings,
                        disabled=preset_active,
                        )
        with clear_defaults_col:
            st.button("Reset defaults",
                        type="primary",
                        width="stretch",
                        help="Restore the generic BevLat default settings for verbs.",
                        on_click=clear_defaults,
                        args=(page_id,),
                        disabled=preset_active or not defaults
                        )
        with link_col:
            exercise_link_popover(page_id, exercise_schema, current_exercise_settings)
    else:
        exercise_link_popover(page_id, exercise_schema, current_exercise_settings)
'''
new_buttons = '''with option_expander:
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
'''
once(old_buttons, new_buttons)

# User-facing option validation.
for old, new in {
    'st.write("You need to choose at least one conjugation or irregular verb.")': 'st.write("Legalább egy coniugatiót vagy rendhagyó igét ki kell választanod.")',
    'st.write("You need to choose at least one tense.")': 'st.write("Legalább egy igeidőt ki kell választanod.")',
    'st.write("You need to choose at least one voice.")': 'st.write("Legalább egy igenemet vagy igetípust ki kell választanod.")',
    'st.write("You need to choose at least one mood.")': 'st.write("Legalább egy módot ki kell választanod.")',
    'st.write("Based on your selections, there are no available verbs to generate forms for.")': 'st.write("A kiválasztott beállításokkal nincs olyan ige, amelyből kérdést lehetne generálni.")',
}.items():
    once(old, new)

old_error = 'st.session_state.question_generation_error_message = ":warning: I\'m having trouble generating a question for you based on your selected options; I suggest you make some changes and hit \'New Question\' again."'
new_error = 'st.session_state.question_generation_error_message = ":warning: A kiválasztott beállításokkal nem sikerült kérdést generálni. Módosíts néhány beállítást, majd kattints újra az \'Új kérdés\' gombra."'
once(old_error, new_error)

# Question, answer form and feedback area.
start = s.index('        tense_voice_mood = [item for item in [verb_abbrevs[voice]')
end = s.index('\n\n    ## GENERATE NEW QUESTIONS AND CHECK ANSWERS ##', start)
new_question_block = '''        voice_label = "" if (voice == "dep" or verb == "fīō") else verb_abbrevs[voice]
        grammatical_parts = [verb_abbrevs[tense], verb_abbrevs[mood]]
        if voice_label:
            grammatical_parts.append(voice_label)
        grammatical_parts.extend([verb_abbrevs[number], f"{person}. személyű"])
        question_html = (
            f'Add meg a <strong><em>{html.escape(verb)}</em></strong> ige '
            f'<strong>{" ".join(grammatical_parts)}</strong> alakját!'
        )

        supplementary = []
        if show_principal_parts:
            supplementary.append(
                "Szótári alak: " + ", ".join(f"<em>{html.escape(str(part))}</em>" for part in verb_pp)
            )

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

        if not st.session_state.question_generation_error_message:
            with st.form(key="verb_answer_form", clear_on_submit=True):
                current_answer = st.text_input("Válaszod:", key="answer_input")

                def submit_verb_answer():
                    submit_and_check_answer()
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
                                f"<strong>Helytelen válasz. {label}: {correct_html}.</strong>",
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
'''
s = s[:start] + new_question_block + s[end:]

# Lower controls: translate and adopt the same spacing/placement as nouns.
start = s.index('    new_question_col, results_col, score_col = st.columns(3)')
end = s.index('\n\nif st.session_state.auto_advance_trigger', start)
controls = s[start:end]
controls = controls.replace(
    '    new_question_col, results_col, score_col = st.columns(3)',
    '    control_row = st.container(height=110, border=False)\n    with control_row:\n        new_question_col, results_col, score_col = st.columns(3, gap="medium", vertical_alignment="top")'
)
lines = controls.splitlines()
controls = "\n".join(lines[:3] + [("    " + line if line else line) for line in lines[3:]])
controls = controls.replace(
    '"New Question" if st.session_state.question_list else "Click here for your first question!"',
    '"Új kérdés" if st.session_state.question_list else "Kattints ide az első kérdéshez!"'
)
controls = controls.replace(
    '            st.markdown(st.session_state.result_message)    # just write the result message, rather than other things as well.\n\n',
    ''
)
controls = controls.replace(
    'help_text = "As this form cannot be conjugated, there is no available chart." if (starting_form["mood"] == "inf" or (starting_form["voice"] == "pass" and complete_verb_vocab[starting_form["verb"]].get("impers_pass_only") is True)) else None',
    'help_text = "Ehhez az alakhoz nem jeleníthető meg ragozási táblázat." if (starting_form["voice"] == "pass" and complete_verb_vocab[starting_form["verb"]].get("impers_pass_only") is True) else None'
)
controls = controls.replace('st.popover("View chart",type="primary", help=help_text)', 'st.popover("Ragozási táblázat", type="primary", help=help_text)')
controls = controls.replace(
    'if starting_form["mood"] not in ["inf"] and not (starting_form["voice"] == "pass" and complete_verb_vocab[starting_form["verb"]].get("impers_pass_only") is True):',
    'if not (starting_form["voice"] == "pass" and complete_verb_vocab[starting_form["verb"]].get("impers_pass_only") is True):'
)
controls = controls.replace(
    'st.caption("*N.B. This is a beta feature; please let me know if it appears to be buggy or if you would find other information helpful.*")',
    'st.caption("Ez a funkció még fejlesztés alatt áll.")'
)
controls = controls.replace('st.button("Reset Score", "reset", on_click=reset, width="stretch")', 'st.button("Pontszám nullázása", "reset", on_click=reset, width="stretch")')
controls = controls.replace(
    'st.markdown(f"Current score: **{st.session_state.current_score}** out of **{st.session_state.total_questions}**")',
    'st.markdown(f"Jelenlegi pontszám: **{st.session_state.current_score}** / **{st.session_state.total_questions}**")'
)
s = s[:start] + controls + s[end:]

# Ensure key English UI strings are gone and syntax is valid.
for leftover in [
    'st.markdown("# Verbs")', 'st.expander("Settings"', '"Enforce macrons?"',
    '"Show principal parts?"', '"Choose which conjugations to practice',
    '"Choose which tenses to practice:', '"Choose which voices and types of verb to practice:',
    '"Choose which moods to practice:', '"Choose which irregular verbs to practice:',
    '"Practice *only* the selected irregular verbs?"', 'st.markdown("### Current question")',
    '"Check Answer"', '"Reset Score"', '"View chart"', '"Save settings"', '"Reset defaults"',
]:
    if leftover in s:
        raise RuntimeError(f"Untranslated UI string remains: {leftover}")

compile(s, "verbs.py", "exec")
p.write_text(s)
