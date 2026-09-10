from pathlib import Path

path = Path('verbs.py')
s = path.read_text()

old = '''    # The identify-stems exercise uses perfect + supine for ordinary active verbs.\n    if data.get("voice") == "act":\n        if conj == 1 and not data.get("irreg"):\n            return head\n'''
new = '''    # For regular 1st-conjugation verbs, the compact dictionary entry is just lemma + conjugation.\n    if conj == 1 and not data.get("irreg"):\n        return head\n\n    # The identify-stems exercise uses perfect + supine for ordinary active verbs.\n    if data.get("voice") == "act":\n'''
if old not in s:
    raise SystemExit('dictionary-entry target not found')
s = s.replace(old, new, 1)

old = '''        voice_label = {\n            "act": "act.",\n            "pass": "pass.",\n            "dep": "deponens",\n            "semidep": "semideponens",\n        }.get(voice, str(voice))\n'''
new = '''        voice_label = "" if voice in ["dep", "semidep"] else {\n            "act": "act.",\n            "pass": "pass.",\n        }.get(voice, str(voice))\n'''
if old not in s:
    raise SystemExit('voice-label target not found')
s = s.replace(old, new, 1)

compile(s, 'verbs.py', 'exec')
path.write_text(s)
