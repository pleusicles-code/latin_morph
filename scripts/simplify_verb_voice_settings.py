from pathlib import Path

path = Path('verbs.py')
text = path.read_text()

replacements = []

def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 occurrence, found {count}')
    text = text.replace(old, new)
    replacements.append(label)

replace_once(
    'master_voice_list = ["act", "pass", "dep", "semidep"]',
    'master_voice_list = ["act", "pass"]',
    'master voice list',
)

replace_once(
'''if isinstance(defaults.get("mood_selector"), list):
    migrated_moods = [mood for mood in defaults["mood_selector"] if mood in default_mood_list]
    if defaults.get("fut_impv") and "fut_impv" not in migrated_moods:
        migrated_moods.append("fut_impv")
    defaults["mood_selector"] = migrated_moods or default_mood_list
defaults.pop("fut_impv", None)
''',
'''if isinstance(defaults.get("mood_selector"), list):
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
''',
    'saved voice migration',
)

replace_once(
'''    voice_dict = {"act": "act.",
                  "pass": "pass.",
                  "dep": "deponens",
                  "semidep": "semideponens"}

    voice_selector = st.multiselect("Válaszd ki, mely igenemeket és igetípusokat szeretnéd gyakorolni:",
                                    master_voice_list,
                                    format_func=lambda x: voice_dict[x],
                                    key=widget_key(page_id, "voice_selector"),
                                    help = "Ha a semideponens igéket kiválasztod, ezek activum és deponens alakjai a többi igenembeállítástól függetlenül előfordulhatnak.")
''',
'''    voice_dict = {"act": "act.",
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
''',
    'voice selector UI',
)

replace_once(
'''tense_list = list(tense_selector)
present_impv = "impv" in mood_selector
''',
'''tense_list = list(tense_selector)
# Visible voice settings describe the morphology the learner wants to practise.
# Deponent forms are internally represented as ``dep`` but belong to visible ``pass.``.
internal_voice_selector = list(voice_selector)
if "pass" in voice_selector and "dep" not in internal_voice_selector:
    internal_voice_selector.append("dep")
present_impv = "impv" in mood_selector
''',
    'internal voice selector',
)

replace_once(
'''verb_vocab = {key: val for key,val in verb_vocab.items() if verb_vocab[key]["voice"] in voice_selector or ("pass" in voice_selector and verb_vocab[key]["voice"] == "act" and "no_pass" not in verb_vocab[key])}
''',
'''def verb_allowed_by_voice_settings(data):
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
''',
    'vocabulary voice filter',
)

replace_once(
'''        avail_tenses = list(tense_list)
        avail_moods = dict(mood_list)
''',
'''        avail_tenses = list(tense_list)
        # With pass. only, semideponents contribute only their deponent
        # perfect-system forms. Their active present-system forms are hidden.
        if verb_vocab.get(verb, {}).get("voice") == "semidep" and "act" not in voice_selector:
            avail_tenses = [tense for tense in avail_tenses if tense in perf_sys]
        avail_moods = dict(mood_list)
''',
    'semideponent tense restriction',
)

replace_once(
'''.query("`id.voice` in @voice_selector")
''',
'''.query("`id.voice` in @internal_voice_selector")
''',
    'adaptive voice filter',
)

# The semideponent voice-selection branch remains correct once present-system
# tenses are removed for pass.-only: present-system forms become active only
# when act. is also selected; perfect-system forms fall through to dep.

compile(text, 'verbs.py', 'exec')
path.write_text(text)
print('Applied:', ', '.join(replacements))
