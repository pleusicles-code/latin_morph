from pathlib import Path
import textwrap

source = Path(__file__).with_name("agreement_base.py").read_text(encoding="utf-8")

source = source.replace('from vocab import import_nouns, filter_vocab_by_repo',
                        'from vocab import import_nouns, import_adjectives, filter_vocab_by_repo')
source = source.replace('st.set_page_config("BevLat – Főnevek", layout="centered")',
                        'st.set_page_config("BevLat – Főnév és melléknév egyeztetése", layout="centered")')
source = source.replace('page_id = "nouns"', 'page_id = "agreement"')
source = source.replace('st.markdown("# Főnevek")', 'st.markdown("# Főnév és melléknév egyeztetése")')
source = source.replace('"nouns.py"', '"agreement.py"')
source = source.replace('nouns_', 'agreement_')
source = source.replace(
    'noun_vocab = {**filter_vocab_by_repo(import_nouns(), "alap1"), **filter_vocab_by_repo(import_nouns(), "alap2"), **filter_vocab_by_repo(import_nouns(), "alap3")}',
    'noun_vocab = {**filter_vocab_by_repo(import_nouns(), "alap1"), **filter_vocab_by_repo(import_nouns(), "alap2"), **filter_vocab_by_repo(import_nouns(), "alap3")}\n'
    'adj_vocab = {**filter_vocab_by_repo(import_adjectives(), "alap1"), **filter_vocab_by_repo(import_adjectives(), "alap2"), **filter_vocab_by_repo(import_adjectives(), "alap3")}'
)

if '"agreement_enforce_macrons"' in source:
    source = source.replace(
        'st.session_state.agreement_enforce_macrons = st.session_state.enforce_macrons["agreement_enforce_macrons"]',
        'st.session_state.enforce_macrons.setdefault("agreement_enforce_macrons", st.session_state.enforce_macrons.get("nouns_enforce_macrons", False))\n'
        'st.session_state.agreement_enforce_macrons = st.session_state.enforce_macrons["agreement_enforce_macrons"]'
    )

source = source.replace(
    '"exercise_type": choice_setting("inflect", ["inflect", "recognize"]),',
    '"exercise_type": choice_setting("inflect", ["inflect", "agreement", "number_switch", "recognize"]),'
)
source = source.replace(
    '"show_dictionary_entry": bool_setting(True),',
    '"show_dictionary_entry": bool_setting(True),\n    "abbreviate_adjective_dictionary": bool_setting(True),'
)
source = source.replace(
    'options=["inflect", "recognize"],\n            format_func=lambda value: {\n                "inflect": "Ragozás",\n                "recognize": "Alakfelismerés",\n            }[value],',
    'options=["inflect", "agreement", "number_switch", "recognize"],\n            format_func=lambda value: {\n                "inflect": "Ragozás",\n                "agreement": "Egyeztetés",\n                "number_switch": "Sg./pl. váltás",\n                "recognize": "Alakfelismerés",\n            }[value],'
)
source = source.replace('if exercise_type == "inflect":', 'if exercise_type in ("inflect", "agreement"):')
source = source.replace(
    '''    if exercise_type in ("inflect", "agreement"):
        st.checkbox(
            "Hosszú magánhangzók ellenőrzése?",
            help="Ha be van jelölve, a hosszú magánhangzók hibás jelölése hibás válasznak számít. Ha nincs bejelölve, a hosszúságjelek használhatók, de a program nem értékeli őket.",
            key="agreement_enforce_macrons",
            on_change=send_setting,
            args=(switch_noun_macrons,),
            kwargs={"streamlit_page": "agreement.py", "setting_name": "agreement_enforce_macrons"},
        )
        macrons = st.session_state.agreement_enforce_macrons

        if macrons:
            st.markdown("A hosszú magánhangzók innen másolhatók:")
            st.code("āēīōū", language=None)
    else:
        print_macrons = st.checkbox(
            "Hosszú magánhangzók jelölése?",
            help="Ha be van kapcsolva, a kérdésben szereplő alakok jelölik a magánhangzók hosszúságát, és a választ ennek figyelembevételével kell megadni. Ha ki van kapcsolva, ugyanaz az írott alak rövid és hosszú magánhangzóval képzett alakokat is jelölhet, ezért több helyes elemzés is lehetséges.",
            key=widget_key(page_id, "print_macrons"),
        )
        indicate_multiple_answers = st.checkbox(
            "Több helyes válaszlehetőség jelzése?",
            help="Ha be van kapcsolva, a kérdés külön jelzi, ha az adott alaknak több helyes elemzése van.",
            key=widget_key(page_id, "indicate_multiple_answers"),
        )
        award_partial_credit = st.checkbox(
            "Részpont adása?",
            help="Ha be van kapcsolva, a részben helyes válasz fél pontot ér; különben csak a teljesen helyes válaszért jár pont.",
            key=widget_key(page_id, "award_partial_credit"),
        )
''',
    '''    if exercise_type == "inflect":
        st.checkbox(
            "Hosszú magánhangzók ellenőrzése?",
            help="Ha be van jelölve, a hosszú magánhangzók hibás jelölése hibás válasznak számít. Ha nincs bejelölve, a hosszúságjelek használhatók, de a program nem értékeli őket.",
            key="agreement_enforce_macrons",
            on_change=send_setting,
            args=(switch_noun_macrons,),
            kwargs={"streamlit_page": "agreement.py", "setting_name": "agreement_enforce_macrons"},
        )
        macrons = st.session_state.agreement_enforce_macrons

        if macrons:
            st.markdown("A hosszú magánhangzók innen másolhatók:")
            st.code("āēīōū", language=None)
    else:
        print_macrons = st.checkbox(
            "Hosszú magánhangzók jelölése a kérdésben",
            help="Ha be van kapcsolva, a kérdésben szereplő alakok jelölik a magánhangzók hosszúságát. Ez az alak lehetséges nyelvtani elemzéseit is pontosíthatja.",
            key=widget_key(page_id, "print_macrons"),
        )
        if exercise_type == "agreement":
            enforce_answer_macrons_key = widget_key(page_id, "enforce_answer_macrons")
            if not print_macrons:
                st.session_state[enforce_answer_macrons_key] = False
            enforce_answer_macrons = st.checkbox(
                "Hosszú magánhangzók ellenőrzése a válaszban",
                help="Ha be van kapcsolva, a válaszban is pontosan jelölni kell a hosszú magánhangzókat.",
                key=enforce_answer_macrons_key,
                disabled=not print_macrons,
            )
            if enforce_answer_macrons:
                st.markdown("A hosszú magánhangzók innen másolhatók:")
                st.code("āēīōū", language=None)
        indicate_multiple_answers = st.checkbox(
            "Több helyes válaszlehetőség jelzése?",
            help="Ha be van kapcsolva, a kérdés külön jelzi, ha az adott alaknak több helyes elemzése van.",
            key=widget_key(page_id, "indicate_multiple_answers"),
        )
        award_partial_credit = st.checkbox(
            "Részpont adása?",
            help="Ha be van kapcsolva, a részben helyes válasz fél pontot ér; különben csak a teljesen helyes válaszért jár pont.",
            key=widget_key(page_id, "award_partial_credit"),
        )
'''
)

# Agreement mode uses the recognition-style option branch. Patch that branch directly,
# because apply_middle_mode() intentionally disables the earlier inflect/agreement routing.
_agreement_macron_options_old = '''        print_macrons = st.checkbox(
            "Hosszú magánhangzók jelölése?",
            help="Ha be van kapcsolva, a kérdésben szereplő alakok jelölik a magánhangzók hosszúságát, és a választ ennek figyelembevételével kell megadni. Ha ki van kapcsolva, ugyanaz az írott alak rövid és hosszú magánhangzóval képzett alakokat is jelölhet, ezért több helyes elemzés is lehetséges.",
            key=widget_key(page_id, "print_macrons"),
        )
'''
_agreement_macron_options_new = '''        print_macrons = st.checkbox(
            "Hosszú magánhangzók jelölése a kérdésben",
            help="Ha be van kapcsolva, a kérdésben szereplő alakok jelölik a magánhangzók hosszúságát. Ez az alak lehetséges nyelvtani elemzéseit is pontosíthatja.",
            key=widget_key(page_id, "print_macrons"),
        )
        if exercise_type == "agreement":
            enforce_answer_macrons_key = widget_key(page_id, "enforce_answer_macrons")
            if not print_macrons:
                st.session_state[enforce_answer_macrons_key] = False
            enforce_answer_macrons = st.checkbox(
                "Hosszú magánhangzók ellenőrzése a válaszban",
                help="Ha be van kapcsolva, a válaszban is pontosan jelölni kell a hosszú magánhangzókat.",
                key=enforce_answer_macrons_key,
                disabled=not print_macrons,
            )
            if enforce_answer_macrons:
                st.markdown("A hosszú magánhangzók innen másolhatók:")
                st.code("āēīōū", language=None)
'''
if _agreement_macron_options_old not in source:
    raise RuntimeError("Could not locate recognition-style macron options for Agreement")
source = source.replace(_agreement_macron_options_old, _agreement_macron_options_new, 1)



adjective_constants = '''\nADJECTIVE_DECLENSION_LABELS = {\n    "1_2": "1-2.",\n    "3_1": "3. (1végű)",\n    "3_2": "3. (2végű)",\n    "3_3": "3. (3végű)",\n}\nDEFAULT_ADJECTIVE_DECLENSIONS = list(ADJECTIVE_DECLENSION_LABELS.keys())\nADJECTIVE_DECLENSION_URL_CHOICES = {key: key for key in DEFAULT_ADJECTIVE_DECLENSIONS}\n'''
source = source.replace(
    'DEFAULT_DECLENSIONS = list(declension_dict.keys())\nDECLENSION_URL_CHOICES = {',
    'DEFAULT_DECLENSIONS = list(declension_dict.keys())' + adjective_constants + '\nDECLENSION_URL_CHOICES = {'
)
source = source.replace(
    '"include_vocative": bool_setting(False),\n    "declension": list_setting(DEFAULT_DECLENSIONS, DECLENSION_URL_CHOICES),',
    '"include_vocative": bool_setting(False),\n    "include_degrees": bool_setting(False),\n    "declension": list_setting(DEFAULT_DECLENSIONS, DECLENSION_URL_CHOICES),\n    "adjective_declension": list_setting(DEFAULT_ADJECTIVE_DECLENSIONS, ADJECTIVE_DECLENSION_URL_CHOICES),'
)

old_selector = '''    declension = st.multiselect(\n        "Válaszd ki, mely declinatiókat szeretnéd gyakorolni (alapértelmezés szerint mindegyik ki van választva):",\n        options=DEFAULT_DECLENSIONS,\n        format_func=lambda x: DECLENSION_LABELS[x],\n        help="Ha a kiválasztott declinatiók között rendhagyó főnevek is vannak, külön megadhatod, melyeket szeretnéd bevonni a gyakorlásba.",\n        key=widget_key(page_id, "declension"),\n    )\n    include_vocative = st.checkbox(\n        "Vocativusszal együtt?",\n        help="Ha be van jelölve, a program a nominativustól eltérő vocativusi alakokat is gyakoroltatja.",\n        key=widget_key(page_id, "include_vocative"),\n    )'''
new_selector = '''    st.markdown("**Főnevek:** Válaszd ki, mely declinatiókat szeretnéd gyakorolni (alapértelmezés szerint mindegyik ki van választva):")\n    declension = st.multiselect(\n        "Főnevek declinatiói",\n        options=DEFAULT_DECLENSIONS,\n        format_func=lambda x: DECLENSION_LABELS[x],\n        help="Ha a kiválasztott declinatiók között rendhagyó főnevek is vannak, külön megadhatod, melyeket szeretnéd bevonni a gyakorlásba.",\n        key=widget_key(page_id, "declension"),\n        label_visibility="collapsed",\n    )\n    st.markdown("**Melléknevek:** Válaszd ki, mely declinatiókat szeretnéd gyakorolni (alapértelmezés szerint mindegyik ki van választva):")\n    adjective_declension = st.multiselect(\n        "Melléknevek declinatiói",\n        options=DEFAULT_ADJECTIVE_DECLENSIONS,\n        format_func=lambda x: ADJECTIVE_DECLENSION_LABELS[x],\n        key=widget_key(page_id, "adjective_declension"),\n        label_visibility="collapsed",\n    )\n    include_vocative = st.checkbox(\n        "Vocativusszal együtt?",\n        help="Ha be van jelölve, a program a nominativustól eltérő vocativusi alakokat is gyakoroltatja.",\n        key=widget_key(page_id, "include_vocative"),\n    )\n    include_degrees = st.checkbox(\n        "Fokozott melléknevek is?",\n        disabled=True,\n        key=widget_key(page_id, "include_degrees"),\n    )'''
source = source.replace(old_selector, new_selector)

old_dictionary_checkbox = '''    show_dictionary_entry = st.checkbox(\n        "Szótári alak megjelenítése?",\n        help="A teljes szótári alak megjelenítése; ennek genitivusából a tő is meghatározható.",\n        key=widget_key(page_id, "show_dictionary_entry"),\n    )'''
new_dictionary_checkbox = old_dictionary_checkbox + '''\n    abbreviate_adjective_dictionary = st.checkbox(\n        "Rövidített melléknévi szótári alakok",\n        key=widget_key(page_id, "abbreviate_adjective_dictionary"),\n        disabled=not show_dictionary_entry,\n    )'''
source = source.replace(old_dictionary_checkbox, new_dictionary_checkbox)

source = source.replace(
    '"include_vocative": include_vocative,\n    "declension": declension,',
    '"include_vocative": include_vocative,\n    "include_degrees": include_degrees,\n    "declension": declension,\n    "adjective_declension": adjective_declension,'
)
source = source.replace(
    '"show_dictionary_entry": show_dictionary_entry,\n    "show_declension": show_declension,',
    '"show_dictionary_entry": show_dictionary_entry,\n    "abbreviate_adjective_dictionary": abbreviate_adjective_dictionary,\n    "show_declension": show_declension,'
)
source = source.replace(
    '"show_dictionary_entry": True,\n        "show_declension": False,',
    '"show_dictionary_entry": True,\n        "abbreviate_adjective_dictionary": True,\n        "show_declension": False,'
)
source = source.replace(
    '"include_vocative": False,\n        "declension": DEFAULT_DECLENSIONS,',
    '"include_vocative": False,\n        "include_degrees": False,\n        "declension": DEFAULT_DECLENSIONS,\n        "adjective_declension": DEFAULT_ADJECTIVE_DECLENSIONS,'
)
source = source.replace(
    'st.session_state.agreement_show_dictionary_entry = True',
    'st.session_state.agreement_show_dictionary_entry = True\n        st.session_state.agreement_abbreviate_adjective_dictionary = True'
)
source = source.replace(
    'st.session_state.agreement_include_vocative = False\n        st.session_state.agreement_declension = DEFAULT_DECLENSIONS',
    'st.session_state.agreement_include_vocative = False\n        st.session_state.agreement_include_degrees = False\n        st.session_state.agreement_declension = DEFAULT_DECLENSIONS\n        st.session_state.agreement_adjective_declension = DEFAULT_ADJECTIVE_DECLENSIONS'
)

quiz_marker = 'if len(declension) == 0 and not st.session_state.current_question:'
marker_index = source.find(quiz_marker)
if marker_index == -1:
    raise RuntimeError("Could not locate cloned noun quiz block for agreement exercise")

prefix = source[:marker_index]
original_quiz = source[marker_index:]

pair_quiz = r'''
if exercise_type == "inflect":
    def _agreement_adjective_group(adj):
        info = adj_vocab[adj]
        if info.get("decl") == (1, 2):
            return "1_2"
        if info.get("decl") != 3:
            return None
        noms = info.get("noms")
        endings = len(noms) if isinstance(noms, (tuple, list)) else 1
        return {1: "3_1", 2: "3_2", 3: "3_3"}.get(endings, "3_1")

    active_adj_vocab = {
        adj: info for adj, info in adj_vocab.items()
        if _agreement_adjective_group(adj) in adjective_declension
        and not info.get("no_sg")
        and info.get("decl") in ((1, 2), 3)
    }

    def _gendered_form(form, gender):
        if not isinstance(form, (tuple, list)):
            return form
        if not form:
            return None
        if gender == "n":
            return form[-1]
        if len(form) in (1, 2):
            return form[0]
        return form[0] if gender == "m" else form[1]

    def _noun_form(noun, case):
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

    def _adjective_nom_sg(adj, gender):
        info = adj_vocab[adj]
        noms = info.get("irreg", {}).get("forms", {}).get("sg", {}).get("nom")
        if not noms:
            noms = info.get("noms")
        if noms:
            return _gendered_form(noms, gender)
        if info.get("decl") == (1, 2):
            if gender == "m":
                return adj
            return info["stem"] + ("a" if gender == "f" else "um")
        return adj if gender != "n" else _gendered_form(info.get("noms", (adj,)), gender)

    def _adjective_form(adj, case, gender):
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

    def _noun_dictionary_entry(noun):
        genitive = _noun_form(noun, "gen")
        if isinstance(genitive, list):
            if str(noun_vocab[noun].get("decl", "")).startswith("2") and noun.endswith(("ius", "ium")):
                genitive = genitive[0]
            else:
                genitive = "/".join(genitive)
        gender = noun_vocab[noun]["gender"]
        return f"{noun}, {genitive} {gender}." if genitive else f"{noun} {gender}."

    def _adjective_nominatives(adj):
        info = adj_vocab[adj]
        noms = info.get("irreg", {}).get("forms", {}).get("sg", {}).get("nom") or info.get("noms")
        if noms:
            if not isinstance(noms, (tuple, list)):
                noms = [noms]
            forms = list(noms)
            if info.get("decl") == 3 and len(forms) == 1 and forms[0] != adj:
                forms.insert(0, adj)
            return forms
        if info.get("decl") == (1, 2):
            return [adj, info["stem"] + "a", info["stem"] + "um"]
        return [adj]

    def _adjective_dictionary_entry(adj):
        info = adj_vocab[adj]
        forms = _adjective_nominatives(adj)
        group = _agreement_adjective_group(adj)

        if group == "3_1":
            genitive = info.get("stem", "") + "is"
            return f"{adj} ({genitive})"

        if abbreviate_adjective_dictionary:
            if info.get("decl") == (1, 2) and adj.endswith("er"):
                return ", ".join(str(form) for form in forms)
            ending_count = 3 if info.get("decl") == (1, 2) else len(forms)
            return f"{adj} {ending_count}"

        return ", ".join(str(form) for form in forms)

    def _forms_list(form):
        return form if isinstance(form, list) else [form]

    def _pair_answer_options(noun_form, adjective_form):
        answers = []
        for n_form in _forms_list(noun_form):
            for a_form in _forms_list(adjective_form):
                if n_form is None or a_form is None:
                    continue
                answers.extend((f"{n_form} {a_form}", f"{a_form} {n_form}"))
        return list(dict.fromkeys(answers))

    def _pair_question():
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

    st.session_state.gen_func = _pair_question

    if not declension:
        st.write("Legalább egy főnévi declinatiót ki kell választanod.")
    elif not adjective_declension:
        st.write("Legalább egy melléknévi declinatiót ki kell választanod.")
    elif not active_vocab:
        st.write("A kiválasztott főnévi beállításokhoz nincs használható szó.")
    elif not active_adj_vocab:
        st.write("A kiválasztott melléknévi beállításokhoz nincs használható szó.")

    if st.session_state.current_question:
        q = st.session_state.current_question
        noun = q["noun"]
        adjective = q["adjective"]
        case = q["case"]
        gender = q["gender"]

        noun_nom = _noun_form(noun, "nom")
        adjective_nom = _adjective_nom_sg(adjective, gender)
        noun_target = _noun_form(noun, case)
        adjective_target = _adjective_form(adjective, case, gender)
        answer_options = _pair_answer_options(noun_target, adjective_target)
        st.session_state.correct_answer = answer_options

        noun_prompt = _noun_dictionary_entry(noun) if show_dictionary_entry else noun_nom
        adjective_prompt = _adjective_dictionary_entry(adjective) if show_dictionary_entry else adjective_nom
        noun_article = hungarian_article(noun)
        adjective_article = hungarian_article(adjective)
        case_prompt = f"singularis {noun_options['case'][case]}ban"
        question_html = (
            f'Add meg {noun_article} <strong>{html.escape(noun_prompt)}</strong> és '
            f'{adjective_article} <strong>{html.escape(adjective_prompt)}</strong> szavak alkotta '
            f'jelzős szerkezetet <strong>{html.escape(case_prompt)}</strong>!'
        )
        prompt_space = st.container(height=82, border=False)
        with prompt_space:
            st.markdown(
                f'<div style="margin-top:0.75rem;font-size:1.75rem;line-height:1.25;">{question_html}</div>',
                unsafe_allow_html=True,
            )

        with st.form(key="agreement_inflect_form", clear_on_submit=True):
            st.text_input("Válaszod:", key="answer_input")

            def submit_pair_answer():
                if st.session_state.get("answer_input"):
                    st.session_state.answer_input = " ".join(st.session_state.answer_input.split())
                submit_and_check_answer()
                if not st.session_state.get("answer_input"):
                    st.session_state.answer_display_message = (
                        "A válaszmező üres. Írd be mindkét alakot, majd kattints a **Válasz ellenőrzése** gombra."
                    )
                elif st.session_state.answer_checked:
                    if "Good job!" in st.session_state.result_message:
                        st.session_state.answer_display_message = feedback_box(
                            "<strong>Helyes válasz!</strong>", "correct"
                        )
                    else:
                        canonical = answer_options[0] if answer_options else "—"
                        st.session_state.answer_display_message = feedback_box(
                            f"<strong>Helytelen válasz. Egy helyes megoldás:</strong> {heavy(canonical, italic=True)}.",
                            "incorrect",
                        )

            st.form_submit_button(
                "Válasz ellenőrzése",
                key="form_submission_button",
                on_click=submit_pair_answer,
                disabled=st.session_state.button_disable,
                width="stretch",
            )

        feedback_space = st.container(height=90, border=False)
        with feedback_space:
            if st.session_state.answer_display_message.lstrip().startswith("<div"):
                st.markdown(st.session_state.answer_display_message, unsafe_allow_html=True)
            else:
                st.markdown(st.session_state.answer_display_message)

        curr_question = {
            "pos": "agreement_inflect",
            "word": [noun, adjective],
            "id": {
                "case": case,
                "num": "sg",
                "gender": gender,
                "noun_decl": str(noun_vocab[noun].get("decl")),
                "adj_decl": str(adj_vocab[adjective].get("decl")),
            },
        }
        if st.session_state.append_answer is True:
            questions_asked.append(curr_question)
            st.session_state.append_answer = False

    control_row = st.container(height=110, border=False)
    with control_row:
        new_question_col, _, score_col = st.columns([1, 1, 1], gap="medium", vertical_alignment="top")
        with new_question_col:
            st.button(
                "Új kérdés" if st.session_state.question_list else "Kattints ide az első kérdéshez!",
                on_click=new_question,
                args=(st.session_state.gen_func,),
                key="question_button",
                width="stretch",
                disabled=not declension or not adjective_declension or not active_vocab or not active_adj_vocab,
                type="secondary" if st.session_state.question_list else "primary",
            )
        with score_col:
            st.button("Pontszám nullázása", "reset", on_click=reset, width="stretch")
            st.markdown(
                f'<div style="text-align:right;">Jelenlegi pontszám: <strong>{st.session_state.current_score}</strong> / <strong>{st.session_state.total_questions}</strong></div>',
                unsafe_allow_html=True,
            )

    if st.session_state.auto_advance_trigger and st.session_state.answer_checked:
        time.sleep(auto_advance_delay())
        new_question(st.session_state.gen_func)
        st.rerun()
else:
'''

source = prefix + pair_quiz + textwrap.indent(original_quiz, "    ")

# Execute the transformed Agreement page. Recognition remains handled by the
# established recognition transform; number switching gets its own normal
# runtime branch below, without further source-to-source rewriting.
exec(compile(source, str(Path(__file__).with_name("agreement_base.py")), "exec"))
