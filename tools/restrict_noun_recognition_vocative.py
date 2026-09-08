from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()

anchor = '''    def build_dictionary_entry(noun):
        genitive = build_noun([noun, "gen", "sg"])
        gender = noun_vocab[noun]["gender"]
        if isinstance(genitive, list):
            genitive = "/".join(genitive)
        if genitive:
            return f"{noun}, {genitive} {gender}."
        return f"{noun} {gender}."

    def recognition_gen_question():
'''
replacement = '''    def build_dictionary_entry(noun):
        genitive = build_noun([noun, "gen", "sg"])
        gender = noun_vocab[noun]["gender"]
        if isinstance(genitive, list):
            genitive = "/".join(genitive)
        if genitive:
            return f"{noun}, {genitive} {gender}."
        return f"{noun} {gender}."

    def recognition_cases_for_noun(noun, number):
        """Return cases used in noun recognition, with vocative only when distinctive."""
        cases = [case for case in noun_options["case"] if case != "voc"]
        if number != "sg":
            return cases

        noun_data = noun_vocab[noun]
        if not str(noun_data.get("decl", "")).startswith("2") or noun_data.get("gender") != "m":
            return cases

        nominative = build_noun([noun, "nom", "sg"])
        vocative = build_noun([noun, "voc", "sg"])
        if vocative is None:
            return cases

        nominative_forms = set(nominative if isinstance(nominative, list) else [nominative])
        vocative_forms = set(vocative if isinstance(vocative, list) else [vocative])
        if vocative_forms != nominative_forms:
            cases.append("voc")
        return cases

    def recognition_gen_question():
'''
if text.count(anchor) != 1:
    raise RuntimeError(f"Expected build_dictionary_entry anchor once, found {text.count(anchor)}")
text = text.replace(anchor, replacement, 1)

old_loop = '''        for possible_number in noun_options["number"]:
            for possible_case in noun_options["case"]:
                possible_form = build_noun([noun, possible_case, possible_number])
'''
new_loop = '''        for possible_number in noun_options["number"]:
            for possible_case in recognition_cases_for_noun(noun, possible_number):
                possible_form = build_noun([noun, possible_case, possible_number])
'''
if text.count(old_loop) != 1:
    raise RuntimeError(f"Expected generator recognition loop once, found {text.count(old_loop)}")
text = text.replace(old_loop, new_loop, 1)

old_match_loop = '''            for possible_number in noun_options["number"]:
                for possible_case in noun_options["case"]:
                    possible_form = build_noun([noun, possible_case, possible_number])
'''
new_match_loop = '''            for possible_number in noun_options["number"]:
                for possible_case in recognition_cases_for_noun(noun, possible_number):
                    possible_form = build_noun([noun, possible_case, possible_number])
'''
if text.count(old_match_loop) != 1:
    raise RuntimeError(f"Expected matching-analysis loop once, found {text.count(old_match_loop)}")
text = text.replace(old_match_loop, new_match_loop, 1)

path.write_text(text)
