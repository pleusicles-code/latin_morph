from pathlib import Path

source = Path(__file__).with_name("agreement_impl.py").read_text(encoding="utf-8")

source = source.replace(
'''    def _noun_form(noun, case):
        info = noun_vocab[noun]
        if case == "nom":
            return noun
        irreg_form = info.get("irreg", {}).get("sg", {}).get(case, "")
        if irreg_form:
            return irreg_form
        if irreg_form is None:
            return None
        decl = info["decl"]
        stem = info["stem"]
        ending = noun_endings[decl]["sg"][case]
        if ((noun.endswith("ius") and decl == "2_us") or
                (noun.endswith("ium") and decl == "2_neut")) and case in ("voc", "gen"):
            stem = stem[:-1]
            ending = "ī" if case == "voc" else ["iī", "ī"]
        if info.get("true_i_stem") is True:
            if case == "acc":
                ending = ["im", "em"]
            elif case == "abl":
                ending = ["ī", "e"]
        if ending is None:
            return noun
        if isinstance(ending, list):
            return [stem + item for item in ending]
        return stem + ending
''',
'''    def _noun_form(noun, case, number="sg"):
        info = noun_vocab[noun]
        if number == "sg" and case == "nom":
            return noun
        irreg_form = info.get("irreg", {}).get(number, {}).get(case, "")
        if irreg_form:
            return irreg_form
        if irreg_form is None:
            return None
        decl = info["decl"]
        stem = info["stem"]
        ending = noun_endings[decl][number][case]
        if (number == "sg" and
                ((noun.endswith("ius") and decl == "2_us") or
                 (noun.endswith("ium") and decl == "2_neut")) and
                case in ("voc", "gen")):
            stem = stem[:-1]
            ending = "ī" if case == "voc" else ["iī", "ī"]
        if number == "sg" and info.get("true_i_stem") is True:
            if case == "acc":
                ending = ["im", "em"]
            elif case == "abl":
                ending = ["ī", "e"]
        if ending is None:
            return noun
        if isinstance(ending, list):
            return [stem + item for item in ending]
        return stem + ending
'''
)

source = source.replace(
'''    def _adjective_form(adj, case, gender):
        info = adj_vocab[adj]
        irreg_forms = info.get("irreg", {}).get("forms", {})
        raw_irregular = irreg_forms.get("sg", {}).get(case)
        if raw_irregular:
            return _gendered_form(raw_irregular, gender)

        if case in ("nom", "voc"):
            nom = _adjective_nom_sg(adj, gender)
            if case == "voc" and info.get("decl") == (1, 2) and gender == "m" and adj.endswith("us"):
                if adj.endswith("ius"):
                    return info["stem"][:-1] + "ī"
                if adj == "meus":
                    return "mī"
                return info["stem"] + "e"
            return nom

        stem = info.get("irreg", {}).get("stems", {}).get("pos") or info["stem"]
        if info.get("decl") == (1, 2):
            if info.get("pronominal") is True and case == "gen":
                ending = "īus"
            elif info.get("pronominal") is True and case == "dat":
                ending = "ī"
            else:
                endings = {
                    "f": {"gen": "ae", "dat": "ae", "acc": "am", "abl": "ā"},
                    "m": {"gen": "ī", "dat": "ō", "acc": "um", "abl": "ō"},
                    "n": {"gen": "ī", "dat": "ō", "acc": "um", "abl": "ō"},
                }
                ending = endings[gender][case]
            return stem + ending

        if case == "gen":
            return stem + "is"
        if case == "dat":
            return stem + "ī"
        if case == "abl":
            return stem + ("e" if info.get("cons_stem") else "ī")
        if case == "acc":
            if gender == "n":
                return _adjective_nom_sg(adj, gender)
            return stem + "em"
        return _adjective_nom_sg(adj, gender)
''',
'''    def _adjective_form(adj, case, gender, number="sg"):
        info = adj_vocab[adj]
        irreg_forms = info.get("irreg", {}).get("forms", {})
        raw_irregular = irreg_forms.get(number, {}).get(case)
        if raw_irregular:
            return _gendered_form(raw_irregular, gender)

        if number == "sg" and case in ("nom", "voc"):
            nom = _adjective_nom_sg(adj, gender)
            if case == "voc" and info.get("decl") == (1, 2) and gender == "m" and adj.endswith("us"):
                if adj.endswith("ius"):
                    return info["stem"][:-1] + "ī"
                if adj == "meus":
                    return "mī"
                return info["stem"] + "e"
            return nom

        stem = info.get("irreg", {}).get("stems", {}).get("pos") or info["stem"]
        if info.get("decl") == (1, 2):
            if number == "sg" and info.get("pronominal") is True and case == "gen":
                ending = "īus"
            elif number == "sg" and info.get("pronominal") is True and case == "dat":
                ending = "ī"
            else:
                endings = {
                    "sg": {
                        "f": {"gen": "ae", "dat": "ae", "acc": "am", "abl": "ā"},
                        "m": {"gen": "ī", "dat": "ō", "acc": "um", "abl": "ō"},
                        "n": {"gen": "ī", "dat": "ō", "acc": "um", "abl": "ō"},
                    },
                    "pl": {
                        "f": {"nom": "ae", "gen": "ārum", "dat": "īs", "acc": "ās", "abl": "īs", "voc": "ae"},
                        "m": {"nom": "ī", "gen": "ōrum", "dat": "īs", "acc": "ōs", "abl": "īs", "voc": "ī"},
                        "n": {"nom": "a", "gen": "ōrum", "dat": "īs", "acc": "a", "abl": "īs", "voc": "a"},
                    },
                }
                ending = endings[number][gender][case]
            return stem + ending

        if number == "pl":
            cons = bool(info.get("cons_stem"))
            if case == "gen":
                return stem + ("um" if cons else "ium")
            if case in ("dat", "abl"):
                return stem + "ibus"
            if gender == "n":
                if case in ("nom", "acc", "voc"):
                    return stem + ("a" if cons else "ia")
            else:
                if case in ("nom", "voc"):
                    return stem + "ēs"
                if case == "acc":
                    return stem + "ēs" if cons else [stem + "īs", stem + "ēs"]

        if case == "gen":
            return stem + "is"
        if case == "dat":
            return stem + "ī"
        if case == "abl":
            return stem + ("e" if info.get("cons_stem") else "ī")
        if case == "acc":
            if gender == "n":
                return _adjective_nom_sg(adj, gender)
            return stem + "em"
        return _adjective_nom_sg(adj, gender)
'''
)

source = source.replace(
'''    def _pair_question():
        if not active_vocab or not active_adj_vocab:
            return None
        noun = random.choice(list(active_vocab))
        gender = noun_vocab[noun]["gender"]
        adjective = random.choice(list(active_adj_vocab))
        cases = ["gen", "dat", "acc", "abl"]
        if include_vocative:
            noun_voc = _noun_form(noun, "voc")
            adj_voc = _adjective_form(adjective, "voc", gender)
            noun_nom = _noun_form(noun, "nom")
            adj_nom = _adjective_nom_sg(adjective, gender)
            if noun_voc != noun_nom or adj_voc != adj_nom:
                cases.append("voc")
        case = random.choice(cases)
        return {"noun": noun, "adjective": adjective, "case": case, "gender": gender}
''',
'''    def _pair_question():
        if not active_vocab or not active_adj_vocab:
            return None
        noun = random.choice(list(active_vocab))
        gender = noun_vocab[noun]["gender"]
        adjective = random.choice(list(active_adj_vocab))

        numbers = ["sg"]
        if not noun_vocab[noun].get("no_pl") and not adj_vocab[adjective].get("no_pl"):
            numbers.append("pl")
        number = random.choice(numbers)

        cases = ["gen", "dat", "acc", "abl"]
        if include_vocative:
            noun_voc = _noun_form(noun, "voc", number)
            adj_voc = _adjective_form(adjective, "voc", gender, number)
            noun_nom = _noun_form(noun, "nom", number)
            adj_nom = _adjective_form(adjective, "nom", gender, number)
            if noun_voc != noun_nom or adj_voc != adj_nom:
                cases.append("voc")
        case = random.choice(cases)
        return {"noun": noun, "adjective": adjective, "case": case, "number": number, "gender": gender}
'''
)

source = source.replace(
'''        case = q["case"]
        gender = q["gender"]

        noun_nom = _noun_form(noun, "nom")
        adjective_nom = _adjective_nom_sg(adjective, gender)
        noun_target = _noun_form(noun, case)
        adjective_target = _adjective_form(adjective, case, gender)
''',
'''        case = q["case"]
        number = q["number"]
        gender = q["gender"]

        noun_nom = _noun_form(noun, "nom")
        adjective_nom = _adjective_nom_sg(adjective, gender)
        noun_target = _noun_form(noun, case, number)
        adjective_target = _adjective_form(adjective, case, gender, number)
'''
)

source = source.replace(
'''        case_prompt = f"singularis {noun_options['case'][case]}ban"
''',
'''        case_prompt = f"{'singularis' if number == 'sg' else 'pluralis'} {noun_options['case'][case]}ban"
'''
)

source = source.replace(
'''                "num": "sg",
''',
'''                "num": number,
'''
)

source = source.replace(
'''        adjective_prompt = _adjective_dictionary_entry(adjective) if show_dictionary_entry else adjective_nom
''',
'''        adjective_prompt = _adjective_dictionary_entry(adjective) if show_dictionary_entry else adjective
'''
)

source = source.replace(
'''        prompt_space = st.container(height=82, border=False)
        with prompt_space:
            st.markdown(
                f'<div style="margin-top:0.75rem;font-size:1.75rem;line-height:1.25;">{question_html}</div>',
                unsafe_allow_html=True,
            )
''',
'''        supplementary = []

        if show_declension:
            noun_decl_key = ""
            noun_decl_value = noun_vocab[noun].get("decl")
            for key, value in declension_dict.items():
                if isinstance(value, list):
                    if noun_decl_value in value:
                        noun_decl_key = key
                        break
                elif noun_decl_value == value:
                    noun_decl_key = key
                    break

            noun_parts = []
            if noun_decl_key:
                noun_parts.append(f"{DECLENSION_NUMBER_LABELS[noun_decl_key]} declinatiós")
            if show_third_group:
                if noun_decl_value in (3, "3_neut"):
                    noun_parts.append("msh.-tövű")
                elif noun_decl_value == "3_istem_neut" or noun_vocab[noun].get("true_i_stem") is True:
                    noun_parts.append("erős i-tövű")
                elif noun_decl_value == "3_istem":
                    noun_parts.append("gyenge i-tövű")

            adjective_parts = []
            adjective_group = _agreement_adjective_group(adjective)
            if adjective_group == "1_2":
                adjective_parts.append("1–2. declinatiós")
            elif adjective_group and adjective_group.startswith("3_"):
                adjective_parts.append("3. declinatiós")
                if show_third_group:
                    ending_count = {"3_1": "1 végű", "3_2": "2 végű", "3_3": "3 végű"}[adjective_group]
                    adjective_parts.append(ending_count)

            if noun_parts:
                supplementary.append("<strong>Főnév:</strong> " + ", ".join(noun_parts))
            if adjective_parts:
                supplementary.append("<strong>Melléknév:</strong> " + ", ".join(adjective_parts))

        if show_stem:
            noun_stem_raw = str(noun_vocab[noun].get("stem", ""))
            if str(noun_vocab[noun].get("decl", "")).startswith("5"):
                noun_stem_raw += "e"
            noun_stem = html.escape(noun_stem_raw)
            adjective_stem = html.escape(str(adj_vocab[adjective].get("stem", "")))
            supplementary.append(
                f'<strong>Tő:</strong> <em>{noun_stem}-</em> (főnév), <em>{adjective_stem}-</em> (melléknév)'
            )

        prompt_height = 112 if supplementary else 82
        prompt_space = st.container(height=prompt_height, border=False)
        with prompt_space:
            st.markdown(
                f'<div style="margin-top:0.75rem;font-size:1.75rem;line-height:1.25;">{question_html}</div>',
                unsafe_allow_html=True,
            )
            if supplementary:
                st.markdown(
                    '<div style="font-size:1.15rem;line-height:1.35;margin-top:0.35rem;">'
                    + " &nbsp;·&nbsp; ".join(supplementary)
                    + "</div>",
                    unsafe_allow_html=True,
                )
'''
)

exec(compile(source, str(Path(__file__).with_name("agreement_impl.py")), "exec"))