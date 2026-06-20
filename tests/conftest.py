"""Shared pytest fixtures and path setup for the test suite."""

import sys
from pathlib import Path

# Ensure `src/` is importable so tests can do `from dingtalk_downloader.xxx import yyy`
SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
