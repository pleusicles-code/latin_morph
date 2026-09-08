from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()
old = '                4: {"sg": {"gen": "ūs",\n                           "dat": ["uī","ū"],'
new = '                4: {"sg": {"gen": "ūs",\n                           "dat": "uī",'
if text.count(old) != 1:
    raise RuntimeError(f"Expected ordinary 4th-declension dative once, found {text.count(old)}")
path.write_text(text.replace(old, new, 1))
