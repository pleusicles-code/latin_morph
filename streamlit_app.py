"""Streamlit deployment entry point."""

import inspect
import runpy
import streamlit as st
import utils
import vocab


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
    st.form_submit_button = _bevlat_form_submit_button
    st._bevlat_noun_form_input_handling = True


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

        # This relaxation belongs only to noun recognition. Other morphology
        # parsers retain the original tokenizer behavior.
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


runpy.run_path("latin_morph.py", run_name="__main__")
