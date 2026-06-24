"""Gherkin-test mapping infrastructure."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class GherkinScenario:
    """Parsed Gherkin scenario."""

    feature_file: Path
    feature_name: str
    scenario_name: str
    line_number: int
    tags: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    message_ids: list[str] = field(default_factory=list)


@dataclass
class GherkinFeature:
    """Parsed Gherkin feature."""

    file_path: Path
    name: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    scenarios: list[GherkinScenario] = field(default_factory=list)


@dataclass
class TestMapping:
    """Mapping between test and Gherkin scenario."""

    test_id: str
    test_file: Path
    test_function: str
    scenario: GherkinScenario | None = None
    message_ids: list[str] = field(default_factory=list)
    status: str = "mapped"  # mapped, unmapped, waived


@dataclass
class MappingReport:
    """Report of test-scenario mappings."""

    total_tests: int = 0
    mapped_tests: int = 0
    unmapped_tests: int = 0
    waived_tests: int = 0
    total_scenarios: int = 0
    covered_scenarios: int = 0
    uncovered_scenarios: int = 0
    mappings: list[TestMapping] = field(default_factory=list)
    unmapped_scenarios: list[GherkinScenario] = field(default_factory=list)


# Message ID patterns in Gherkin steps
MESSAGE_ID_RE = re.compile(r"[A-Z]{3}-\d{3}")

# Tag patterns
REQ_TAG_RE = re.compile(r"@req-(\w+)")
AC_TAG_RE = re.compile(r"@ac-(\w+)")
MESSAGE_TAG_RE = re.compile(r"@msg-([A-Z]{3}-\d{3})")


def extract_message_ids(text: str) -> list[str]:
    """Extract message IDs from text."""
    return MESSAGE_ID_RE.findall(text)


def parse_feature_file(file_path: Path) -> GherkinFeature:
    """Parse a Gherkin feature file."""
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    feature_name = ""
    feature_description = ""
    feature_tags: list[str] = []
    scenarios: list[GherkinScenario] = []

    current_tags: list[str] = []
    current_scenario_name = ""
    current_scenario_line = 0
    current_steps: list[str] = []
    in_scenario = False

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Collect tags
        if stripped.startswith("@"):
            tags = [t.lstrip("@") for t in stripped.split()]
            current_tags.extend(tags)
            continue

        # Feature line
        if stripped.startswith("Feature:"):
            feature_name = stripped[8:].strip()
            feature_tags = current_tags.copy()
            current_tags = []
            continue

        # Scenario line
        if stripped.startswith("Scenario:") or stripped.startswith("Example:"):
            # Save previous scenario
            if in_scenario and current_scenario_name:
                message_ids = []
                for step in current_steps:
                    message_ids.extend(extract_message_ids(step))

                scenarios.append(
                    GherkinScenario(
                        feature_file=file_path,
                        feature_name=feature_name,
                        scenario_name=current_scenario_name,
                        line_number=current_scenario_line,
                        tags=current_tags.copy(),
                        steps=current_steps.copy(),
                        message_ids=message_ids,
                    )
                )

            current_scenario_name = stripped.split(":", 1)[1].strip()
            current_scenario_line = i
            current_steps = []
            in_scenario = True
            # Don't reset current_tags - they belong to this scenario
            continue

        # Steps
        if in_scenario and stripped and not stripped.startswith("#"):
            if any(stripped.startswith(kw) for kw in ("Given", "When", "Then", "And", "But")):
                current_steps.append(stripped)

    # Save last scenario
    if in_scenario and current_scenario_name:
        message_ids = []
        for step in current_steps:
            message_ids.extend(extract_message_ids(step))

        scenarios.append(
            GherkinScenario(
                feature_file=file_path,
                feature_name=feature_name,
                scenario_name=current_scenario_name,
                line_number=current_scenario_line,
                tags=current_tags.copy(),
                steps=current_steps.copy(),
                message_ids=message_ids,
            )
        )

    return GherkinFeature(
        file_path=file_path,
        name=feature_name,
        description=feature_description,
        tags=feature_tags,
        scenarios=scenarios,
    )


def discover_feature_files(specs_dir: Path) -> list[Path]:
    """Discover all Gherkin feature files."""
    return sorted(specs_dir.rglob("*.feature"))


def discover_test_files(tests_dir: Path) -> list[Path]:
    """Discover all test files."""
    return sorted(tests_dir.rglob("test_*.py"))


def extract_test_mappings(test_file: Path) -> list[TestMapping]:
    """Extract test mappings from a test file."""
    content = test_file.read_text(encoding="utf-8")
    mappings: list[TestMapping] = []

    # Find test functions with specmason comments
    # Format: # specmason: @msg-RSC-005 or # specmason: unmapped=...
    specmason_re = re.compile(r"#\s*specmason:\s*(.+)")
    test_func_re = re.compile(r"def\s+(test_\w+)\s*\(")

    lines = content.splitlines()
    pending_spec_content = None

    for i, line in enumerate(lines, 1):
        # Find specmason mapping comments
        spec_match = specmason_re.search(line)
        if spec_match:
            pending_spec_content = spec_match.group(1).strip()
            continue

        # Find test function definitions
        func_match = test_func_re.search(line)
        if func_match and pending_spec_content:
            current_func = func_match.group(1)
            spec_content = pending_spec_content
            pending_spec_content = None

            # Check if it's unmapped
            if spec_content.startswith("unmapped="):
                mappings.append(
                    TestMapping(
                        test_id=f"{test_file.stem}::{current_func}",
                        test_file=test_file,
                        test_function=current_func,
                        message_ids=[],
                        status="unmapped",
                    )
                )
            else:
                # Extract message IDs
                tags = spec_content.split()
                message_ids = [t.replace("@msg-", "") for t in tags if t.startswith("@msg-") or "@" not in t]
                # Also extract any bare message IDs
                message_ids.extend(extract_message_ids(spec_content))
                message_ids = list(set(message_ids))

                mappings.append(
                    TestMapping(
                        test_id=f"{test_file.stem}::{current_func}",
                        test_file=test_file,
                        test_function=current_func,
                        message_ids=message_ids,
                        status="mapped" if message_ids else "unmapped",
                    )
                )
        elif func_match:
            pending_spec_content = None

    return mappings


def generate_mapping_report(
    specs_dir: Path,
    tests_dir: Path,
    intentional_unmapped: dict[str, str] | None = None,
) -> MappingReport:
    """Generate a mapping report."""
    # Discover features
    feature_files = discover_feature_files(specs_dir)
    features = [parse_feature_file(f) for f in feature_files]

    # Collect all scenarios
    all_scenarios: list[GherkinScenario] = []
    for feature in features:
        all_scenarios.extend(feature.scenarios)

    # Discover tests
    test_files = discover_test_files(tests_dir)
    all_mappings: list[TestMapping] = []
    for test_file in test_files:
        all_mappings.extend(extract_test_mappings(test_file))

    # Count mapped/unmapped
    mapped = sum(1 for m in all_mappings if m.status == "mapped")
    unmapped = sum(1 for m in all_mappings if m.status == "unmapped")
    waived = sum(1 for m in all_mappings if m.status == "waived")

    # Find uncovered scenarios
    covered_scenario_names = set()
    for mapping in all_mappings:
        if mapping.scenario:
            covered_scenario_names.add(mapping.scenario.scenario_name)

    uncovered = [s for s in all_scenarios if s.scenario_name not in covered_scenario_names]

    return MappingReport(
        total_tests=len(all_mappings),
        mapped_tests=mapped,
        unmapped_tests=unmapped,
        waived_tests=waived,
        total_scenarios=len(all_scenarios),
        covered_scenarios=len(covered_scenario_names),
        uncovered_scenarios=uncovered,
        mappings=all_mappings,
    )


def load_intentional_unmapped(file_path: Path) -> dict[str, str]:
    """Load intentional unmapped policy."""
    if not file_path.exists():
        return {}

    try:
        content = file_path.read_text(encoding="utf-8")
        return json.loads(content)
    except Exception:
        return {}


def save_mapping_report(report: MappingReport, output_path: Path) -> None:
    """Save mapping report to JSON."""
    data = {
        "summary": {
            "total_tests": report.total_tests,
            "mapped_tests": report.mapped_tests,
            "unmapped_tests": report.unmapped_tests,
            "waived_tests": report.waived_tests,
            "total_scenarios": report.total_scenarios,
            "covered_scenarios": report.covered_scenarios,
            "uncovered_scenarios": len(report.uncovered_scenarios),
        },
        "mappings": [
            {
                "test_id": m.test_id,
                "test_file": str(m.test_file),
                "test_function": m.test_function,
                "message_ids": m.message_ids,
                "status": m.status,
            }
            for m in report.mappings
        ],
        "uncovered_scenarios": [
            {
                "feature_file": str(s.feature_file),
                "feature_name": s.feature_name,
                "scenario_name": s.scenario_name,
                "line_number": s.line_number,
                "message_ids": s.message_ids,
            }
            for s in report.uncovered_scenarios
        ],
    }

    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
