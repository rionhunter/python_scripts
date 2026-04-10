import importlib
import os
import pytest


def test_startup_check_offscreen():
    """Smoke-test that the application can be created in offscreen mode."""
    try:
        importlib.import_module("PyQt6")
    except ImportError:
        pytest.skip("PyQt6 not installed")

    import subprocess
    import sys

    # Run the startup check in a subprocess to avoid Qt state issues in-process
    cmd = [sys.executable, "main.py", "--check", "--offscreen"]
    env = dict(**os.environ)
    env["TFC_SKIP_DEP_CHECK"] = "1"
    result = subprocess.run(cmd, cwd=".", env=env)
    assert result.returncode == 0
