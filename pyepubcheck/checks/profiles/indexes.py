"""Index profile checks.

Self-gates on the OPF collection role ``index`` (or the requested
profile). A publication that declares an index must include at least one
XHTML content document that contains an ``index``-typed section.
"""

from __future__ import annotations

from pyepubcheck.checks.profiles import ProfileContext, has_collection_role, is_profile_active
from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml


def _document_has_index_element(path) -> bool:
    xml_doc = load_xml(path)
    if xml_doc.errors or xml_doc.root is None:
        return False
    xhtml_ns = "http://www.w3.org/1999/xhtml"
    epub_ns = "http://www.idpf.org/2007/ops"
    # Check div, section, and body elements for epub:type="index"
    for tag in (f"{{{xhtml_ns}}}div", f"{{{xhtml_ns}}}section", f"{{{xhtml_ns}}}body"):
        for el in xml_doc.root.iter(tag):
            epub_type = el.get(f"{{{epub_ns}}}type", "") or el.get("epub:type", "")
            if "index" in epub_type:
                return True
    return False


def _index_documents(context: ProfileContext) -> list:
    candidates = []
    is_index_type = is_profile_active(context, "index")
    has_index_collection = "index" in context.collection_roles
    
    # First check manifest items with index property
    for item in context.opf.manifest:
        if not item.href or item.media_type != "application/xhtml+xml":
            continue
        if "index" in item.properties:
            candidates.append(context.opf_dir / item.href)
    
    # If there's an index collection, get the linked documents
    if has_index_collection and context.opf.xml_doc is not None and context.opf.xml_doc.root is not None:
        opf_ns = "http://www.idpf.org/2007/opf"
        for collection in context.opf.xml_doc.root.iter(f"{{{opf_ns}}}collection"):
            if collection.get("role", "") != "index":
                continue
            for link in collection.findall(f"{{{opf_ns}}}link"):
                href = link.get("href", "")
                if href:
                    path = context.opf_dir / href
                    if path not in candidates:
                        candidates.append(path)
    
    # If dc:type is index but no specific index documents found,
    # all XHTML documents are candidates
    if is_index_type and not candidates:
        for item in context.opf.manifest:
            if item.href and item.media_type == "application/xhtml+xml":
                candidates.append(context.opf_dir / item.href)
    return candidates


def run(context: ProfileContext) -> list[ResultMessage]:
    is_index_profile = context.requested_profile == "idx"
    is_collection = has_collection_role(context, "index")
    is_index_type = is_profile_active(context, "index")
    if not (is_index_profile or is_collection or is_index_type):
        return []
    candidates = _index_documents(context)
    if not candidates:
        return [
            build_message(
                "RSC-005",
                path=str(context.opf_path),
                message=(
                    "An index collection must include at least one "
                    "XHTML index document."
                ),
            )
        ]
    for path in candidates:
        if not path.exists():
            continue
        if _document_has_index_element(path):
            return []
    return [
        build_message(
            "RSC-005",
            path=str(context.opf_path),
            message=(
                'At least one "index" element must be present in a document '
                "declared as an index in the OPF"
            ),
        )
    ]
