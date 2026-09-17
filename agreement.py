from pathlib import Path

# Initial agreement exercise scaffold: execute an isolated clone of the noun exercise.
# The source clone lives in agreement_base.py so subsequent agreement-specific work
# can diverge without changing nouns.py.
source = Path(__file__).with_name("agreement_base.py").read_text(encoding="utf-8")

# Give the cloned page its own identity and settings namespace while preserving
# the noun exercise's behaviour for the initial scaffold.
source = source.replace('st.set_page_config("BevLat – Főnevek", layout="centered")',
                        'st.set_page_config("BevLat – Egyeztetés", layout="centered")')
source = source.replace('page_id = "nouns"', 'page_id = "agreement"')
source = source.replace('st.markdown("# Főnevek")', 'st.markdown("# Egyeztetés")')
source = source.replace('"nouns.py"', '"agreement.py"')
source = source.replace('nouns_', 'agreement_')

# agreement_base.py still refers to the shared macron preference dictionary.
# Seed the agreement-specific key from the noun default until we design the
# agreement exercise's own option set.
if '"agreement_enforce_macrons"' in source:
    source = source.replace(
        'st.session_state.agreement_enforce_macrons = st.session_state.enforce_macrons["agreement_enforce_macrons"]',
        'st.session_state.enforce_macrons.setdefault("agreement_enforce_macrons", st.session_state.enforce_macrons.get("nouns_enforce_macrons", False))\n'
        'st.session_state.agreement_enforce_macrons = st.session_state.enforce_macrons["agreement_enforce_macrons"]'
    )

exec(compile(source, str(Path(__file__).with_name("agreement_base.py")), "exec"))
