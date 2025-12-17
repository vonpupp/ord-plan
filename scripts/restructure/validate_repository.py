"""
Repository restructuring validation utilities.

This module provides validation tools to ensure the repository
is in a clean state before restructuring operations begin.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class RepositoryValidator:
    """Validates repository state for restructuring operations."""

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize validator with repository root path."""
        self.repo_root = repo_root or Path.cwd()

    def check_git_repository(self) -> bool:
        """Check if current directory is a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def check_clean_working_directory(self) -> bool:
        """Check if git working directory is clean (no uncommitted changes)."""
        try:
            # Check for staged and unstaged changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return len(result.stdout.strip()) == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def check_ord_plan_exists(self) -> bool:
        """Check if ord-plan/ subdirectory exists."""
        ord_plan_path = self.repo_root / "ord-plan"
        return ord_plan_path.exists() and ord_plan_path.is_dir()

    def get_git_status(self) -> List[str]:
        """Get detailed git status information."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain", "-v"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip().split("\n") if result.stdout.strip() else []
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []

    def validate_repository_state(self) -> tuple[bool, List[str]]:
        """
        Validate repository is ready for restructuring.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not self.check_git_repository():
            errors.append("Not a git repository. Initialize git first.")

        if not self.check_clean_working_directory():
            errors.append(
                "Git working directory is not clean. Commit or stash changes first."
            )
            status_lines = self.get_git_status()
            if status_lines:
                errors.append("Changes found:")
                for line in status_lines[:5]:  # Show first 5 changes
                    if line.strip():
                        errors.append(f"  {line}")

        if not self.check_ord_plan_exists():
            errors.append("ord-plan/ directory not found. Cannot restructure.")

        return len(errors) == 0, errors

    def run_basic_tests(self) -> tuple[bool, List[str]]:
        """
        Run basic tests to ensure current state is functional.

        Returns:
            Tuple of (tests_pass, error_messages)
        """
        errors = []

        try:
            # Run pytest on current ord-plan/tests with correct PYTHONPATH
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.repo_root / "ord-plan" / "src")

            result = subprocess.run(
                ["python", "-m", "pytest", "ord-plan/tests/", "--tb=short"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=60,
                env=env,
            )

            if result.returncode != 0:
                errors.append(
                    "Current tests are failing. Fix tests before restructuring."
                )
                if result.stdout:
                    errors.append("Test output:")
                    errors.append(result.stdout[-500:])  # Last 500 chars
        except subprocess.TimeoutExpired:
            errors.append("Tests timed out. Check test suite.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            errors.append("Could not run pytest. Check Python environment.")

        return len(errors) == 0, errors


def main():
    """Main validation function."""
    validator = RepositoryValidator()

    print("🔍 Validating repository state for restructuring...")

    # Check repository state
    is_valid, errors = validator.validate_repository_state()

    if not is_valid:
        print("❌ Repository validation failed:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)

    print("✅ Repository state is valid")

    # Run basic tests
    print("🧪 Running basic tests...")
    tests_pass, test_errors = validator.run_basic_tests()

    if not tests_pass:
        print("❌ Tests failed:")
        for error in test_errors:
            print(f"  {error}")
        print("Fix failing tests before restructuring.")
        sys.exit(1)

    print("✅ All tests pass - repository is ready for restructuring")


if __name__ == "__main__":
    main()
