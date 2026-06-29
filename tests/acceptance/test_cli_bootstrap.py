from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


# specmason: @scenario-EPUBCHECK-5FBA1639
def test_python_module_version() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pyepubcheck", "--version"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "EPUBCheck v0.1.0"


# specmason: @scenario-EPUBCHECK-070C55A5
def test_python_module_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pyepubcheck", "-h"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage: pyepubcheck" in result.stdout
