"""Configuration handling for ord-plan."""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Union


@dataclass
class Configuration:
    """Configuration for formatting and behavior."""

    reverse_datetree_year_format: str = "%Y"
    reverse_datetree_week_format: str = "%Y-W%V"
    reverse_datetree_date_format: str = "%Y-%m-%d %a"
    default_todo_state: str = "TODO"

    # Performance settings
    max_events_per_file: int = 10000
    processing_timeout_seconds: int = 120

    # Output settings
    preserve_timestamps: bool = True
    backup_existing_files: bool = False

    @classmethod
    def from_dict(
        cls, config_dict: Optional[Dict[str, Union[str, int, bool]]] = None
    ) -> "Configuration":
        """Create configuration from dictionary."""
        if config_dict is None:
            config_dict = {}

        return cls(
            reverse_datetree_year_format=str(
                config_dict.get("REVERSE_DATETREE_YEAR_FORMAT", "%Y")
            ),
            reverse_datetree_week_format=str(
                config_dict.get("REVERSE_DATETREE_WEEK_FORMAT", "%Y-W%V")
            ),
            reverse_datetree_date_format=str(
                config_dict.get("REVERSE_DATETREE_DATE_FORMAT", "%Y-%m-%d %a")
            ),
            default_todo_state=str(config_dict.get("default_todo_state", "TODO")),
            max_events_per_file=int(config_dict.get("max_events_per_file", 10000)),
            processing_timeout_seconds=int(
                config_dict.get("processing_timeout_seconds", 120)
            ),
            preserve_timestamps=str(
                config_dict.get("preserve_timestamps", "true")
            ).lower()
            == "true",
            backup_existing_files=str(
                config_dict.get("backup_existing_files", "false")
            ).lower()
            == "true",
        )

    @classmethod
    def from_env_and_dict(
        cls, config_dict: Optional[Dict[str, Union[str, int, bool]]] = None
    ) -> "Configuration":
        """Create configuration from environment variables and dictionary."""
        if config_dict is None:
            config_dict = {}

        # Environment variables override config file
        env_overrides = {
            "REVERSE_DATETREE_YEAR_FORMAT": os.getenv("ORD_PLAN_YEAR_FORMAT"),
            "REVERSE_DATETREE_WEEK_FORMAT": os.getenv("ORD_PLAN_WEEK_FORMAT"),
            "REVERSE_DATETREE_DATE_FORMAT": os.getenv("ORD_PLAN_DATE_FORMAT"),
            "default_todo_state": os.getenv("ORD_PLAN_DEFAULT_TODO_STATE"),
            "max_events_per_file": os.getenv("ORD_PLAN_MAX_EVENTS"),
            "processing_timeout_seconds": os.getenv("ORD_PLAN_TIMEOUT"),
            "preserve_timestamps": os.getenv("ORD_PLAN_PRESERVE_TIMESTAMPS"),
            "backup_existing_files": os.getenv("ORD_PLAN_BACKUP_FILES"),
        }

        # Apply environment overrides
        for key, env_value in env_overrides.items():
            if env_value is not None:
                if key in ["max_events_per_file", "processing_timeout_seconds"]:
                    config_dict[key] = int(env_value)
                elif key in ["preserve_timestamps", "backup_existing_files"]:
                    config_dict[key] = env_value.lower() in ("true", "1", "yes")
                else:
                    config_dict[key] = env_value

        return cls.from_dict(config_dict)

    def validate_date_formats(self) -> list[str]:
        """Validate date format strings.

        Returns:
            List of validation error messages
        """
        errors = []

        # Test each format string
        formats_to_test = [
            ("Year format", self.reverse_datetree_year_format),
            ("Week format", self.reverse_datetree_week_format),
            ("Date format", self.reverse_datetree_date_format),
        ]

        for format_name, format_string in formats_to_test:
            try:
                from datetime import datetime

                datetime.now().strftime(format_string)
            except ValueError as e:
                errors.append(f"{format_name} '{format_string}' is invalid: {e}")
            except Exception as e:
                errors.append(f"{format_name} '{format_string}' caused error: {e}")

        return errors

    def get_performance_limits(self) -> Dict[str, int]:
        """Get performance limit settings.

        Returns:
            Dictionary with performance limits
        """
        return {
            "max_events_per_file": self.max_events_per_file,
            "processing_timeout_seconds": self.processing_timeout_seconds,
        }
