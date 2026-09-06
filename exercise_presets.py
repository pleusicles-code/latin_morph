import streamlit as st
from urllib.parse import urlencode


def bool_setting(default):
    return {"kind": "bool", "default": default}


def choice_setting(default, choices):
    """Define a scalar setting.

    ``choices`` may be an iterable of internal values or a mapping of stable URL
    tokens to internal values. Using a mapping is useful where the internal value
    is not itself a convenient URL token (for example ``(1, 2)``).
    """
    if isinstance(choices, dict):
        token_map = dict(choices)
    else:
        token_map = {str(value): value for value in choices}
    return {"kind": "choice", "default": default, "tokens": token_map}


def list_setting(default, choices):
    """Define a list-valued setting with comma-separated URL serialization."""
    if isinstance(choices, dict):
        token_map = dict(choices)
    else:
        token_map = {str(value): value for value in choices}
    return {"kind": "list", "default": list(default), "tokens": token_map}


def _decode_bool(raw):
    normalized = str(raw).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError("invalid boolean")


def _decode_value(raw, spec):
    kind = spec["kind"]
    if kind == "bool":
        return _decode_bool(raw)

    token_map = spec["tokens"]
    if kind == "choice":
        if raw not in token_map:
            raise ValueError("invalid choice")
        return token_map[raw]

    if kind == "list":
        if raw == "":
            return []
        raw_tokens = raw.split(",")
        if any(token not in token_map for token in raw_tokens):
            raise ValueError("invalid list choice")
        # Preserve URL order, while rejecting duplicate values as malformed.
        values = [token_map[token] for token in raw_tokens]
        if len({repr(value) for value in values}) != len(values):
            raise ValueError("duplicate list choice")
        return values

    raise ValueError("unknown setting kind")


def _encode_value(value, spec):
    kind = spec["kind"]
    if kind == "bool":
        return "true" if value else "false"

    token_map = spec["tokens"]
    reverse_map = {repr(internal): token for token, internal in token_map.items()}

    if kind == "choice":
        token = reverse_map.get(repr(value))
        if token is None:
            raise ValueError("current value is not valid for this setting")
        return token

    if kind == "list":
        tokens = []
        for item in value:
            token = reverse_map.get(repr(item))
            if token is None:
                raise ValueError("current list value is not valid for this setting")
            tokens.append(token)
        return ",".join(tokens)

    raise ValueError("unknown setting kind")


def resolve_exercise_settings(page_id, schema, saved_defaults):
    """Resolve exercise settings with URL presets taking highest precedence.

    Precedence is URL -> saved per-user exercise defaults -> generic defaults.
    Unknown parameters are ignored. A recognized parameter with an invalid value
    is discarded and falls back exactly as though that parameter were absent.
    The preset is considered active only when at least one recognized parameter
    contains a valid value.
    """
    query = st.query_params.to_dict()
    resolved = {}
    valid_url_setting_seen = False

    for name, spec in schema.items():
        fallback = saved_defaults.get(name, spec["default"])
        if name not in query:
            resolved[name] = fallback
            continue

        try:
            resolved[name] = _decode_value(query[name], spec)
            valid_url_setting_seen = True
        except (TypeError, ValueError):
            resolved[name] = fallback

    st.session_state.url_preset_active = valid_url_setting_seen
    st.session_state.url_preset_page = page_id if valid_url_setting_seen else None
    return resolved


def url_preset_active(page_id):
    return bool(
        st.session_state.get("url_preset_active")
        and st.session_state.get("url_preset_page") == page_id
    )


def build_exercise_link(schema, current_settings):
    """Serialize a complete snapshot of every setting in ``schema``."""
    params = []
    for name, spec in schema.items():
        value = current_settings.get(name, spec["default"])
        params.append((name, _encode_value(value, spec)))
    return f"{st.context.url}?{urlencode(params)}"


def exercise_link_popover(schema, current_settings, *, label="Copy exercise link"):
    """Render a compact link control whose code block has Streamlit's copy UI."""
    link = build_exercise_link(schema, current_settings)
    with st.popover(
        label,
        width="stretch",
        help="Create a link that reproduces the current exercise settings. The link does not include personal preferences such as macron enforcement or auto-advance.",
    ):
        st.caption("Copy this link and send it to your students:")
        st.code(link, language=None, wrap_lines=True)
