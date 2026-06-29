"""Profile-specific checks.

Each profile module exposes a ``run(context: ProfileContext) -> list[ResultMessage]``
function. Modules self-gate on the OPF metadata (dc:type, dc:language, and
collection roles) and emit messages only when the publication declares the
matching profile.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING
from collections.abc import Callable

from pyepubcheck.result import ResultMessage

if TYPE_CHECKING:
    from pyepubcheck.opf_parser import OpfDocument


@dataclass(frozen=True)
class ProfileContext:
    """Shared publication context threaded through every profile module.

    Built once per ``validate_path`` call from the parsed OPF. The
    :class:`OpfDocument` is the canonical source; the derived fields
    (``manifest_hrefs``, ``spine_hrefs``, ``collection_roles``,
    ``dc_types``, ``source_language``, ``target_language``) are precomputed
    to keep modules read-only.
    """

    opf: OpfDocument
    opf_path: Path
    opf_dir: Path
    requested_profile: str = "default"
    manifest_hrefs: frozenset[str] = field(default_factory=frozenset)
    spine_hrefs: frozenset[str] = field(default_factory=frozenset)
    collection_roles: frozenset[str] = field(default_factory=frozenset)
    dc_types: tuple[str, ...] = ()
    source_language: str | None = None
    target_language: str | None = None


def build_profile_context(
    opf: OpfDocument,
    opf_path: Path,
    requested_profile: str = "default",
) -> ProfileContext:
    """Construct a :class:`ProfileContext` from a parsed :class:`OpfDocument`."""
    opf_dir = opf_path.parent
    manifest_hrefs = frozenset(item.href for item in opf.manifest if item.href)
    manifest_by_id = opf.manifest_by_id
    spine_hrefs = frozenset(
        manifest_by_id[item.idref].href
        for item in opf.spine
        if item.idref in manifest_by_id and manifest_by_id[item.idref].href
    )
    collection_roles = frozenset(
        c.get("role", "") for c in opf.collections if c.get("role")
    )
    dc_types = tuple(opf.metadata.types)
    languages = opf.metadata.languages
    source_language = languages[0] if languages else None
    target_language = languages[-1] if len(languages) > 1 else None
    return ProfileContext(
        opf=opf,
        opf_path=opf_path,
        opf_dir=opf_dir,
        requested_profile=requested_profile,
        manifest_hrefs=manifest_hrefs,
        spine_hrefs=spine_hrefs,
        collection_roles=collection_roles,
        dc_types=dc_types,
        source_language=source_language,
        target_language=target_language,
    )


def is_profile_active(context: ProfileContext, *profile_types: str) -> bool:
    """Return ``True`` when any of ``profile_types`` is declared in dc:type."""
    if not profile_types:
        return True
    declared = {t.lower() for t in context.dc_types}
    return any(p.lower() in declared for p in profile_types)


def has_collection_role(context: ProfileContext, *roles: str) -> bool:
    """Return ``True`` when any of ``roles`` is declared as an OPF collection role."""
    return any(role in context.collection_roles for role in roles)


ProfileRunner = Callable[[ProfileContext], list[ResultMessage]]


def _load_modules() -> dict[str, ProfileRunner]:
    """Lazily import every profile module and return a name -> runner map."""
    from pyepubcheck.checks.profiles import (
        accessibility,
        dictionaries,
        distributable_objects,
        edupub,
        indexes,
        previews,
        scriptable_components,
    )

    return {
        "dictionaries": dictionaries.run,
        "edupub": edupub.run,
        "indexes": indexes.run,
        "previews": previews.run,
        "accessibility": accessibility.run,
        "distributable_objects": distributable_objects.run,
        "scriptable_components": scriptable_components.run,
    }


PROFILE_MODULES: dict[str, ProfileRunner] = _load_modules()


__all__ = [
    "PROFILE_MODULES",
    "ProfileContext",
    "ProfileRunner",
    "build_profile_context",
    "has_collection_role",
    "is_profile_active",
]
