"""CSS checks."""

from __future__ import annotations

import re
from pathlib import Path

import tinycss2

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage
from pyepubcheck.severity import Severity

# Disallowed CSS properties in EPUB
DISALLOWED_PROPERTIES = {
    "position",
    "float",
    "direction",
    "unicode-bidi",
}

# URL pattern in CSS
URL_RE = re.compile(r'url\(["\']?([^"\')\s]+)["\']?\)')


def _validate_css_properties(path: Path, content: str) -> list[ResultMessage]:
    """Validate CSS properties."""
    errors: list[ResultMessage] = []

    # Check for unmatched braces (syntax errors)
    open_braces = 0
    for char in content:
        if char == "{":
            open_braces += 1
        elif char == "}":
            open_braces -= 1
        if open_braces < 0:
            errors.append(
                build_message(
                    "CSS-008",
                    path=str(path),
                    message="CSS syntax error: unexpected closing brace",
                )
            )
            open_braces = 0

    if open_braces > 0:
        for _ in range(open_braces):
            errors.append(
                build_message(
                    "CSS-008",
                    path=str(path),
                    message="CSS syntax error: missing closing brace",
                )
            )

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

        # Reject file:// URLs
        if url.startswith("file:"):
            errors.append(
                build_message(
                    "RSC-006",
                    path=str(path),
                    message=f"file URL not allowed: '{url}'",
                )
            )
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


def run(path: str | Path, *, manifest_hrefs: set[str] | None = None) -> list[ResultMessage]:
    """Run CSS content document checks."""
    candidate = Path(path)
    errors: list[ResultMessage] = []

    # Only check CSS files
    if candidate.suffix.lower() != ".css":
        return []

    if not candidate.exists():
        return []

    # Read raw bytes for encoding detection
    try:
        raw_bytes = candidate.read_bytes()
    except Exception:
        return []

    # Detect encoding from BOM or @charset
    encoding = "utf-8"

    # Check for BOM
    if raw_bytes[:3] == b"\xef\xbb\xbf":
        encoding = "utf-8"
    elif raw_bytes[:2] == b"\xff\xfe":
        encoding = "utf-16-le"
    elif raw_bytes[:2] == b"\xfe\xff":
        encoding = "utf-16-be"

    # Try to read with detected encoding
    try:
        content = raw_bytes.decode(encoding)
    except Exception:
        try:
            content = raw_bytes.decode("utf-8")
        except Exception:
            return []

    # Check for @charset declaration in content
    charset_re = re.compile(r"@charset\s+['\"]([^'\"]+)['\"]\s*;", re.IGNORECASE)
    charset_match = charset_re.search(content)
    if charset_match:
        declared_encoding = charset_match.group(1).strip().lower()
        # Report warning for UTF-16 encoding
        if "utf-16" in declared_encoding:
            errors.append(
                build_message(
                    "CSS-003",
                    path=str(candidate),
                    message="CSS encoded in UTF-16",
                    severity=Severity.WARNING,
                )
            )
        # Report error for non-UTF-8/UTF-16 encoding
        elif declared_encoding not in ("utf-8", "utf-16"):
            errors.append(
                build_message(
                    "CSS-004",
                    path=str(candidate),
                    message=f"CSS @charset encoding '{declared_encoding}' is not allowed",
                )
            )
    elif "utf-16" in encoding:
        # No @charset but UTF-16 BOM detected
        errors.append(
            build_message(
                "CSS-003",
                path=str(candidate),
                message="CSS encoded in UTF-16",
                severity=Severity.WARNING,
            )
        )

    css_dir = candidate.parent

    # Validate CSS properties
    errors.extend(_validate_css_properties(candidate, content))

    # Validate CSS URLs
    errors.extend(_validate_css_urls(candidate, content))

    # Validate CSS @import
    errors.extend(_validate_css_import(candidate, content, css_dir, manifest_hrefs))

    # Validate CSS @font-face
    errors.extend(_validate_css_font_face(candidate, content))

    return errors


def _validate_css_encoding(path: Path, content: str) -> list[ResultMessage]:
    """Validate CSS @charset encoding."""
    errors: list[ResultMessage] = []

    # Check for @charset declaration
    charset_re = re.compile(r"@charset\s+['\"]([^'\"]+)['\"]\s*;")
    match = charset_re.search(content)
    if match:
        encoding = match.group(1).strip().lower()
        if encoding not in ("utf-8", "utf-16"):
            errors.append(
                build_message(
                    "CSS-004",
                    path=str(path),
                    message=f"CSS @charset encoding '{encoding}' is not allowed",
                )
            )

    # Check for UTF-16 encoding warning
    if "utf-16" in content.lower():
        errors.append(
            build_message(
                "CSS-003",
                path=str(path),
                message="CSS encoded in UTF-16",
            )
        )

    return errors


def _validate_css_import(
    path: Path, content: str, css_dir: Path, manifest_hrefs: set[str] | None = None
) -> list[ResultMessage]:
    """Validate CSS @import statements."""
    errors: list[ResultMessage] = []

    import_re = re.compile(r"@import\s+(?:url\()?['\"]?([^'\"\);]+)['\"]?\)?")
    for match in import_re.finditer(content):
        url = match.group(1).strip()

        # Skip remote URLs
        if url.startswith(("http://", "https://", "data:")):
            continue

        # Resolve URL relative to CSS file
        resolved_url = (css_dir / url).resolve()

        # Check if URL exists
        if not resolved_url.exists():
            errors.append(
                build_message(
                    "RSC-001",
                    path=str(path),
                    message=f"@import resource not found: '{url}'",
                )
            )
        elif manifest_hrefs is not None and url not in manifest_hrefs:
            errors.append(
                build_message(
                    "RSC-008",
                    path=str(path),
                    message=f"@import resource '{url}' not declared in manifest",
                )
            )

    return errors


def _validate_css_font_face(path: Path, content: str) -> list[ResultMessage]:
    """Validate CSS @font-face declarations."""
    errors: list[ResultMessage] = []

    # Check for empty @font-face declarations
    font_face_re = re.compile(r"@font-face\s*\{\s*\}")
    if font_face_re.search(content):
        errors.append(
            build_message(
                "CSS-008",
                path=str(path),
                message="Empty @font-face declaration",
            )
        )

    # Check for @font-face with empty URL
    font_face_url_re = re.compile(r"@font-face\s*\{[^}]*url\(\s*['\"]?\s*['\"]?\s*\)[^}]*\}")
    if font_face_url_re.search(content):
        errors.append(
            build_message(
                "CSS-008",
                path=str(path),
                message="@font-face with empty URL reference",
            )
        )

    return errors


def _validate_css_direction(path: Path, content: str) -> list[ResultMessage]:
    """Validate CSS direction property usage."""
    errors: list[ResultMessage] = []

    # Check for direction property - always report as error in EPUB
    direction_re = re.compile(r"direction\s*:\s*([^;]+)")
    for match in direction_re.finditer(content):
        match.group(1).strip().lower()
        errors.append(
            build_message(
                "CSS-001",
                path=str(path),
                message="CSS 'direction' property is not allowed in EPUB",
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
