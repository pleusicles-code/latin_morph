from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()

# Conditional nominative weighting in the ordinary generator.
old = '''        if number == "sg":
            case_weights = [1,9,9,9,9]
            # if decl_rand == "2nd":
'''
new = '''        if number == "sg":
            nom_weight = 1 if is_diagnostic_sg_nom(noun, st.session_state.nouns_enforce_macrons) else 9
            case_weights = [nom_weight,9,9,9,9]
            # if decl_rand == "2nd":
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected ordinary singular case-weight block once, found {text.count(old)}")
text = text.replace(old, new, 1)

# Conditional nominative weighting in the adaptive fallback generator.
old = '''                    if number == "sg" and noun != "deus":
                        case_weights = [1,9,9,9,9]
                        if decl == "2_us":
'''
new = '''                    if number == "sg" and noun != "deus":
                        nom_weight = 1 if is_diagnostic_sg_nom(noun, st.session_state.nouns_enforce_macrons) else 9
                        case_weights = [nom_weight,9,9,9,9]
                        if decl == "2_us":
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected adaptive singular case-weight block once, found {text.count(old)}")
text = text.replace(old, new, 1)

# Add shared diagnostic helper after the recognition-eligible case helper.
anchor = '''        if vocative_forms != nominative_forms:
            cases.append("voc")
        return cases

    def recognition_gen_question():
'''
replacement = '''        if vocative_forms != nominative_forms:
            cases.append("voc")
        return cases

    def is_diagnostic_sg_nom(noun, preserve_macrons):
        """Whether the displayed sg. nom. has no other recognition-eligible analysis."""
        nominative = build_noun([noun, "nom", "sg"])
        nominative_forms = nominative if isinstance(nominative, list) else [nominative]
        displayed_nominatives = {
            form if preserve_macrons else remove_macrons(form)
            for form in nominative_forms
            if form is not None
        }

        analyses = set()
        for possible_number in noun_options["number"]:
            for possible_case in recognition_cases_for_noun(noun, possible_number):
                possible_form = build_noun([noun, possible_case, possible_number])
                if possible_form is None:
                    continue
                possible_forms = possible_form if isinstance(possible_form, list) else [possible_form]
                for form in possible_forms:
                    displayed = form if preserve_macrons else remove_macrons(form)
                    if displayed in displayed_nominatives:
                        analyses.add((possible_number, possible_case))
                        break

        return analyses == {("sg", "nom")}

    def recognition_gen_question():
'''
if text.count(anchor) != 1:
    raise RuntimeError(f"Expected recognition helper anchor once, found {text.count(anchor)}")
text = text.replace(anchor, replacement, 1)

# Weight recognition forms 1:9 only when the displayed form is uniquely sg. nom.
old = '''        displayed_form = random.choice(list(form_analyses))
        case, number = random.choice(list(form_analyses[displayed_form]))
'''
new = '''        displayed_forms = list(form_analyses)
        diagnostic_nom = is_diagnostic_sg_nom(noun, print_macrons)
        displayed_nom = noun if print_macrons else remove_macrons(noun)
        form_weights = [
            1 if diagnostic_nom and form == displayed_nom else 9
            for form in displayed_forms
        ]
        displayed_form = random.choices(displayed_forms, weights=form_weights, k=1)[0]
        case, number = random.choice(list(form_analyses[displayed_form]))
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected recognition form selection once, found {text.count(old)}")
text = text.replace(old, new, 1)

path.write_text(text)
