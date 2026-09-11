"""Streamlit deployment entry point."""

import inspect
import runpy
import streamlit as st
import utils
import vocab


if not getattr(st, "_bevlat_global_content_width", False):
    _original_set_page_config = st.set_page_config

    def _bevlat_set_page_config(*args, **kwargs):
        result = _original_set_page_config(*args, **kwargs)
        st.markdown(
            """
            <style>
            [data-testid="stMainBlockContainer"],
            .stMainBlockContainer {
                max-width: 1300px !important;
                padding-top: 2rem !important;
            }

            .block-container {
                max-width: 1300px !important;
                padding-top: 2rem !important;
                padding-left: 40px !important;
                margin-top: 0 !important;
                margin-left: 0 !important;
                margin-right: auto !important;
            }

            [data-testid="stElementContainer"]:has(.bevlat-global-style-marker),
            .element-container:has(.bevlat-global-style-marker) {
                display: none !important;
            }
            </style>
            <span class="bevlat-global-style-marker"></span>
            """,
            unsafe_allow_html=True,
        )
        return result

    st.set_page_config = _bevlat_set_page_config
    st._bevlat_global_content_width = True


if not getattr(st, "_bevlat_hungarian_select_placeholders", False):
    _original_selectbox = st.selectbox
    _original_multiselect = st.multiselect

    def _hungarian_selectbox(*args, **kwargs):
        kwargs.setdefault("placeholder", "Válassz egy lehetőséget!")
        return _original_selectbox(*args, **kwargs)

    def _hungarian_multiselect(*args, **kwargs):
        kwargs.setdefault("placeholder", "Válassz egy vagy több lehetőséget!")
        return _original_multiselect(*args, **kwargs)

    st.selectbox = _hungarian_selectbox
    st.multiselect = _hungarian_multiselect
    st._bevlat_hungarian_select_placeholders = True


if not getattr(st, "_bevlat_noun_form_input_handling", False):
    _original_form = st.form
    _original_form_submit_button = st.form_submit_button
    _original_text_input = st.text_input

    class _BevlatFormContext:
        def __init__(self, context, key):
            self.context = context
            self.key = key
            self.previous_key = None

        def __enter__(self):
            self.previous_key = getattr(st, "_bevlat_current_form_key", None)
            st._bevlat_current_form_key = self.key
            return self.context.__enter__()

        def __exit__(self, exc_type, exc_value, traceback):
            try:
                return self.context.__exit__(exc_type, exc_value, traceback)
            finally:
                st._bevlat_current_form_key = self.previous_key

    def _bevlat_form(*args, **kwargs):
        key = kwargs.get("key", args[0] if args else None)
        if key == "noun_form":
            kwargs["clear_on_submit"] = False
        return _BevlatFormContext(_original_form(*args, **kwargs), key)

    def _bevlat_text_input(*args, **kwargs):
        label = kwargs.get("label", args[0] if args else None)
        if (
            getattr(st, "_bevlat_current_form_key", None) == "noun_form"
            and st.session_state.get("nouns_exercise_type") == "recognize"
            and label == "Válaszod:"
        ):
            kwargs.setdefault(
                "help",
                "A válaszokat beírhatod rövidítés nélkül (**pluralis nominativus**) vagy rövidítve "
                "(**sing. acc.** vagy **sg. gen.**), azonos számú eseteket egymás után (**sg. dat. abl.**) "
                "és mindezt bármilyen központozással vagy anélkül (**sg.gen** vagy akár **sggen**). "
                "Ha minden megadott esetet ugyanolyan számúnak veszel, akkor a sorrend sem számít "
                "(**abl,sg** = **sg. abl.**).",
            )
        return _original_text_input(*args, **kwargs)

    def _bevlat_form_submit_button(*args, **kwargs):
        if (
            getattr(st, "_bevlat_current_form_key", None) == "noun_form"
            and kwargs.get("on_click") is not None
        ):
            original_callback = kwargs["on_click"]

            def wrapped_callback(*callback_args, **callback_kwargs):
                original_callback(*callback_args, **callback_kwargs)

                if st.session_state.get("nouns_exercise_type") == "recognize":
                    parse_failed = (
                        not st.session_state.get("answer_checked", False)
                        and st.session_state.get("answer_display_message", "").startswith(
                            "Ellenőrizd a válasz formátumát"
                        )
                    )
                    if parse_failed:
                        return

                st.session_state["answer_input"] = ""

            kwargs["on_click"] = wrapped_callback

        return _original_form_submit_button(*args, **kwargs)

    st.form = _bevlat_form
    st.text_input = _bevlat_text_input
    st.form_submit_button = _bevlat_form_submit_button
    st._bevlat_noun_form_input_handling = True


if not getattr(st, "_bevlat_noun_recognition_input_help_v2", False):
    _previous_text_input = st.text_input

    def _bevlat_noun_recognition_text_input(*args, **kwargs):
        label = kwargs.get("label", args[0] if args else None)
        if (
            getattr(st, "_bevlat_current_form_key", None) == "noun_form"
            and st.session_state.get("nouns_exercise_type") == "recognize"
            and label == "Válaszod:"
        ):
            kwargs.setdefault(
                "help",
                "A válaszokat beírhatod rövidítés nélkül (**pluralis nominativus**) vagy rövidítve "
                "(**sing. acc.** vagy **sg. gen.**), azonos számú eseteket egymás után (**sg. dat. abl.**) "
                "és mindezt bármilyen központozással vagy anélkül (**sg.gen** vagy akár **sggen**). "
                "Ha minden megadott esetet ugyanolyan számúnak veszel, akkor a sorrend sem számít "
                "(**abl,sg** = **sg. abl.**).",
            )
        return _previous_text_input(*args, **kwargs)

    st.text_input = _bevlat_noun_recognition_text_input
    st._bevlat_noun_recognition_input_help_v2 = True


if not getattr(st, "_bevlat_deferred_answer_input_clear", False):
    _previous_text_input_for_clear = st.text_input

    def _bevlat_deferred_clear_text_input(*args, **kwargs):
        key = kwargs.get("key")
        if key == "answer_input" and st.session_state.pop("_bevlat_clear_answer_input", False):
            st.session_state.pop("answer_input", None)
        return _previous_text_input_for_clear(*args, **kwargs)

    st.text_input = _bevlat_deferred_clear_text_input
    st._bevlat_deferred_answer_input_clear = True


if not getattr(st, "_bevlat_noun_multiple_answer_inline", False):
    _original_markdown = st.markdown

    def _bevlat_markdown(body, *args, **kwargs):
        if isinstance(body, str) and "Több helyes válaszlehetőség" in body:
            body = body.replace(
                '<br><span style="color:#7c3aed;">Több helyes válaszlehetőség van.</span>',
                '<span style="color:#7c3aed;">Több helyes válaszlehetőség van.</span>',
            )
            body = body.replace("<br>Több helyes válaszlehetőség is lehet.", "Több helyes válaszlehetőség is lehet.")
        return _original_markdown(body, *args, **kwargs)

    st.markdown = _bevlat_markdown
    st._bevlat_noun_multiple_answer_inline = True


if not getattr(utils, "_bevlat_noun_single_number_token_order", False):
    _original_tokenize_morphology_answer = utils.tokenize_morphology_answer
    _noun_number_tokens = {
        "sg", "sing", "singular", "singularis",
        "pl", "plur", "plural", "pluralis",
    }
    _noun_case_tokens = {
        "nom", "nominative", "nominativus",
        "voc", "vocative", "vocativus",
        "acc", "accusative", "accusativus",
        "gen", "genitive", "genitivus",
        "dat", "dative", "dativus",
        "abl", "ablative", "ablativus",
    }
    _noun_analysis_tokens = tuple(
        sorted(_noun_number_tokens | _noun_case_tokens, key=len, reverse=True)
    )

    def _segment_noun_answer_token(token):
        memo = {}

        def segment_from(index):
            if index == len(token):
                return []
            if index in memo:
                return memo[index]
            for candidate in _noun_analysis_tokens:
                if token.startswith(candidate, index):
                    remainder = segment_from(index + len(candidate))
                    if remainder is not None:
                        memo[index] = [candidate] + remainder
                        return memo[index]
            memo[index] = None
            return None

        return segment_from(0)

    def _bevlat_tokenize_morphology_answer(text):
        raw_tokens = _original_tokenize_morphology_answer(text)

        if not any(frame.function == "parse_noun_analysis_answer" for frame in inspect.stack()[1:6]):
            return raw_tokens

        segmented = []
        for raw_token in raw_tokens:
            pieces = _segment_noun_answer_token(raw_token)
            if pieces is None:
                return raw_tokens
            segmented.extend(pieces)

        number_tokens = [token for token in segmented if token in _noun_number_tokens]
        case_tokens = [token for token in segmented if token in _noun_case_tokens]
        if len(number_tokens) == 1 and case_tokens:
            return number_tokens + case_tokens

        return raw_tokens

    utils.tokenize_morphology_answer = _bevlat_tokenize_morphology_answer
    utils._bevlat_noun_single_number_token_order = True


if not getattr(vocab, "_bevlat_noun_data_fixes", False):
    _original_import_nouns = vocab.import_nouns

    def _bevlat_import_nouns():
        noun_vocab = _original_import_nouns()
        mare = noun_vocab.get("mare")
        if mare:
            mare.get("irreg", {}).get("pl", {}).pop("gen", None)
        return noun_vocab

    vocab.import_nouns = _bevlat_import_nouns
    vocab._bevlat_noun_data_fixes = True


if not getattr(st, "_bevlat_score_reset_panel", False):
    _score_original_button = st.button
    _score_previous_markdown = st.markdown

    def _mix_hex(start, end, amount):
        amount = max(0.0, min(1.0, amount))
        start_rgb = tuple(int(start[index:index + 2], 16) for index in (1, 3, 5))
        end_rgb = tuple(int(end[index:index + 2], 16) for index in (1, 3, 5))
        mixed = tuple(round(a + (b - a) * amount) for a, b in zip(start_rgb, end_rgb))
        return "#" + "".join(f"{value:02x}" for value in mixed)

    def _score_color(percentage):
        if percentage <= 50:
            return _mix_hex("#b93232", "#d95749", percentage / 50 if percentage else 0)
        if percentage <= 80:
            return _mix_hex("#d95749", "#dfca3f", (percentage - 50) / 30)
        return _mix_hex("#dfca3f", "#2f9e55", (percentage - 80) / 20)

    def _bevlat_score_button(label, *args, **kwargs):
        if label != "Pontszám nullázása":
            return _score_original_button(label, *args, **kwargs)

        current_score = st.session_state.get("current_score", 0)
        total_questions = st.session_state.get("total_questions", 0)
        percentage = (100 * current_score / total_questions) if total_questions else 0
        percentage_text = f"{percentage:.0f}%"

        score_col, reset_col = st.columns(
            [2, 1],
            gap="small",
            vertical_alignment="center",
        )

        with score_col:
            fill_html = ""
            if total_questions >= 6:
                fill_html = (
                    f'<div style="height:100%;width:{max(0, min(100, percentage)):.1f}%;'
                    f'background:{_score_color(percentage)};border-radius:999px;"></div>'
                )
            bar_html = (
                '<div style="height:6px;background:rgba(128,128,128,0.18);border-radius:999px;'
                f'overflow:hidden;margin-top:0.25rem;">{fill_html}</div>'
            )
            score_html = (
                '<div style="min-height:2.5rem;display:flex;flex-direction:column;justify-content:center;'
                'padding:0.28rem 0.5rem 0.32rem 0.5rem;line-height:1.2;font-size:1.08rem;'
                'transform:translateY(-7px);background:rgba(128,128,128,0.055);border-radius:0.55rem;">'
                '<div style="display:flex;align-items:center;justify-content:space-between;white-space:nowrap;">'
                f'<span>Pontszám: <strong>{current_score:g}</strong> / <strong>{total_questions}</strong></span>'
                f'<strong style="margin-left:0.75rem;">{percentage_text}</strong>'
                '</div>'
                f'{bar_html}'
                '</div>'
            )
            _score_previous_markdown(score_html, unsafe_allow_html=True)

        with reset_col:
            return _score_original_button("Újrakezdés", *args, **kwargs)

    def _bevlat_score_markdown(body, *args, **kwargs):
        if (
            isinstance(body, str)
            and "Jelenlegi pontszám:" in body
            and "text-align:right" in body
        ):
            return None
        return _score_previous_markdown(body, *args, **kwargs)

    st.button = _bevlat_score_button
    st.markdown = _bevlat_score_markdown
    st._bevlat_score_reset_panel = True


runpy.run_path("latin_morph.py", run_name="__main__")
