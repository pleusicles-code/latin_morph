"""Dictionary-form generation and validation for Latin participles.

Independent of Streamlit so accepted answer spellings can be tested in isolation.
"""
import re
import unicodedata


PARTICIPLE_VOWELS = {1: "ā", 2: "ē", 3: "ē", "3io": "iē", 4: "iē"}


def _clean_fourth_part(value):
    """Exclude absent, annotated or bracketed dictionary entries."""
    return (
        isinstance(value, str)
        and bool(value.strip())
        and not any(mark in value for mark in "[]()")
    )


def _future_only_fourth_part(value):
    """Recognize -ūrus or the stored future-participle stem -ūr."""
    if not _clean_fourth_part(value):
        return False
    normalized = "".join(
        char for char in unicodedata.normalize("NFD", value.casefold().strip())
        if unicodedata.category(char) != "Mn"
    )
    return normalized.endswith(("ur", "urus"))


def _future_stem(value):
    """The vocabulary normally stores stems; also tolerate full -ūrus forms."""
    if _future_only_fourth_part(value):
        return value.strip()[:-2] if value.strip().casefold().endswith(("ūrus", "urus")) else value.strip()
    return None


def has_real_perfect_passive_stem(data):
    """A true PPP/supine stem, not a bracketed or future-only substitute."""
    return (
        _clean_fourth_part(data.get("ppp"))
        and not _future_only_fourth_part(data["ppp"])
    )


def has_usable_fourth_part(data):
    """Either a genuine PPP or a genuine future-active fourth principal part."""
    return has_real_perfect_passive_stem(data) or (
        _future_stem(data.get("fap")) is not None
        or _future_stem(data.get("ppp")) is not None
    )


def participle_dictionary_entry(data, kind):
    """Return a canonical dictionary form and its grammatical components.

    kind: pap (present active), ppp (perfect passive), fap (future active),
    gdv (gerundive / future passive).

    Dictionary-form practice excludes verbs whose fourth principal part
    is missing or merely a bracketed/special substitute.
    """
    if not has_usable_fourth_part(data):
        return None
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
        if data.get("no_pass") or not has_real_perfect_passive_stem(data):
            return None
        stem = data["ppp"]
    elif kind == "fap":
        if "fap" in data and data["fap"] is None:
            return None
        # A future-only fourth part may supply the future participle, but
        # never a perfect passive. Ordinary PPPs supply the regular -ūr form.
        stem = _future_stem(data.get("fap")) or _future_stem(data.get("ppp"))
        if not stem and has_real_perfect_passive_stem(data):
            stem = data["ppp"] + "ūr"
        if not stem:
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
    # Accept traditional compact entries without the separator: dictus3,
    # dictūrus3, dicendus3 (also punctuation after the numeral).
    if entry["kind"] == "three" and len(given) == 1 and given[0].endswith("3"):
        given = [given[0][:-1], "3"]
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
