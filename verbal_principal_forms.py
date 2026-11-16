"""Dictionary-form generation and validation for Latin participles.

Independent of Streamlit so accepted answer spellings can be tested in isolation.
"""
import re
import unicodedata


PARTICIPLE_VOWELS = {1: "ā", 2: "ē", 3: "ē", "3io": "iē", 4: "iē"}


def participle_dictionary_entry(data, kind):
    """Return a canonical dictionary form and its grammatical components.

    kind: pap (present active), ppp (perfect passive), fap (future active),
    gdv (gerundive / future passive).
    """
    if kind == "pap":
        special = data.get("pap")
        if special is None and "pap" in data:
            return None
        if isinstance(special, (tuple, list)) and len(special) >= 2:
            nominative, stem = special[:2]
        else:
            vowel = PARTICIPLE_VOWELS.get(data.get("conj"))
            base = data.get("pres")
            if not vowel or not base:
                return None
            nominative = base + vowel + "ns"
            stem = base + vowel.replace("ē", "e").replace("ā", "a") + "nt"
        if not isinstance(nominative, str) or not isinstance(stem, str):
            return None
        return {
            "kind": "pap",
            "canonical": f"{nominative} (ntis)",
            "nominative": nominative,
            "genitive": stem + "is",
        }

    if kind == "ppp":
        stem = data.get("ppp")
        if data.get("no_pass"):
            return None
    elif kind == "fap":
        if "fap" in data and data["fap"] is None:
            return None
        stem = data.get("fap") or ((data.get("ppp") or "") + "ūr")
        if not (data.get("fap") or data.get("ppp")):
            return None
    elif kind == "gdv":
        if "gdv" in data and data["gdv"] is None:
            return None
        stem = data.get("gdv")
        if not stem:
            base, vowel = data.get("pres"), PARTICIPLE_VOWELS.get(data.get("conj"))
            if not base or not vowel:
                return None
            stem = base + vowel.replace("ē", "e").replace("ā", "a") + "nd"
    else:
        return None

    if not isinstance(stem, str) or not stem:
        return None
    masculine = stem + "us"
    return {
        "kind": "three",
        "canonical": masculine + " 3",
        "masculine": masculine,
        "feminine": stem + "a",
        "neuter": stem + "um",
    }


def accepts_participle_dictionary_answer(answer, entry, *, enforce_macrons=False,
                                           normalize_v=False):
    """Recognize abbreviated and expanded dictionary forms, not arbitrary inflections."""
    if not isinstance(answer, str) or not isinstance(entry, dict):
        return False

    def tokens(value):
        value = unicodedata.normalize("NFC", value.casefold())
        if not enforce_macrons:
            value = "".join(
                char for char in unicodedata.normalize("NFD", value)
                if char != "\u0304"
            )
            value = unicodedata.normalize("NFC", value)
        if normalize_v:
            value = value.replace("v", "u")
        # Commas, periods, parentheses, slashes and dashes are separators.
        return re.findall(r"[^\W_]+", value, flags=re.UNICODE)

    given = tokens(answer)
    if entry["kind"] == "pap":
        return len(given) == 2 and given[0] == tokens(entry["nominative"])[0] and (
            given[1] == "ntis" or given[1] == tokens(entry["genitive"])[0]
        )
    if entry["kind"] == "three":
        masculine = tokens(entry["masculine"])[0]
        feminine = tokens(entry["feminine"])[0]
        neuter = tokens(entry["neuter"])[0]
        return (
            given == [masculine, "3"]
            or (
                len(given) == 3 and given[0] == masculine
                and given[1] in {feminine, "a"}
                and given[2] in {neuter, "um"}
            )
        )
    return False
