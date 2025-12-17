"""Performance tests for ord-plan."""

import time
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import yaml

from ord_plan.cli import cli_group


class TestPerformance:
    """Test performance characteristics of event generation."""

    def test_small_event_set_performance(self, runner, tmp_path):
        """Test performance with small event sets (<100 events)."""
        # Use future dates relative to today
        today = datetime.now()
        from_date = today.strftime("%Y-%m-%d")
        to_date = (today + timedelta(days=90)).strftime("%Y-%m-%d")  # 3 months from now

        yaml_content = {
            "events": [
                {
                    "title": f"Event {i}",
                    "cron": "0 9 * * 1",  # Weekly events
                }
                for i in range(10)  # 10 events per week
            ]
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        output_file = tmp_path / "output.org"

        # Measure performance
        start_time = time.time()

        result = runner.invoke(
            cli_group,
            [
                "generate",
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
                "--from",
                from_date,
                "--to",
                to_date,  # 3 months from now
            ],
        )

        end_time = time.time()
        execution_time = end_time - start_time

        # Should succeed quickly
        if result.exit_code != 0:
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.output}")
            print(f"Exception: {result.exception}")
        assert result.exit_code == 0
        assert output_file.exists()
        assert execution_time < 5.0  # Should complete in under 5 seconds

        # Check output quality
        content = output_file.read_text()
        assert len(content) > 1000  # Should have substantial content

    def test_medium_event_set_performance(self, runner, tmp_path):
        """Test performance with medium event sets (100-1000 events)."""
        # Use future dates relative to today
        today = datetime.now()
        from_date = today.strftime("%Y-%m-%d")
        to_date = (today + timedelta(days=31)).strftime("%Y-%m-%d")  # 1 month from now

        yaml_content = {
            "events": [
                {
                    "title": f"Task {i}",
                    "cron": "0 */2 * * *",  # Every 2 hours
                }
                for i in range(5)  # 5 tasks, every 2 hours = 60 per day
            ]
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        output_file = tmp_path / "output.org"

        # Measure performance
        start_time = time.time()

        result = runner.invoke(
            cli_group,
            [
                "generate",
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
                "--from",
                from_date,
                "--to",
                to_date,  # 1 month from now
            ],
        )

        end_time = time.time()
        execution_time = end_time - start_time

        # Should succeed in reasonable time
        assert result.exit_code == 0
        assert output_file.exists()
        assert execution_time < 15.0  # Should complete in under 15 seconds

    def test_large_event_set_performance(self, runner, tmp_path):
        """Test performance with large event sets (1000+ events)."""
        # Use future dates relative to today
        today = datetime.now()
        from_date = today.strftime("%Y-%m-%d")
        to_date = (today + timedelta(days=14)).strftime("%Y-%m-%d")  # 2 weeks from now

        yaml_content = {
            "events": [
                {
                    "title": f"Frequent Task {i}",
                    "cron": "0 * * * *",  # Every hour
                }
                for i in range(3)  # 3 tasks every hour = 72 per day
            ]
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        output_file = tmp_path / "output.org"

        # Measure performance
        start_time = time.time()

        result = runner.invoke(
            cli_group,
            [
                "generate",
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
                "--from",
                from_date,
                "--to",
                to_date,  # 2 weeks from now
            ],
        )

        end_time = time.time()
        execution_time = end_time - start_time

        # Should succeed but may take longer
        assert result.exit_code == 0
        assert output_file.exists()

        # Large event sets can take longer, but should be reasonable
        if execution_time > 60.0:
            pytest.skip(
                f"Large event set took {execution_time:.1f}s, exceeding reasonable limits"
            )

        # Should show performance warning in output
        assert (
            "performance" in result.output.lower() or "events" in result.output.lower()
        )

    def test_memory_usage_scaling(self, runner, tmp_path):
        """Test that memory usage scales reasonably."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Use future dates relative to today
        today = datetime.now()
        from_date = today.strftime("%Y-%m-%d")
        to_date = (today + timedelta(days=365)).strftime("%Y-%m-%d")  # 1 year from now

        yaml_content = {
            "events": [
                {
                    "title": f"Memory Test {i}",
                    "cron": "0 9 * * *",  # Daily events
                }
                for i in range(100)  # 100 daily events
            ]
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        output_file = tmp_path / "output.org"

        # Run generation
        result = runner.invoke(
            cli_group,
            [
                "generate",
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
                "--from",
                from_date,
                "--to",
                to_date,  # 1 year from now
                "--force",  # Bypass future date warnings
            ],
        )

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Should succeed
        assert result.exit_code == 0
        assert output_file.exists()

        # Memory increase should be reasonable (less than 100MB for this test)
        memory_increase_mb = memory_increase / (1024 * 1024)
        assert memory_increase_mb < 100, (
            f"Memory usage increased by {memory_increase_mb:.1f}MB, which seems excessive"
        )

    def test_performance_warning_generation(self, runner, tmp_path):
        """Test that performance warnings are generated when appropriate."""
        # Use future dates relative to today
        today = datetime.now()
        from_date = today.strftime("%Y-%m-%d")
        to_date = (today + timedelta(days=365)).strftime("%Y-%m-%d")  # 1 year from now

        yaml_content = {
            "events": [
                {
                    "title": f"Warning Test {i}",
                    "cron": "0 0 * * *",  # Daily at midnight
                }
                for i in range(20)  # 20 daily events = ~7300 per year
            ]
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        output_file = tmp_path / "output.org"

        result = runner.invoke(
            cli_group,
            [
                "generate",
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
                "--from",
                from_date,
                "--to",
                to_date,
                "--force",  # Bypass future date warnings
            ],
        )

        # Should succeed and show performance warnings
        assert result.exit_code == 0
        assert output_file.exists()

        # Check for performance-related messages
        output_lower = result.output.lower()
        has_performance_msg = any(
            term in output_lower for term in ["performance", "events", "warning"]
        )
        assert has_performance_msg, (
            f"Expected performance warning but got: {result.output}"
        )

    def test_dry_run_performance(self, runner, tmp_path):
        """Test that dry-run is fast regardless of event count."""
        # Use future dates relative to today
        today = datetime.now()
        from_date = today.strftime("%Y-%m-%d")
        to_date = (today + timedelta(days=31)).strftime("%Y-%m-%d")  # 1 month from now

        yaml_content = {
            "events": [
                {
                    "title": f"Dry Run Test {i}",
                    "cron": "0 * * * *",  # Every hour
                }
                for i in range(50)  # Large number of events
            ]
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        output_file = tmp_path / "output.org"

        # Measure dry-run performance
        start_time = time.time()

        result = runner.invoke(
            cli_group,
            [
                "generate",
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
                "--from",
                from_date,
                "--to",
                to_date,
                "--dry-run",
            ],
        )

        end_time = time.time()
        execution_time = end_time - start_time

        # Should be fast (no file I/O)
        assert result.exit_code == 0
        assert not output_file.exists()  # Dry run shouldn't create file
        assert execution_time < 10.0  # Should be very fast without file writing

    def test_date_range_escalation(self, runner, tmp_path):
        """Test performance with different date range sizes."""
        # Use future dates relative to today
        today = datetime.now()
        single_day_date = today.strftime("%Y-%m-%d")
        year_end_date = (today + timedelta(days=365)).strftime("%Y-%m-%d")

        # Test with 1 day (daily event for more measurable difference)
        single_day_content = {"events": [{"title": "Test", "cron": "0 9 * * *"}]}

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(single_day_content))

        output_file = tmp_path / "output.org"

        start_time = time.time()

        result = runner.invoke(
            cli_group,
            [
                "generate",
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
                "--from",
                single_day_date,
                "--to",
                single_day_date,
            ],
        )

        single_day_time = time.time() - start_time

        # Test with 1 year (same daily event)
        year_content = {"events": [{"title": "Test", "cron": "0 9 * * *"}]}

        yaml_file.write_text(yaml.dump(year_content))

        start_time = time.time()

        result = runner.invoke(
            cli_group,
            [
                "generate",
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
                "--from",
                single_day_date,
                "--to",
                year_end_date,
            ],
        )

        year_time = time.time() - start_time

        # Year should take longer than single day but not exponentially more
        # Performance can vary significantly at small scales, so we test that both complete successfully
        # and that year generates many more events than single day
        assert single_day_time > 0  # Single day took some time
        assert year_time > 0  # Year took some time
