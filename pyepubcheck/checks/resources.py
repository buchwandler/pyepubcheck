"""Publication-resource checks."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

from pyepubcheck.messages import build_message
from pyepubcheck.opf_parser import parse_opf
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml


def _is_remote_url(href: str) -> bool:
    """Check if href is a remote URL."""
    parsed = urlparse(href)
    return parsed.scheme in ("http", "https")


def _is_data_url(href: str) -> bool:
    """Check if href is a data URL."""
    return href.startswith("data:")


def _has_fragment(href: str) -> bool:
    """Check if href has a fragment identifier."""
    return "#" in href


def _validate_href_format(path: Path, href: str) -> list[ResultMessage]:
    """Validate href format."""
    errors: list[ResultMessage] = []

    # Check for spaces in href
    if " " in href:
        errors.append(
            build_message(
                "RSC-007",
                path=str(path),
                message=f"referenced resource not found: '{href}'",
            )
        )

    return errors


def _validate_resource_references(path: Path, opf) -> list[ResultMessage]:
    """Validate resource references in OPF manifest."""
    errors: list[ResultMessage] = []

    for item in opf.manifest:
        href = item.href

        # Skip remote URLs and data URLs
        if _is_remote_url(href) or _is_data_url(href):
            continue

        # Check for fragment-only references
        if href.startswith("#"):
            continue

        # Check for empty href
        if not href:
            errors.append(
                build_message(
                    "RSC-007",
                    path=str(path),
                    message="manifest item has empty href",
                )
            )
            continue

        # Check for invalid characters in href
        if "<" in href or ">" in href or '"' in href:
            errors.append(
                build_message(
                    "RSC-007",
                    path=str(path),
                    message=f"invalid characters in href: '{href}'",
                )
            )

    return errors


def _validate_meta_inf_resources(path: Path, opf) -> list[ResultMessage]:
    """Validate META-INF resource restrictions."""
    errors: list[ResultMessage] = []

    # Check if any manifest items reference META-INF
    for item in opf.manifest:
        if item.href.startswith("META-INF/"):
            errors.append(
                build_message(
                    "PKG-025",
                    path=str(path),
                    message=f"publication resource in META-INF: '{item.href}'",
                )
            )

    return errors


def run(path: str | Path) -> list[ResultMessage]:
    """Run resource reference checks."""
    candidate = Path(path)
    errors: list[ResultMessage] = []

    # Only check OPF files
    if candidate.suffix.lower() != ".opf":
        return []

    # Load and parse XML
    xml_doc = load_xml(candidate)
    if xml_doc.errors:
        return xml_doc.errors

    # Check if this is an OPF document
    if xml_doc.doc_type != "opf":
        return []

    # Parse OPF
    opf = parse_opf(candidate)
    if opf.errors:
        return opf.errors

    # Validate resource references
    errors.extend(_validate_resource_references(candidate, opf))

    # Validate META-INF resources
    errors.extend(_validate_meta_inf_resources(candidate, opf))

    return errors
