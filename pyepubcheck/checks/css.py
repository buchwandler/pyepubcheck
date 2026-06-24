"""CSS checks."""

from __future__ import annotations

import re
from pathlib import Path

import tinycss2

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage


# Disallowed CSS properties in EPUB
DISALLOWED_PROPERTIES = {
    "position",
    "float",
}

# URL pattern in CSS
URL_RE = re.compile(r'url\(["\']?([^"\')\s]+)["\']?\)')


def _validate_css_properties(path: Path, content: str) -> list[ResultMessage]:
    """Validate CSS properties."""
    errors: list[ResultMessage] = []

    try:
        rules = tinycss2.parse_stylesheet(content, skip_comments=True, skip_whitespace=True)
    except Exception:
        errors.append(
            build_message(
                "CSS-008",
                path=str(path),
                message="CSS syntax error",
            )
        )
        return errors

    for rule in rules:
        if rule.type == "qualified-rule":
            for declaration in tinycss2.parse_declaration_list(rule.content):
                if declaration.type == "declaration":
                    prop_name = declaration.name.lower()
                    if prop_name in DISALLOWED_PROPERTIES:
                        errors.append(
                            build_message(
                                "CSS-001",
                                path=str(path),
                                message=f"disallowed CSS property: '{prop_name}'",
                            )
                        )

    return errors


def _validate_css_urls(path: Path, content: str) -> list[ResultMessage]:
    """Validate CSS URL references."""
    errors: list[ResultMessage] = []

    # Find all URLs in CSS
    for match in URL_RE.finditer(content):
        url = match.group(1)

        # Skip data URLs and remote URLs
        if url.startswith("data:") or url.startswith("http://") or url.startswith("https://"):
            continue

        # Skip fragment-only URLs
        if url.startswith("#"):
            continue

        # Resolve URL relative to CSS file
        css_dir = path.parent
        resolved_url = (css_dir / url).resolve()

        # Check if URL exists
        if not resolved_url.exists():
            errors.append(
                build_message(
                    "RSC-007",
                    path=str(path),
                    message=f"referenced resource not found: '{url}'",
                )
            )

    return errors


def run(path: str | Path) -> list[ResultMessage]:
    """Run CSS content document checks."""
    candidate = Path(path)
    errors: list[ResultMessage] = []

    # Only check CSS files
    if candidate.suffix.lower() != ".css":
        return []

    if not candidate.exists():
        return []

    try:
        content = candidate.read_text(encoding="utf-8")
    except Exception:
        return []

    # Validate CSS properties
    errors.extend(_validate_css_properties(candidate, content))

    # Validate CSS URLs
    errors.extend(_validate_css_urls(candidate, content))

    return errors


def _validate_css_direction(path: Path, content: str) -> list[ResultMessage]:
    """Validate CSS direction property usage."""
    errors: list[ResultMessage] = []

    # Check for direction property
    direction_re = re.compile(r'direction\s*:\s*([^;]+)')
    for match in direction_re.finditer(content):
        value = match.group(1).strip().lower()
        if value not in ('ltr', 'rtl'):
            errors.append(
                build_message(
                    "CSS-001",
                    path=str(path),
                    message=f"invalid CSS direction value: '{value}'",
                )
            )

    return errors


def _validate_css_selectors(path: Path, content: str) -> list[ResultMessage]:
    """Validate CSS selectors."""
    errors: list[ResultMessage] = []

    try:
        rules = tinycss2.parse_stylesheet(content, skip_comments=True, skip_whitespace=True)
    except Exception:
        return errors

    for rule in rules:
        if rule.type == "qualified-rule":
            # Check for invalid selector patterns
            prelude = tinycss2.serialize(rule.prelude)
            if "::" in prelude and "::before" not in prelude and "::after" not in prelude:
                # Check for invalid pseudo-elements
                pass

    return errors
