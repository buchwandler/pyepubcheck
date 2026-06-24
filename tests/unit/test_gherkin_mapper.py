"""Unit tests for Gherkin mapper."""

from __future__ import annotations

from pathlib import Path

import pytest

from pyepubcheck.gherkin_mapper import (
    GherkinFeature,
    GherkinScenario,
    MappingReport,
    TestMapping,
    extract_message_ids,
    extract_test_mappings,
    generate_mapping_report,
    load_intentional_unmapped,
    parse_feature_file,
    save_mapping_report,
)


class TestExtractMessageIds:
    """Test message ID extraction."""

    def test_single_message_id(self) -> None:
        ids = extract_message_ids("Then error RSC-005 is reported")
        assert ids == ["RSC-005"]

    def test_multiple_message_ids(self) -> None:
        ids = extract_message_ids("Then error RSC-005 and RSC-007 are reported")
        assert ids == ["RSC-005", "RSC-007"]

    def test_no_message_ids(self) -> None:
        ids = extract_message_ids("Then no errors are reported")
        assert ids == []


class TestParseFeatureFile:
    """Test feature file parsing."""

    def test_minimal_feature(self, tmp_path: Path) -> None:
        feature_file = tmp_path / "test.feature"
        feature_file.write_text(
            """Feature: Test Feature

  Scenario: Test scenario
    Given something
    When action
    Then result
"""
        )
        feature = parse_feature_file(feature_file)
        assert feature.name == "Test Feature"
        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].scenario_name == "Test scenario"

    def test_message_ids_in_steps(self, tmp_path: Path) -> None:
        feature_file = tmp_path / "test.feature"
        feature_file.write_text(
            """Feature: Test Feature

  Scenario: Test scenario
    Given something
    Then error RSC-005 is reported
"""
        )
        feature = parse_feature_file(feature_file)
        assert len(feature.scenarios) == 1
        assert "RSC-005" in feature.scenarios[0].message_ids

    def test_multiple_scenarios(self, tmp_path: Path) -> None:
        feature_file = tmp_path / "test.feature"
        feature_file.write_text(
            """Feature: Test Feature

  Scenario: First scenario
    Given something
    Then result

  Scenario: Second scenario
    Given something else
    Then another result
"""
        )
        feature = parse_feature_file(feature_file)
        assert len(feature.scenarios) == 2

    def test_tags(self, tmp_path: Path) -> None:
        feature_file = tmp_path / "test.feature"
        feature_file.write_text(
            """@tag1 @tag2
Feature: Test Feature

  @scenario-tag
  Scenario: Test scenario
    Given something
    Then result
"""
        )
        feature = parse_feature_file(feature_file)
        assert "tag1" in feature.tags
        assert "tag2" in feature.tags
        assert "scenario-tag" in feature.scenarios[0].tags


class TestExtractTestMappings:
    """Test test mapping extraction."""

    def test_mapped_test(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test_example.py"
        test_file.write_text(
            """# specmason: @msg-RSC-005
def test_example() -> None:
    pass
"""
        )
        mappings = extract_test_mappings(test_file)
        assert len(mappings) == 1
        assert mappings[0].test_function == "test_example"
        assert "RSC-005" in mappings[0].message_ids

    def test_unmapped_test(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test_example.py"
        test_file.write_text(
            """# specmason: unmapped=pending
def test_example() -> None:
    pass
"""
        )
        mappings = extract_test_mappings(test_file)
        assert len(mappings) == 1
        assert mappings[0].status == "unmapped"

    def test_no_mapping(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test_example.py"
        test_file.write_text(
            """def test_example() -> None:
    pass
"""
        )
        mappings = extract_test_mappings(test_file)
        assert len(mappings) == 0


class TestGenerateMappingReport:
    """Test mapping report generation."""

    def test_basic_report(self, tmp_path: Path) -> None:
        # Create specs directory
        specs_dir = tmp_path / "specs" / "behavior" / "features"
        specs_dir.mkdir(parents=True)

        feature_file = specs_dir / "test.feature"
        feature_file.write_text(
            """Feature: Test Feature

  Scenario: Test scenario
    Given something
    Then error RSC-005 is reported
"""
        )

        # Create tests directory
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()

        test_file = tests_dir / "test_example.py"
        test_file.write_text(
            """# specmason: @msg-RSC-005
def test_example() -> None:
    pass
"""
        )

        report = generate_mapping_report(specs_dir, tests_dir)
        assert report.total_tests == 1
        assert report.mapped_tests == 1
        assert report.total_scenarios == 1


class TestLoadIntentionalUnmapped:
    """Test intentional unmapped loading."""

    def test_valid_file(self, tmp_path: Path) -> None:
        unmapped_file = tmp_path / "intentional-unmapped.json"
        unmapped_file.write_text('{"test1": "internal implementation"}')
        result = load_intentional_unmapped(unmapped_file)
        assert result == {"test1": "internal implementation"}

    def test_missing_file(self, tmp_path: Path) -> None:
        unmapped_file = tmp_path / "missing.json"
        result = load_intentional_unmapped(unmapped_file)
        assert result == {}


class TestSaveMappingReport:
    """Test mapping report saving."""

    def test_save_report(self, tmp_path: Path) -> None:
        report = MappingReport(
            total_tests=10,
            mapped_tests=8,
            unmapped_tests=2,
            waived_tests=0,
            total_scenarios=5,
            covered_scenarios=4,
            uncovered_scenarios=[],
            mappings=[],
        )

        output_path = tmp_path / "report.json"
        save_mapping_report(report, output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "total_tests" in content
