from pathlib import Path

patch_source = Path("scripts/translate_verbs_page.py").read_text()
start = patch_source.index("# Lower controls: translate and adopt the same spacing/placement as nouns.")
end = patch_source.index("# Ensure key English UI strings are gone and syntax is valid.", start)

replacement = r"""# Lower controls: replace the whole block explicitly, matching the noun layout.
start = s.index('    new_question_col, results_col, score_col = st.columns(3)')
end = s.index('\\n\\nif st.session_state.auto_advance_trigger', start)
new_controls = '''    control_row = st.container(height=110, border=False)
    with control_row:
        new_question_col, results_col, score_col = st.columns(3, gap="medium", vertical_alignment="top")

        new_q_button_text = "Új kérdés" if st.session_state.question_list else "Kattints ide az első kérdéshez!"
        new_q_button_type = "secondary" if st.session_state.question_list else "primary"
        with new_question_col:
            st.button(
                new_q_button_text,
                on_click=new_question,
                args=(build_verb,),
                key="question_button",
                width="stretch",
                type=new_q_button_type,
            )

        with results_col:
            if (
                st.session_state.current_question
                and st.session_state.answer_checked
                and "Incorrect" in st.session_state.result_message
            ):
                starting_form = dict(st.session_state.current_question[1])
                next_form = dict(starting_form)
                help_text = (
                    "Ehhez az alakhoz nem jeleníthető meg ragozási táblázat."
                    if (
                        starting_form["voice"] == "pass"
                        and complete_verb_vocab[starting_form["verb"]].get("impers_pass_only") is True
                    )
                    else None
                )

                chart_popover = st.popover("Ragozási táblázat", type="primary", help=help_text)

                with chart_popover:
                    if not (
                        starting_form["voice"] == "pass"
                        and complete_verb_vocab[starting_form["verb"]].get("impers_pass_only") is True
                    ):
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
                                finally:
                                    if starting_form["mood"] == "impv":
                                        if starting_form["tense"] == "pres" and pers != 2:
                                            form = None
                                        if (
                                            starting_form["voice"] in ["pass", "dep"]
                                            and starting_form["tense"] == "fut"
                                            and num == "pl"
                                            and pers != 3
                                        ):
                                            form = None

                                conj_table[num].append(form if isinstance(form, str) else "--")

                        conjugation_table = pd.DataFrame(conj_table, index=table_index)
                        st.table(conjugation_table)

        with score_col:
            st.button("Pontszám nullázása", "reset", on_click=reset, width="stretch")
            st.markdown(
                f"Jelenlegi pontszám: **{st.session_state.current_score}** / **{st.session_state.total_questions}**"
            )
'''
s = s[:start] + new_controls + s[end:]

"""

patch_source = patch_source[:start] + replacement + patch_source[end:]
exec(compile(patch_source, "scripts/translate_verbs_page.py", "exec"))
