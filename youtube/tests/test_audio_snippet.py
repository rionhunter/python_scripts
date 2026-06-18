import os
import sys
import tempfile
import subprocess
import time

import pytest

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from audio_snippet import convert_to_seconds


YT_TEST_URL = "https://www.youtube.com/watch?v=BaW_jenozKc"


def test_convert_to_seconds_basic():
    assert convert_to_seconds("5") == 5
    assert convert_to_seconds("01:02") == 62
    assert convert_to_seconds("1:02:03") == 3723
    with pytest.raises(ValueError):
        convert_to_seconds("")


@pytest.mark.integration
def test_cli_download_snippet_mp3():
    # Downloads a 2-second snippet and verifies file exists and nonempty
    with tempfile.TemporaryDirectory() as tmp:
        out_path = os.path.join(tmp, "clip.mp3")
        cmd = [
            sys.executable,
            "audio_snippet.py",
            "--no-gui",
            "--url",
            YT_TEST_URL,
            "--start",
            "0",
            "--end",
            "2",
            "--format",
            "mp3",
            "--output",
            out_path,
            "--quality",
            "128",
        ]
        print("Running:", " ".join(cmd))
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print("STDOUT:\n", res.stdout)
            print("STDERR:\n", res.stderr)
        assert res.returncode == 0
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0
