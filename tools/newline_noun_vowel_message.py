from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()
old = '            question += f" Vowel lengths {vowel_phrase} indicated"\n'
new = '            question += f"  \\nVowel lengths {vowel_phrase} indicated"\n'
if text.count(old) != 1:
    raise RuntimeError(f"Expected one vowel guidance line, found {text.count(old)}")
path.write_text(text.replace(old, new, 1))
