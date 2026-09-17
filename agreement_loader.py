from pathlib import Path
from itertools import permutations
from agreement_middle_patch import apply_middle_mode
from agreement_weight_patch import apply_pair_weighting


def apply_multiple_answer_hint(source):
    old = '''        if len(adjective_forms) > 1:\n            if st.session_state[widget_key(page_id, "indicate_multiple_answers")]:\n                supplementary.append('<span style="color:#7c3aed;">Több helyes válaszlehetőség van.</span>')\n            else:\n                supplementary.append("Több helyes válaszlehetőség is lehet.")\n'''
    new = '''        if st.session_state[widget_key(page_id, "indicate_multiple_answers")]:\n            if len(adjective_forms) > 1:\n                supplementary.append('<span style="color:#7c3aed;">Több helyes válaszlehetőség is van.</span>')\n        else:\n            supplementary.append("Több helyes válaszlehetőség is lehet.")\n'''
    if old not in source:
        raise RuntimeError("Could not locate agreement multiple-answer hint block")
    return source.replace(old, new, 1)


def apply_weak_istem_is_ambiguity(source):
    old_answers = '''        adjective_forms.sort(key=lambda value: value.casefold())\n        answer_options = [" ".join(items) for items in permutations(adjective_forms)] if adjective_forms else []\n        st.session_state.correct_answer = answer_options\n'''
    new_answers = '''        adjective_forms.sort(key=lambda value: value.casefold())\n        canonical_adjective_forms = list(adjective_forms)\n        accepted_token_sets = {frozenset(form.casefold() for form in adjective_forms)} if adjective_forms else set()\n\n        weak_istem_is_ambiguity = (\n            noun_vocab[noun].get("decl") == "3_istem"\n            and ("sg", "gen") in matching_analyses\n            and ("pl", "acc") in matching_analyses\n        )\n        if weak_istem_is_ambiguity:\n            def _am_forms_for_analysis(number, case):\n                forms = []\n                seen = set()\n                raw = _am_adjective_form(adjective, case, gender, number)\n                for item in _am_forms_list(raw):\n                    rendered = _am_surface(item, print_macrons)\n                    key = rendered.casefold()\n                    if key not in seen:\n                        seen.add(key)\n                        forms.append(rendered)\n                return forms\n\n            sg_gen_forms = _am_forms_for_analysis("sg", "gen")\n            pl_acc_forms = _am_forms_for_analysis("pl", "acc")\n            canonical_adjective_forms = sg_gen_forms or list(adjective_forms)\n\n            special_forms = []\n            special_seen = set()\n            for form in sg_gen_forms + pl_acc_forms:\n                key = form.casefold()\n                if key not in special_seen:\n                    special_seen.add(key)\n                    special_forms.append(form)\n\n            accepted_token_sets = {frozenset([form.casefold()]) for form in special_forms}\n            for primary in sg_gen_forms:\n                for optional in pl_acc_forms:\n                    accepted_token_sets.add(frozenset([primary.casefold(), optional.casefold()]))\n            if special_forms:\n                accepted_token_sets.add(frozenset(form.casefold() for form in special_forms))\n\n            surface_by_key = {form.casefold(): form for form in special_forms}\n            answer_options = []\n            for accepted_set in accepted_token_sets:\n                values = [surface_by_key[key] for key in accepted_set]\n                answer_options.extend(" ".join(items) for items in permutations(values))\n        else:\n            answer_options = [" ".join(items) for items in permutations(adjective_forms)] if adjective_forms else []\n\n        st.session_state.correct_answer = answer_options\n'''
    if old_answers not in source:
        raise RuntimeError("Could not locate agreement answer-option block")
    source = source.replace(old_answers, new_answers, 1)

    old_check = '''                required = {form.casefold() for form in adjective_forms}\n                supplied = {\n                    _am_surface(token, print_macrons).casefold()\n                    for token in answer_tokens\n                }\n                partial = bool(supplied & required) and supplied != required\n'''
    new_check = '''                required = {form.casefold() for form in canonical_adjective_forms}\n                supplied = {\n                    _am_surface(token, print_macrons).casefold()\n                    for token in answer_tokens\n                }\n                accepted = frozenset(supplied) in accepted_token_sets\n                all_accepted_tokens = set().union(*(set(items) for items in accepted_token_sets)) if accepted_token_sets else set()\n                partial = bool(supplied & all_accepted_tokens) and not accepted\n'''
    if old_check not in source:
        raise RuntimeError("Could not locate agreement answer-check block")
    source = source.replace(old_check, new_check, 1)

    old_success = '''                    if supplied == required:\n'''
    new_success = '''                    if accepted:\n'''
    if old_success not in source:
        raise RuntimeError("Could not locate agreement success condition")
    source = source.replace(old_success, new_success, 1)

    source = source.replace(
        '''                        correct_text = " ".join(adjective_forms)\n''',
        '''                        correct_text = " ".join(canonical_adjective_forms)\n''',
        2,
    )
    return source


stage = Path(__file__).with_name("agreement_stage.py").read_text(encoding="utf-8")
needle = 'exec(compile(source, str(Path(__file__).with_name("agreement_impl.py")), "exec"))'
replacement = (
    'source = apply_middle_mode(source)\n'
    'source = apply_pair_weighting(source)\n'
    'source = apply_multiple_answer_hint(source)\n'
    'source = apply_weak_istem_is_ambiguity(source)\n'
    + needle
)
if needle not in stage:
    raise RuntimeError("Could not locate agreement stage execution point")
stage = stage.replace(needle, replacement, 1)
exec(compile(stage, str(Path(__file__).with_name("agreement_stage.py")), "exec"))
