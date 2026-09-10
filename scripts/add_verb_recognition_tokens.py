from pathlib import Path

utils_path = Path('utils.py')
utils = utils_path.read_text()
old_utils = '''def tokenize_morphology_answer(text):
    """Return lowercase alphabetic tokens from a morphology-analysis answer.

    All non-letter characters are treated purely as separators. Grammatical
    interpretation and alias normalization (e.g. ``sing`` -> ``sg``) belong
    to exercise-specific parsers built on top of this tokenizer.
    """
    if not isinstance(text, str):
        return []
    return re.findall(r"[^\\W\\d_]+", text.casefold(), flags=re.UNICODE)
'''
new_utils = '''def tokenize_morphology_answer(text):
    """Return lowercase word tokens and standalone person digits 1-3.

    All other non-letter/digit characters are treated purely as separators.
    Grammatical interpretation and alias normalization belong to
    exercise-specific parsers built on top of this tokenizer.
    """
    if not isinstance(text, str):
        return []
    return re.findall(r"[^\\W\\d_]+|[1-3]", text.casefold(), flags=re.UNICODE)
'''
if utils.count(old_utils) != 1:
    raise SystemExit(f'Expected exactly one tokenizer block, found {utils.count(old_utils)}')
utils = utils.replace(old_utils, new_utils)
compile(utils, 'utils.py', 'exec')
utils_path.write_text(utils)

verbs_path = Path('verbs.py')
verbs = verbs_path.read_text()
old_import = 'from utils import radio_change, reset, new_question, remove_macrons, submit_and_check_answer, clear_page, send_setting, save_defaults, clear_defaults, auto_advance_delay\n'
new_import = 'from utils import radio_change, reset, new_question, remove_macrons, submit_and_check_answer, clear_page, send_setting, save_defaults, clear_defaults, auto_advance_delay, tokenize_morphology_answer\n'
if verbs.count(old_import) != 1:
    raise SystemExit(f'Expected exactly one utils import line, found {verbs.count(old_import)}')
verbs = verbs.replace(old_import, new_import)

anchor = '''def hungarian_article(word):
    normalized = "".join(
        char for char in unicodedata.normalize("NFD", str(word).lower())
        if unicodedata.category(char) != "Mn"
    )
    if not normalized or normalized[0] not in LATIN_VOWELS:
        return "a"
    if len(normalized) > 1 and normalized[1] in LATIN_VOWELS:
        return "az" if normalized[:2] in LATIN_DIPHTHONGS else "a"
    return "az"


'''
addition = '''VERB_MORPHOLOGY_ALIASES = {
    # relative tense
    "praesens": ("relative_tense", "pres"),
    "praes": ("relative_tense", "pres"),
    "praeteritum": ("relative_tense", "past"),
    "praet": ("relative_tense", "past"),
    "futurum": ("relative_tense", "fut"),
    "fut": ("relative_tense", "fut"),
    # aspect
    "imperfectum": ("aspect", "impf"),
    "impf": ("aspect", "impf"),
    "imp": ("aspect", "impf"),
    "perfectum": ("aspect", "perf"),
    "perf": ("aspect", "perf"),
    # voice
    "activum": ("voice", "act"),
    "activi": ("voice", "act"),
    "act": ("voice", "act"),
    "passivum": ("voice", "pass"),
    "passivi": ("voice", "pass"),
    "pass": ("voice", "pass"),
    # mood
    "indicativus": ("mood", "ind"),
    "ind": ("mood", "ind"),
    "coniunctivus": ("mood", "subj"),
    "coni": ("mood", "subj"),
    "imperativus": ("mood", "impv"),
    "imper": ("mood", "impv"),
    # number
    "singularis": ("number", "sg"),
    "sing": ("number", "sg"),
    "sg": ("number", "sg"),
    "pluralis": ("number", "pl"),
    "plur": ("number", "pl"),
    "pl": ("number", "pl"),
    # person
    "1": ("person", "1"),
    "2": ("person", "2"),
    "3": ("person", "3"),
}


def normalize_verb_morphology_tokens(text):
    """Normalize recognized verb-analysis tokens; ignore unrecognized tokens.

    Exact-token lookup keeps ``imper`` distinct from the imperfect alias ``imp``.
    Future/second imperatives are not distinguished yet.
    """
    return [
        VERB_MORPHOLOGY_ALIASES[token]
        for token in tokenize_morphology_answer(text)
        if token in VERB_MORPHOLOGY_ALIASES
    ]


'''
if verbs.count(anchor) != 1:
    raise SystemExit(f'Expected exactly one Hungarian article anchor, found {verbs.count(anchor)}')
verbs = verbs.replace(anchor, anchor + addition)
compile(verbs, 'verbs.py', 'exec')
verbs_path.write_text(verbs)

# Lightweight tokenizer/alias checks without importing Streamlit application modules.
import re

def tok(text):
    return re.findall(r"[^\\W\\d_]+|[1-3]", text.casefold(), flags=re.UNICODE)

assert tok('praes. impf. ind. pass. sg. 2') == ['praes', 'impf', 'ind', 'pass', 'sg', '2']
assert tok('imper. 2') == ['imper', '2']
assert tok('imp. 2') == ['imp', '2']
assert VERB_MORPHOLOGY_ALIASES['imper'] == ('mood', 'impv')
assert VERB_MORPHOLOGY_ALIASES['imp'] == ('aspect', 'impf')
