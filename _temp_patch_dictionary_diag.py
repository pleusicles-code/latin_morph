from pathlib import Path
import py_compile

p = Path('inflection_tables.py')
text = p.read_text(encoding='utf-8')

marker = '''meta = []
if data.get("meaning"):
    meta.append(f"**Jelentés:** {data['meaning']}")
meta.append(f"**Szófaj:** {pos}")
meta.append(f"**Repó:** {selected_repo}")
st.markdown("  \\n".join(meta))
'''

replacement = '''def noun_dictionary_entry(noun, data):
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
st.markdown("  \\n".join(meta))
'''

if marker not in text:
    raise SystemExit('metadata block not found')
text = text.replace(marker, replacement, 1)
p.write_text(text, encoding='utf-8')
py_compile.compile('inflection_tables.py', doraise=True)
