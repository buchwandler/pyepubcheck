"""Distributable Objects profile checks.

Self-gates on the OPF collection role ``distributable-object``. A publication
that declares the role must also declare a ``dc:identifier``; otherwise the
package is incomplete.
"""

from __future__ import annotations

from pyepubcheck.checks.profiles import ProfileContext, has_collection_role
from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage


def _validate_identifier(context: ProfileContext) -> list[ResultMessage]:
    if context.opf.metadata.identifiers:
        return []
    return [
        build_message(
            "RSC-005",
            path=str(context.opf_path),
            message="A Distributable Object must declare a dc:identifier.",
        )
    ]


def run(context: ProfileContext) -> list[ResultMessage]:
    if not has_collection_role(context, "distributable-object"):
        return []
    return _validate_identifier(context)
