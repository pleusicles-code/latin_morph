from pathlib import Path

path = Path(__file__).resolve().parents[1] / "utils.py"
text = path.read_text()

old_import = "import unicodedata\nimport os\n"
new_import = "import unicodedata\nimport re\nimport os\n"
if text.count(old_import) != 1:
    raise RuntimeError(f"Expected one import anchor, found {text.count(old_import)}")
text = text.replace(old_import, new_import, 1)

anchor = '''def remove_macrons(text):
    for macron, vowel in {"ā": "a",
                        "ē": "e",
                        "ī": "i",
                        "ō": "o",
                        "ū": "u"}.items():
        if macron in text:
            text = text.replace(macron, vowel)
    return text

'''

addition = '''def remove_macrons(text):
    for macron, vowel in {"ā": "a",
                        "ē": "e",
                        "ī": "i",
                        "ō": "o",
                        "ū": "u"}.items():
        if macron in text:
            text = text.replace(macron, vowel)
    return text


def tokenize_morphology_answer(text):
    """Return lowercase alphabetic tokens from a morphology-analysis answer.

    All non-letter characters are treated purely as separators. Grammatical
    interpretation and alias normalization (e.g. ``sing`` -> ``sg``) belong
    to exercise-specific parsers built on top of this tokenizer.
    """
    if not isinstance(text, str):
        return []
    return re.findall(r"[^\\W\\d_]+", text.casefold(), flags=re.UNICODE)

'''

if text.count(anchor) != 1:
    raise RuntimeError(f"Expected one remove_macrons block, found {text.count(anchor)}")
text = text.replace(anchor, addition, 1)
path.write_text(text)
