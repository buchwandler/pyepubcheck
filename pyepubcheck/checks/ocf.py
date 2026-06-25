"""OCF-level checks."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from pyepubcheck.io.archive import ZipSource
from pyepubcheck.io.expanded import DirectorySource
from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage

EXPECTED_MIMETYPE = "application/epub+zip"

# Characters forbidden in OCF file names (excluding / which is path separator)
FORBIDDEN_CHARS = set('"*+;<=>?\\|')
FORBIDDEN_CONTROL_CHARS = {chr(i) for i in range(0x00, 0x20)} | {chr(0x7F)}

# Filename validation regex
FILENAME_RE = re.compile(r'^[^"<>*+/;:=?\\|\x00-\x1f\x7f]+$')


def _validate_mimetype_content(content: str) -> list[ResultMessage]:
    """Validate mimetype file content."""
    # Check for leading whitespace (explicitly forbidden)
    if content.startswith(" ") or content.startswith("\t"):
        return [build_message("PKG-007", message="mimetype file has leading whitespace")]

    # Strip trailing whitespace for value check
    # Trailing newlines are common in valid EPUBs and tolerated
    stripped = content.rstrip("\r\n")

    # Check content value
    if stripped != EXPECTED_MIMETYPE:
        return [build_message("PKG-007", message="mimetype file has incorrect value")]

    return []


def _validate_filename(filename: str) -> list[ResultMessage]:
    """Validate a single filename against OCF rules."""
    errors: list[ResultMessage] = []

    # Check for forbidden characters
    for char in filename:
        if char in FORBIDDEN_CHARS:
            errors.append(
                build_message("PKG-009", message=f"forbidden character '{char}' in filename '{filename}'")
            )
            break
        if char in FORBIDDEN_CONTROL_CHARS:
            errors.append(
                build_message("PKG-009", message=f"forbidden control character in filename '{filename}'")
            )
            break

    return errors


def _check_duplicate_filenames(filenames: list[str]) -> list[ResultMessage]:
    """Check for duplicate filenames after case folding."""
    errors: list[ResultMessage] = []
    seen: set[str] = set()

    for name in filenames:
        folded = name.lower()
        if folded in seen:
            errors.append(
                build_message(
                    "OPF-060",
                    message=f"duplicate filename after case folding: '{name}'",
                )
            )
        else:
            seen.add(folded)

    return errors


def _check_meta_inf_resources(filenames: list[str]) -> list[ResultMessage]:
    """Check for publication resources in META-INF."""
    errors: list[ResultMessage] = []

    # Files allowed in META-INF
    allowed_meta_inf = {
        "META-INF/container.xml",
        "META-INF/encryption.xml",
        "META-INF/manifest.xml",
        "META-INF/metadata.xml",
        "META-INF/rights.xml",
        "META-INF/signatures.xml",
        "META-INF/",
    }

    for name in filenames:
        if name.startswith("META-INF/") and name not in allowed_meta_inf:
            # Check if it's a directory
            if not name.endswith("/"):
                errors.append(
                    build_message("PKG-025", message=f"publication resource found in META-INF: '{name}'")
                )

    return errors


def _validate_directory(path: Path) -> list[ResultMessage]:
    """Validate an expanded EPUB directory."""
    errors: list[ResultMessage] = []
    source = DirectorySource.from_path(path)

    # Check mimetype file existence
    if not source.has("mimetype"):
        errors.append(build_message("PKG-006", path=str(path / "mimetype")))
        return errors

    # Check mimetype content
    mimetype_content = source.read_text("mimetype")
    mimetype_errors = _validate_mimetype_content(mimetype_content)
    errors.extend(mimetype_errors)

    # Check for container.xml
    container_path = path / "META-INF" / "container.xml"
    if not container_path.exists():
        errors.append(build_message("FATAL-001", path=str(container_path), message="container.xml not found"))
        return errors

    # Validate container.xml
    container_errors = _validate_container_xml(path)
    errors.extend(container_errors)

    # Collect all files in the directory
    filenames = []
    for file_path in path.rglob("*"):
        if file_path.is_file():
            relative = file_path.relative_to(path).as_posix()
            filenames.append(relative)

    # Check filenames
    for filename in filenames:
        filename_errors = _validate_filename(filename)
        errors.extend(filename_errors)

    # Check for duplicate filenames
    duplicate_errors = _check_duplicate_filenames(filenames)
    errors.extend(duplicate_errors)


    # Check META-INF resources for EPUB 3
    # Determine EPUB version from OPF
    is_epub3 = False
    container_path = path / "META-INF" / "container.xml"
    if container_path.exists():
        try:
            from pyepubcheck.xml_parser import load_xml
            doc = load_xml(container_path)
            if not doc.errors:
                rootfile = doc.find(".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile")
                if rootfile is not None:
                    full_path = rootfile.get("full-path", "")
                    if full_path:
                        opf_path = path / full_path
                        if opf_path.exists():
                            opf_doc = load_xml(opf_path)
                            if not opf_doc.errors and opf_doc.root is not None:
                                version = opf_doc.root.get("version", "")
                                if version.startswith("3"):
                                    is_epub3 = True
        except Exception:
            pass
    if is_epub3:
        meta_inf_errors = _check_meta_inf_resources(filenames)
        errors.extend(meta_inf_errors)

    # Note: Unknown files in META-INF are ignored (not reported as errors)

    return errors


def _validate_archive(path: Path) -> list[ResultMessage]:
    """Validate a packaged EPUB archive."""
    errors: list[ResultMessage] = []
    source = ZipSource.from_path(path)
    entries = source.entries()

    # Check mimetype entry exists and is first
    if not entries:
        errors.append(build_message("PKG-006", path=str(path)))
        return errors

    mimetype_found = False
    for entry in entries:
        if entry.name == "mimetype":
            mimetype_found = True
            break

    if not mimetype_found:
        errors.append(build_message("PKG-006", path=str(path)))
        return errors

    # Check mimetype is first entry
    if entries[0].name != "mimetype":
        errors.append(build_message("PKG-005", path=str(path)))

    # Check mimetype content
    try:
        mimetype_content = source.read_text("mimetype")
        mimetype_errors = _validate_mimetype_content(mimetype_content)
        errors.extend(mimetype_errors)
    except Exception:
        errors.append(build_message("PKG-007", path=str(path)))

    # Check filenames
    filenames = [e.name for e in entries]
    for filename in filenames:
        filename_errors = _validate_filename(filename)
        errors.extend(filename_errors)

    # Check for duplicate filenames
    duplicate_errors = _check_duplicate_filenames(filenames)
    errors.extend(duplicate_errors)

    # Check META-INF resources
    meta_inf_errors = _check_meta_inf_resources(filenames)
    errors.extend(meta_inf_errors)

    return errors


def run(path: str | Path) -> list[ResultMessage]:
    """Run OCF-level checks on a path."""
    candidate = Path(path)
    if candidate.is_dir():
        return _validate_directory(candidate)
    if candidate.suffix.lower() == ".epub":
        return _validate_archive(candidate)
    return []


def _validate_container_xml(path: Path) -> list[ResultMessage]:
    """Validate container.xml file."""
    errors: list[ResultMessage] = []
    container_path = path / "META-INF" / "container.xml"

    if not container_path.exists():
        return errors

    try:
        from pyepubcheck.xml_parser import load_xml
        doc = load_xml(container_path)
        if doc.errors:
            return doc.errors

        root = doc.root
        if root is None:
            return errors

        # Check namespace
        ns = "urn:oasis:names:tc:opendocument:xmlns:container"
        if not root.tag.startswith(f"{{{ns}}}"):
            errors.append(build_message("RSC-005", path=str(container_path), message="invalid container namespace"))
            return errors

        # Find rootfiles element
        rootfiles = root.find(f"{{{ns}}}rootfiles")
        if rootfiles is None:
            errors.append(build_message("RSC-005", path=str(container_path), message="missing rootfiles element"))
            return errors

        # Check each rootfile
        rootfile_count = 0
        for rootfile in rootfiles.findall(f"{{{ns}}}rootfile"):
            rootfile_count += 1
            full_path = rootfile.get("full-path", "")
            media_type = rootfile.get("media-type", "")

            # Validate full-path
            if not full_path:
                errors.append(build_message("PKG-001", path=str(container_path), message="rootfile full-path is empty or missing"))
            else:
                # Check if the OPF file exists (only for primary rootfile)
                if rootfile_count == 1:
                    opf_path = path / full_path
                    if not opf_path.exists():
                        errors.append(build_message("FATAL-001", path=str(container_path), message=f"rootfile '{full_path}' not found"))

            # Validate media-type (only for primary rootfile)
            if rootfile_count == 1 and media_type and media_type != "application/oebps-package+xml":
                errors.append(build_message("PKG-007", path=str(container_path), message=f"invalid rootfile media-type '{media_type}'"))

        # Check for multiple rootfiles with same media-type (error)
        if rootfile_count > 1:
            # Multiple rootfiles with same media-type is an error
            media_types = []
            for rootfile in rootfiles.findall(f"{{{ns}}}rootfile"):
                mt = rootfile.get("media-type", "")
                if mt:
                    media_types.append(mt)
            if len(media_types) > 1 and len(set(media_types)) == 1:
                errors.append(build_message("PKG-001", path=str(container_path), message="multiple rootfiles with same media-type"))

    except Exception as e:
        errors.append(build_message("RSC-002", path=str(container_path), message=f"error parsing container.xml: {e}"))

    return errors
