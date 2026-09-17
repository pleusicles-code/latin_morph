def apply_regular_adjective_filter(source):
    marker = (
        'adj_vocab = {**filter_vocab_by_repo(import_adjectives(), "alap1"), '
        '**filter_vocab_by_repo(import_adjectives(), "alap2"), '
        '**filter_vocab_by_repo(import_adjectives(), "alap3")}'
    )
    replacement = marker + '''
adj_vocab = {
    adj: info for adj, info in adj_vocab.items()
    if not info.get("pronominal")
    and not info.get("irreg")
}'''
    if marker not in source:
        raise RuntimeError("Could not locate agreement adjective vocabulary")
    return source.replace(marker, replacement, 1)
