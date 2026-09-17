import streamlit as st
import utils


if not hasattr(st, "_bevlat_original_expander"):
    st._bevlat_original_expander = st.expander

    def _bevlat_expander(label, *args, **kwargs):
        is_settings = label in ("Beállítások", "Settings")
        practice_active = bool(st.session_state.get("current_question"))
        collapse_once = bool(
            st.session_state.pop("_bevlat_collapse_settings_once", False)
        ) if is_settings else False

        if is_settings and (practice_active or collapse_once):
            args = list(args)
            if args:
                args[0] = False
            else:
                kwargs["expanded"] = False
            args = tuple(args)
        return st._bevlat_original_expander(label, *args, **kwargs)

    st.expander = _bevlat_expander


if not hasattr(utils, "_bevlat_original_new_question"):
    utils._bevlat_original_new_question = utils.new_question

    def _bevlat_new_question(gen_question):
        st.session_state["_bevlat_collapse_settings_once"] = True
        return utils._bevlat_original_new_question(gen_question)

    utils.new_question = _bevlat_new_question


if not hasattr(st, "_bevlat_original_button"):
    st._bevlat_original_button = st.button

    def _bevlat_button(label, *args, **kwargs):
        new_question_labels = (
            "Új kérdés",
            "Kattints ide az első kérdéshez!",
            "New Question",
            "Click here for the first question!",
        )
        button_key = str(kwargs.get("key") or "")
        is_new_question_button = (
            label in new_question_labels
            or button_key == "question_button"
            or button_key.endswith("_question_button")
        )

        if is_new_question_button:
            original_on_click = kwargs.get("on_click")

            def collapse_then_call(*callback_args, **callback_kwargs):
                st.session_state["_bevlat_collapse_settings_once"] = True
                if original_on_click is not None:
                    return original_on_click(*callback_args, **callback_kwargs)
                return None

            kwargs["on_click"] = collapse_then_call

        return st._bevlat_original_button(label, *args, **kwargs)

    st.button = _bevlat_button
