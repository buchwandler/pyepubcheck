"""Usage/reporting checks.

Currently limited to OPF-003 (USAGE) reports: scan the OCF container for
files that exist on disk but are not declared in the OPF manifest.
"""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.messages import build_message
from pyepubcheck.opf_parser import parse_opf
from pyepubcheck.result import ResultMessage
from pyepubcheck.severity import Severity

# Files that may exist in the OCF container without being in the manifest.
_OCF_RESERVED = {
    "mimetype",
    "META-INF/container.xml",
    "META-INF/encryption.xml",
    "META-INF/manifest.xml",
    "META-INF/metadata.xml",
    "META-INF/rights.xml",
    "META-INF/signatures.xml",
}


def run(
    opf_path: Path,
    container_files: list[Path] | None = None,
) -> list[ResultMessage]:
    """Emit USAGE messages for container files not in the OPF manifest.

    The OPF-003 message has catalog severity ERROR, so we override it to
    USAGE here to match the test expectation.
    """
    opf = parse_opf(opf_path)
    if opf.errors or opf.xml_doc is None:
        return []

    manifest_hrefs = {item.href for item in opf.manifest if item.href}
    opf_dir = opf_path.parent
    if container_files is None:
        return []

    opf_relative = opf_path.name
    results: list[ResultMessage] = []
    for file_path in container_files:
        if not file_path.is_file():
            continue
        try:
            relative = file_path.relative_to(opf_dir).as_posix()
        except ValueError:
            continue
        if not relative or relative in _OCF_RESERVED:
            continue
        if relative == opf_relative:
            continue
        if relative in manifest_hrefs:
            continue
        results.append(
            build_message(
                "OPF-003",
                path=str(file_path),
                message=(
                    f"File '{relative}' is in the container but not "
                    f"declared in the manifest."
                ),
            )
        )
        results[-1] = ResultMessage(
            id=results[-1].id,
            severity=Severity.USAGE,
            message=results[-1].message,
            suggestion=results[-1].suggestion,
            path=results[-1].path,
        )
    return results
