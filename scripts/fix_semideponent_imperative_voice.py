from pathlib import Path

path = Path('verbs.py')
text = path.read_text()
old = '''        elif lexical_voice == "semidep":
            expected_voice = "act" if analysis["aspect"] == "impf" else "pass"
            if analysis.get("voice") not in [None, expected_voice]:
                return {"valid": False, "analyses": [], "error": "invalid semideponent voice"}
'''
new = '''        elif lexical_voice == "semidep":
            if analysis.get("mood") == "impv":
                expected_voice = "act"
            else:
                expected_voice = "act" if analysis.get("aspect") == "impf" else "pass"
            if analysis.get("voice") not in [None, expected_voice]:
                return {"valid": False, "analyses": [], "error": "invalid semideponent voice"}
'''
if text.count(old) != 1:
    raise SystemExit(f'Expected semideponent voice block once, found {text.count(old)}')
text = text.replace(old, new)
compile(text, 'verbs.py', 'exec')
path.write_text(text)
