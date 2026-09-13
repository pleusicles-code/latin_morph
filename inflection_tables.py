import streamlit as st
import pandas as pd
import unicodedata

import vocab as vocab_module
from vocab import import_nouns, import_adjectives, import_verbs, import_pronouns, filter_vocab_by_repo

st.set_page_config("BevLat – Ragozási táblák", layout="centered")
st.markdown("# Ragozási táblák")
st.caption("Diagnosztikai oldal a szókincs morfológiai adatainak ellenőrzéséhez.")

CASES = ["nom", "acc", "gen", "dat", "abl"]
CASE_LABELS = {"nom":"nom.", "gen":"gen.", "dat":"dat.", "acc":"acc.", "abl":"abl.", "voc":"voc."}
GENDERS = ["m", "f", "n"]

def repo_values(data):
    value = data.get("repo")
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value] if value else []

def sort_key(value):
    normalized = unicodedata.normalize("NFD", str(value).casefold())
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")

# category, display POS, vocabulary.  Current pronouns belong under the diagnostic
# "misc" filter; future miscellaneous import functions are picked up automatically.
sources = [
    ("nouns", "főnév", import_nouns()),
    ("adjectives", "melléknév", import_adjectives()),
    ("verbs", "ige", import_verbs()),
    ("misc", "névmás", import_pronouns()),
]
for function_name, pos_label in (("import_misc", "egyéb"), ("import_adverbs", "határozószó"), ("import_indeclinables", "egyéb")):
    function = getattr(vocab_module, function_name, None)
    if callable(function):
        extra = function()
        if isinstance(extra, dict):
            sources.append(("misc", pos_label, extra))

available_repos = sorted(
    {repo for _, _, vocabulary in sources for data in vocabulary.values() for repo in repo_values(data)},
    key=lambda repo: (repo != "core", sort_key(repo)),
)
if not available_repos:
    st.warning("Jelenleg nincs repóadat a szókincsben.")
    st.stop()

default_repo = "alap2" if "alap2" in available_repos else ("alap1" if "alap1" in available_repos else available_repos[0])
selected_repo = st.selectbox("Repó:", available_repos, index=available_repos.index(default_repo))

pos_labels = {
    "all": "mind",
    "nouns": "főnevek",
    "verbs": "igék",
    "adjectives": "melléknevek",
    "misc": "egyéb",
}
selected_pos = st.selectbox(
    "Szófaj:",
    list(pos_labels),
    format_func=lambda value: pos_labels[value],
)

entries = []
for category, pos, vocabulary in sources:
    if selected_pos != "all" and category != selected_pos:
        continue
    for lemma, data in filter_vocab_by_repo(vocabulary, selected_repo).items():
        display = data.get("lemma_lexical") or lemma
        entries.append((sort_key(display), sort_key(lemma), category, pos, lemma, data))
entries.sort(key=lambda row: (row[0], row[3], row[1]))

if not entries:
    st.warning("Ebben a repó- és szófaj-kombinációban jelenleg nincs megjeleníthető szó.")
    st.stop()

option_ids = list(range(len(entries)))
def option_label(index):
    _, _, _, pos, lemma, data = entries[index]
    display = data.get("lemma_lexical") or lemma
    alias = sort_key(display)
    label = f"{display} — {pos}"
    if alias != str(display).casefold():
        label += f" · {alias}"
    return label

selected = st.selectbox("Szó:", option_ids, format_func=option_label)
_, _, category, pos, lemma, data = entries[selected]

def noun_dictionary_entry(noun, data):
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
        if str(data.get("decl", "")).startswith("2") and noun.endswith(("ius", "ium")):
            genitive = genitive[0]
        else:
            genitive = "/".join(genitive)
    if genitive:
        return f"{noun}, {genitive} {data['gender']}."
    return f"{noun} {data['gender']}."


def adjective_dictionary_entry(adjective, data):
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


def verb_dictionary_entry(verb, data):
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


def dictionary_entry(category, lemma, data):
    if category == "nouns":
        return noun_dictionary_entry(lemma, data)
    if category == "adjectives":
        return adjective_dictionary_entry(lemma, data)
    if category == "verbs":
        return verb_dictionary_entry(lemma, data)
    return data.get("lemma_lexical") or lemma


meta = [f"**Szótári alak:** {dictionary_entry(category, lemma, data)}"]
if data.get("meaning"):
    meta.append(f"**Jelentés:** {data['meaning']}")
meta.append(f"**Szófaj:** {pos}")
meta.append(f"**Repó:** {selected_repo}")
st.markdown("  \n".join(meta))

def join_form(value):
    if value is None:
        return "—"
    if isinstance(value, (list, tuple)):
        return " / ".join(str(item) for item in value if item is not None) or "—"
    return str(value)

NOUN_ENDINGS = {
    1: {"sg":{"gen":"ae","dat":"ae","acc":"am","abl":"ā","voc":None},"pl":{"nom":"ae","gen":"ārum","dat":"īs","acc":"ās","abl":"īs","voc":None}},
    "2_us": {"sg":{"gen":"ī","dat":"ō","acc":"um","abl":"ō","voc":"e"},"pl":{"nom":"ī","gen":"ōrum","dat":"īs","acc":"ōs","abl":"īs","voc":None}},
    "2_er": {"sg":{"gen":"ī","dat":"ō","acc":"um","abl":"ō","voc":None},"pl":{"nom":"ī","gen":"ōrum","dat":"īs","acc":"ōs","abl":"īs","voc":None}},
    "2_neut": {"sg":{"gen":"ī","dat":"ō","acc":"um","abl":"ō","voc":None},"pl":{"nom":"a","gen":"ōrum","dat":"īs","acc":"a","abl":"īs","voc":None}},
    3: {"sg":{"gen":"is","dat":"ī","acc":"em","abl":"e","voc":None},"pl":{"nom":"ēs","gen":"um","dat":"ibus","acc":"ēs","abl":"ibus","voc":None}},
    "3_neut": {"sg":{"gen":"is","dat":"ī","acc":None,"abl":"e","voc":None},"pl":{"nom":"a","gen":"um","dat":"ibus","acc":"a","abl":"ibus","voc":None}},
    "3_istem": {"sg":{"gen":"is","dat":"ī","acc":"em","abl":"e","voc":None},"pl":{"nom":"ēs","gen":"ium","dat":"ibus","acc":["ēs","īs"],"abl":"ibus","voc":None}},
    "3_istem_neut": {"sg":{"gen":"is","dat":"ī","acc":None,"abl":"ī","voc":None},"pl":{"nom":"ia","gen":"ium","dat":"ibus","acc":"ia","abl":"ibus","voc":None}},
    4: {"sg":{"gen":"ūs","dat":"uī","acc":"um","abl":"ū","voc":None},"pl":{"nom":"ūs","gen":"uum","dat":"ibus","acc":"ūs","abl":"ibus","voc":None}},
    "4_neut": {"sg":{"gen":"ūs","dat":"ū","acc":"ū","abl":"ū","voc":None},"pl":{"nom":"ua","gen":"uum","dat":"ibus","acc":"ua","abl":"ibus","voc":None}},
    "5_vowel": {"sg":{"gen":"ēī","dat":"ēī","acc":"em","abl":"ē","voc":None},"pl":{"nom":"ēs","gen":"ērum","dat":"ēbus","acc":"ēs","abl":"ēbus","voc":None}},
    "5_consonant": {"sg":{"gen":"eī","dat":"eī","acc":"em","abl":"ē","voc":None},"pl":{"nom":"ēs","gen":"ērum","dat":"ēbus","acc":"ēs","abl":"ēbus","voc":None}},
}

def noun_form(word, info, case, number):
    restriction = info.get("number")
    if restriction == "singular" and number == "pl" or restriction == "plural" and number == "sg":
        return None
    irregular = info.get("irreg", {}).get(number, {})
    if case in irregular:
        value = irregular[case]
        if value is None:
            return None
        return value
    decl = info["decl"]
    stem = info["stem"]
    if number == "sg" and case == "nom":
        return word
    ending = NOUN_ENDINGS[decl][number][case]
    if ending is None:
        if case == "voc" or (info.get("gender") == "n" and case == "acc"):
            return noun_form(word, info, "nom", number)
        return None
    if info.get("true_i_stem") and number == "sg" and case == "acc":
        return [stem + "im", stem + "em"]
    if info.get("true_i_stem") and number == "sg" and case == "abl":
        return [stem + "ī", stem + "e"]
    if isinstance(ending, (list, tuple)):
        return [stem + item for item in ending]
    return stem + ending

ADJ_12 = {
    "sg": {
        "m":{"nom":"us","gen":"ī","dat":"ō","acc":"um","abl":"ō","voc":"e"},
        "f":{"nom":"a","gen":"ae","dat":"ae","acc":"am","abl":"ā","voc":"a"},
        "n":{"nom":"um","gen":"ī","dat":"ō","acc":"um","abl":"ō","voc":"um"},
    },
    "pl": {
        "m":{"nom":"ī","gen":"ōrum","dat":"īs","acc":"ōs","abl":"īs","voc":"ī"},
        "f":{"nom":"ae","gen":"ārum","dat":"īs","acc":"ās","abl":"īs","voc":"ae"},
        "n":{"nom":"a","gen":"ōrum","dat":"īs","acc":"a","abl":"īs","voc":"a"},
    },
}
ADJ_3 = {
    "sg": {
        "m":{"gen":"is","dat":"ī","acc":"em","abl":"ī","voc":None},
        "f":{"gen":"is","dat":"ī","acc":"em","abl":"ī","voc":None},
        "n":{"gen":"is","dat":"ī","acc":None,"abl":"ī","voc":None},
    },
    "pl": {
        "m":{"nom":"ēs","gen":"ium","dat":"ibus","acc":["īs","ēs"],"abl":"ibus","voc":"ēs"},
        "f":{"nom":"ēs","gen":"ium","dat":"ibus","acc":["īs","ēs"],"abl":"ibus","voc":"ēs"},
        "n":{"nom":"ia","gen":"ium","dat":"ibus","acc":"ia","abl":"ibus","voc":"ia"},
    },
}

def pick_gender_form(value, gender):
    if not isinstance(value, tuple):
        return value
    if gender == "n":
        return value[-1]
    if len(value) <= 2:
        return value[0]
    return value[0] if gender == "m" else value[1]

def adj_form(word, info, case, number, gender):
    if info.get("no_pl") and number == "pl" or info.get("no_sg") and number == "sg":
        return None
    irregular = info.get("irreg", {}).get("forms", {}).get(number, {})
    if case in irregular:
        return pick_gender_form(irregular[case], gender)
    stem = info.get("stem", "")
    noms = info.get("noms")
    if info.get("decl") == (1, 2):
        if info.get("pronominal") and number == "sg" and case in ("gen", "dat"):
            return stem + ("īus" if case == "gen" else "ī")
        if number == "sg" and case == "nom":
            if noms:
                return pick_gender_form(noms, gender)
            if gender == "m":
                return word
        ending = ADJ_12[number][gender][case]
        if number == "sg" and gender == "m" and case == "voc" and word.endswith("ius"):
            ending = "ī"
        if number == "sg" and gender == "m" and case == "voc" and not word.endswith("us"):
            return word
        return stem + ending
    if number == "sg" and case in ("nom", "voc"):
        if noms:
            return pick_gender_form(noms, gender)
        if case == "nom":
            return word
    if number == "sg" and gender == "n" and case == "acc":
        return adj_form(word, info, "nom", number, gender)
    ending = ADJ_3[number][gender].get(case)
    if ending is None:
        return adj_form(word, info, "nom", number, gender)
    if isinstance(ending, (list, tuple)):
        return [stem + item for item in ending]
    return stem + ending

SUM = {
    "pres":{"sg":["sum","es","est"],"pl":["sumus","estis","sunt"]},
    "impf":{"sg":["eram","erās","erat"],"pl":["erāmus","erātis","erant"]},
    "fut":{"sg":["erō","eris","erit"],"pl":["erimus","eritis","erunt"]},
}
REG_IND = {
    1:{"pres":{"sg":["ō","ās","at"],"pl":["āmus","ātis","ant"]},"impf":{"sg":["ābam","ābās","ābat"],"pl":["ābāmus","ābātis","ābant"]},"fut":{"sg":["ābō","ābis","ābit"],"pl":["ābimus","ābitis","ābunt"]}},
    2:{"pres":{"sg":["eō","ēs","et"],"pl":["ēmus","ētis","ent"]},"impf":{"sg":["ēbam","ēbās","ēbat"],"pl":["ēbāmus","ēbātis","ēbant"]},"fut":{"sg":["ēbō","ēbis","ēbit"],"pl":["ēbimus","ēbitis","ēbunt"]}},
    3:{"pres":{"sg":["ō","is","it"],"pl":["imus","itis","unt"]},"impf":{"sg":["ēbam","ēbās","ēbat"],"pl":["ēbāmus","ēbātis","ēbant"]},"fut":{"sg":["am","ēs","et"],"pl":["ēmus","ētis","ent"]}},
    "3io":{"pres":{"sg":["iō","is","it"],"pl":["imus","itis","iunt"]},"impf":{"sg":["iēbam","iēbās","iēbat"],"pl":["iēbāmus","iēbātis","iēbant"]},"fut":{"sg":["iam","iēs","iet"],"pl":["iēmus","iētis","ient"]}},
    4:{"pres":{"sg":["iō","īs","it"],"pl":["īmus","ītis","iunt"]},"impf":{"sg":["iēbam","iēbās","iēbat"],"pl":["iēbāmus","iēbātis","iēbant"]},"fut":{"sg":["iam","iēs","iet"],"pl":["iēmus","iētis","ient"]}},
}
PERF_ACT = {
    "perf":{"sg":["ī","istī","it"],"pl":["imus","istis","ērunt"]},
    "plupf":{"sg":["eram","erās","erat"],"pl":["erāmus","erātis","erant"]},
    "fut_pf":{"sg":["erō","eris","erit"],"pl":["erimus","eritis","erint"]},
}

def irregular_verb_form(info, tense, voice, mood, number, person):
    return info.get("irreg", {}).get("forms", {}).get(tense, {}).get(voice, {}).get(mood, {}).get(number, {}).get(person)

def regular_present_stem(info):
    stem = info.get("pres")
    conj = info.get("conj")
    if stem is None:
        return None
    return stem

def verb_ind_form(word, info, tense, voice, number, person):
    special = irregular_verb_form(info, tense, voice, "ind", number, person)
    if special is not None:
        return special
    lexical_voice = info.get("voice")
    if lexical_voice == "dep":
        voice = "pass"
    if lexical_voice == "semidep" and tense in ("perf","plupf","fut_pf"):
        voice = "pass"
    if tense in ("perf","plupf","fut_pf"):
        if voice == "act":
            stem = info.get("perf")
            if not stem:
                return None
            return stem + PERF_ACT[tense][number][person-1]
        stem = info.get("ppp")
        if not stem:
            return None
        endings = ["us","a","um"] if number == "sg" else ["ī","ae","a"]
        aux_tense = {"perf":"pres","plupf":"impf","fut_pf":"fut"}[tense]
        aux = SUM[aux_tense][number][person-1]
        return [stem + ending + " " + aux for ending in endings]
    stem = regular_present_stem(info)
    conj = info.get("conj")
    if stem is None or conj not in REG_IND:
        return None
    if voice == "act":
        ending = REG_IND[conj][tense][number][person-1]
        return stem + ending
    # Diagnostic passive generation; irregular forms above always take precedence.
    active = REG_IND[conj][tense][number][person-1]
    if number == "sg":
        pass_end = {1:"r",2:"ris",3:"tur"}[person]
    else:
        pass_end = {1:"mur",2:"minī",3:"ntur"}[person]
    if tense == "pres":
        base = stem
        if conj == 1:
            vowel = {1:"o",2:"ā",3:"ā"}.get(person,"ā") if number == "sg" else "ā"
        elif conj == 2:
            vowel = "e" if number == "sg" and person == 1 else "ē"
        elif conj in (3,"3io"):
            vowel = "i" if not (number == "pl" and person == 3) else "u"
        else:
            vowel = "ī" if not (number == "pl" and person == 3) else "iu"
        if number == "sg" and person == 1:
            return base + ("or" if conj in (1,3) else "eor" if conj == 2 else "ior")
        if number == "sg" and person == 2 and conj in (3, "3io"):
            return base + "eris"
        return base + vowel + pass_end
    if tense == "impf":
        bridge = "ābā" if conj == 1 else "ēbā" if conj in (2,3) else "iēbā"
    else:
        bridge = "ābi" if conj == 1 else "ēbi" if conj == 2 else "ē" if conj == 3 else "iē"
    if tense == "impf" and number == "sg" and person == 1:
        return stem + bridge[:-1] + "ar"
    if tense == "impf" and number == "pl" and person == 3:
        return stem + bridge[:-1] + "antur"
    if tense == "fut" and number == "sg" and person == 1:
        if conj == 3:
            return stem + "ar"
        if conj in ("3io", 4):
            return stem + "iar"
    if tense == "fut" and number == "pl" and person == 3:
        if conj == 3:
            return stem + "entur"
        if conj in ("3io", 4):
            return stem + "ientur"
    if number == "sg" and person == 1:
        return stem + bridge[:-1] + "or"
    return stem + bridge + pass_end

if pos == "főnév":
    noun_cases = ["nom"]
    distinct_vocative = any(
        noun_form(lemma, data, "voc", number) != noun_form(lemma, data, "nom", number)
        for number in ("sg", "pl")
        if noun_form(lemma, data, "nom", number) is not None
    )
    if distinct_vocative:
        noun_cases.append("voc")
    noun_cases.extend(["acc", "gen", "dat", "abl"])
    table = {"sg.": [], "pl.": []}
    for case in noun_cases:
        table["sg."].append(join_form(noun_form(lemma, data, case, "sg")))
        table["pl."].append(join_form(noun_form(lemma, data, case, "pl")))
    st.table(pd.DataFrame(table, index=[CASE_LABELS[c] for c in noun_cases]))

elif pos == "melléknév":
    adjective_cases = ["nom"]
    distinct_vocative = any(
        adj_form(lemma, data, "voc", number, gender) != adj_form(lemma, data, "nom", number, gender)
        for number in ("sg", "pl")
        for gender in GENDERS
        if adj_form(lemma, data, "nom", number, gender) is not None
    )
    if distinct_vocative:
        adjective_cases.append("voc")
    adjective_cases.extend(["acc", "gen", "dat", "abl"])
    columns = {}
    for number in ("sg", "pl"):
        for gender in GENDERS:
            columns[(number, gender)] = [join_form(adj_form(lemma, data, case, number, gender)) for case in adjective_cases]
    st.table(pd.DataFrame(columns, index=[CASE_LABELS[c] for c in adjective_cases]))

elif pos == "ige":
    st.caption("Az igei diagnosztikai nézet jelenleg az indicativus hat igeidejét mutatja; a tárolt rendhagyó alakok elsőbbséget élveznek a szabályos képzéssel szemben.")
    lexical_voice = data.get("voice")
    voices = ["act"]
    if lexical_voice == "dep":
        voices = ["dep"]
    elif lexical_voice == "semidep":
        voices = ["act", "dep"]
    elif not data.get("no_pass"):
        voices.append("pass")
    tense_names = [("pres","praes. impf."),("impf","praet. impf."),("fut","fut. impf."),("perf","praes. perf."),("plupf","praet. perf."),("fut_pf","fut. perf.")]
    for voice in voices:
        voice_label = "deponens" if voice == "dep" else "act." if voice == "act" else "pass."
        st.markdown(f"### {voice_label}")
        for tense, tense_label in tense_names:
            # semideponents: active present system, deponent perfect system only
            if lexical_voice == "semidep" and ((voice == "act" and tense in ("perf","plupf","fut_pf")) or (voice == "dep" and tense in ("pres","impf","fut"))):
                continue
            forms = {"sg.": [], "pl.": []}
            for number in ("sg","pl"):
                for person in (1,2,3):
                    form_voice = "pass" if voice == "dep" else voice
                    forms["sg." if number == "sg" else "pl."].append(join_form(verb_ind_form(lemma, data, tense, form_voice, number, person)))
            st.markdown(f"**{tense_label} indicativus**")
            st.table(pd.DataFrame(forms, index=["1.","2.","3."]))

else:
    st.info("Ehhez a szóhoz jelenleg nincs morfológiai ragozási tábla a diagnosztikai oldalon.")
