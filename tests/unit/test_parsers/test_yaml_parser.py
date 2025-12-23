"""Unit tests for YAML parser format file functionality."""

from pathlib import Path

import pytest
import yaml

from ord_plan.parsers.yaml_parser import YamlParser


class TestFormatFileParsing:
    """Test format file parsing functionality."""

    def test_parse_format_file_valid(self, tmp_path: Path) -> None:
        """Test parsing a valid format file."""
        format_content = {
            "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
            "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
            "REVERSE_DATETREE_USE_WEEK_TREE": True,
        }

        format_file = tmp_path / "format.yaml"
        format_file.write_text(yaml.dump(format_content))

        result = YamlParser.parse_format_file(str(format_file))

        assert result == format_content

    def test_parse_format_file_empty(self, tmp_path: Path) -> None:
        """Test parsing an empty format file."""
        format_file = tmp_path / "format.yaml"
        format_file.write_text("# All formatting options will use defaults\n")

        result = YamlParser.parse_format_file(str(format_file))

        assert result == {}

    def test_parse_format_file_invalid_yaml(self, tmp_path: Path) -> None:
        """Test parsing a format file with invalid YAML."""
        format_file = tmp_path / "format.yaml"
        format_file.write_text("invalid: yaml: content: [unclosed")

        with pytest.raises(yaml.YAMLError):
            YamlParser.parse_format_file(str(format_file))


class TestFormatSchemaValidation:
    """Test format file schema validation."""

    def test_validate_format_schema_valid(self) -> None:
        """Test validating a valid format schema."""
        format_config = {
            "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
            "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
            "REVERSE_DATETREE_USE_WEEK_TREE": True,
        }

        errors = YamlParser.validate_format_schema(format_config)

        # Should only have warnings for unknown keys, no errors
        errors_list = [err for err in errors if not err.startswith("Warning:")]
        assert len(errors_list) == 0

    def test_validate_format_schema_empty(self) -> None:
        """Test validating an empty format schema."""
        format_config = {}

        errors = YamlParser.validate_format_schema(format_config)

        # Should be valid
        errors_list = [err for err in errors if not err.startswith("Warning:")]
        assert len(errors_list) == 0

    def test_validate_format_schema_with_events(self) -> None:
        """Test validating a format schema with events section (forbidden)."""
        format_config = {
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ],
        }

        errors = YamlParser.validate_format_schema(format_config)

        # Should have an error about events section
        errors_list = [err for err in errors if not err.startswith("Warning:")]
        assert len(errors_list) > 0
        assert any(
            "events" in err.lower() for err in errors_list
        ), "Should have error about events section"

    def test_validate_format_schema_partial(self) -> None:
        """Test validating a format schema with partial options."""
        format_config = {
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
        }

        errors = YamlParser.validate_format_schema(format_config)

        # Should be valid
        errors_list = [err for err in errors if not err.startswith("Warning:")]
        assert len(errors_list) == 0

    def test_validate_format_schema_unknown_key(self) -> None:
        """Test validating a format schema with unknown key (warning)."""
        format_config = {
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
            "UNKNOWN_KEY": "value",
        }

        errors = YamlParser.validate_format_schema(format_config)

        # Should have a warning for unknown key
        warnings = [err for err in errors if err.startswith("Warning:")]
        assert len(warnings) > 0
        assert any(
            "UNKNOWN_KEY" in warn for warn in warnings
        ), "Should have warning about unknown key"

        # Should not have any errors
        errors_list = [err for err in errors if not err.startswith("Warning:")]
        assert len(errors_list) == 0

    def test_validate_format_schema_not_dict(self) -> None:
        """Test validating a format schema that is not a dictionary."""
        format_config = "invalid"

        errors = YamlParser.validate_format_schema(format_config)

        # Should have an error
        assert len(errors) > 0
        assert any(
            "must be a dictionary" in err for err in errors
        ), "Should have error about root structure"

    def test_validate_format_schema_events_section(self) -> None:
        """Test validating a format schema with events section (already tested)."""
        format_config = {
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ],
        }

        errors = YamlParser.validate_format_schema(format_config)

        # Should have an error about events section
        errors_list = [err for err in errors if not err.startswith("Warning:")]
        assert len(errors_list) > 0
        assert any(
            "events" in err.lower() for err in errors_list
        ), "Should have error about events section"
