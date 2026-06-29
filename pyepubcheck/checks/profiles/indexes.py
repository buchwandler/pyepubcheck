"""Index profile checks.

Self-gates on the OPF collection role ``index`` (or the requested
profile). A publication that declares an index must include at least one
XHTML content document that contains an ``index``-typed section.
"""

from __future__ import annotations

from pyepubcheck.checks.profiles import ProfileContext, has_collection_role
from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage
from pyepubcheck.xml_parser import load_xml


def _document_has_index_element(path) -> bool:
    xml_doc = load_xml(path)
    if xml_doc.errors or xml_doc.root is None:
        return False
    xhtml_ns = "http://www.w3.org/1999/xhtml"
    epub_ns = "http://www.idpf.org/2007/ops"
    for el in xml_doc.root.iter(f"{{{xhtml_ns}}}div"):
        epub_type = el.get(f"{{{epub_ns}}}type", "") or el.get("epub:type", "")
        if "index" in epub_type:
            return True
    return False


def _index_documents(context: ProfileContext) -> list:
    candidates = []
    for item in context.opf.manifest:
        if not item.href or item.media_type != "application/xhtml+xml":
            continue
        if "index" in item.properties or "index" in context.collection_roles:
            candidates.append(context.opf_dir / item.href)
    return candidates


def run(context: ProfileContext) -> list[ResultMessage]:
    is_index_profile = context.requested_profile == "idx"
    is_collection = has_collection_role(context, "index")
    if not (is_index_profile or is_collection):
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
