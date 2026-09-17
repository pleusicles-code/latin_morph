from pathlib import Path
from itertools import permutations
from agreement_middle_patch import apply_middle_mode
from agreement_weight_patch import apply_pair_weighting

stage = Path(__file__).with_name("agreement_stage.py").read_text(encoding="utf-8")
needle = 'exec(compile(source, str(Path(__file__).with_name("agreement_impl.py")), "exec"))'
replacement = (
    'source = apply_middle_mode(source)\n'
    'source = apply_pair_weighting(source)\n'
    + needle
)
if needle not in stage:
    raise RuntimeError("Could not locate agreement stage execution point")
stage = stage.replace(needle, replacement, 1)
exec(compile(stage, str(Path(__file__).with_name("agreement_stage.py")), "exec"))
