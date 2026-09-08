from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()

old = '''    if not normalized_tokens:
        return {
            "valid": False,
            "tokens": [],
            "analyses": set(),
            "error": "no grammatical tokens found",
        }

    analyses = set()
'''
new = '''    if not normalized_tokens:
        return {
            "valid": False,
            "tokens": [],
            "analyses": set(),
            "error": "no grammatical tokens found",
        }

    # A distinctive noun vocative can only be singular, so allow the
    # pedagogically natural shorthand "voc" / "voc." and normalize it.
    if normalized_tokens == ["voc"]:
        normalized_tokens = ["sg", "voc"]

    analyses = set()
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected parser insertion anchor once, found {text.count(old)}")
path.write_text(text.replace(old, new, 1))
