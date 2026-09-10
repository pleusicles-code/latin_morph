from pathlib import Path

path = Path('verbs.py')
text = path.read_text()

old = '''def normalize_verb_morphology_tokens(text):
    """Normalize recognized verb-analysis tokens; ignore unrecognized tokens.

    Exact-token lookup keeps ``imper`` distinct from the imperfect alias ``imp``.
    Future/second imperatives are not distinguished yet.
    """
    return [
        VERB_MORPHOLOGY_ALIASES[token]
        for token in tokenize_morphology_answer(text)
        if token in VERB_MORPHOLOGY_ALIASES
    ]
'''

new = '''VERB_MORPHOLOGY_SOURCE_TOKENS = tuple(
    sorted(VERB_MORPHOLOGY_ALIASES, key=len, reverse=True)
)


def segment_verb_morphology_token(token):
    """Fully segment one tokenizer token into known verb-analysis tokens."""
    memo = {}

    def segment_from(index):
        if index == len(token):
            return []
        if index in memo:
            return memo[index]
        for candidate in VERB_MORPHOLOGY_SOURCE_TOKENS:
            if token.startswith(candidate, index):
                remainder = segment_from(index + len(candidate))
                if remainder is not None:
                    memo[index] = [candidate] + remainder
                    return memo[index]
        memo[index] = None
        return None

    return segment_from(0)


def recognized_verb_morphology_tokens(text):
    """Return recognized source tokens in input order, including concatenated forms."""
    recognized = []
    for raw_token in tokenize_morphology_answer(text):
        pieces = segment_verb_morphology_token(raw_token)
        if pieces is not None:
            recognized.extend(pieces)
    return recognized


def normalize_verb_morphology_tokens(text):
    """Normalize recognized verb-analysis tokens, including concatenated forms.

    Longest-first segmentation ensures ``imper`` is tried before the imperfect
    alias ``imp``. Future/second imperatives are not distinguished yet.
    """
    return [
        VERB_MORPHOLOGY_ALIASES[token]
        for token in recognized_verb_morphology_tokens(text)
    ]
'''

if text.count(old) != 1:
    raise SystemExit(f'Expected exactly one normalization block, found {text.count(old)}')
text = text.replace(old, new)

old_feedback = '''                        recognized_tokens = [
                            token for token in tokenize_morphology_answer(user_answer)
                            if token in VERB_MORPHOLOGY_ALIASES
                        ]
'''
new_feedback = '''                        recognized_tokens = recognized_verb_morphology_tokens(user_answer)
'''
if text.count(old_feedback) != 1:
    raise SystemExit(f'Expected exactly one recognition feedback block, found {text.count(old_feedback)}')
text = text.replace(old_feedback, new_feedback)

compile(text, 'verbs.py', 'exec')
path.write_text(text)

# Lightweight segmentation tests using the same alias keys.
alias_keys = {
    "praesens", "praes", "praeteritum", "praet", "futurum", "fut",
    "imperfectum", "impf", "imp", "perfectum", "perf",
    "activum", "activi", "act", "passivum", "passivi", "pass",
    "indicativus", "ind", "coniunctivus", "coni", "imperativus", "imper",
    "singularis", "sing", "sg", "pluralis", "plur", "pl", "1", "2", "3",
}
source_tokens = tuple(sorted(alias_keys, key=len, reverse=True))

def segment(token):
    memo = {}
    def from_index(index):
        if index == len(token):
            return []
        if index in memo:
            return memo[index]
        for candidate in source_tokens:
            if token.startswith(candidate, index):
                remainder = from_index(index + len(candidate))
                if remainder is not None:
                    memo[index] = [candidate] + remainder
                    return memo[index]
        memo[index] = None
        return None
    return from_index(0)

assert segment('praesperfconipasssg') == ['praes', 'perf', 'coni', 'pass', 'sg']
assert segment('praesimpfindactsg') == ['praes', 'impf', 'ind', 'act', 'sg']
assert segment('imperpl') == ['imper', 'pl']
assert segment('impsg') == ['imp', 'sg']
