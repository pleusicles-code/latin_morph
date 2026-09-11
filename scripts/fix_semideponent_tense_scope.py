from pathlib import Path

path = Path('verbs.py')
text = path.read_text()

old = '''    def gen_verb_id():
        avail_tenses = list(tense_list)
        # With pass. only, semideponents contribute only their deponent
        # perfect-system forms. Their active present-system forms are hidden.
        if verb_vocab.get(verb, {}).get("voice") == "semidep" and "act" not in voice_selector:
            avail_tenses = [tense for tense in avail_tenses if tense in perf_sys]
        avail_moods = dict(mood_list)
'''
new = '''    def gen_verb_id():
        avail_tenses = list(tense_list)
        avail_moods = dict(mood_list)
'''
if text.count(old) != 1:
    raise SystemExit(f'Expected misplaced semideponent block once, found {text.count(old)}')
text = text.replace(old, new)

old = '''        if len(avail_verbs) > 0:
            verb = random.choice(avail_verbs)
        else:
            verb = random.choice(list(verb_vocab.keys()))

     #    verb = "eō"    ## UNCOMMENT AND SET FOR TESTING

        # SET MOOD
'''
new = '''        if len(avail_verbs) > 0:
            verb = random.choice(avail_verbs)
        else:
            verb = random.choice(list(verb_vocab.keys()))

        # With pass. only, semideponents contribute only their deponent
        # perfect-system forms. Their active present-system forms are hidden.
        if verb_vocab.get(verb, {}).get("voice") == "semidep" and "act" not in voice_selector:
            avail_tenses = [tense for tense in avail_tenses if tense in perf_sys]

     #    verb = "eō"    ## UNCOMMENT AND SET FOR TESTING

        # SET MOOD
'''
if text.count(old) != 1:
    raise SystemExit(f'Expected verb-selection block once, found {text.count(old)}')
text = text.replace(old, new)

compile(text, 'verbs.py', 'exec')
path.write_text(text)
