"""Dictionary profile checks.

Self-gates on the CLI-requested profile (or the OPF metadata). When the
``dict`` profile is requested, the publication must declare a
``dictionary`` dc:type. Single-dictionary publications must also include a
search key map and a source language.
"""

from __future__ import annotations

from pyepubcheck.checks.profiles import (
    ProfileContext,
    is_profile_active,
)
from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage


def _is_dict_profile_active(context: ProfileContext) -> bool:
    return context.requested_profile == "dict" or is_profile_active(
        context, "dictionary"
    )


def _is_glossary_profile_active(context: ProfileContext) -> bool:
    return context.requested_profile == "dict" or is_profile_active(context, "glossary")


def _validate_dc_type(context: ProfileContext) -> list[ResultMessage]:
    if is_profile_active(context, "dictionary"):
        return []
    return [
        build_message(
            "RSC-005",
            path=str(context.opf_path),
            message='The dc:type identifier "dictionary" is required.',
        ),
        build_message(
            "OPF-079",
            path=str(context.opf_path),
            message="dictionary metadata warning",
        ),
    ]


def _validate_source_language(context: ProfileContext) -> list[ResultMessage]:
    if context.source_language:
        return []
    return [
        build_message(
            "RSC-005",
            path=str(context.opf_path),
            message=(
                "The source language of a single-dictionary publication "
                "must be defined."
            ),
        )
    ]


def _validate_search_key_map(context: ProfileContext) -> list[ResultMessage]:
    if context.opf.xml_doc is None or context.opf.xml_doc.root is None:
        return []
    package_ns = "http://www.idpf.org/2007/opf"
    for link in context.opf.xml_doc.root.iter(f"{{{package_ns}}}link"):
        if link.get("rel", "") == "search-key-map":
            return []
    for item in context.opf.manifest:
        if "search-key-map" in item.properties:
            return []
    return [
        build_message(
            "RSC-005",
            path=str(context.opf_path),
            message="A single EPUB Dictionary must declare a search key map.",
        )
    ]


def _validate_monolingual_type(context: ProfileContext) -> list[ResultMessage]:
    if context.target_language and context.target_language != context.source_language:
        return [
            build_message(
                "RSC-005",
                path=str(context.opf_path),
                message=(
                    "A monolingual dictionary must declare a single source language."
                ),
            )
        ]
    return []


def _validate_glossary_marker(context: ProfileContext) -> list[ResultMessage]:
    for item in context.opf.manifest:
        if "glossary" in item.properties:
            return []
    return [
        build_message(
            "RSC-005",
            path=str(context.opf_path),
            message=(
                "A glossary publication must declare a manifest item "
                'with property "glossary".'
            ),
        )
    ]


def run(context: ProfileContext) -> list[ResultMessage]:
    is_dict = _is_dict_profile_active(context)
    is_glossary = is_profile_active(context, "glossary")
    if not (is_dict or is_glossary):
        return []
    errors: list[ResultMessage] = []
    if is_dict:
        errors.extend(_validate_dc_type(context))
        errors.extend(_validate_source_language(context))
        errors.extend(_validate_search_key_map(context))
        errors.extend(_validate_monolingual_type(context))
    if is_glossary:
        errors.extend(_validate_glossary_marker(context))
    return errors
