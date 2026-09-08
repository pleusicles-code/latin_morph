from pathlib import Path

path = Path(__file__).resolve().parents[1] / "nouns.py"
text = path.read_text()

anchor = '''noun_options = {"case": {"nom": "nominative",
                         "gen": "genitive",
                         "dat": "dative",
                         "acc": "accusative",
                         "abl": "ablative",
                         "voc": "vocative"},
                "number": {"sg": "singular",
                           "pl": "plural"}}

'''

insert = '''noun_options = {"case": {"nom": "nominative",
                         "gen": "genitive",
                         "dat": "dative",
                         "acc": "accusative",
                         "abl": "ablative",
                         "voc": "vocative"},
                "number": {"sg": "singular",
                           "pl": "plural"}}


NOUN_ANALYSIS_TOKEN_ALIASES = {
    "sg": "sg",
    "sing": "sg",
    "pl": "pl",
    "plur": "pl",
    "nom": "nom",
    "voc": "voc",
    "acc": "acc",
    "gen": "gen",
    "dat": "dat",
    "abl": "abl",
}
NOUN_ANALYSIS_SOURCE_TOKENS = tuple(
    sorted(NOUN_ANALYSIS_TOKEN_ALIASES, key=len, reverse=True)
)


def segment_noun_analysis_token(token):
    """Fully segment one tokenizer token into known noun-analysis abbreviations."""
    memo = {}

    def segment_from(index):
        if index == len(token):
            return []
        if index in memo:
            return memo[index]
        for candidate in NOUN_ANALYSIS_SOURCE_TOKENS:
            if token.startswith(candidate, index):
                remainder = segment_from(index + len(candidate))
                if remainder is not None:
                    memo[index] = [candidate] + remainder
                    return memo[index]
        memo[index] = None
        return None

    return segment_from(0)


def parse_noun_analysis_answer(text):
    """Parse NUMBER CASE+ (NUMBER CASE+)* from free-form noun analysis input."""
    raw_tokens = tokenize_morphology_answer(text)
    normalized_tokens = []

    for raw_token in raw_tokens:
        pieces = segment_noun_analysis_token(raw_token)
        if pieces is None:
            return {
                "valid": False,
                "tokens": normalized_tokens,
                "analyses": set(),
                "error": f"unrecognized token: {raw_token}",
            }
        normalized_tokens.extend(NOUN_ANALYSIS_TOKEN_ALIASES[piece] for piece in pieces)

    if not normalized_tokens:
        return {
            "valid": False,
            "tokens": [],
            "analyses": set(),
            "error": "no grammatical tokens found",
        }

    analyses = set()
    current_number = None
    current_number_has_case = False

    for token in normalized_tokens:
        if token in noun_options["number"]:
            if current_number is not None and not current_number_has_case:
                return {
                    "valid": False,
                    "tokens": normalized_tokens,
                    "analyses": analyses,
                    "error": f"number {current_number} has no case",
                }
            current_number = token
            current_number_has_case = False
        elif token in noun_options["case"]:
            if current_number is None:
                return {
                    "valid": False,
                    "tokens": normalized_tokens,
                    "analyses": analyses,
                    "error": f"case {token} appears before any number",
                }
            analyses.add((current_number, token))
            current_number_has_case = True

    if current_number is not None and not current_number_has_case:
        return {
            "valid": False,
            "tokens": normalized_tokens,
            "analyses": analyses,
            "error": f"number {current_number} has no case",
        }

    return {
        "valid": True,
        "tokens": normalized_tokens,
        "analyses": analyses,
        "error": None,
    }

'''

if text.count(anchor) != 1:
    raise RuntimeError(f"Expected noun_options anchor once, found {text.count(anchor)}")
text = text.replace(anchor, insert, 1)

old = '''                    if recognition_answer:
                        tokens = tokenize_morphology_answer(recognition_answer)
                        st.session_state.answer_display_message = (
                            f":green-background[Your answer is correct: {tokens}]"
                        )
'''
new = '''                    if recognition_answer:
                        parsed_answer = parse_noun_analysis_answer(recognition_answer)
                        if parsed_answer["valid"]:
                            analyses_display = sorted(parsed_answer["analyses"])
                            st.session_state.answer_display_message = (
                                f":green-background[Your answer is correct: "
                                f"tokens={parsed_answer['tokens']}; analyses={analyses_display}]"
                            )
                        else:
                            st.session_state.answer_display_message = (
                                f":green-background[Your answer is temporarily accepted. "
                                f"tokens={parsed_answer['tokens']}; parser error: {parsed_answer['error']}]"
                            )
'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected token feedback block once, found {text.count(old)}")
text = text.replace(old, new, 1)

path.write_text(text)
