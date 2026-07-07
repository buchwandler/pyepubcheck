"""OCF-level checks."""

from __future__ import annotations

import re
from pathlib import Path

from pyepubcheck.io.archive import ZipSource
from pyepubcheck.io.expanded import DirectorySource
from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage

EXPECTED_MIMETYPE = "application/epub+zip"

# Characters forbidden in OCF file names (excluding / which is path separator)
FORBIDDEN_CHARS = set('"*+;<=>?\\|')
FORBIDDEN_CONTROL_CHARS = {chr(i) for i in range(0x00, 0x20)} | {chr(0x7F)}

# Characters that produce warnings (whitespace)
WARNING_CHARS = {
    chr(0x0009): "TAB",
    chr(0x000A): "LF",
    chr(0x000C): "FF",
    chr(0x000D): "CR",
    chr(0x0020): "SPACE",
    chr(0x2009): "THIN SPACE",
}

# Extended forbidden characters (including Unicode ranges)
EXTENDED_FORBIDDEN = {
    chr(0x007F): "CONTROL",
    chr(0x0000): "CONTROL",
    chr(0x0080): "CONTROL",  # Actually control range but simplified
    chr(0xE000): "PRIVATE USE",
    chr(0xFDD0): "NON CHARACTER",
    chr(0xFFFD): "REPLACEMENT CHARACTER (SPECIALS)",
    chr(0xFFFE): "NON CHARACTER",
}

# Tag characters allowed for Emoji Tag Sequences
TAG_CHARS = {chr(i) for i in range(0xE0020, 0xE0080)}

# Filename validation regex
FILENAME_RE = re.compile(r'^[^"<>\x2a\x2b\x3a\x3b\x3d\x3f\x5c\x7c\x00-\x1f\x7f]+$')


def _validate_mimetype_content(content: str) -> list[ResultMessage]:
    """Validate mimetype file content."""
    # Check for leading whitespace (explicitly forbidden)
    if content.startswith(" ") or content.startswith("\t"):
        return [
            build_message("PKG-007", message="mimetype file has leading whitespace")
        ]

    # Check for any whitespace inside the content (forbidden, except a single
    # trailing newline which is the common carriage-returned variant).
    if " " in content.strip("\r\n") or "\t" in content.strip("\r\n"):
        return [
            build_message("PKG-007", message="mimetype file has internal whitespace")
        ]

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

    # Check for full stop as last character
    if filename.endswith("."):
        errors.append(
            build_message(
                "PKG-011",
                message=f"filename '{filename}' ends with a full stop",
            )
        )

    # Collect forbidden characters for reporting
    found_forbidden: list[str] = []
    found_control: list[str] = []

    for char in filename:
        # Check for whitespace warnings
        if char in WARNING_CHARS:
            errors.append(
                build_message(
                    "PKG-010",
                    message=f"filename '{filename}' contains whitespace character",
                )
            )
            break

        # Check for forbidden characters
        if char in FORBIDDEN_CHARS:
            found_forbidden.append(f"U+{ord(char):04X} ({char})")
        elif char in FORBIDDEN_CONTROL_CHARS:
            found_control.append(f"U+{ord(char):04X} (CONTROL)")
        elif char in EXTENDED_FORBIDDEN:
            desc = EXTENDED_FORBIDDEN[char]
            found_forbidden.append(f"U+{ord(char):04X} ({desc})")
        elif char in TAG_CHARS:
            # Tag characters allowed for Emoji Tag Sequences
            pass
        elif ord(char) >= 0xE0001 and ord(char) <= 0xE001F:
            # Language tag characters (deprecated)
            found_forbidden.append(f"U+{ord(char):04X} LANGUAGE TAG (DEPRECATED)")
        elif (ord(char) >= 0xF0000 and ord(char) <= 0xFFFFD) or (
            ord(char) >= 0x100000 and ord(char) <= 0x10FFFD
        ):
            found_forbidden.append(f"U+{ord(char):04X} (PRIVATE USE)")
        elif (
            (ord(char) >= 0x1FFFE and ord(char) <= 0x1FFFF)
            or (ord(char) >= 0x2FFFE and ord(char) <= 0x2FFFF)
            or (ord(char) >= 0x3FFFE and ord(char) <= 0x3FFFF)
            or (ord(char) >= 0x4FFFE and ord(char) <= 0x4FFFF)
            or (ord(char) >= 0x5FFFE and ord(char) <= 0x5FFFF)
            or (ord(char) >= 0x6FFFE and ord(char) <= 0x6FFFF)
            or (ord(char) >= 0x7FFFE and ord(char) <= 0x7FFFF)
            or (ord(char) >= 0x8FFFE and ord(char) <= 0x8FFFF)
            or (ord(char) >= 0x9FFFE and ord(char) <= 0x9FFFF)
            or (ord(char) >= 0xAFFFE and ord(char) <= 0xAFFFF)
            or (ord(char) >= 0xBFFFE and ord(char) <= 0xBFFFF)
            or (ord(char) >= 0xCFFFE and ord(char) <= 0xCFFFF)
            or (ord(char) >= 0xDFFFE and ord(char) <= 0xDFFFF)
            or (ord(char) >= 0xEFFFE and ord(char) <= 0xEFFFF)
            or (ord(char) >= 0xFFFFE and ord(char) <= 0xFFFFF)
            or (ord(char) >= 0x10FFFE and ord(char) <= 0x10FFFF)
        ):
            found_forbidden.append(f"U+{ord(char):04X} (NON CHARACTER)")

    # Report forbidden characters
    if found_forbidden:
        chars_str = ", ".join(found_forbidden)
        errors.append(
            build_message(
                "PKG-009",
                message=f"forbidden characters in filename '{filename}': {chars_str}",
            )
        )

    # Report control characters
    if found_control:
        chars_str = ", ".join(found_control)
        errors.append(
            build_message(
                "PKG-009",
                message=f"forbidden control characters in filename '{filename}': {chars_str}",
            )
        )

    return errors


def check_filename(filename: str) -> list[ResultMessage]:
    """Public API to validate a single filename against OCF rules."""
    return _validate_filename(filename)


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
                    build_message(
                        "PKG-025",
                        message=f"publication resource found in META-INF: '{name}'",
                    )
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
        errors.append(
            build_message(
                "FATAL-001", path=str(container_path), message="container.xml not found"
            )
        )
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
                rootfile = doc.find(
                    ".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile"
                )
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


def _is_valid_media_query(query: str) -> bool:
    """Basic media query syntax validation."""
    # Simple validation: check for balanced parentheses and basic structure
    if not query.strip():
        return False

    # Check for balanced parentheses
    depth = 0
    for char in query:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if depth < 0:
            return False

    if depth != 0:
        return False

    # Check for basic media query structure
    # Valid examples: (min-width: 1920px), (orientation: landscape), etc.
    # Invalid examples: syntaxerror, (invalid), etc.
    query = query.strip()
    if query.startswith("(") and query.endswith(")"):
        # Check for colon inside parentheses
        inner = query[1:-1].strip()
        if ":" not in inner:
            return False
        # Check for valid media feature
        parts = inner.split(":", 1)
        if len(parts) != 2:
            return False
        feature = parts[0].strip()
        value = parts[1].strip()
        if not feature or not value:
            return False
        return True

    return False


def _validate_mapping_document(path: Path) -> list[ResultMessage]:
    """Validate a rendition mapping document."""
    errors: list[ResultMessage] = []

    try:
        from pyepubcheck.xml_parser import load_xml

        doc = load_xml(path)
        if doc.errors:
            return doc.errors

        root = doc.root
        if root is None:
            return errors

        # Check for epub.multiple.renditions.version meta tag
        xhtml_ns = "http://www.w3.org/1999/xhtml"
        epub_ns = "http://www.idpf.org/2007/ops"

        head = root.find(f"{{{xhtml_ns}}}head")
        if head is None:
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message='A meta tag with the name "epub.multiple.renditions.version" and value "1.0" is required',
                )
            )
            return errors

        # Check for version meta tag
        version_found = False
        for meta in head.findall(f"{{{xhtml_ns}}}meta"):
            name = meta.get("name", "")
            content = meta.get("content", "")
            if name == "epub.multiple.renditions.version" and content == "1.0":
                version_found = True
                break

        if not version_found:
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message='A meta tag with the name "epub.multiple.renditions.version" and value "1.0" is required',
                )
            )

        # Check for resource-map nav element
        body = root.find(f"{{{xhtml_ns}}}body")
        if body is None:
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message='A Rendition Mapping Document must contain exactly one "resource-map" nav element',
                )
            )
            return errors

        resource_map_count = 0
        for nav in body.findall(f".//{{{xhtml_ns}}}nav"):
            epub_type = nav.get(f"{{{epub_ns}}}type", "")
            if "resource-map" in epub_type:
                resource_map_count += 1
            elif epub_type:
                # Check for untyped nav elements
                pass
            else:
                # Nav element without epub:type
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(path),
                        message="nav element must have an epub:type attribute",
                    )
                )

        if resource_map_count == 0:
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message='A Rendition Mapping Document must contain exactly one "resource-map" nav element',
                )
            )
        elif resource_map_count > 1:
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(path),
                    message='A Rendition Mapping Document must contain exactly one "resource-map" nav element',
                )
            )

    except Exception as e:
        errors.append(
            build_message(
                "RSC-002",
                path=str(path),
                message=f"error parsing mapping document: {e}",
            )
        )

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
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(container_path),
                    message="invalid container namespace",
                )
            )
            return errors

        # Find rootfiles element
        rootfiles = root.find(f"{{{ns}}}rootfiles")
        if rootfiles is None:
            errors.append(
                build_message(
                    "RSC-005",
                    path=str(container_path),
                    message="missing rootfiles element",
                )
            )
            return errors

        # Check each rootfile
        rootfile_count = 0
        for rootfile in rootfiles.findall(f"{{{ns}}}rootfile"):
            rootfile_count += 1
            full_path = rootfile.get("full-path", "")
            media_type = rootfile.get("media-type", "")

            # Validate full-path
            if not full_path:
                errors.append(
                    build_message(
                        "PKG-001",
                        path=str(container_path),
                        message="rootfile full-path is empty or missing",
                    )
                )
            else:
                # Check if the OPF file exists (only for primary rootfile)
                if rootfile_count == 1:
                    opf_path = path / full_path
                    if not opf_path.exists():
                        errors.append(
                            build_message(
                                "FATAL-001",
                                path=str(container_path),
                                message=f"rootfile '{full_path}' not found",
                            )
                        )

            # Validate media-type (only for primary rootfile)
            if (
                rootfile_count == 1
                and media_type
                and media_type != "application/oebps-package+xml"
            ):
                errors.append(
                    build_message(
                        "PKG-007",
                        path=str(container_path),
                        message=f"invalid rootfile media-type '{media_type}'",
                    )
                )

        # Check for multiple rootfiles
        if rootfile_count > 1:
            # Count OPF rootfiles (application/oebps-package+xml)
            opf_rootfiles = []
            rootfile_elements = rootfiles.findall(f"{{{ns}}}rootfile")
            for rootfile in rootfile_elements:
                media_type = rootfile.get("media-type", "")
                if media_type == "application/oebps-package+xml":
                    opf_rootfiles.append(rootfile)

            # Multiple OPF files are allowed for multiple renditions (EPUB 3)
            # if a rendition mapping document is declared. Otherwise the
            # container must declare a single OPF.
            links_element = root.find(f"{{{ns}}}links")
            has_mapping = links_element is not None and any(
                link.get("rel", "") == "mapping"
                for link in links_element.findall(f"{{{ns}}}link")
            )
            if len(opf_rootfiles) > 1 and not has_mapping:
                primary_version = ""
                if opf_rootfiles:
                    primary_path_attr = opf_rootfiles[0].get("full-path", "")
                    if primary_path_attr:
                        primary_opf = path / primary_path_attr
                        if primary_opf.exists():
                            from pyepubcheck.xml_parser import load_xml as _load

                            primary_doc = _load(primary_opf)
                            if not primary_doc.errors and primary_doc.root is not None:
                                primary_version = primary_doc.root.get("version", "")
                if not primary_version.startswith("3"):
                    errors.append(
                        build_message(
                            "PKG-001",
                            path=str(container_path),
                            message="Multiple rootfile entries are not allowed without a rendition mapping document.",
                        )
                    )

            # Validate rendition selection attributes for non-primary rootfiles
            # Only for OPF rootfiles (not for alternative files like text/plain)
            rendition_ns = "http://www.idpf.org/2013/rendition"
            for i, rootfile in enumerate(rootfile_elements):
                if i > 0:  # Skip primary rootfile
                    media_type = rootfile.get("media-type", "")
                    # Only check rendition attributes for OPF files
                    if media_type == "application/oebps-package+xml":
                        # Check for rendition selection attributes
                        has_rendition_attr = False
                        for attr_name, attr_value in rootfile.attrib.items():
                            if attr_name.startswith(f"{{{rendition_ns}}}"):
                                has_rendition_attr = True
                                # Validate rendition:media attribute
                                if "media" in attr_name:
                                    # Basic media query syntax validation
                                    if not attr_value.strip():
                                        errors.append(
                                            build_message(
                                                "RSC-005",
                                                path=str(container_path),
                                                message=f"empty rendition:media attribute on rootfile '{rootfile.get('full-path', '')}'",
                                            )
                                        )
                                    elif not _is_valid_media_query(attr_value):
                                        errors.append(
                                            build_message(
                                                "RSC-005",
                                                path=str(container_path),
                                                message='value of attribute "rendition:media" is invalid',
                                            )
                                        )
                                # Check for unknown rendition selection attributes
                                known_attrs = {
                                    f"{{{rendition_ns}}}media",
                                    f"{{{rendition_ns}}}label",
                                }
                                if attr_name not in known_attrs:
                                    errors.append(
                                        build_message(
                                            "RSC-005",
                                            path=str(container_path),
                                            message=f'attribute "{attr_name}" not allowed here',
                                        )
                                    )

                        if not has_rendition_attr:
                            errors.append(
                                build_message(
                                    "RSC-017",
                                    path=str(container_path),
                                    message="At least one rendition selection attribute should be specified",
                                )
                            )

        # Check for links element (mapping documents)
        links = root.find(f"{{{ns}}}links")
        if links is not None:
            mapping_docs = []
            for link in links.findall(f"{{{ns}}}link"):
                rel = link.get("rel", "")
                href = link.get("href", "")
                media_type = link.get("media-type", "")

                if rel == "mapping":
                    # Validate mapping document media type
                    if media_type != "application/xhtml+xml":
                        errors.append(
                            build_message(
                                "RSC-005",
                                path=str(container_path),
                                message='The media type of Rendition Mapping Documents must be "application/xhtml+xml"',
                            )
                        )
                    else:
                        mapping_docs.append(href)

            # Check for multiple mapping documents
            if len(mapping_docs) > 1:
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(container_path),
                        message="The Container Document must not reference more than one mapping document.",
                    )
                )

            # Validate single mapping document
            if len(mapping_docs) == 1:
                mapping_path = path / mapping_docs[0]
                if mapping_path.exists():
                    errors.extend(_validate_mapping_document(mapping_path))

    except Exception as e:
        errors.append(
            build_message(
                "RSC-002",
                path=str(container_path),
                message=f"error parsing container.xml: {e}",
            )
        )

    return errors
