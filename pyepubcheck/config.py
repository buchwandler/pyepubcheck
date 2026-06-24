"""Validation configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

ValidationMode = Literal["auto", "opf", "xhtml", "svg", "nav", "mo", "exp"]


@dataclass(frozen=True)
class ValidationConfig:
    input_path: Path | None = None
    mode: ValidationMode = "auto"
    epub_version: str = "3.0"
    profile: str = "default"
    quiet: bool = False
    fail_on_warnings: bool = False
    xml_report: str | None = None
    json_report: str | None = None
    xmp_report: str | None = None
    locale: str | None = None
    custom_messages: str | None = None
