from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()
old = '        noun, _, _ = gen_question()\n'
new = '        noun, _, _ = adap_gen_question()\n'
if text.count(old) != 1:
    raise RuntimeError(f"Expected one recognition noun selector, found {text.count(old)}")
path.write_text(text.replace(old, new, 1))
