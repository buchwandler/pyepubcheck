"""Metadata extraction helpers for inspection."""

from __future__ import annotations

from lxml import etree

from pyepubcheck.inspect.models import MetadataEntry, PackageInfo
from pyepubcheck.opf_parser import OpfDocument

XML_NS = "http://www.w3.org/XML/1998/namespace"


def build_package_info(package_path: str, opf: OpfDocument) -> PackageInfo:
    """Build package summary information from a parsed OPF."""

    xml_lang = ""
    if opf.xml_doc is not None:
        xml_lang = opf.xml_doc.root.get(f"{{{XML_NS}}}lang", "") or ""

    return PackageInfo(
        path=package_path,
        version=opf.version,
        unique_identifier_id=opf.unique_identifier,
        unique_identifier_value=resolve_unique_identifier_value(opf),
        primary_language=(opf.metadata.languages[0] if opf.metadata.languages else xml_lang),
        title=opf.metadata.titles[0] if opf.metadata.titles else "",
        rendition_layout=opf.metadata.rendition_layout,
        spine_count=len(opf.spine),
        linear_spine_count=sum(1 for item in opf.spine if item.linear),
    )


def resolve_unique_identifier_value(opf: OpfDocument) -> str:
    """Resolve the package unique identifier value."""

    if opf.xml_doc is None:
        return opf.metadata.identifiers[0] if opf.metadata.identifiers else ""

    metadata_el = _find_metadata_element(opf)
    if metadata_el is None or not opf.unique_identifier:
        return opf.metadata.identifiers[0] if opf.metadata.identifiers else ""

    for element in metadata_el:
        if _local_name(element.tag) != "identifier":
            continue
        if (element.get("id") or "").strip() == opf.unique_identifier:
            return _text_value(element)
    return opf.metadata.identifiers[0] if opf.metadata.identifiers else ""


def extract_metadata_entries(package_path: str, opf: OpfDocument) -> list[MetadataEntry]:
    """Extract package-level and OPF metadata entries."""

    if opf.xml_doc is None:
        return []

    entries: list[MetadataEntry] = []
    root = opf.xml_doc.root
    for attr_name, value in root.attrib.items():
        entries.append(
            MetadataEntry(
                package_path=package_path,
                namespace="package",
                name=_attribute_name(attr_name),
                value=value.strip(),
            )
        )

    metadata_el = _find_metadata_element(opf)
    if metadata_el is None:
        return entries

    for element in metadata_el:
        if not isinstance(element.tag, str):
            continue
        tag_name = _local_name(element.tag)
        namespace = _namespace(element.tag)
        attributes = {_attribute_name(name): value for name, value in element.attrib.items()}

        entries.append(
            MetadataEntry(
                package_path=package_path,
                namespace=namespace,
                name=tag_name,
                value=_text_value(element),
                attributes=attributes,
            )
        )
    return entries


def _find_metadata_element(opf: OpfDocument) -> etree._Element | None:
    if opf.xml_doc is None:
        return None
    ns = opf.xml_doc.nsmap
    if "opf" not in ns:
        ns["opf"] = "http://www.idpf.org/2007/opf"
    return opf.xml_doc.root.find("opf:metadata", ns)


def _text_value(element: etree._Element) -> str:
    return "".join(element.itertext()).strip()


def _local_name(tag: str) -> str:
    if tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def _namespace(tag: str) -> str:
    if tag.startswith("{"):
        return tag[1:].split("}", 1)[0]
    return ""


def _attribute_name(name: str) -> str:
    if not name.startswith("{"):
        return name
    namespace, local = name[1:].split("}", 1)
    if namespace == XML_NS:
        return f"xml:{local}"
    return local
