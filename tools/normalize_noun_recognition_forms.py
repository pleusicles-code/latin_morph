from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()

old_import = "import ast\n"
new_import = "import ast\nimport unicodedata\n"
if text.count(old_import) != 1:
    raise RuntimeError(f"Expected import anchor once, found {text.count(old_import)}")
text = text.replace(old_import, new_import, 1)

anchor = '''    def recognition_cases_for_noun(noun, number):
        """Return cases used in noun recognition, with vocative only when distinctive."""
'''
replacement = '''    def normalize_noun_surface(form, preserve_macrons):
        """Normalize a generated/displayed noun form before morphology comparisons."""
        normalized = unicodedata.normalize("NFC", form)
        return normalized if preserve_macrons else remove_macrons(normalized)

    def recognition_cases_for_noun(noun, number):
        """Return cases used in noun recognition, with vocative only when distinctive."""
'''
if text.count(anchor) != 1:
    raise RuntimeError(f"Expected recognition-case anchor once, found {text.count(anchor)}")
text = text.replace(anchor, replacement, 1)

old = '''        displayed_nominatives = {
            form if preserve_macrons else remove_macrons(form)
            for form in nominative_forms
            if form is not None
        }
'''
new = '''        displayed_nominatives = {
            normalize_noun_surface(form, preserve_macrons)
            for form in nominative_forms
            if form is not None
        }
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected nominative normalization block once, found {text.count(old)}")
text = text.replace(old, new, 1)

old = '''                    displayed = form if preserve_macrons else remove_macrons(form)
                    if displayed in displayed_nominatives:
'''
new = '''                    displayed = normalize_noun_surface(form, preserve_macrons)
                    if displayed in displayed_nominatives:
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected diagnostic comparison once, found {text.count(old)}")
text = text.replace(old, new, 1)

old = '''                    displayed = form if print_macrons else remove_macrons(form)
                    form_analyses.setdefault(displayed, set()).add((possible_case, possible_number))
'''
new = '''                    displayed = normalize_noun_surface(form, print_macrons)
                    form_analyses.setdefault(displayed, set()).add((possible_case, possible_number))
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected recognition grouping comparison once, found {text.count(old)}")
text = text.replace(old, new, 1)

old = '''        displayed_nom = noun if print_macrons else remove_macrons(noun)
'''
new = '''        displayed_nom = normalize_noun_surface(noun, print_macrons)
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected displayed nominative once, found {text.count(old)}")
text = text.replace(old, new, 1)

old = '''            comparable_displayed_form = displayed_form if print_macrons else remove_macrons(displayed_form)
'''
new = '''            comparable_displayed_form = normalize_noun_surface(displayed_form, print_macrons)
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected displayed-form comparison once, found {text.count(old)}")
text = text.replace(old, new, 1)

old = '''                        comparable_form = form if print_macrons else remove_macrons(form)
                        if comparable_form == comparable_displayed_form:
'''
new = '''                        comparable_form = normalize_noun_surface(form, print_macrons)
                        if comparable_form == comparable_displayed_form:
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected generated-form comparison once, found {text.count(old)}")
text = text.replace(old, new, 1)

path.write_text(text)
