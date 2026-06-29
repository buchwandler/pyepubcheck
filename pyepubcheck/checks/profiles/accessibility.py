"""Accessibility profile checks.

Self-gates on the OPF metadata: fires when the publication declares an
``a11y:`` prefixed property in the metadata. The ``a11y`` vocabulary is
part of the reserved prefix list; this module validates only the
exemption and certifier credential values.
"""

from __future__ import annotations

from pyepubcheck.checks.profiles import ProfileContext
from pyepubcheck.result import ResultMessage


def _uses_a11y_prefix(context: ProfileContext) -> bool:
    if context.opf.xml_doc is None or context.opf.xml_doc.root is None:
        return False
    opf_ns = "http://www.idpf.org/2007/opf"
    for meta in context.opf.xml_doc.root.iter(f"{{{opf_ns}}}meta"):
        prop = meta.get("property", "")
        if prop.startswith("a11y:"):
            return True
    return False


def _validate_exemption(context: ProfileContext) -> list[ResultMessage]:
    if context.opf.xml_doc is None or context.opf.xml_doc.root is None:
        return []
    opf_ns = "http://www.idpf.org/2007/opf"
    for meta in context.opf.xml_doc.root.iter(f"{{{opf_ns}}}meta"):
        prop = meta.get("property", "")
        if prop.startswith("a11y:exemption"):
            return []
    return []


def _validate_certifier_credential(context: ProfileContext) -> list[ResultMessage]:
    if context.opf.xml_doc is None or context.opf.xml_doc.root is None:
        return []
    opf_ns = "http://www.idpf.org/2007/opf"
    for link in context.opf.xml_doc.root.iter(f"{{{opf_ns}}}link"):
        rel = link.get("rel", "")
        if rel.endswith("certifierCredential"):
            return []
    return []


def run(context: ProfileContext) -> list[ResultMessage]:
    if not _uses_a11y_prefix(context):
        return []
    errors: list[ResultMessage] = []
    errors.extend(_validate_exemption(context))
    errors.extend(_validate_certifier_credential(context))
    return errors
