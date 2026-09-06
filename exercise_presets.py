import streamlit as st
from urllib.parse import urlencode, urlsplit, urlunsplit


EXERCISE_PARAM = "_exercise"


def widget_key(page_id, setting_name):
    return f"{page_id}_{setting_name}"


def widget_kwargs(page_id, setting_name, resolved_settings, value_arg="value"):
    """Return widget kwargs without conflicting with preloaded session state."""
    key = widget_key(page_id, setting_name)
    kwargs = {"key": key}
    if key not in st.session_state:
        kwargs[value_arg] = resolved_settings[setting_name]
    return kwargs


def bool_setting(default):
    return {"kind": "bool", "default": default}


def choice_setting(default, choices):
    if isinstance(choices, dict):
        token_map = dict(choices)
    else:
        token_map = {str(value): value for value in choices}
    return {"kind": "choice", "default": default, "tokens": token_map}


def list_setting(default, choices):
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
        values = [token_map[token] for token in raw_tokens]
        if len({repr(value) for value in values}) != len(values):
            raise ValueError("duplicate list choice")
        return values
    raise ValueError("unknown setting kind")


def _encode_value(value, spec):
    kind = spec["kind"]
    if kind == "bool":
        return "true" if bool(value) else "false"
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


def _clear_widget_state(page_id, schema):
    for name in schema:
        st.session_state.pop(widget_key(page_id, name), None)


def resolve_exercise_settings(page_id, schema, saved_defaults):
    """Resolve URL -> saved exercise defaults -> generic defaults.

    Invalid/obsolete parameters are ignored. A newly loaded valid URL initializes
    widget state once; later reruns preserve user edits. Generated links are scoped
    to one exercise so their parameters are cleared after navigation elsewhere.
    """
    query = st.query_params.to_dict()
    scoped_page = query.get(EXERCISE_PARAM)
    if scoped_page is not None and scoped_page != page_id:
        st.query_params.clear()
        query = {}

    resolved = {}
    valid_url_setting_seen = False
    valid_raw_params = []
    for name, spec in schema.items():
        fallback = saved_defaults.get(name, spec["default"])
        if name not in query:
            resolved[name] = fallback
            continue
        try:
            resolved[name] = _decode_value(query[name], spec)
            valid_url_setting_seen = True
            valid_raw_params.append((name, query[name]))
        except (TypeError, ValueError):
            resolved[name] = fallback

    previous_page = st.session_state.get("url_preset_page")
    previous_active = bool(st.session_state.get("url_preset_active"))

    if valid_url_setting_seen:
        signature = (page_id, tuple(valid_raw_params))
        if st.session_state.get("url_preset_signature") != signature:
            for name, value in resolved.items():
                st.session_state[widget_key(page_id, name)] = value
            st.session_state.url_preset_signature = signature
        st.session_state.url_preset_active = True
        st.session_state.url_preset_page = page_id
    else:
        if previous_active and previous_page == page_id:
            _clear_widget_state(page_id, schema)
        st.session_state.url_preset_active = False
        st.session_state.url_preset_page = None
        st.session_state.url_preset_signature = None
    return resolved


def url_preset_active(page_id):
    return bool(st.session_state.get("url_preset_active") and st.session_state.get("url_preset_page") == page_id)


def build_exercise_link(page_id, schema, current_settings):
    params = [(EXERCISE_PARAM, page_id)]
    for name, spec in schema.items():
        value = current_settings.get(name, spec["default"])
        params.append((name, _encode_value(value, spec)))
    parts = urlsplit(st.context.url)
    base_url = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    return f"{base_url}?{urlencode(params)}"


def exercise_link_popover(page_id, schema, current_settings, *, label="Copy exercise link"):
    link = build_exercise_link(page_id, schema, current_settings)
    with st.popover(
        label,
        width="stretch",
        help=("Create a link that reproduces the current exercise settings. "
              "The link does not include personal preferences such as macron enforcement, consonantal u, or auto-advance."),
    ):
        st.caption("Copy this link and send it to your students:")
        st.code(link, language=None, wrap_lines=True)
