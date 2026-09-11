from pathlib import Path

path = Path('verbs.py')
text = path.read_text()
replacements = {
    'spacer = \'<td aria-hidden="true" style="width:0.8rem;padding:0;"></td>\'':
        'spacer = \'<td aria-hidden="true" style="width:0.45rem;padding:0;border:0;background:transparent;"></td>\'',
    "cell_style = 'padding:0.08rem 0.28rem;text-align:center;white-space:nowrap;font-weight:800;'":
        "cell_style = 'padding:0 0.18rem;text-align:center;white-space:nowrap;font-weight:800;border:0!important;background:transparent!important;box-shadow:none!important;'",
    "label_style = 'padding:0.08rem 0.55rem 0.08rem 0;text-align:right;white-space:nowrap;font-weight:700;'":
        "label_style = 'padding:0 0.4rem 0 0;text-align:right;white-space:nowrap;font-weight:700;border:0!important;background:transparent!important;box-shadow:none!important;'",
    "'<table role=\"presentation\" style=\"border-collapse:collapse;border:0;background:transparent;line-height:1.55;\">'":
        "'<table role=\"presentation\" cellspacing=\"0\" cellpadding=\"0\" style=\"border-collapse:collapse!important;border-spacing:0!important;border:0!important;outline:0!important;background:transparent!important;box-shadow:none!important;line-height:1.45;\">'",
}
for old, new in replacements.items():
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'Expected 1 occurrence of {old!r}, found {count}')
    text = text.replace(old, new)
compile(text, 'verbs.py', 'exec')
path.write_text(text)
