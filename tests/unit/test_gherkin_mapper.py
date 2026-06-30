"""Unit tests for Gherkin mapper."""

from __future__ import annotations

from pathlib import Path

from pyepubcheck.gherkin_mapper import (
    MappingReport,
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

    def test_wildcard_step(self, tmp_path: Path) -> None:
        feature_file = tmp_path / "test.feature"
        feature_file.write_text(
            """Feature: Test Feature

  Scenario: Test scenario
    * something happens
    And another thing
"""
        )
        feature = parse_feature_file(feature_file)
        assert len(feature.scenarios) == 1
        assert len(feature.scenarios[0].steps) == 2
        assert feature.scenarios[0].steps[0] == "* something happens"

    def test_background_steps_prepended(self, tmp_path: Path) -> None:
        feature_file = tmp_path / "test.feature"
        feature_file.write_text(
            """Feature: Test Feature

  Background:
    Given a shared setup
    And another setup step

  Scenario: First scenario
    When action
    Then result

  Scenario: Second scenario
    When other action
    Then other result
"""
        )
        feature = parse_feature_file(feature_file)
        assert len(feature.background_steps) == 2
        assert feature.background_steps[0] == "Given a shared setup"
        assert len(feature.scenarios) == 2
        assert len(feature.scenarios[0].steps) == 4
        assert feature.scenarios[0].steps[0] == "Given a shared setup"
        assert feature.scenarios[0].steps[1] == "And another setup step"
        assert feature.scenarios[0].steps[2] == "When action"
        assert len(feature.scenarios[1].steps) == 4
        assert feature.scenarios[1].steps[0] == "Given a shared setup"

    def test_no_background(self, tmp_path: Path) -> None:
        feature_file = tmp_path / "test.feature"
        feature_file.write_text(
            """Feature: Test Feature

  Scenario: Test scenario
    Given something
    Then result
"""
        )
        feature = parse_feature_file(feature_file)
        assert feature.background_steps == []
        assert len(feature.scenarios[0].steps) == 2

    def test_scenario_outline_expansion(self, tmp_path: Path) -> None:
        feature_file = tmp_path / "test.feature"
        feature_file.write_text(
            """Feature: Test Feature

  Scenario Outline: parsing <value>
    When parsing <value>
    Then result is <result>

    Examples:
      | value  | result |
      | hello  | ok     |
      | world  | ok     |
"""
        )
        feature = parse_feature_file(feature_file)
        assert len(feature.scenarios) == 2
        assert feature.scenarios[0].scenario_name == "parsing hello"
        assert feature.scenarios[0].steps[0] == "When parsing hello"
        assert feature.scenarios[0].steps[1] == "Then result is ok"
        assert feature.scenarios[1].scenario_name == "parsing world"
        assert feature.scenarios[1].steps[0] == "When parsing world"

    def test_scenario_outline_multiple_tables(self, tmp_path: Path) -> None:
        feature_file = tmp_path / "test.feature"
        feature_file.write_text(
            """Feature: Test Feature

  Scenario Outline: test <value>
    When test <value>

    Scenarios:
      | value |
      | a     |
      | b     |

    Scenarios: Second set
      | value |
      | c     |
"""
        )
        feature = parse_feature_file(feature_file)
        assert len(feature.scenarios) == 3
        assert feature.scenarios[0].scenario_name == "test a"
        assert feature.scenarios[1].scenario_name == "test b"
        assert feature.scenarios[2].scenario_name == "test c"

    def test_scenario_outline_with_background(self, tmp_path: Path) -> None:
        feature_file = tmp_path / "test.feature"
        feature_file.write_text(
            """Feature: Test Feature

  Background:
    Given setup

  Scenario Outline: test <value>
    When test <value>
    Then ok

    Examples:
      | value |
      | x     |
"""
        )
        feature = parse_feature_file(feature_file)
        assert len(feature.scenarios) == 1
        assert feature.scenarios[0].steps[0] == "Given setup"
        assert feature.scenarios[0].steps[1] == "When test x"

    def test_scenario_outline_wildcard_step(self, tmp_path: Path) -> None:
        feature_file = tmp_path / "test.feature"
        feature_file.write_text(
            """Feature: Test Feature

  Scenario Outline: test <id>
    * <id> is valid

    Scenarios:
      | id |
      | a  |
      | b  |
"""
        )
        feature = parse_feature_file(feature_file)
        assert len(feature.scenarios) == 2
        assert feature.scenarios[0].steps[0] == "* a is valid"
        assert feature.scenarios[1].steps[0] == "* b is valid"

    def test_data_table_after_step(self, tmp_path: Path) -> None:
        feature_file = tmp_path / "test.feature"
        feature_file.write_text(
            """Feature: Test Feature

  Scenario: Test scenario
    Given something
    Then the following errors are reported
    | RSC-005 | error message one |
    | RSC-005 | error message two |
    And no other errors
"""
        )
        feature = parse_feature_file(feature_file)
        assert len(feature.scenarios) == 1
        scenario = feature.scenarios[0]
        # Step index 1 = "Then the following errors are reported"
        assert 1 in scenario.data_tables
        assert len(scenario.data_tables[1]) == 2
        assert scenario.data_tables[1][0] == ["RSC-005", "error message one"]
        assert scenario.data_tables[1][1] == ["RSC-005", "error message two"]

    def test_no_data_table(self, tmp_path: Path) -> None:
        feature_file = tmp_path / "test.feature"
        feature_file.write_text(
            """Feature: Test Feature

  Scenario: Test scenario
    Given something
    Then result
"""
        )
        feature = parse_feature_file(feature_file)
        assert feature.scenarios[0].data_tables == {}


class TestFullCorpusIntegration:
    """Integration test for the full Gherkin corpus."""

    def test_all_feature_files_parse(self) -> None:
        """All 49 feature files should parse without errors."""
        from pyepubcheck.gherkin_mapper import discover_feature_files

        specs_dir = Path("specs/behavior/features")
        files = discover_feature_files(specs_dir)
        assert len(files) == 49

        total_scenarios = 0
        for f in files:
            feature = parse_feature_file(f)
            total_scenarios += len(feature.scenarios)

        # After expansion, we should have more than the original 966 scenarios
        assert total_scenarios > 966

    def test_scenario_outline_expansion_count(self) -> None:
        """Scenario Outline expansion should produce expected counts."""
        from pyepubcheck.gherkin_mapper import discover_feature_files

        specs_dir = Path("specs/behavior/features")
        files = discover_feature_files(specs_dir)

        # Count scenarios before and after
        total = 0
        for f in files:
            feature = parse_feature_file(f)
            total += len(feature.scenarios)

        # We should have significantly more than 966 due to outline expansion
        assert total >= 1100


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
