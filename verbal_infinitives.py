"""Infinitive paradigms for BevLat's verbal-noun exercises.

All six conventional active/passive forms for regular verbs, restricted to
attested/derivable forms for deponent, semideponent and defective verbs.
"""
import unicodedata

from verbal_principal_forms import has_real_perfect_passive_stem


ALL_INFINITIVE_TYPES = (
    "inf_impf_act",
    "inf_impf_pass",
    "inf_perf_act",
    "inf_perf_pass",
    "inf_inst_act",
    "inf_inst_pass",
)

def expand_selected_form_types(selected):
    """Expand 'inf_all' without requiring or duplicating 'inf_impf_act'."""
    return list(dict.fromkeys(
        [kind for kind in selected if kind != "inf_all"]
        + (list(ALL_INFINITIVE_TYPES) if "inf_all" in selected else [])
    ))


PRESENT_ACTIVE_VOWELS = {1: "ā", 2: "ē", 3: "e", "3io": "e", 4: "ī"}
PRESENT_PASSIVE_ENDINGS = {1: "ārī", 2: "ērī", 3: "ī", "3io": "ī", 4: "īrī"}


def infinitive_paradigm(lemma, data):
    """Map each available infinitive type to its accepted spellings.

    Infinitives with a finite stem missing are omitted, rather than fabricated.
    Perfect deponent forms occupy the morphological perfect-passive slot.
    """
    results = {}
    voice = data.get("voice")
    conj = data.get("conj")
    pres = data.get("pres")
    perf = data.get("perf")
    ppp = data.get("ppp")
    true_ppp = has_real_perfect_passive_stem(data)
    no_pass = data.get("no_pass", False)
    irregular = (data.get("irreg") or {}).get("forms", {})

    def irregular_inf(tense, kind):
        value = irregular.get(tense, {}).get(kind, {}).get("inf")
        return value if isinstance(value, str) and value else None

    def add(kind, *forms):
        values = list(dict.fromkeys(form for form in forms if isinstance(form, str) and form))
        if values:
            results[kind] = values

    if voice in ("act", "semidep"):
        if lemma != "fīō":
            active_present = irregular_inf("pres", "act")
            if not active_present and pres and conj in PRESENT_ACTIVE_VOWELS:
                active_present = pres + PRESENT_ACTIVE_VOWELS[conj] + "re"
            add("inf_impf_act", active_present)
    if voice in ("act", "dep", "semidep"):
        if voice == "dep" or lemma == "fīō":
            passive_present = irregular_inf("pres", "dep") or irregular_inf("pres", "pass")
        else:
            passive_present = irregular_inf("pres", "pass")
        if not passive_present and voice == "act" and not no_pass and not data.get("impers_pass_only"):
            if lemma == "faciō":
                passive_present = "fierī"
            elif pres and conj in PRESENT_PASSIVE_ENDINGS:
                passive_present = pres + PRESENT_PASSIVE_ENDINGS[conj]
        if not passive_present and voice == "dep" and pres and conj in PRESENT_PASSIVE_ENDINGS:
            passive_present = pres + PRESENT_PASSIVE_ENDINGS[conj]
        add("inf_impf_pass", passive_present)

    if voice == "act" and isinstance(perf, str) and perf:
        normal = irregular_inf("perf", "act") or perf + "isse"
        variants = [normal]
        if perf.endswith("īv"):
            shorter = perf[:-2] + "iisse"
            variants.append(shorter)
            variants.append(shorter.replace("iis", "īs"))
        add("inf_perf_act", *variants)

    if true_ppp and (voice in ("dep", "semidep") or (voice == "act" and not no_pass)):
        add(
            "inf_perf_pass",
            irregular_inf("perf", "dep") or irregular_inf("perf", "pass") or (ppp + "um esse"),
            ppp + "us esse", ppp + "a esse",
        )

    future_stem = None
    fap = data.get("fap")
    if isinstance(fap, str) and fap:
        normalized = "".join(c for c in unicodedata.normalize("NFD", fap.casefold())
                             if unicodedata.category(c) != "Mn")
        if normalized.endswith("urus"):
            future_stem = fap[:-2]
        elif normalized.endswith("ur"):
            future_stem = fap
    elif "fap" not in data and true_ppp:
        future_stem = ppp + "ūr"

    if future_stem:
        future = irregular_inf("fut", "act") or irregular_inf("fut", "dep")
        add("inf_inst_act", future or (future_stem + "um esse"),
            future_stem + "us esse", future_stem + "a esse")

    if (voice == "act" and true_ppp and not no_pass) or (lemma == "fīō" and true_ppp):
        # fīō uses factum īrī as the future infinitive (as on the Igék page).
        add("inf_inst_pass", irregular_inf("fut", "pass") or (ppp + "um īrī"))

    if lemma == "sum" and "inf_inst_act" in results:
        add("inf_inst_act", *results["inf_inst_act"], "fore")

    return results
