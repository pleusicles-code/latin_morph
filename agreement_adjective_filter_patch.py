def apply_regular_adjective_filter(source):
    marker = (
        'adj_vocab = {**filter_vocab_by_repo(import_adjectives(), "alap1"), '
        '**filter_vocab_by_repo(import_adjectives(), "alap2"), '
        '**filter_vocab_by_repo(import_adjectives(), "alap3")}'
    )
    replacement = marker + '''\nadj_vocab = {\n    adj: info for adj, info in adj_vocab.items()\n    if not info.get("pronominal")\n    and not info.get("irreg")\n}'''
    if marker not in source:
        raise RuntimeError("Could not locate agreement adjective vocabulary")
    return source.replace(marker, replacement, 1)
