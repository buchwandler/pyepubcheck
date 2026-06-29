"""Scriptable Components profile checks.

Self-gates on the OPF collection role ``scriptable-component``. A scriptable
component publication must declare the ``epubsc`` prefix in the OPF
``prefix`` attribute so that ``epubsc:foo`` property values resolve.
"""

from __future__ import annotations

from pyepubcheck.checks.profiles import ProfileContext, has_collection_role
from pyepubcheck.messages import build_message
from pyepubcheck.result import ResultMessage


def _validate_epubsc_prefix(context: ProfileContext) -> list[ResultMessage]:
    declared = {p.prefix for p in context.opf.prefixes}
    if "epubsc" in declared:
        return []
    return [
        build_message(
            "OPF-028",
            path=str(context.opf_path),
            message='The "epubsc" prefix must be declared in the OPF prefix attribute.',
        )
    ]


def run(context: ProfileContext) -> list[ResultMessage]:
    if not has_collection_role(context, "scriptable-component"):
        return []
    return _validate_epubsc_prefix(context)
