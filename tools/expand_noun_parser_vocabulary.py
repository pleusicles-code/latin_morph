from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()

old = '''NOUN_ANALYSIS_TOKEN_ALIASES = {
    "sg": "sg",
    "sing": "sg",
    "pl": "pl",
    "plur": "pl",
    "nom": "nom",
    "voc": "voc",
    "acc": "acc",
    "gen": "gen",
    "dat": "dat",
    "abl": "abl",
}
'''
new = '''NOUN_ANALYSIS_TOKEN_ALIASES = {
    "sg": "sg",
    "sing": "sg",
    "singular": "sg",
    "singularis": "sg",
    "pl": "pl",
    "plur": "pl",
    "plural": "pl",
    "pluralis": "pl",
    "nom": "nom",
    "nominative": "nom",
    "nominativus": "nom",
    "voc": "voc",
    "vocative": "voc",
    "vocativus": "voc",
    "acc": "acc",
    "accusative": "acc",
    "accusativus": "acc",
    "gen": "gen",
    "genitive": "gen",
    "genitivus": "gen",
    "dat": "dat",
    "dative": "dat",
    "dativus": "dat",
    "abl": "abl",
    "ablative": "abl",
    "ablativus": "abl",
}
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected noun alias table once, found {text.count(old)}")
path.write_text(text.replace(old, new, 1))
