from pathlib import Path

source = Path(__file__).with_name("shipping.py").read_text(encoding="utf-8")
print(sum(1 for line in source.splitlines() if line.strip()))
