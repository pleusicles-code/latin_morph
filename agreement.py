from pathlib import Path

# Agreement exercise scaffold: execute an isolated clone of the noun exercise.
# The source clone lives in agreement_base.py so agreement-specific work can
# diverge without changing nouns.py.
source = Path(__file__).with_name("agreement_base.py").read_text(encoding="utf-8")

# Give the cloned page its own identity and settings namespace.
source = source.replace('st.set_page_config("BevLat – Főnevek", layout="centered")',
                        'st.set_page_config("BevLat – Főnév és melléknév egyeztetése", layout="centered")')
source = source.replace('page_id = "nouns"', 'page_id = "agreement"')
source = source.replace('st.markdown("# Főnevek")', 'st.markdown("# Főnév és melléknév egyeztetése")')
source = source.replace('"nouns.py"', '"agreement.py"')
source = source.replace('nouns_', 'agreement_')

# agreement_base.py still refers to the shared macron preference dictionary.
# Seed the agreement-specific key from the noun default for now.
if '"agreement_enforce_macrons"' in source:
    source = source.replace(
        'st.session_state.agreement_enforce_macrons = st.session_state.enforce_macrons["agreement_enforce_macrons"]',
        'st.session_state.enforce_macrons.setdefault("agreement_enforce_macrons", st.session_state.enforce_macrons.get("nouns_enforce_macrons", False))\n'
        'st.session_state.agreement_enforce_macrons = st.session_state.enforce_macrons["agreement_enforce_macrons"]'
    )

# Agreement-specific exercise types. Until the new agreement mechanics are
# implemented, the middle mode follows the inflection path so the page remains
# operational rather than falling into recognition logic.
source = source.replace(
    '"exercise_type": choice_setting("inflect", ["inflect", "recognize"]),',
    '"exercise_type": choice_setting("inflect", ["inflect", "agreement", "recognize"]),'
)
source = source.replace(
    'options=["inflect", "recognize"],\n            format_func=lambda value: {\n                "inflect": "Ragozás",\n                "recognize": "Alakfelismerés",\n            }[value],',
    'options=["inflect", "agreement", "recognize"],\n            format_func=lambda value: {\n                "inflect": "Ragozás",\n                "agreement": "Egyeztetés",\n                "recognize": "Alakfelismerés",\n            }[value],'
)
source = source.replace(
    'if exercise_type == "inflect":',
    'if exercise_type in ("inflect", "agreement"):'
)

# Adjective declension selector and future degree option.
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

# Persist the two new settings alongside the cloned noun settings.
source = source.replace(
    '"include_vocative": include_vocative,\n    "declension": declension,',
    '"include_vocative": include_vocative,\n    "include_degrees": include_degrees,\n    "declension": declension,\n    "adjective_declension": adjective_declension,'
)
source = source.replace(
    '"include_vocative": False,\n        "declension": DEFAULT_DECLENSIONS,',
    '"include_vocative": False,\n        "include_degrees": False,\n        "declension": DEFAULT_DECLENSIONS,\n        "adjective_declension": DEFAULT_ADJECTIVE_DECLENSIONS,'
)
source = source.replace(
    'st.session_state.agreement_include_vocative = False\n        st.session_state.agreement_declension = DEFAULT_DECLENSIONS',
    'st.session_state.agreement_include_vocative = False\n        st.session_state.agreement_include_degrees = False\n        st.session_state.agreement_declension = DEFAULT_DECLENSIONS\n        st.session_state.agreement_adjective_declension = DEFAULT_ADJECTIVE_DECLENSIONS'
)

exec(compile(source, str(Path(__file__).with_name("agreement_base.py")), "exec"))
