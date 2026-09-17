def apply_pair_weighting(source):
    inflect_helper = r'''
    def _agreement_pair_weight(noun, adjective):
        noun_decl = noun_vocab[noun].get("decl")
        adj_decl = adj_vocab[adjective].get("decl")

        if noun_decl == 1:
            noun_family = "1"
        elif str(noun_decl).startswith("2"):
            noun_family = "2"
        elif str(noun_decl).startswith("3") or noun_decl == 3:
            noun_family = "3"
        elif str(noun_decl).startswith("4") or noun_decl == 4:
            noun_family = "4"
        elif str(noun_decl).startswith("5"):
            noun_family = "5"
        else:
            noun_family = str(noun_decl)

        if adj_decl == (1, 2):
            same_family = noun_family in ("1", "2")
        elif adj_decl == 3:
            same_family = noun_family == "3"
        else:
            same_family = False

        if not same_family:
            return 2.0

        if adj_decl == 3 and noun_family == "3":
            strong_i_stem = (
                noun_decl == "3_istem_neut"
                or noun_vocab[noun].get("true_i_stem") is True
            )
            if not strong_i_stem:
                return 1.5

        return 1.0

    def _weighted_agreement_pair():
        pairs = [
            (noun, adjective)
            for noun in active_vocab
            for adjective in active_adj_vocab
        ]
        if not pairs:
            return None, None
        weights = [
            _agreement_pair_weight(noun, adjective)
            for noun, adjective in pairs
        ]
        return random.choices(pairs, weights=weights, k=1)[0]
'''

    inflect_marker = '''    def _pair_question():\n        if not active_vocab or not active_adj_vocab:\n            return None\n        noun = random.choice(list(active_vocab))\n        gender = noun_vocab[noun]["gender"]\n        adjective = random.choice(list(active_adj_vocab))\n'''
    inflect_replacement = inflect_helper + '''\n    def _pair_question():\n        if not active_vocab or not active_adj_vocab:\n            return None\n        noun, adjective = _weighted_agreement_pair()\n        gender = noun_vocab[noun]["gender"]\n'''
    if inflect_marker not in source:
        raise RuntimeError("Could not locate inflection pair generator for weighting")
    source = source.replace(inflect_marker, inflect_replacement, 1)

    middle_helper = r'''
    def _am_pair_weight(noun, adjective):
        noun_decl = noun_vocab[noun].get("decl")
        adj_decl = adj_vocab[adjective].get("decl")

        if noun_decl == 1:
            noun_family = "1"
        elif str(noun_decl).startswith("2"):
            noun_family = "2"
        elif str(noun_decl).startswith("3") or noun_decl == 3:
            noun_family = "3"
        elif str(noun_decl).startswith("4") or noun_decl == 4:
            noun_family = "4"
        elif str(noun_decl).startswith("5"):
            noun_family = "5"
        else:
            noun_family = str(noun_decl)

        if adj_decl == (1, 2):
            same_family = noun_family in ("1", "2")
        elif adj_decl == 3:
            same_family = noun_family == "3"
        else:
            same_family = False

        if not same_family:
            return 2.0

        if adj_decl == 3 and noun_family == "3":
            strong_i_stem = (
                noun_decl == "3_istem_neut"
                or noun_vocab[noun].get("true_i_stem") is True
            )
            if not strong_i_stem:
                return 1.5

        return 1.0

    def _am_weighted_pair():
        pairs = [
            (noun, adjective)
            for noun in active_vocab
            for adjective in active_adj_vocab
        ]
        if not pairs:
            return None, None
        weights = [
            _am_pair_weight(noun, adjective)
            for noun, adjective in pairs
        ]
        return random.choices(pairs, weights=weights, k=1)[0]
'''

    middle_marker = '''    def _am_question():\n        if not active_vocab or not active_adj_vocab:\n            return None\n        noun = random.choice(list(active_vocab))\n        adjective = random.choice(list(active_adj_vocab))\n        gender = noun_vocab[noun]["gender"]\n'''
    middle_replacement = middle_helper + '''\n    def _am_question():\n        if not active_vocab or not active_adj_vocab:\n            return None\n        noun, adjective = _am_weighted_pair()\n        gender = noun_vocab[noun]["gender"]\n'''
    if middle_marker not in source:
        raise RuntimeError("Could not locate agreement pair generator for weighting")
    source = source.replace(middle_marker, middle_replacement, 1)

    return source
