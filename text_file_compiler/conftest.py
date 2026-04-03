import sys
from pathlib import Path

# Ensure project root is on sys.path so tests can import top-level modules
ROOT = Path(__file__).parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
