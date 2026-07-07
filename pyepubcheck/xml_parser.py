"""XML document loading and validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree

from pyepubcheck.result import ResultMessage
from pyepubcheck.severity import Severity


@dataclass
class XmlDocument:
    """Parsed XML document with metadata."""

    path: Path
    tree: etree._ElementTree
    root: etree._Element
    doc_type: str = ""
    errors: list[ResultMessage] = field(default_factory=list)

    @property
    def nsmap(self) -> dict[str, str]:
        """Return namespace map from root element."""
        return dict(self.root.nsmap) if self.root.nsmap else {}

    def find(self, xpath: str, namespaces: dict[str, str] | None = None) -> etree._Element | None:
        """Find a single element by XPath."""
        ns = namespaces or self.nsmap
        try:
            return self.root.find(xpath, ns)
        except etree.XPathEvalError:
            return None

    def findall(self, xpath: str, namespaces: dict[str, str] | None = None) -> list[etree._Element]:
        """Find all elements matching XPath."""
        ns = namespaces or self.nsmap
        try:
            return self.root.findall(xpath, ns)
        except etree.XPathEvalError:
            return []

    def get_attr(self, element: etree._Element, attr: str, default: str = "") -> str:
        """Get attribute value, handling namespaces."""
        val = element.get(attr)
        return val if val is not None else default


# Common EPUB namespaces
OPF_NS = "http://www.idpf.org/2007/opf"
DC_NS = "http://purl.org/dc/elements/1.1/"
XHTML_NS = "http://www.w3.org/1999/xhtml"
SVG_NS = "http://www.w3.org/2000/svg"
EPUB_NS = "http://www.idpf.org/2007/ops"
NCX_NS = "http://www.daisy.org/z3986/2005/ncx/"
SMIL_NS = "http://www.w3.org/ns/SMIL"
DAISY_NS = "http://www.daisy.org/z3986/2005/ncx/"

EPUB_NAMESPACES = {
    "opf": OPF_NS,
    "dc": DC_NS,
    "xhtml": XHTML_NS,
    "svg": SVG_NS,
    "epub": EPUB_NS,
    "ncx": NCX_NS,
    "smil": SMIL_NS,
}


def detect_doc_type(root: etree._Element) -> str:
    """Detect document type from root element."""
    tag = root.tag
    if isinstance(tag, str):
        # Strip namespace
        local = tag.split("}")[-1] if "}" in tag else tag
        ns = tag.split("}")[0].lstrip("{") if "}" in tag else ""

        if local == "package" and ns == OPF_NS:
            return "opf"
        if local == "html" and ns == XHTML_NS:
            return "xhtml"
        if local == "svg" and ns == SVG_NS:
            return "svg"
        if local == "ncx" and ns == NCX_NS:
            return "ncx"
        if local == "smil" and ns == SMIL_NS:
            return "smil"
        if local == "html":
            return "xhtml"
        if local == "svg":
            return "svg"
    return "unknown"


def load_xml(path: Path | str) -> XmlDocument:
    """Load and parse an XML document.

    Returns XmlDocument with parsed tree, or errors if parsing fails.
    """
    file_path = Path(path)
    errors: list[ResultMessage] = []

    if not file_path.exists():
        errors.append(
            ResultMessage(
                id="RSC-001",
                severity=Severity.ERROR,
                message=f"File not found: {file_path}",
                path=str(file_path),
            )
        )
        # Return a minimal XmlDocument for error cases
        dummy = etree.Element("dummy")
        return XmlDocument(path=file_path, tree=etree.ElementTree(dummy), root=dummy, errors=errors)

    try:
        return load_xml_bytes(file_path.read_bytes(), path=file_path)
    except etree.XMLSyntaxError as e:
        errors.append(
            ResultMessage(
                id="RSC-005",
                severity=Severity.ERROR,
                message=f"XML parsing error: {e}",
                path=str(file_path),
                line=e.lineno if hasattr(e, "lineno") else None,
            )
        )
        dummy = etree.Element("dummy")
        return XmlDocument(path=file_path, tree=etree.ElementTree(dummy), root=dummy, errors=errors)


def load_xml_bytes(content: bytes, path: Path | str = "<bytes>") -> XmlDocument:
    """Load XML from bytes."""

    errors: list[ResultMessage] = []
    try:
        parser = etree.XMLParser(recover=False)
        root = etree.fromstring(content, parser)
        tree = etree.ElementTree(root)
        doc_type = detect_doc_type(root)
        return XmlDocument(path=Path(path), tree=tree, root=root, doc_type=doc_type, errors=errors)
    except etree.XMLSyntaxError as e:
        errors.append(
            ResultMessage(
                id="RSC-005",
                severity=Severity.ERROR,
                message=f"XML parsing error: {e}",
                path=str(path),
                line=e.lineno if hasattr(e, "lineno") else None,
            )
        )
        dummy = etree.Element("dummy")
        return XmlDocument(path=Path(path), tree=etree.ElementTree(dummy), root=dummy, errors=errors)


def load_xml_string(content: str, path: Path | str = "<string>") -> XmlDocument:
    """Load XML from a string."""
    return load_xml_bytes(content.encode("utf-8"), path=path)


def validate_xml_well_formedness(path: Path | str) -> list[ResultMessage]:
    """Validate XML well-formedness without full parsing."""
    file_path = Path(path)
    errors: list[ResultMessage] = []

    if not file_path.exists():
        errors.append(
            ResultMessage(
                id="RSC-001",
                severity=Severity.ERROR,
                message=f"File not found: {file_path}",
                path=str(file_path),
            )
        )
        return errors

    try:
        parser = etree.XMLParser(recover=False)
        etree.parse(str(file_path), parser)
    except etree.XMLSyntaxError as e:
        errors.append(
            ResultMessage(
                id="RSC-005",
                severity=Severity.ERROR,
                message=f"XML well-formedness error: {e}",
                path=str(file_path),
                line=e.lineno if hasattr(e, "lineno") else None,
            )
        )

    return errors
