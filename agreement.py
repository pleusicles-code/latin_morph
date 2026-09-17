from pathlib import Path

loader = Path(__file__).with_name("agreement_loader.py").read_text(encoding="utf-8")
exec(compile(loader, str(Path(__file__).with_name("agreement_loader.py")), "exec"))
