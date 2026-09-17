from pathlib import Path
import vocab


_original_import_adjectives = vocab.import_adjectives


def _agreement_import_adjectives():
    adjectives = _original_import_adjectives()
    return {
        adjective: info
        for adjective, info in adjectives.items()
        if not info.get("pronominal")
        and not info.get("irreg")
    }


vocab.import_adjectives = _agreement_import_adjectives
try:
    loader = Path(__file__).with_name("agreement_loader.py").read_text(encoding="utf-8")
    exec(compile(loader, str(Path(__file__).with_name("agreement_loader.py")), "exec"))
finally:
    vocab.import_adjectives = _original_import_adjectives
