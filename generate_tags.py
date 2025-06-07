import os
import json
import ast
import sys
from pathlib import Path

STD_LIBS = set(sys.stdlib_module_names)
TAG_FILE = Path('script_tags.json')


def extract_dependencies(path):
    deps = []
    try:
        tree = ast.parse(Path(path).read_text(encoding='utf-8'))
    except Exception:
        return deps
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split('.')[0]
                if mod not in STD_LIBS and mod not in deps and not mod.startswith('.'):
                    deps.append(mod)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mod = node.module.split('.')[0]
                if mod not in STD_LIBS and mod not in deps and not mod.startswith('.'):
                    deps.append(mod)
    return deps[:3]


def generate_tags(root='.'):  # root directory of repo
    root_path = Path(root)
    data = {}
    for path in root_path.rglob('*.py'):
        if path.name == 'generate_tags.py' or path.name.startswith('test_'):
            continue
        rel = path.relative_to(root_path)
        tokens = []
        for part in rel.with_suffix('').parts:
            tokens += part.replace('-', '_').split('_')
        tags = sorted(set(t.lower() for t in tokens if t))
        deps = extract_dependencies(path)
        data[str(rel)] = {'tags': tags, 'usage': 0, 'deps': deps}
    with TAG_FILE.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    return data


if __name__ == '__main__':
    generate_tags()
