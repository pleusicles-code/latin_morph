import streamlit as st
import utils


def _invisible_version(value):
    """Encode a small integer invisibly so a new question gets a new expander identity."""
    value = max(0, int(value))
    bits = bin(value)[2:] or "0"
    return "\u2063" + "".join("\u200b" if bit == "0" else "\u200c" for bit in bits)


if "_bevlat_settings_expander_version" not in st.session_state:
    st.session_state["_bevlat_settings_expander_version"] = 0


if not hasattr(st, "_bevlat_original_expander"):
    st._bevlat_original_expander = st.expander

    def _bevlat_expander(label, *args, **kwargs):
        if label in ("Beállítások", "Settings"):
            version = st.session_state.get("_bevlat_settings_expander_version", 0)
            label = label + _invisible_version(version)
            practice_active = bool(st.session_state.get("current_question"))

            # Before practice starts the settings are open. Every newly generated
            # question gets a fresh invisible expander identity and starts closed.
            args = list(args)
            if args:
                args[0] = not practice_active
            else:
                kwargs["expanded"] = not practice_active
            args = tuple(args)

        return st._bevlat_original_expander(label, *args, **kwargs)

    st.expander = _bevlat_expander


if not hasattr(utils, "_bevlat_original_new_question"):
    utils._bevlat_original_new_question = utils.new_question

    def _bevlat_new_question(gen_question):
        st.session_state["_bevlat_settings_expander_version"] = (
            st.session_state.get("_bevlat_settings_expander_version", 0) + 1
        )
        return utils._bevlat_original_new_question(gen_question)

    utils.new_question = _bevlat_new_question
