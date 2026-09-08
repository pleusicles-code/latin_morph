from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()
replacements = {
    'f":green-background[The correct answer is: {all_possible_text}]"':
        'f":green-background[**The correct answer is: {all_possible_text}**]"',
    'f":red-background[Correct: {all_possible_text}]"':
        'f":red-background[**Correct: {all_possible_text}**]"',
}
for old, new in replacements.items():
    if text.count(old) != 1:
        raise RuntimeError(f"Expected feedback fragment once: {old!r}; found {text.count(old)}")
    text = text.replace(old, new, 1)
path.write_text(text)
