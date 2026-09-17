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


stage = Path(__file__).with_name("agreement_stage.py").read_text(encoding="utf-8")
needle = 'exec(compile(source, str(Path(__file__).with_name("agreement_impl.py")), "exec"))'
replacement = (
    'source = apply_middle_mode(source)\n'
    'source = apply_pair_weighting(source)\n'
    'source = apply_multiple_answer_hint(source)\n'
    + needle
)
if needle not in stage:
    raise RuntimeError("Could not locate agreement stage execution point")
stage = stage.replace(needle, replacement, 1)
exec(compile(stage, str(Path(__file__).with_name("agreement_stage.py")), "exec"))
