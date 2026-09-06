"""Reviewable metadata for nouns used by the morphology exercises.

Gender values are intentionally stored as short dictionary-style labels. The
code accepts combined values such as ``m/f`` for nouns used in more than one
gender.
"""

NOUN_GENDERS = {
    # 1st declension
    "puella": "f",
    "hōra": "f",
    "agricola": "m",
    "mēnsa": "f",
    "poena": "f",
    "silva": "f",
    "umbra": "f",
    "aqua": "f",
    "causa": "f",
    "anima": "f",
    "pecūnia": "f",
    "stēlla": "f",
    "fēmina": "f",
    "fīlia": "f",
    "dea": "f",

    # 2nd declension
    "servus": "m",
    "equus": "m",
    "fīlius": "m",
    "lupus": "m",
    "animus": "m",
    "annus": "m",
    "gladius": "m",
    "dolus": "m",
    "colōnus": "m",
    "dominus": "m",
    "nātus": "m",
    "amīcus": "m",
    "puer": "m",
    "vir": "m",
    "ager": "m",
    "liber": "m",
    "magister": "m",
    "culter": "m",
    "templum": "n",
    "verbum": "n",
    "iugum": "n",
    "beneficium": "n",
    "signum": "n",
    "bellum": "n",
    "regnum": "n",
    "saxum": "n",
    "somnium": "n",
    "dōnum": "n",

    # 3rd declension
    "leo": "m",
    "mīles": "m",
    "sōl": "m",
    "vōx": "f",
    "rēx": "m",
    "flōs": "m",
    "fūr": "m/f",
    "rūmor": "m",
    "homō": "m/f",
    "servitūs": "f",
    "cīvis": "m/f",
    "nāvis": "f",
    "urbs": "f",
    "mōns": "m",
    "aedis": "f",
    "ignis": "m",
    "nox": "f",
    "turris": "f",
    "nōmen": "n",
    "carmen": "n",
    "genus": "n",
    "lītus": "n",
    "onus": "n",
    "sīdus": "n",
    "caput": "n",
    "animal": "n",
    "mare": "n",
    "rēte": "n",
    "exemplar": "n",

    # 4th declension
    "manus": "f",
    "senātus": "m",
    "cāsus": "m",
    "ictus": "m",
    "gradus": "m",
    "exercitus": "m",
    "vultus": "m",
    "impetus": "m",
    "currus": "m",
    "sinus": "m",
    "metus": "m",
    "portus": "m",
    "frūctus": "m",
    "cornū": "n",
    "genū": "n",

    # 5th declension
    "rēs": "f",
    "diēs": "m/f",
    "faciēs": "f",
    "fidēs": "f",
    "spēs": "f",
    "aciēs": "f",
    "speciēs": "f",

    # irregular nouns
    "deus": "m",
    "vīs": "f",
    "bōs": "m/f",
}


def attach_noun_genders(noun_vocab):
    """Attach explicit gender metadata and fail loudly if coverage drifts."""
    missing = set(noun_vocab) - set(NOUN_GENDERS)
    extra = set(NOUN_GENDERS) - set(noun_vocab)
    if missing or extra:
        raise ValueError(
            f"Noun gender metadata mismatch. Missing: {sorted(missing)}; extra: {sorted(extra)}"
        )
    for noun, data in noun_vocab.items():
        data["gender"] = NOUN_GENDERS[noun]
    return noun_vocab
