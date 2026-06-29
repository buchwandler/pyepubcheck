"""Preview profile checks.

Self-gates on the CLI-requested profile (or the OPF metadata). When the
``preview`` profile is requested, the publication must declare a
``preview`` dc:type, a source publication, and (for the collection form)
an embedded manifest.
"""

from __future__ import annotations

from pyepubcheck.checks.profiles import (
    ProfileContext,
    has_collection_role,
    is_profile_active,
)
from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage


def _validate_dc_type(context: ProfileContext) -> list[ResultMessage]:
    if is_profile_active(context, "preview"):
        return []
    return [
        build_message(
            "RSC-005",
            path=str(context.opf_path),
            message='An EPUB Preview publication must have a "preview" dc:type',
        )
    ]


def _validate_source_publication(context: ProfileContext) -> list[ResultMessage]:
    if context.opf.xml_doc is None or context.opf.xml_doc.root is None:
        return []
    dc_ns = "http://purl.org/dc/elements/1.1/"
    for identifier in context.opf.xml_doc.root.iter(f"{{{dc_ns}}}source"):
        if identifier.text and identifier.text.strip():
            return []
    for relation in context.opf.xml_doc.root.iter(f"{{{dc_ns}}}relation"):
        rel = relation.get("rel", "")
        if "source" in rel and relation.text and relation.text.strip():
            return []
    return [
        build_message(
            "RSC-005",
            path=str(context.opf_path),
            message="An EPUB Preview publication must declare a source publication.",
        )
    ]


def _validate_embedded_manifest(context: ProfileContext) -> list[ResultMessage]:
    for item in context.opf.manifest:
        if "preview" in item.properties and "manifest" in item.properties:
            return []
    return [
        build_message(
            "RSC-005",
            path=str(context.opf_path),
            message=(
                "An embedded preview must declare a manifest item with the "
                "'preview' and 'manifest' properties."
            ),
        )
    ]


def run(context: ProfileContext) -> list[ResultMessage]:
    is_preview_profile = context.requested_profile == "preview"
    is_preview_meta = is_profile_active(context, "preview")
    in_collection = has_collection_role(context, "preview")
    if not (is_preview_profile or is_preview_meta or in_collection):
        return []
    errors: list[ResultMessage] = []
    if is_preview_profile or is_preview_meta:
        errors.extend(_validate_dc_type(context))
        errors.extend(_validate_source_publication(context))
    if in_collection:
        errors.extend(_validate_embedded_manifest(context))
    return errors
