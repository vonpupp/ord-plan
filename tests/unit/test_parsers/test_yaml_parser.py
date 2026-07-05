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
        format_config: dict[str, str | int | bool] = {}

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
        assert any("events" in err.lower() for err in errors_list), (
            "Should have error about events section"
        )

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
        assert any("UNKNOWN_KEY" in warn for warn in warnings), (
            "Should have warning about unknown key"
        )

        # Should not have any errors
        errors_list = [err for err in errors if not err.startswith("Warning:")]
        assert len(errors_list) == 0

    def test_validate_format_schema_not_dict(self) -> None:
        """Test validating a format schema that is not a dictionary."""
        format_config = "invalid"

        errors = YamlParser.validate_format_schema(format_config)  # type: ignore[arg-type]

        # Should have an error
        assert len(errors) > 0
        assert any("must be a dictionary" in err for err in errors), (
            "Should have error about root structure"
        )

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
        assert any("events" in err.lower() for err in errors_list), (
            "Should have error about events section"
        )


class TestPropertiesParsing:
    """Test properties field parsing functionality."""

    def test_parse_event_with_properties(self, tmp_path: Path) -> None:
        """Test parsing an event with properties."""
        events_content = {
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                    "properties": [
                        {"category": "test"},
                        {"priority": "high"},
                    ],
                }
            ]
        }

        events_file = tmp_path / "events.yaml"
        events_file.write_text(yaml.dump(events_content))

        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        assert len(event_rules) == 1
        assert event_rules[0].properties == {"category": "test", "priority": "high"}

    def test_parse_event_with_empty_properties(self, tmp_path: Path) -> None:
        """Test parsing an event with empty properties."""
        events_content = {
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                    "properties": [],
                }
            ]
        }

        events_file = tmp_path / "events.yaml"
        events_file.write_text(yaml.dump(events_content))

        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        assert len(event_rules) == 1
        assert event_rules[0].properties == {}

    def test_parse_event_with_null_properties(self, tmp_path: Path) -> None:
        """Test parsing an event with null properties."""
        events_content = {
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                    "properties": None,
                }
            ]
        }

        events_file = tmp_path / "events.yaml"
        events_file.write_text(yaml.dump(events_content))

        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        assert len(event_rules) == 1
        assert event_rules[0].properties == {}

    def test_parse_event_with_dict_properties(self, tmp_path: Path) -> None:
        """Test parsing an event with dict properties (alternative format)."""
        events_content = {
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                    "properties": {"category": "test", "priority": "high"},
                }
            ]
        }

        events_file = tmp_path / "events.yaml"
        events_file.write_text(yaml.dump(events_content))

        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        assert len(event_rules) == 1
        assert event_rules[0].properties == {"category": "test", "priority": "high"}


class TestPropertiesValidation:
    """Test properties field validation functionality."""

    def test_validate_properties_valid(self) -> None:
        """Test validating valid properties."""
        event_config = {
            "title": "Test Event",
            "cron": "0 9 * * 1",
            "properties": [
                {"category": "test"},
                {"priority": "high"},
            ],
        }

        errors = YamlParser._validate_event_schema(event_config, 0)

        # Should not have any errors
        errors_list = [err for err in errors if not err.startswith("Warning:")]
        assert len(errors_list) == 0

    def test_validate_properties_invalid_type(self) -> None:
        """Test validating properties with invalid type."""
        event_config = {
            "title": "Test Event",
            "cron": "0 9 * * 1",
            "properties": "invalid",
        }

        errors = YamlParser._validate_event_schema(event_config, 0)

        # Should have an error about properties type
        assert any("'properties' must be a list" in err for err in errors), (
            "Should have error about properties type"
        )

    def test_validate_properties_invalid_item_type(self) -> None:
        """Test validating properties with invalid item type."""
        event_config = {
            "title": "Test Event",
            "cron": "0 9 * * 1",
            "properties": ["invalid"],
        }

        errors = YamlParser._validate_event_schema(event_config, 0)

        # Should have an error about property item type
        assert any("property 0 must be a dictionary" in err for err in errors), (
            "Should have error about property item type"
        )

    def test_validate_properties_multiple_keys(self) -> None:
        """Test validating properties with multiple keys in single item."""
        event_config = {
            "title": "Test Event",
            "cron": "0 9 * * 1",
            "properties": [{"key1": "value1", "key2": "value2"}],
        }

        errors = YamlParser._validate_event_schema(event_config, 0)

        # Should have an error about multiple keys
        assert any("exactly one key-value pair" in err for err in errors), (
            "Should have error about multiple keys"
        )

    def test_validate_properties_duplicate_keys(self) -> None:
        """Test validating properties with duplicate keys."""
        event_config = {
            "title": "Test Event",
            "cron": "0 9 * * 1",
            "properties": [
                {"category": "test1"},
                {"category": "test2"},
            ],
        }

        errors = YamlParser._validate_event_schema(event_config, 0)

        # Should have an error about duplicate keys
        assert any("duplicate property key" in err for err in errors), (
            "Should have error about duplicate keys"
        )

    def test_validate_properties_too_many(self) -> None:
        """Test validating too many properties."""
        event_config = {
            "title": "Test Event",
            "cron": "0 9 * * 1",
            "properties": [{f"prop{i}": "value"} for i in range(21)],
        }

        errors = YamlParser._validate_event_schema(event_config, 0)

        # Should have an error about too many properties
        assert any("too many properties" in err for err in errors), (
            "Should have error about too many properties"
        )

    def test_validate_property_key_too_long(self) -> None:
        """Test validating property key that is too long."""
        event_config = {
            "title": "Test Event",
            "cron": "0 9 * * 1",
            "properties": [{"a" * 51: "value"}],
        }

        errors = YamlParser._validate_event_schema(event_config, 0)

        # Should have an error about key length
        assert any("key too long" in err for err in errors), (
            "Should have error about key length"
        )

    def test_validate_property_value_too_long(self) -> None:
        """Test validating property value that is too long."""
        event_config = {
            "title": "Test Event",
            "cron": "0 9 * * 1",
            "properties": [{"key": "v" * 501}],
        }

        errors = YamlParser._validate_event_schema(event_config, 0)

        # Should have an error about value length
        assert any("value too long" in err for err in errors), (
            "Should have error about value length"
        )

    def test_validate_property_key_invalid_chars(self) -> None:
        """Test validating property key with invalid characters."""
        event_config = {
            "title": "Test Event",
            "cron": "0 9 * * 1",
            "properties": [{"key-with-dash": "value"}],
        }

        errors = YamlParser._validate_event_schema(event_config, 0)

        # Should have an error about invalid characters
        assert any("must contain only alphanumeric" in err for err in errors), (
            "Should have error about invalid characters"
        )
