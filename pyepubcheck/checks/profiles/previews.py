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
    # Check for collection with role "preview" containing a child collection with role "manifest"
    for item in context.opf.manifest:
        if "preview" in item.properties and "manifest" in item.properties:
            return []
    # Check for OPF collection structure
    if context.opf.xml_doc is None or context.opf.xml_doc.root is None:
        return []
    opf_ns = "http://www.idpf.org/2007/opf"
    for collection in context.opf.xml_doc.root.iter(f"{{{opf_ns}}}collection"):
        role = collection.get("role", "")
        if role == "preview":
            # Check for child manifest collection
            for child in collection.findall(f"{{{opf_ns}}}collection"):
                child_role = child.get("role", "")
                if child_role == "manifest":
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
    # Validate dc:type and source publication when explicitly declared as preview
    # or when --profile preview is requested (but not for collection-based previews)
    if is_preview_meta:
        errors.extend(_validate_dc_type(context))
        errors.extend(_validate_source_publication(context))
    elif is_preview_profile and not in_collection:
        # Only require dc:type when --profile preview is requested
        # but there's no collection structure
        errors.extend(_validate_dc_type(context))
        errors.extend(_validate_source_publication(context))
    # Validate embedded manifest when in collection
    if in_collection:
        errors.extend(_validate_embedded_manifest(context))
    return errors
