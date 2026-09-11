from pathlib import Path

path = Path('verbs.py')
text = path.read_text()

def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 occurrence, found {count}')
    text = text.replace(old, new)

old = '''    analyses = []
    explicit_categories = {
        category for category, values in by_category.items() if values
    }
    for index in range(analysis_count):
        analysis = {
            "_explicit_categories": set(explicit_categories),
            "_explicit_second_imperative": explicit_second_imperative,
        }
        for category in VERB_ANALYSIS_CATEGORY_ORDER:
            values = by_category[category]
            if not values:
                continue
            analysis[category] = values[0] if len(values) == 1 else values[index]
        analyses.append(analysis)
'''
new = '''    analyses = []
    # Build tense/aspect and the other categories first. Mood needs one special
    # distribution rule below: an explicitly supplied subjunctive must not be
    # copied onto a parallel future analysis, because future finite forms are
    # unambiguously indicative.
    for index in range(analysis_count):
        analysis = {
            "_explicit_categories": set(),
            "_explicit_second_imperative": explicit_second_imperative,
        }
        for category in VERB_ANALYSIS_CATEGORY_ORDER:
            if category == "mood":
                continue
            values = by_category[category]
            if not values:
                continue
            analysis[category] = values[0] if len(values) == 1 else values[index]
            analysis["_explicit_categories"].add(category)
        analyses.append(analysis)

    mood_values = by_category["mood"]
    if mood_values:
        if (
            analysis_count > 1
            and len(mood_values) == 1
            and mood_values[0] == "subj"
            and any(analysis.get("relative_tense") == "fut" for analysis in analyses)
        ):
            nonfuture = [
                analysis for analysis in analyses
                if analysis.get("relative_tense") != "fut"
            ]
            if len(nonfuture) == 1:
                nonfuture[0]["mood"] = "subj"
                nonfuture[0]["_explicit_categories"].add("mood")
            else:
                # If more than one non-future analysis remains, the single mood
                # token is genuinely ambiguous, so retain the normal shared rule.
                for analysis in analyses:
                    analysis["mood"] = "subj"
                    analysis["_explicit_categories"].add("mood")
        else:
            for index, analysis in enumerate(analyses):
                analysis["mood"] = mood_values[0] if len(mood_values) == 1 else mood_values[index]
                analysis["_explicit_categories"].add("mood")
'''
replace_once(old, new, 'mood distribution')

old = '''    def spacer():
        return '<div aria-hidden="true" style="width:0.35rem;min-width:0.35rem;"></div>'
'''
new = '''    def spacer():
        return '<div aria-hidden="true" style="padding:0 0.16rem;color:#111;font-weight:700;white-space:nowrap;">/</div>'
'''
replace_once(old, new, 'analysis delimiter')

compile(text, 'verbs.py', 'exec')
path.write_text(text)
