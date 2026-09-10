from pathlib import Path

p = Path("verbs.py")
s = p.read_text()


def once(old, new):
    global s
    n = s.count(old)
    if n != 1:
        raise RuntimeError(f"Expected one match, got {n}: {old[:100]!r}")
    s = s.replace(old, new, 1)

# Add display helpers near the existing HTML helpers.
marker = '''def heavy(text, italic=False):
    escaped = html.escape(str(text))
    if italic:
        escaped = f"<em>{escaped}</em>"
    return f'<span style="font-weight:900;">{escaped}</span>'
'''
replacement = marker + '''\n\ndef verb_dictionary_entry(verb):
    """Use the same compact verb-entry format as the identify-stems exercise."""
    data = complete_verb_vocab[verb]
    conj = data.get("conj")
    conj_label = 3 if conj == "3io" else conj
    head = f"{verb} {conj_label}" if conj_label is not None else verb

    # The identify-stems exercise uses perfect + supine for ordinary active verbs.
    if data.get("voice") == "act":
        if conj == 1 and not data.get("irreg"):
            return head
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
'''
once(marker, replacement)

# Add the new setting to the schema.
once(
'''exercise_schema = {
    "show_principal_parts": bool_setting(False),
''',
'''exercise_schema = {
    "show_principal_parts": bool_setting(False),
    "show_stems": bool_setting(False),
''')

# Add checkbox directly below dictionary-entry display setting.
once(
'''    show_principal_parts = st.checkbox("Szótári alak megjelenítése?",
                                        help="Az ige szótári alakjának (főalakjainak) megjelenítése.",
                                        key=widget_key(page_id, "show_principal_parts"))
''',
'''    show_principal_parts = st.checkbox("Szótári alak megjelenítése?",
                                        help="Az ige szótári alakjának (főalakjainak) megjelenítése.",
                                        key=widget_key(page_id, "show_principal_parts"))
    show_stems = st.checkbox("Tövek megjelenítése?",
                             help="A jelenlegi ige töveinek megjelenítése a kérdés alatt.",
                             key=widget_key(page_id, "show_stems"))
''')

# Include it in saved/shared settings.
once(
'''current_exercise_settings = {
    "show_principal_parts": show_principal_parts,
''',
'''current_exercise_settings = {
    "show_principal_parts": show_principal_parts,
    "show_stems": show_stems,
''')

# Replace the prompt construction/rendering block.
start = s.index('        voice_label = "" if (voice == "dep" or verb == "fīō") else verb_abbrevs[voice]')
end = s.index('\n        if not st.session_state.question_generation_error_message:', start)
new_prompt = '''        tense_labels = {
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
        voice_label = {
            "act": "act.",
            "pass": "pass.",
            "dep": "deponens",
            "semidep": "semideponens",
        }.get(voice, str(voice))
        number_label = {"sg": "sg.", "pl": "pl."}.get(number, "")
        form_label = " ".join(
            part for part in [tense_labels[tense], mood_label, voice_label, number_label, str(person)]
            if part and part != "None"
        )

        verb_label = verb_dictionary_entry(verb) if show_principal_parts else verb
        question_html = (
            f'Add meg a <strong><em>{html.escape(verb_label)}</em></strong> ige '
            f'<strong>{html.escape(form_label)}</strong> alakját!'
        )

        stems = verb_stem_display(verb) if show_stems else []
        prompt_height = 104 if stems else 72
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
'''
s = s[:start] + new_prompt + s[end:]

compile(s, "verbs.py", "exec")
p.write_text(s)
