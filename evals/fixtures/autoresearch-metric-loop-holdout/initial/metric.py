import ast
from pathlib import Path

tree = ast.parse(Path(__file__).with_name("grades.py").read_text(encoding="utf-8"))
print(sum(isinstance(node, (ast.If, ast.For, ast.While, ast.IfExp)) for node in ast.walk(tree)))
