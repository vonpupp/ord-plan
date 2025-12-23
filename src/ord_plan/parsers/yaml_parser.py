"""YAML parser for ord-plan rules files."""

from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import yaml

from ..models.event_rule import EventRule


class YamlParser:
    """Parser for YAML rules files."""

    @staticmethod
    def parse_rules_file(file_path: str) -> Dict[str, Any]:
        """Parse YAML rules file.

        Args:
            file_path: Path to YAML rules file

        Returns:
            Dictionary containing the parsed configuration
        """
        with open(file_path) as f:
            content: Dict[str, Any] = yaml.safe_load(f) or {}

        return content

    @staticmethod
    def parse_format_file(file_path: str) -> Dict[str, Any]:
        """Parse YAML format file containing only formatting options.

        Args:
            file_path: Path to YAML format file

        Returns:
            Dictionary containing the parsed format configuration

        Raises:
            YAMLError: If YAML parsing fails
            Exception: For other file reading errors
        """
        try:
            with open(file_path) as f:
                content: Dict[str, Any] = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in {file_path}: {e}") from e
        except Exception as e:
            raise Exception(f"Error reading {file_path}: {e}") from e

        return content

    @staticmethod
    def validate_format_schema(format_config: Dict[str, Any]) -> List[str]:
        """Validate format file schema.

        Format files contain only formatting options, no events section.

        Args:
            format_config: Parsed format configuration

        Returns:
            List of validation errors and warnings
        """
        errors = []

        # Validate root structure
        if not isinstance(format_config, dict):
            errors.append("Root of format file must be a dictionary/object")
            return errors

        # Check for forbidden events section
        if "events" in format_config:
            errors.append("Format file must not contain 'events' section")
            return errors

        # Validate allowed format keys
        allowed_format_keys = {
            "REVERSE_DATETREE_YEAR_FORMAT",
            "REVERSE_DATETREE_WEEK_FORMAT",
            "REVERSE_DATETREE_DATE_FORMAT",
            "REVERSE_DATETREE_USE_WEEK_TREE",
        }

        # Check for unknown keys (warning only)
        unknown_keys = set(format_config.keys()) - allowed_format_keys
        if unknown_keys:
            for key in sorted(unknown_keys):
                errors.append(
                    f"Warning: Unknown configuration key {key!r} will be ignored"
                )

        return errors

    @staticmethod
    def parse_event_rules(config: Dict[str, Any]) -> List[EventRule]:
        """Parse event rules from configuration.

        Args:
            config: Parsed YAML configuration

        Returns:
            List of EventRule objects

        Raises:
            ValueError: If required fields are missing or invalid
        """
        events_config = config.get("events", [])

        if not isinstance(events_config, list):
            raise ValueError("'events' must be a list")

        event_rules = []

        for i, event_config in enumerate(events_config):
            if not isinstance(event_config, dict):
                raise ValueError(f"Event at index {i} must be a dictionary")

            # Required fields
            title = event_config.get("title")
            if not title or not isinstance(title, str):
                raise ValueError(f"Event at index {i} missing required 'title' field")

            cron = event_config.get("cron")
            if not cron or not isinstance(cron, str):
                raise ValueError(f"Event at index {i} missing required 'cron' field")

            # Optional fields
            tags = event_config.get("tags", [])
            if tags is None:
                tags = []
            elif not isinstance(tags, list):
                raise ValueError(f"Event at index {i} 'tags' must be a list")

            todo_state = event_config.get("todo_state")
            if todo_state is not None and not isinstance(todo_state, str):
                raise ValueError(f"Event at index {i} 'todo_state' must be a string")

            description = event_config.get("description")
            if description is not None and not isinstance(description, str):
                raise ValueError(f"Event at index {i} 'description' must be a string")

            body = event_config.get("body")
            if body is not None and not isinstance(body, str):
                raise ValueError(f"Event at index {i} 'body' must be a string")

            try:
                event_rule = EventRule(
                    title=title,
                    cron=cron,
                    tags=tags,
                    todo_state=todo_state,
                    description=description,
                    body=body,
                )
                event_rules.append(event_rule)
            except ValueError as e:
                raise ValueError(f"Event at index {i}: {e}") from e

        return event_rules

    @staticmethod
    def validate_yaml_schema(
        config: Dict[str, Any], require_headers: bool = False
    ) -> List[str]:
        """Validate YAML schema with detailed error messages.

        Args:
            config: Parsed YAML configuration
            require_headers: If True, require mandatory header variables.

        Returns:
            List of validation errors, empty if valid
        """
        errors = []

        # Validate root structure
        if not isinstance(config, dict):
            errors.append("Root of YAML file must be a dictionary/object")
            return errors

        # Validate mandatory header variables (if required)
        if require_headers:
            mandatory_headers = {
                "REVERSE_DATETREE_WEEK_FORMAT",
                "REVERSE_DATETREE_DATE_FORMAT",
                "REVERSE_DATETREE_YEAR_FORMAT",
                "REVERSE_DATETREE_USE_WEEK_TREE",
            }

            missing_headers = mandatory_headers - set(config.keys())
            if missing_headers:
                for header in sorted(missing_headers):
                    errors.append(f"Missing mandatory header variable: {header}")
                return errors

        # Validate configuration keys (allow unknown keys for extensibility)
        config_keys = set(config.keys())
        known_config_keys = {
            "events",
            "REVERSE_DATETREE_WEEK_FORMAT",
            "REVERSE_DATETREE_DATE_FORMAT",
            "REVERSE_DATETREE_YEAR_FORMAT",
            "REVERSE_DATETREE_USE_WEEK_TREE",
        }

        # Check for unknown keys (warning only)
        unknown_keys = config_keys - known_config_keys
        if unknown_keys:
            for key in sorted(unknown_keys):
                errors.append(
                    f"Warning: Unknown configuration key {key!r} will be ignored"
                )

        # Validate events section
        if "events" not in config:
            errors.append("Missing required 'events' section")
            return errors

        events_config = config["events"]
        if not isinstance(events_config, list):
            errors.append("'events' must be a list")
            return errors

        if not events_config:
            errors.append("'events' list cannot be empty")
            return errors

        # Validate each event
        for i, event_config in enumerate(events_config):
            event_errors = YamlParser._validate_event_schema(event_config, i)
            errors.extend(event_errors)

        return errors

    @staticmethod
    def _validate_event_schema(
        event_config: Any, index: int
    ) -> List[str]:  # noqa: C901
        """Validate a single event configuration.

        Args:
            event_config: Event configuration object
            index: Event index for error context

        Returns:
            List of validation errors
        """
        errors = []
        event_prefix = f"Event at index {index}"

        if not isinstance(event_config, dict):
            errors.append(f"{event_prefix}: must be a dictionary/object")
            return errors

        # Required fields
        required_fields = ["title", "cron"]
        for field in required_fields:
            if field not in event_config:
                errors.append(f"{event_prefix}: missing required field {field!r}")
            elif not event_config[field]:
                errors.append(f"{event_prefix}: field {field!r} cannot be empty")

        # Title validation
        title = event_config.get("title")
        if title is not None:
            if not isinstance(title, str):
                errors.append(f"{event_prefix}: 'title' must be a string")
            elif not title.strip():
                errors.append(f"{event_prefix}: 'title' cannot be empty")
            elif len(title) > 200:
                errors.append(f"{event_prefix}: 'title' too long (max 200 characters)")

        # Cron expression validation
        cron = event_config.get("cron")
        if cron is not None:
            if not isinstance(cron, str):
                errors.append(f"{event_prefix}: 'cron' must be a string")
            elif not cron.strip():
                errors.append(f"{event_prefix}: 'cron' cannot be empty")

        # Tags validation
        tags = event_config.get("tags", [])
        if tags is not None:
            if not isinstance(tags, list):
                errors.append(f"{event_prefix}: 'tags' must be a list")
            else:
                if len(tags) > 10:
                    errors.append(f"{event_prefix}: too many tags (max 10)")

                for j, tag in enumerate(tags):
                    if not isinstance(tag, str):
                        errors.append(f"{event_prefix}: tag {j} must be a string")
                    elif not tag.strip():
                        errors.append(f"{event_prefix}: tag {j} cannot be empty")
                    elif len(tag) > 50:
                        errors.append(
                            f"{event_prefix}: tag {j} too long (max 50 characters)"
                        )
                    elif " " in tag:
                        errors.append(
                            f"{event_prefix}: tag {j} {tag!r} cannot contain spaces"
                        )

        # TODO state validation
        todo_state = event_config.get("todo_state")
        if todo_state is not None:
            if not isinstance(todo_state, str):
                errors.append(f"{event_prefix}: 'todo_state' must be a string")
            elif len(todo_state) > 20:
                errors.append(
                    f"{event_prefix}: 'todo_state' too long (max 20 characters)"
                )

        # Description validation
        description = event_config.get("description")
        if description is not None:
            if not isinstance(description, str):
                errors.append(f"{event_prefix}: 'description' must be a string")
            elif len(description) > 1000:
                errors.append(
                    f"{event_prefix}: 'description' too long (max 1000 characters)"
                )

        # Body validation
        body = event_config.get("body")
        if body is not None:
            if not isinstance(body, str):
                errors.append(f"{event_prefix}: 'body' must be a string")
            elif len(body) > 5000:
                errors.append(f"{event_prefix}: 'body' too long (max 5000 characters)")

        # Check for unknown fields (warning only)
        known_fields = {"title", "cron", "tags", "todo_state", "description", "body"}
        unknown_fields = set(event_config.keys()) - known_fields
        for field in sorted(unknown_fields):
            errors.append(
                f"{event_prefix}: Warning - unknown field {field!r} will be ignored"
            )

        return errors

    @staticmethod
    def parse_and_validate(
        file_path: str, require_headers: bool = False
    ) -> Tuple[Dict[str, Any], List[str]]:
        """Parse YAML file and validate schema with comprehensive error reporting.

        Args:
            file_path: Path to YAML rules file
            require_headers: If True, require mandatory header variables.

        Returns:
            Tuple of (config_dict, errors_list)

        Raises:
            YAMLError: If YAML parsing fails
            Exception: For other file reading errors
        """
        try:
            config = YamlParser.parse_rules_file(file_path)
        except yaml.YAMLError as e:
            # Enhance YAML parsing errors with context
            raise yaml.YAMLError(f"Invalid YAML in {file_path}: {e}") from e
        except Exception as e:
            raise Exception(f"Error reading {file_path}: {e}") from e

        # Validate schema
        errors = YamlParser.validate_yaml_schema(config, require_headers)

        return config, errors
