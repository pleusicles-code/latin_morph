def apply_pair_weighting(source):
    inflect_helper = r'''
    def _agreement_pair_category(noun, adjective):
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
            return "different"

        if adj_decl == 3 and noun_family == "3":
            strong_i_stem = (
                noun_decl == "3_istem_neut"
                or noun_vocab[noun].get("true_i_stem") is True
            )
            if not strong_i_stem:
                return "third_mixed"

        return "same"

    def _weighted_agreement_pair():
        pools = {"different": [], "third_mixed": [], "same": []}
        for noun in active_vocab:
            for adjective in active_adj_vocab:
                category = _agreement_pair_category(noun, adjective)
                pools[category].append((noun, adjective))

        available = [category for category, pairs in pools.items() if pairs]
        if not available:
            return None, None

        category_weights = {
            "different": 0.60,
            "third_mixed": 0.25,
            "same": 0.15,
        }
        category = random.choices(
            available,
            weights=[category_weights[item] for item in available],
            k=1,
        )[0]
        return random.choice(pools[category])
'''

    inflect_marker = '''    def _pair_question():\n        if not active_vocab or not active_adj_vocab:\n            return None\n        noun = random.choice(list(active_vocab))\n        gender = noun_vocab[noun]["gender"]\n        adjective = random.choice(list(active_adj_vocab))\n'''
    inflect_replacement = inflect_helper + '''\n    def _pair_question():\n        if not active_vocab or not active_adj_vocab:\n            return None\n        noun, adjective = _weighted_agreement_pair()\n        raw_gender = noun_vocab[noun]["gender"]\n        gender = random.choice(["m", "f"]) if raw_gender == "m/f" else raw_gender\n'''
    if inflect_marker not in source:
        raise RuntimeError("Could not locate inflection pair generator for weighting")
    source = source.replace(inflect_marker, inflect_replacement, 1)

    middle_helper = r'''
    def _am_pair_category(noun, adjective):
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
            return "different"

        if adj_decl == 3 and noun_family == "3":
            strong_i_stem = (
                noun_decl == "3_istem_neut"
                or noun_vocab[noun].get("true_i_stem") is True
            )
            if not strong_i_stem:
                return "third_mixed"

        return "same"

    def _am_weighted_pair():
        pools = {"different": [], "third_mixed": [], "same": []}
        for noun in active_vocab:
            for adjective in active_adj_vocab:
                category = _am_pair_category(noun, adjective)
                pools[category].append((noun, adjective))

        available = [category for category, pairs in pools.items() if pairs]
        if not available:
            return None, None

        category_weights = {
            "different": 0.60,
            "third_mixed": 0.25,
            "same": 0.15,
        }
        category = random.choices(
            available,
            weights=[category_weights[item] for item in available],
            k=1,
        )[0]
        return random.choice(pools[category])

    def _am_weighted_target(noun, adjective, gender):
        targets = []
        weights = []
        for number in _am_allowed_numbers(noun, adjective):
            for case in _am_cases(noun, adjective, number, gender):
                targets.append((number, case))
                if number == "sg" and case == "nom":
                    weight = 0.7
                elif number == "pl" and case in ("dat", "abl"):
                    weight = 0.5
                else:
                    weight = 1.0
                weights.append(weight)
        if not targets:
            return None, None
        return random.choices(targets, weights=weights, k=1)[0]
'''

    middle_marker = '''    def _am_question():\n        if not active_vocab or not active_adj_vocab:\n            return None\n        noun = random.choice(list(active_vocab))\n        adjective = random.choice(list(active_adj_vocab))\n        gender = noun_vocab[noun]["gender"]\n'''
    middle_replacement = middle_helper + '''\n    def _am_question():\n        if not active_vocab or not active_adj_vocab:\n            return None\n        noun, adjective = _am_weighted_pair()\n        raw_gender = noun_vocab[noun]["gender"]\n        gender = random.choice(["m", "f"]) if raw_gender == "m/f" else raw_gender\n'''
    if middle_marker not in source:
        raise RuntimeError("Could not locate agreement pair generator for weighting")
    source = source.replace(middle_marker, middle_replacement, 1)

    middle_target_marker = '''        numbers = _am_allowed_numbers(noun, adjective)\n        if not numbers:\n            return None\n        number = random.choice(numbers)\n        case = random.choice(_am_cases(noun, adjective, number, gender))\n'''
    middle_target_replacement = '''        number, case = _am_weighted_target(noun, adjective, gender)\n        if number is None:\n            return None\n'''
    if middle_target_marker not in source:
        raise RuntimeError("Could not locate agreement target generator for weighting")
    source = source.replace(middle_target_marker, middle_target_replacement, 1)

    return source
