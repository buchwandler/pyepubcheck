"""OPF package document parsing."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from pyepubcheck.result import ResultMessage
from pyepubcheck.severity import Severity
from pyepubcheck.xml_parser import (
    DC_NS,
    OPF_NS,
    XmlDocument,
    load_xml,
)


@dataclass
class ManifestItem:
    """OPF manifest item."""

    id: str
    href: str
    media_type: str
    properties: list[str] = field(default_factory=list)
    fallback: str = ""
    media_overlay: str = ""


@dataclass
class SpineItemref:
    """OPF spine itemref."""

    idref: str
    linear: bool = True
    properties: list[str] = field(default_factory=list)
    id: str = ""


@dataclass
class OpfMetadata:
    """OPF metadata extracted from package document."""

    identifiers: list[str] = field(default_factory=list)
    titles: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    creators: list[str] = field(default_factory=list)
    contributors: list[str] = field(default_factory=list)
    types: list[str] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)
    publishers: list[str] = field(default_factory=list)
    dates: list[str] = field(default_factory=list)
    subjects: list[str] = field(default_factory=list)
    rights: list[str] = field(default_factory=list)
    modified: str = ""
    rendition_layout: str = ""
    rendition_orientation: str = ""
    rendition_spread: str = ""
    media_active_classes: list[str] = field(default_factory=list)
    extra: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class PrefixDeclaration:
    """Prefix declaration from prefix attribute."""

    prefix: str
    uri: str


@dataclass
class OpfDocument:
    """Parsed OPF package document."""

    path: Path
    version: str = "3.0"
    unique_identifier: str = ""
    metadata: OpfMetadata = field(default_factory=OpfMetadata)
    manifest: list[ManifestItem] = field(default_factory=list)
    spine: list[SpineItemref] = field(default_factory=list)
    spine_toc: str = ""
    prefixes: list[PrefixDeclaration] = field(default_factory=list)
    collections: list[dict[str, str]] = field(default_factory=list)
    errors: list[ResultMessage] = field(default_factory=list)
    xml_doc: XmlDocument | None = None

    @property
    def manifest_by_id(self) -> dict[str, ManifestItem]:
        """Manifest items indexed by id."""
        return {item.id: item for item in self.manifest}

    @property
    def manifest_by_href(self) -> dict[str, ManifestItem]:
        """Manifest items indexed by href."""
        return {item.href: item for item in self.manifest}

    def get_manifest_item(self, id: str) -> ManifestItem | None:
        """Get manifest item by id."""
        return self.manifest_by_id.get(id)


# Default EPUB 3 prefixes
DEFAULT_PREFIXES = {
    "dcterms": "http://purl.org/dc/terms/",
    "marc": "http://id.loc.gov/vocabulary/",
    "media": "http://www.idpf.org/epub/vocab/overlays/#",
    "onix": "http://www.editeur.org/ONIX/book/codelists/main.html",
    "rendition": "http://www.idpf.org/vocab/rendition/#",
    "schema": "http://schema.org/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}

# Predefined vocabulary prefixes
PREDEFINED_PREFIXES = {
    "a11y": "http://www.idpf.org/epub/vocab/package/a11y/#",
    "dcterms": "http://purl.org/dc/terms/",
    "marc": "http://id.loc.gov/vocabulary/",
    "media": "http://www.idpf.org/epub/vocab/overlays/#",
    "onix": "http://www.editeur.org/ONIX/book/codelists/main.html",
    "rendition": "http://www.idpf.org/vocab/rendition/#",
    "schema": "http://schema.org/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "foaf": "http://xmlns.com/foaf/spec/",
    "opf": "http://www.idpf.org/2007/opf",
    "db": "http://dbpedia.org/ontology/",
}

PREFIX_RE = re.compile(r"(\w+):\s*(\S+)")


def parse_prefix_attribute(value: str) -> list[PrefixDeclaration]:
    """Parse prefix attribute value into declarations."""
    prefixes = []
    for match in PREFIX_RE.finditer(value):
        prefix = match.group(1)
        uri = match.group(2)
        prefixes.append(PrefixDeclaration(prefix=prefix, uri=uri))
    return prefixes


def _text_or_empty(element, xpath: str, namespaces: dict[str, str]) -> str:
    """Get text content of element or empty string."""
    found = element.find(xpath, namespaces)
    if found is not None and found.text:
        return found.text.strip()
    return ""


def _text_list(element, xpath: str, namespaces: dict[str, str]) -> list[str]:
    """Get list of text contents from elements matching xpath."""
    return [
        el.text.strip()
        for el in element.findall(xpath, namespaces)
        if el.text and el.text.strip()
    ]


def parse_opf(path: Path | str) -> OpfDocument:
    """Parse an OPF package document.

    Returns OpfDocument with extracted metadata, manifest, spine.
    """
    file_path = Path(path)
    errors: list[ResultMessage] = []

    xml_doc = load_xml(file_path)
    if xml_doc.errors:
        return OpfDocument(path=file_path, errors=xml_doc.errors)

    root = xml_doc.root
    ns = xml_doc.nsmap

    # Ensure OPF namespace is available
    if "opf" not in ns and root.tag.startswith("{"):
        tag_ns = root.tag.split("}")[0].lstrip("{")
        ns["opf"] = tag_ns
    elif "opf" not in ns:
        ns["opf"] = OPF_NS

    # Ensure DC namespace
    if "dc" not in ns:
        ns["dc"] = DC_NS

    version = root.get("version", "3.0")
    unique_identifier = root.get("unique-identifier", "")

    # Parse metadata
    metadata = OpfMetadata()
    metadata_el = root.find("opf:metadata", ns)
    if metadata_el is not None:
        metadata.identifiers = _text_list(metadata_el, "dc:identifier", ns)
        metadata.titles = _text_list(metadata_el, "dc:title", ns)
        metadata.languages = _text_list(metadata_el, "dc:language", ns)
        metadata.creators = _text_list(metadata_el, "dc:creator", ns)
        metadata.contributors = _text_list(metadata_el, "dc:contributor", ns)
        metadata.types = _text_list(metadata_el, "dc:type", ns)
        metadata.descriptions = _text_list(metadata_el, "dc:description", ns)
        metadata.publishers = _text_list(metadata_el, "dc:publisher", ns)
        metadata.dates = _text_list(metadata_el, "dc:date", ns)
        metadata.subjects = _text_list(metadata_el, "dc:subject", ns)
        metadata.rights = _text_list(metadata_el, "dc:rights", ns)

        # Modified date
        modified_el = metadata_el.find("opf:meta[@property='dcterms:modified']", ns)
        if modified_el is not None and modified_el.text:
            metadata.modified = modified_el.text.strip()

        # Rendition properties
        for prop, attr in [
            ("rendition:layout", "rendition_layout"),
            ("rendition:orientation", "rendition_orientation"),
            ("rendition:spread", "rendition_spread"),
        ]:
            meta_el = metadata_el.find(f"opf:meta[@property='{prop}']", ns)
            if meta_el is not None and meta_el.text:
                setattr(metadata, attr, meta_el.text.strip())

    # Parse prefix attribute
    prefix_attr = root.get("prefix", "")
    if prefix_attr:
        prefixes = parse_prefix_attribute(prefix_attr)
    else:
        prefixes = []

    # Parse manifest
    manifest: list[ManifestItem] = []
    manifest_el = root.find("opf:manifest", ns)
    if manifest_el is not None:
        for item_el in manifest_el.findall("opf:item", ns):
            item_id = item_el.get("id", "")
            href = item_el.get("href", "")
            media_type = item_el.get("media-type", "")
            properties_str = item_el.get("properties", "")
            properties = properties_str.split() if properties_str else []
            fallback = item_el.get("fallback", "")
            media_overlay = item_el.get("media-overlay", "")

            if item_id:
                manifest.append(
                    ManifestItem(
                        id=item_id,
                        href=href,
                        media_type=media_type,
                        properties=properties,
                        fallback=fallback,
                        media_overlay=media_overlay,
                    )
                )

    # Parse spine
    spine: list[SpineItemref] = []
    spine_toc = ""
    spine_el = root.find("opf:spine", ns)
    if spine_el is not None:
        spine_toc = spine_el.get("toc", "")
        for itemref_el in spine_el.findall("opf:itemref", ns):
            idref = itemref_el.get("idref", "")
            linear_str = itemref_el.get("linear", "yes")
            linear = linear_str != "no"
            properties_str = itemref_el.get("properties", "")
            properties = properties_str.split() if properties_str else []
            item_id = itemref_el.get("id", "")

            if idref:
                spine.append(
                    SpineItemref(
                        idref=idref,
                        linear=linear,
                        properties=properties,
                        id=item_id,
                    )
                )

    # Parse collections
    collections: list[dict[str, str]] = []
    for coll_el in root.findall("opf:collection", ns):
        coll_role = coll_el.get("role", "")
        coll_id = coll_el.get("id", "")
        if coll_role:
            collections.append({"role": coll_role, "id": coll_id})

    return OpfDocument(
        path=file_path,
        version=version,
        unique_identifier=unique_identifier,
        metadata=metadata,
        manifest=manifest,
        spine=spine,
        spine_toc=spine_toc,
        prefixes=prefixes,
        collections=collections,
        errors=errors,
        xml_doc=xml_doc,
    )


def validate_opf_required_metadata(opf: OpfDocument) -> list[ResultMessage]:
    """Validate required metadata fields."""
    errors: list[ResultMessage] = []

    if not opf.metadata.identifiers:
        errors.append(
            ResultMessage(
                id="RSC-005",
                severity=Severity.ERROR,
                message="OPF metadata must contain at least one dc:identifier",
                path=str(opf.path),
            )
        )

    if not opf.metadata.titles:
        errors.append(
            ResultMessage(
                id="RSC-005",
                severity=Severity.ERROR,
                message="OPF metadata must contain at least one dc:title",
                path=str(opf.path),
            )
        )

    if not opf.metadata.languages:
        errors.append(
            ResultMessage(
                id="RSC-005",
                severity=Severity.ERROR,
                message="OPF metadata must contain at least one dc:language",
                path=str(opf.path),
            )
        )

    return errors


def validate_opf_prefixes(opf: OpfDocument) -> list[ResultMessage]:
    """Validate prefix declarations."""
    errors: list[ResultMessage] = []

    # Check for undeclared prefixes used in properties
    declared_prefixes = {p.prefix for p in opf.prefixes}
    declared_prefixes.update(PREDEFINED_PREFIXES.keys())

    # Known property prefixes that don't need declaration
    known_property_prefixes = {"nav", "cover", "mathml", "remote-resources", "scripted", "svg", "switch", "data-nav"}

    # Check manifest item properties
    for item in opf.manifest:
        for prop in item.properties:
            if ":" in prop:
                prefix = prop.split(":")[0]
                if prefix not in declared_prefixes and prefix not in known_property_prefixes:
                    errors.append(
                        ResultMessage(
                            id="OPF-028",
                            severity=Severity.ERROR,
                            message=f'Undeclared prefix: "{prefix}"',
                            path=str(opf.path),
                        )
                    )

    # Check meta property attributes in XML
    if opf.xml_doc:
        for meta_el in opf.xml_doc.root.iter("{http://www.idpf.org/2007/opf}meta"):
            prop = meta_el.get("property", "")
            if ":" in prop:
                prefix = prop.split(":")[0]
                if prefix not in declared_prefixes and prefix not in known_property_prefixes:
                    errors.append(
                        ResultMessage(
                            id="OPF-028",
                            severity=Severity.ERROR,
                            message=f'Undeclared prefix: "{prefix}"',
                            path=str(opf.path),
                        )
                    )

    return errors
