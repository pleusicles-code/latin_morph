from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()
old = 'f":green-background[{all_possible_text}]"'
new = 'f":green-background[The correct answer is: {all_possible_text}]"'
if text.count(old) != 1:
    raise RuntimeError(f"Expected correct-answer feedback once, found {text.count(old)}")
path.write_text(text.replace(old, new, 1))
