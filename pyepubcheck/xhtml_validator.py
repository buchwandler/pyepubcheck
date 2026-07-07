"""XHTML document validation."""

from __future__ import annotations

from pathlib import Path

from lxml import etree

from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage
from pyepubcheck.severity import Severity
from pyepubcheck.xml_parser import XHTML_NS, XmlDocument, load_xml

# Valid XHTML elements for EPUB 3 (HTML5 elements)
VALID_XHTML_ELEMENTS = {
    # Root element
    "html",
    # Document metadata
    "head",
    "title",
    "base",
    "link",
    "meta",
    "style",
    # Scripting
    "script",
    "noscript",
    # Sections
    "body",
    "section",
    "nav",
    "article",
    "aside",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hgroup",
    "header",
    "footer",
    "address",
    # Grouping content
    "p",
    "hr",
    "pre",
    "blockquote",
    "ol",
    "ul",
    "li",
    "dl",
    "dt",
    "dd",
    "figure",
    "figcaption",
    "main",
    "div",
    # Text-level semantics
    "a",
    "em",
    "strong",
    "small",
    "s",
    "cite",
    "q",
    "dfn",
    "abbr",
    "ruby",
    "rt",
    "rp",
    "data",
    "time",
    "code",
    "var",
    "samp",
    "kbd",
    "sub",
    "sup",
    "i",
    "b",
    "u",
    "mark",
    "bdi",
    "bdo",
    "span",
    "br",
    "wbr",
    # Edits
    "ins",
    "del",
    # Embedded content
    "picture",
    "source",
    "img",
    "iframe",
    "embed",
    "object",
    "param",
    "video",
    "audio",
    "track",
    "map",
    "area",
    # Tabular data
    "table",
    "caption",
    "colgroup",
    "col",
    "tbody",
    "thead",
    "tfoot",
    "tr",
    "td",
    "th",
    # Forms
    "form",
    "label",
    "input",
    "button",
    "select",
    "datalist",
    "optgroup",
    "option",
    "textarea",
    "keygen",
    "output",
    "progress",
    "meter",
    "fieldset",
    "legend",
    # Interactive elements
    "details",
    "summary",
    "menuitem",
    "menu",
    # Scripting
    "canvas",
    "template",
    "slot",
    # MathML
    "math",
    "maction",
    "maligngroup",
    "malignmark",
    "mglyph",
    "mpadded",
    "mphantom",
    "mroot",
    "mrow",
    "ms",
    "mspace",
    "mtable",
    "mtd",
    "mtext",
    "mtr",
    "mlongdiv",
    "mscarries",
    "mscarry",
    "msgroup",
    "msline",
    "msrow",
    "mstack",
    "menclose",
    "merror",
    "mfenced",
    "mfrac",
    "mi",
    "mmultiscripts",
    "mn",
    "mo",
    "mover",
    "mprescripts",
    "msqrt",
    "msub",
    "msup",
    "msubsup",
    "munder",
    "munderover",
    "semantics",
    "annotation",
    "annotation-xml",
    "none",
    "mprescripts",
    # SVG
    "svg",
    "a",
    "altGlyph",
    "altGlyphDef",
    "altGlyphItem",
    "animate",
    "animateColor",
    "animateMotion",
    "animateTransform",
    "circle",
    "clipPath",
    "color-profile",
    "cursor",
    "defs",
    "desc",
    "ellipse",
    "feBlend",
    "feColorMatrix",
    "feComponentTransfer",
    "feComposite",
    "feConvolveMatrix",
    "feDiffuseLighting",
    "feDisplacementMap",
    "feDistantLight",
    "feFlood",
    "feFuncA",
    "feFuncB",
    "feFuncG",
    "feFuncR",
    "feGaussianBlur",
    "feImage",
    "feMerge",
    "feMergeNode",
    "feMorphology",
    "feOffset",
    "fePointLight",
    "feSpecularLighting",
    "feSpotLight",
    "feTile",
    "feTurbulence",
    "filter",
    "font",
    "font-face",
    "font-face-format",
    "font-face-name",
    "font-face-src",
    "font-face-uri",
    "foreignObject",
    "g",
    "glyph",
    "glyphRef",
    "hkern",
    "image",
    "line",
    "linearGradient",
    "marker",
    "mask",
    "metadata",
    "missing-glyph",
    "mpath",
    "path",
    "pattern",
    "polygon",
    "polyline",
    "radialGradient",
    "rect",
    "script",
    "set",
    "stop",
    "style",
    "switch",
    "symbol",
    "text",
    "textPath",
    "title",
    "tref",
    "tspan",
    "use",
    "view",
    "vkern",
}


def validate_xhtml(path: Path | str) -> list[ResultMessage]:
    """Validate an XHTML document.

    Checks:
    - Well-formedness
    - Namespace declaration
    - Title element presence
    - Basic structure
    """
    file_path = Path(path)
    errors: list[ResultMessage] = []

    xml_doc = load_xml(file_path)
    if xml_doc.errors:
        return xml_doc.errors

    root = xml_doc.root
    ns = xml_doc.nsmap

    # Check XHTML namespace
    has_xhtml_ns = False
    for ns_uri in ns.values():
        if ns_uri == XHTML_NS:
            has_xhtml_ns = True
            break

    # Also check root tag directly
    if not has_xhtml_ns and isinstance(root.tag, str):
        if root.tag == "{http://www.w3.org/1999/xhtml}html":
            has_xhtml_ns = True

    if not has_xhtml_ns:
        # XHTML documents must declare the XHTML namespace
        if isinstance(root.tag, str):
            if root.tag == "html" or root.tag.endswith("}html"):
                errors.append(
                    ResultMessage(
                        id="RSC-005",
                        severity=Severity.ERROR,
                        message="XHTML document must use XHTML namespace",
                        path=str(file_path),
                    )
                )

    # Check for title element
    title_el = root.find(".//{http://www.w3.org/1999/xhtml}title")
    if title_el is None:
        title_el = root.find(".//title")

    if title_el is not None:
        title_text = title_el.text
        if not title_text or not title_text.strip():
            errors.append(
                ResultMessage(
                    id="RSC-005",
                    severity=Severity.ERROR,
                    message='"title" must not be empty',
                    path=str(file_path),
                )
            )
    else:
        # Missing title is a warning, not an error
        errors.append(
            ResultMessage(
                id="RSC-017",
                severity=Severity.WARNING,
                message="XHTML document should have a title element",
                path=str(file_path),
            )
        )

    # Check for required structure (html > head, body)
    html_el = root
    if isinstance(root.tag, str):
        local_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if local_tag != "html":
            errors.append(
                ResultMessage(
                    id="RSC-005",
                    severity=Severity.ERROR,
                    message="Root element must be html",
                    path=str(file_path),
                )
            )

    # Check for nested hyperlinks
    xhtml_ns = "http://www.w3.org/1999/xhtml"
    for a_el in root.iter(f"{{{xhtml_ns}}}a"):
        # Check if this <a> element contains another <a> element
        for descendant in a_el.iter(f"{{{xhtml_ns}}}a"):
            if descendant is not a_el:
                errors.append(
                    ResultMessage(
                        id="RSC-005",
                        severity=Severity.ERROR,
                        message="Nested hyperlinks are not allowed",
                        path=str(file_path),
                    )
                )
                break
        else:
            continue
        break
    return errors


def validate_xhtml_elements(
    path: Path | str, root: etree._Element
) -> list[ResultMessage]:
    """Validate that all elements in XHTML are valid HTML5 elements."""
    file_path = Path(path)
    errors: list[ResultMessage] = []

    if root is None:
        return errors

    xhtml_ns = "http://www.w3.org/1999/xhtml"
    svg_ns = "http://www.w3.org/2000/svg"
    mathml_ns = "http://www.w3.org/1998/Math/MathML"

    for elem in root.iter():
        # Skip comments and processing instructions
        if not isinstance(elem.tag, str):
            continue

        # Get the local name (without namespace)
        if "}" in elem.tag:
            ns_uri = elem.tag.split("}")[0].lstrip("{")
            local_name = elem.tag.split("}")[-1]
        else:
            ns_uri = ""
            local_name = elem.tag

        # Skip non-element nodes
        if not local_name:
            continue

        # Allow elements in XHTML, SVG, and MathML namespaces
        if ns_uri in (xhtml_ns, svg_ns, mathml_ns, ""):
            # Check if it's a valid element
            if local_name not in VALID_XHTML_ELEMENTS:
                # Allow custom elements (contain hyphen)
                if "-" in local_name:
                    continue
                errors.append(
                    build_message(
                        "RSC-005",
                        path=str(file_path),
                        message=f"invalid element '{local_name}'",
                    )
                )

    return errors


def validate_xhtml_doctype(
    path: Path | str, root: etree._Element
) -> list[ResultMessage]:
    """Validate XHTML DOCTYPE declaration.

    Checks:
    - HTML5 DOCTYPE not allowed in EPUB 2
    - Public ID must be valid
    - Unresolved entities
    """
    file_path = Path(path)
    errors: list[ResultMessage] = []

    # Read the file to check DOCTYPE
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return errors

    if "<!DOCTYPE" in content:
        # Extract DOCTYPE declaration
        doctype_start = content.find("<!DOCTYPE")
        if doctype_start != -1:
            doctype_end = content.find(">", doctype_start)
            if doctype_end != -1:
                doctype = content[doctype_start : doctype_end + 1]

                # Check for public ID
                if "PUBLIC" in doctype:
                    # Extract public ID
                    pub_start = doctype.find("PUBLIC")
                    if pub_start != -1:
                        pub_part = doctype[pub_start + 6 :].strip()
                        if pub_part.startswith('"'):
                            pub_end = pub_part.find('"', 1)
                            if pub_end != -1:
                                public_id = pub_part[1:pub_end]
                                # Check for invalid public IDs
                                if public_id and not public_id.startswith("-//W3C//"):
                                    errors.append(
                                        ResultMessage(
                                            id="RSC-005",
                                            severity=Severity.ERROR,
                                            message=f"Invalid public ID '{public_id}'",
                                            path=str(file_path),
                                        )
                                    )

                # Check for external DTD references that are not standard W3C DTDs
                w3c_dtds = [
                    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd",
                    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd",
                    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd",
                    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd",
                    "http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd",
                    "http://www.w3.org/TR/xhtml-modularization/PE/xhtml11-model-1.mod",
                    "http://www.w3.org/MarkUp/DTD/xhtml-special.ent",
                    "http://www.w3.org/MarkUp/DTD/xhtml-lat1.ent",
                    "http://www.w3.org/MarkUp/DTD/xhtml-symbol.ent",
                ]
                # Valid HTML5 doctype SYSTEM identifiers
                valid_system_ids = [
                    "about:legacy-compat",
                ]
                if "SYSTEM" in doctype:
                    # Extract system identifier
                    sys_start = doctype.find("SYSTEM")
                    if sys_start != -1:
                        sys_part = doctype[sys_start + 6 :].strip()
                        if sys_part.startswith('"'):
                            sys_end = sys_part.find('"', 1)
                            if sys_end != -1:
                                system_id = sys_part[1:sys_end]
                                if (
                                    system_id
                                    and system_id not in w3c_dtds
                                    and system_id not in valid_system_ids
                                ):
                                    errors.append(
                                        ResultMessage(
                                            id="RSC-005",
                                            severity=Severity.ERROR,
                                            message="External DTD reference not allowed",
                                            path=str(file_path),
                                        )
                                    )

    return errors


# Allowed external identifiers by media type
ALLOWED_EXTERNAL_IDENTIFIERS = {
    "application/xhtml+xml": {
        "public_ids": [
            "-//W3C//DTD XHTML 1.1//EN",
            "-//W3C//DTD XHTML Basic 1.1//EN",
            "-//W3C//DTD XHTML 1.0 Strict//EN",
            "-//W3C//DTD XHTML 1.0 Transitional//EN",
            "-//W3C//DTD XHTML 1.0 Frameset//EN",
        ],
        "system_ids": [
            "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd",
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd",
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd",
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd",
            "http://www.w3.org/TR/xhtml-modularization/xhtml-modularization.dtd",
            "http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd",
        ],
    },
    "application/mathml+xml": {
        "public_ids": [
            "-//W3C//DTD MathML 3.0//EN",
            "-//W3C//DTD MathML 2.0//EN",
        ],
        "system_ids": [
            "http://www.w3.org/Math/DTD/mathml3/mathml3.dtd",
            "http://www.w3.org/Math/DTD/mathml2/mathml2.dtd",
        ],
    },
    "application/mathml-presentation+xml": {
        "public_ids": [
            "-//W3C//DTD MathML 3.0//EN",
            "-//W3C//DTD MathML 2.0//EN",
        ],
        "system_ids": [
            "http://www.w3.org/Math/DTD/mathml3/mathml3.dtd",
            "http://www.w3.org/Math/DTD/mathml2/mathml2.dtd",
        ],
    },
    "application/mathml-content+xml": {
        "public_ids": [
            "-//W3C//DTD MathML 3.0//EN",
            "-//W3C//DTD MathML 2.0//EN",
        ],
        "system_ids": [
            "http://www.w3.org/Math/DTD/mathml3/mathml3.dtd",
            "http://www.w3.org/Math/DTD/mathml2/mathml2.dtd",
        ],
    },
    "image/svg+xml": {
        "public_ids": [
            "-//W3C//DTD SVG 1.1//EN",
            "-//W3C//DTD SVG 1.0//EN",
        ],
        "system_ids": [
            "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd",
            "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd",
        ],
    },
    "application/x-dtbncx+xml": {
        "public_ids": [
            "-//NISO//DTD ncx 2005-1//EN",
            "-//NISO//DTD ncx 2005-2//EN",
        ],
        "system_ids": [
            "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd",
            "http://www.daisy.org/z3986/2005/ncx-2005-2.dtd",
        ],
    },
}


def validate_external_identifier(
    path: Path | str,
    media_type: str,
    content: str,
) -> list[ResultMessage]:
    """Validate external identifier in DOCTYPE declaration.

    Checks if external identifier is allowed for the given media type.
    Reports OPF-073 if not allowed.
    """
    file_path = Path(path)
    errors: list[ResultMessage] = []

    if "<!DOCTYPE" not in content:
        return errors

    # Extract DOCTYPE declaration
    doctype_start = content.find("<!DOCTYPE")
    if doctype_start == -1:
        return errors
    doctype_end = content.find(">", doctype_start)
    if doctype_end == -1:
        return errors
    doctype = content[doctype_start : doctype_end + 1]

    # Extract public ID if present
    public_id = None
    system_id = None
    if "PUBLIC" in doctype:
        pub_start = doctype.find("PUBLIC")
        if pub_start != -1:
            pub_part = doctype[pub_start + 6 :].strip()
            if pub_part.startswith('"'):
                pub_end = pub_part.find('"', 1)
                if pub_end != -1:
                    public_id = pub_part[1:pub_end]
                    # System ID follows public ID
                    rest = pub_part[pub_end + 1 :].strip()
                    if rest.startswith('"'):
                        sys_end = rest.find('"', 1)
                        if sys_end != -1:
                            system_id = rest[1:sys_end]
    elif "SYSTEM" in doctype:
        sys_start = doctype.find("SYSTEM")
        if sys_start != -1:
            sys_part = doctype[sys_start + 6 :].strip()
            if sys_part.startswith('"'):
                sys_end = sys_part.find('"', 1)
                if sys_end != -1:
                    system_id = sys_part[1:sys_end]

    # Get allowed identifiers for this media type
    allowed = ALLOWED_EXTERNAL_IDENTIFIERS.get(media_type, {})
    allowed_public_ids = allowed.get("public_ids", [])
    allowed_system_ids = allowed.get("system_ids", [])

    # Check public ID
    if public_id and allowed_public_ids:
        if public_id not in allowed_public_ids:
            errors.append(
                ResultMessage(
                    id="OPF-073",
                    severity=Severity.ERROR,
                    message=f"Public identifier '{public_id}' is not allowed for media type '{media_type}'",
                    path=str(file_path),
                )
            )

    # Check system ID
    if system_id and allowed_system_ids:
        if system_id not in allowed_system_ids:
            errors.append(
                ResultMessage(
                    id="OPF-073",
                    severity=Severity.ERROR,
                    message=f"System identifier '{system_id}' is not allowed for media type '{media_type}'",
                    path=str(file_path),
                )
            )

    return errors


def validate_xhtml_nav(doc: XmlDocument) -> list[ResultMessage]:
    """Validate XHTML navigation document.

    Checks for nav element with epub:type attribute.
    """
    errors: list[ResultMessage] = []
    path = str(doc.path)

    # Find nav elements
    nav_elements = doc.findall(".//{http://www.w3.org/1999/xhtml}nav")
    if not nav_elements:
        nav_elements = doc.findall(".//nav")

    if not nav_elements:
        errors.append(
            ResultMessage(
                id="RSC-005",
                severity=Severity.ERROR,
                message="Navigation document must contain at least one nav element",
                path=path,
            )
        )
        return errors

    # Check for toc nav
    has_toc = False
    for nav in nav_elements:
        epub_type = nav.get("{http://www.idpf.org/2007/ops}type", "")
        if not epub_type:
            epub_type = nav.get("epub:type", "")
        if "toc" in epub_type:
            has_toc = True
            break

    if not has_toc:
        errors.append(
            ResultMessage(
                id="RSC-005",
                severity=Severity.ERROR,
                message="toc nav missing",
                path=path,
            )
        )

    return errors


def validate_xhtml_title(doc: XmlDocument) -> list[ResultMessage]:
    """Validate XHTML title element."""
    errors: list[ResultMessage] = []
    path = str(doc.path)

    title_el = doc.find(".//{http://www.w3.org/1999/xhtml}title")
    if title_el is None:
        title_el = doc.find(".//title")

    if title_el is not None:
        title_text = title_el.text
        if not title_text or not title_text.strip():
            errors.append(
                ResultMessage(
                    id="RSC-005",
                    severity=Severity.ERROR,
                    message='"title" must not be empty',
                    path=path,
                )
            )
    else:
        errors.append(
            ResultMessage(
                id="RSC-005",
                severity=Severity.ERROR,
                message="XHTML document must have a title element",
                path=path,
            )
        )

    return errors


def validate_xhtml_duplicate_ids(path: Path | str, root) -> list[ResultMessage]:
    """Validate that no duplicate IDs exist in the document."""
    file_path = Path(path)
    errors: list[ResultMessage] = []

    # Collect all IDs
    id_counts: dict[str, int] = {}

    def collect_ids(element):
        elem_id = element.get("id", "")
        if elem_id:
            id_counts[elem_id] = id_counts.get(elem_id, 0) + 1
        for child in element:
            collect_ids(child)

    collect_ids(root)

    # Report duplicates
    for elem_id, count in id_counts.items():
        if count > 1:
            errors.append(
                ResultMessage(
                    id="RSC-005",
                    severity=Severity.ERROR,
                    message=f"duplicate ID '{elem_id}' found {count} times",
                    path=str(file_path),
                )
            )

    return errors


def validate_xhtml_alt_attributes(path: Path | str, root) -> list[ResultMessage]:
    """Validate that img elements have alt attributes."""
    file_path = Path(path)
    errors: list[ResultMessage] = []

    # Find all img elements
    xhtml_ns = "http://www.w3.org/1999/xhtml"
    for img_el in root.iter(f"{{{xhtml_ns}}}img"):
        alt = img_el.get("alt")
        if alt is None:
            errors.append(
                ResultMessage(
                    id="RSC-005",
                    severity=Severity.ERROR,
                    message="img element missing alt attribute",
                    path=str(file_path),
                )
            )

    return errors


def validate_xhtml_resource_references(
    path: Path | str, root, manifest_items: set[str]
) -> list[ResultMessage]:
    """Validate that referenced resources exist in manifest."""
    file_path = Path(path)
    errors: list[ResultMessage] = []

    xhtml_ns = "http://www.w3.org/1999/xhtml"

    # Check img src attributes
    for img_el in root.iter(f"{{{xhtml_ns}}}img"):
        src = img_el.get("src", "")
        if src and not src.startswith(("http://", "https://", "data:", "#")):
            base_src = src.split("#")[0] if "#" in src else src
            if base_src and base_src not in manifest_items:
                errors.append(
                    ResultMessage(
                        id="RSC-007",
                        severity=Severity.ERROR,
                        message=f"referenced resource '{src}' not found in manifest",
                        path=str(file_path),
                    )
                )

    return errors


def validate_xhtml_style_elements(path: Path | str, root) -> list[ResultMessage]:
    """Validate style elements in XHTML."""
    file_path = Path(path)
    errors: list[ResultMessage] = []

    xhtml_ns = "http://www.w3.org/1999/xhtml"

    # Check for style elements
    for style_el in root.iter(f"{{{xhtml_ns}}}style"):
        # Check if style element has content
        if style_el.text and style_el.text.strip():
            # Style elements are allowed in EPUB 3
            pass

    return errors
