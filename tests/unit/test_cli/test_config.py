"""Unit tests for Configuration merge_format_config."""

from ord_plan.cli.config import Configuration


class TestMergeFormatConfig:
    """Test format configuration merging functionality."""

    def test_merge_format_only(self) -> None:
        """Test merging with only format config."""
        format_config = {
            "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
            "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
            "REVERSE_DATETREE_USE_WEEK_TREE": True,
        }

        config = Configuration.merge_format_config(format_config=format_config)

        assert config.reverse_datetree_week_format == "%Y-W%V"
        assert config.reverse_datetree_date_format == "%Y-%m-%d %a"
        assert config.reverse_datetree_year_format == "%Y"
        assert config.default_todo_state == "TODO"  # Default value

    def test_merge_rules_only(self) -> None:
        """Test merging with only rules config."""
        rules_config = {
            "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
            "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
            "REVERSE_DATETREE_USE_WEEK_TREE": True,
        }

        config = Configuration.merge_format_config(rules_config=rules_config)

        assert config.reverse_datetree_week_format == "%Y-W%V"
        assert config.reverse_datetree_date_format == "%Y-%m-%d %a"
        assert config.reverse_datetree_year_format == "%Y"

    def test_merge_format_overrides_rules(self) -> None:
        """Test that format config overrides rules config."""
        rules_config = {
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d",
            "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
            "REVERSE_DATETREE_USE_WEEK_TREE": True,
        }

        format_config = {
            "REVERSE_DATETREE_DATE_FORMAT": "%d/%m/%Y",
        }

        config = Configuration.merge_format_config(
            rules_config=rules_config, format_config=format_config
        )

        # Format config value should be used
        assert config.reverse_datetree_date_format == "%d/%m/%Y"

        # Rules config values should be used for other fields
        assert config.reverse_datetree_week_format == "%Y-W%V"
        assert config.reverse_datetree_year_format == "%Y"

    def test_merge_both_empty(self) -> None:
        """Test merging with both configs empty (uses defaults)."""
        config = Configuration.merge_format_config()

        assert config.reverse_datetree_week_format == "%Y-W%V"  # Default
        assert config.reverse_datetree_date_format == "%Y-%m-%d %a"  # Default
        assert config.reverse_datetree_year_format == "%Y"  # Default

    def test_merge_format_partial(self) -> None:
        """Test merging with partial format config."""
        rules_config = {
            "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d",
            "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
            "REVERSE_DATETREE_USE_WEEK_TREE": True,
        }

        format_config = {
            "REVERSE_DATETREE_DATE_FORMAT": "%d/%m/%Y",
        }

        config = Configuration.merge_format_config(
            rules_config=rules_config, format_config=format_config
        )

        # Format config overrides date format
        assert config.reverse_datetree_date_format == "%d/%m/%Y"
        # Rules config provides other values
        assert config.reverse_datetree_week_format == "%Y-W%V"
        assert config.reverse_datetree_year_format == "%Y"

    def test_merge_rules_partial(self) -> None:
        """Test merging with partial rules config."""
        rules_config = {
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d",
        }

        format_config = {}

        config = Configuration.merge_format_config(
            rules_config=rules_config, format_config=format_config
        )

        # Rules config provides date format
        assert config.reverse_datetree_date_format == "%Y-%m-%d"
        # Defaults for other values
        assert config.reverse_datetree_week_format == "%Y-W%V"
        assert config.reverse_datetree_year_format == "%Y"

    def test_precedence_format_over_rules(self) -> None:
        """Test that format file has highest precedence."""
        rules_config = {
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d",
            "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
            "REVERSE_DATETREE_USE_WEEK_TREE": True,
        }

        format_config = {
            "REVERSE_DATETREE_DATE_FORMAT": "%d/%m/%Y",
        }

        config = Configuration.merge_format_config(
            rules_config=rules_config, format_config=format_config
        )

        # Format config value should override rules config
        assert config.reverse_datetree_date_format == "%d/%m/%Y"
        # Rules config values should be used for other fields
        assert config.reverse_datetree_week_format == "%Y-W%V"
        assert config.reverse_datetree_year_format == "%Y"

    def test_precedence_order(self) -> None:
        """Test precedence order: format > rules > defaults."""
        rules_config = {
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d",
        }

        format_config = {}

        config = Configuration.merge_format_config(
            rules_config=rules_config, format_config=format_config
        )

        # Rules config value should be used
        assert config.reverse_datetree_date_format == "%Y-%m-%d"

        # Now add format config to override
        format_config_override = {
            "REVERSE_DATETREE_DATE_FORMAT": "%d/%m/%Y",
        }

        config_override = Configuration.merge_format_config(
            rules_config=rules_config, format_config=format_config_override
        )

        # Format config should override rules config
        assert config_override.reverse_datetree_date_format == "%d/%m/%Y"
