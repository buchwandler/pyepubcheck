"""Acceptance-harness helpers for pyepubcheck."""

from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
import xml.etree.ElementTree as ET

from pyepubcheck.cli import main as cli_main

REPO_ROOT = Path(__file__).resolve().parents[1]
MESSAGE_RE = re.compile(r"(?P<severity>FATAL|ERROR|WARNING|USAGE)\((?P<id>[A-Z]+-\d{3})\)")


class FixtureLocator:
    """Resolve fixture paths under the imported behavior corpus."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def resolve(self, relative: str | Path) -> Path:
        cleaned = str(relative).lstrip("/")
        return (self.root / cleaned).resolve()

    def fixture_dir(self, relative: str | Path) -> Path:
        return self.resolve(relative)

    def fixture_path(self, base: str | Path, leaf: str | Path = "") -> Path:
        return self.resolve(Path(str(base).lstrip("/")) / leaf)


@dataclass
class CliResult:
    returncode: int
    stdout: str
    stderr: str
    json_report: dict[str, Any] | None = None
    xml_report: ET.Element | None = None

    def _messages(self) -> list[dict[str, str]]:
        if self.json_report is not None:
            payload = self.json_report.get("messages", [])
            if isinstance(payload, list):
                return [
                    {
                        "id": str(item.get("id", "")),
                        "severity": str(item.get("severity", "")),
                    }
                    for item in payload
                    if isinstance(item, dict)
                ]
        combined = f"{self.stdout}\n{self.stderr}"
        return [
            {"severity": match.group("severity"), "id": match.group("id")}
            for match in MESSAGE_RE.finditer(combined)
        ]

    def _has(self, severity: str, message_id: str) -> bool:
        return any(
            item["severity"] == severity and item["id"] == message_id
            for item in self._messages()
        )

    def has_error(self, message_id: str) -> bool:
        return self._has("ERROR", message_id) or self._has("FATAL", message_id)

    def has_warning(self, message_id: str) -> bool:
        return self._has("WARNING", message_id)

    def has_usage(self, message_id: str) -> bool:
        return self._has("USAGE", message_id)

    def count(self, message_id: str) -> int:
        return sum(1 for item in self._messages() if item["id"] == message_id)

    def no_other_errors_or_warnings(
        self,
        except_ids: set[str] = frozenset(),
    ) -> bool:
        return all(
            item["id"] in except_ids
            for item in self._messages()
            if item["severity"] in {"FATAL", "ERROR", "WARNING"}
        )


def build_epub_from_directory(source_dir: Path, output_path: Path | None = None) -> Path:
    source_dir = source_dir.resolve()
    destination = output_path or source_dir.with_suffix(".epub")
    with zipfile.ZipFile(destination, "w") as archive:
        mimetype = source_dir / "mimetype"
        if mimetype.is_file():
            archive.write(mimetype, "mimetype", compress_type=zipfile.ZIP_STORED)
        for path in sorted(source_dir.rglob("*")):
            if not path.is_file() or path == mimetype:
                continue
            archive.write(path, path.relative_to(source_dir).as_posix())
    return destination


def _option_value(args: list[str], names: Iterable[str]) -> str | None:
    names = tuple(names)
    for index, value in enumerate(args):
        if value in names and index + 1 < len(args):
            return args[index + 1]
    return None


def _load_optional_reports(args: list[str], cwd: Path, stdout: str) -> tuple[dict[str, Any] | None, ET.Element | None]:
    json_target = _option_value(args, ("--json", "-j"))
    xml_target = _option_value(args, ("--out", "-o"))

    json_report: dict[str, Any] | None = None
    if json_target == "-":
        json_report = json.loads(stdout) if stdout.strip() else None
    elif json_target and (cwd / json_target).is_file():
        json_report = json.loads((cwd / json_target).read_text(encoding="utf-8"))

    xml_report: ET.Element | None = None
    if xml_target and xml_target != "-" and (cwd / xml_target).is_file():
        xml_report = ET.fromstring((cwd / xml_target).read_text(encoding="utf-8"))

    return json_report, xml_report


def invoke_pyepubcheck(
    args: Iterable[str | Path],
    *,
    cwd: Path,
    transport: str = "in_process",
) -> CliResult:
    rendered = [str(arg) for arg in args]
    cwd = cwd.resolve()

    if transport == "subprocess":
        env = os.environ.copy()
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(REPO_ROOT) if not existing else f"{REPO_ROOT}{os.pathsep}{existing}"
        completed = subprocess.run(
            [sys.executable, "-m", "pyepubcheck", *rendered],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        json_report, xml_report = _load_optional_reports(rendered, cwd, completed.stdout)
        return CliResult(completed.returncode, completed.stdout, completed.stderr, json_report, xml_report)

    if transport != "in_process":
        raise ValueError(f"unsupported transport: {transport}")

    stdout = io.StringIO()
    stderr = io.StringIO()
    previous_cwd = Path.cwd()
    try:
        os.chdir(cwd)
        with redirect_stdout(stdout), redirect_stderr(stderr):
            returncode = cli_main(rendered)
    finally:
        os.chdir(previous_cwd)

    out = stdout.getvalue()
    err = stderr.getvalue()
    json_report, xml_report = _load_optional_reports(rendered, cwd, out)
    return CliResult(returncode, out, err, json_report, xml_report)
