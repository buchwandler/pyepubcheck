"""Shared pytest configuration for pyepubcheck."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import FixtureLocator, invoke_pyepubcheck


@pytest.fixture
def fixtures() -> FixtureLocator:
    return FixtureLocator(Path("specs/behavior/features"))


@pytest.fixture
def run_pyepubcheck(tmp_path: Path):
    def run(
        *args: str | Path,
        transport: str = "in_process",
    ):
        return invoke_pyepubcheck(args, cwd=tmp_path, transport=transport)

    return run
