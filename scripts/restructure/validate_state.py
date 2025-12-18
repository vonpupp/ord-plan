"""
Repository state validation framework for restructuring operations.

This module provides comprehensive validation for repository state transitions
during the restructuring process.
"""

import os
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


class RepositoryState(Enum):
    """Enum representing repository states during restructuring."""

    INITIAL = "INITIAL"  # Repository in original state with ord-plan/ subdirectory
    FILES_MOVED = "FILES_MOVED"  # Files moved to root level
    REFERENCES_UPDATED = "REFERENCES_UPDATED"  # All paths and imports updated
    VALIDATED = "VALIDATED"  # All functionality verified through tests
    COMPLETED = "COMPLETED"  # Restructuring complete and functional


@dataclass
class ValidationResult:
    """Result of a validation check."""

    success: bool
    message: str
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


class RepositoryStateValidator:
    """Validates repository state transitions during restructuring."""

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize validator with repository root path."""
        self.repo_root = repo_root or Path.cwd()
        self.validation_history = []

    def detect_current_state(self) -> RepositoryState:
        """
        Detect the current repository state.

        Returns:
            Current RepositoryState
        """
        ord_plan_exists = (self.repo_root / "ord-plan").exists()
        src_at_root = (self.repo_root / "src").exists()
        tests_at_root = (self.repo_root / "tests").exists()
        pyproject_at_root = (self.repo_root / "pyproject.toml").exists()

        if ord_plan_exists and not src_at_root:
            return RepositoryState.INITIAL

        if src_at_root and tests_at_root and pyproject_at_root:
            # Check if imports have been updated
            try:
                test_file = self.repo_root / "tests" / "test_main.py"
                if test_file.exists():
                    with open(test_file) as f:
                        content = f.read()
                        if "from ord_plan." in content or "import ord_plan." in content:
                            return RepositoryState.FILES_MOVED
                        else:
                            return RepositoryState.REFERENCES_UPDATED
            except Exception:
                pass

            return RepositoryState.FILES_MOVED

        # If some files moved but not all, we're in transition
        if src_at_root or tests_at_root or pyproject_at_root:
            return RepositoryState.FILES_MOVED

        return RepositoryState.INITIAL

    def validate_state_transition(
        self, from_state: RepositoryState, to_state: RepositoryState
    ) -> ValidationResult:
        """
        Validate that a state transition is valid.

        Args:
            from_state: Current state
            to_state: Target state

        Returns:
            ValidationResult indicating if transition is valid
        """
        # Define valid transitions
        valid_transitions = {
            RepositoryState.INITIAL: [RepositoryState.FILES_MOVED],
            RepositoryState.FILES_MOVED: [
                RepositoryState.REFERENCES_UPDATED,
                RepositoryState.INITIAL,  # Can rollback
            ],
            RepositoryState.REFERENCES_UPDATED: [
                RepositoryState.VALIDATED,
                RepositoryState.FILES_MOVED,  # Can rollback
            ],
            RepositoryState.VALIDATED: [
                RepositoryState.COMPLETED,
                RepositoryState.REFERENCES_UPDATED,  # Can rollback
            ],
            RepositoryState.COMPLETED: [],  # Final state
        }

        if to_state not in valid_transitions.get(from_state, []):
            return ValidationResult(
                success=False,
                message=f"Invalid transition from {from_state.value} to {to_state.value}",
                details={
                    "from_state": from_state.value,
                    "to_state": to_state.value,
                    "valid_transitions": [
                        state.value for state in valid_transitions.get(from_state, [])
                    ],
                },
            )

        return ValidationResult(
            success=True,
            message=f"Valid transition from {from_state.value} to {to_state.value}",
        )

    def validate_file_structure(self, state: RepositoryState) -> ValidationResult:
        """
        Validate file structure for a given state.

        Args:
            state: State to validate

        Returns:
            ValidationResult
        """
        issues = []
        expected_files = []
        missing_files = []
        unexpected_files = []

        if state == RepositoryState.INITIAL:
            expected_dirs = ["ord-plan/src", "ord-plan/tests", "ord-plan/docs"]
            expected_files = [
                "ord-plan/pyproject.toml",
                "ord-plan/README.md",
                "ord-plan/LICENSE",
            ]

            for expected_dir in expected_dirs:
                if not (self.repo_root / expected_dir).exists():
                    missing_files.append(expected_dir)

            for expected_file in expected_files:
                if not (self.repo_root / expected_file).exists():
                    missing_files.append(expected_file)

            # Check that root-level directories don't exist yet
            root_dirs = ["src", "tests", "docs"]
            for root_dir in root_dirs:
                if (self.repo_root / root_dir).exists():
                    unexpected_files.append(root_dir)

        elif state in [
            RepositoryState.FILES_MOVED,
            RepositoryState.REFERENCES_UPDATED,
            RepositoryState.VALIDATED,
            RepositoryState.COMPLETED,
        ]:
            expected_dirs = ["src", "tests", "docs"]
            expected_files = ["pyproject.toml", "README.md", "LICENSE"]

            for expected_dir in expected_dirs:
                if not (self.repo_root / expected_dir).exists():
                    missing_files.append(expected_dir)

            for expected_file in expected_files:
                if not (self.repo_root / expected_file).exists():
                    missing_files.append(expected_file)

        if missing_files:
            issues.append(f"Missing files/directories: {', '.join(missing_files)}")

        if unexpected_files:
            issues.append(
                f"Unexpected files/directories: {', '.join(unexpected_files)}"
            )

        return ValidationResult(
            success=len(issues) == 0,
            message="File structure validation"
            + (" passed" if not issues else " failed"),
            details={
                "missing_files": missing_files,
                "unexpected_files": unexpected_files,
                "issues": issues,
            },
        )

    def validate_python_imports(self, state: RepositoryState) -> ValidationResult:
        """
        Validate Python import statements for a given state.

        Args:
            state: State to validate

        Returns:
            ValidationResult
        """
        issues = []
        files_with_old_imports = []

        if state in [
            RepositoryState.REFERENCES_UPDATED,
            RepositoryState.VALIDATED,
            RepositoryState.COMPLETED,
        ]:
            # Check that no ord_plan imports remain
            try:
                cmd = [
                    "find",
                    ".",
                    "-name",
                    "*.py",
                    "-exec",
                    "grep",
                    "-l",
                    "ord_plan\\.",
                    "{}",
                    "+",
                ]
                result = subprocess.run(
                    ["/usr/bin/git"] + cmd,
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0 and result.stdout.strip():
                    files_with_old_imports = [
                        f.strip() for f in result.stdout.strip().split("\n")
                    ]
                    issues.append(
                        f"Files still contain ord_plan imports: {', '.join(files_with_old_imports)}"
                    )

            except Exception as e:
                issues.append(f"Failed to check imports: {e}")

        return ValidationResult(
            success=len(issues) == 0,
            message="Python import validation"
            + (" passed" if not issues else " failed"),
            details={
                "files_with_old_imports": files_with_old_imports,
                "issues": issues,
            },
        )

    def validate_functionality(self, state: RepositoryState) -> ValidationResult:
        """
        Validate that functionality works for a given state.

        Args:
            state: State to validate

        Returns:
            ValidationResult
        """
        if state not in [RepositoryState.VALIDATED, RepositoryState.COMPLETED]:
            return ValidationResult(
                success=True,
                message="Functionality validation not required for this state",
            )

        issues = []

        # Run tests with correct PYTHONPATH
        env = os.environ.copy()
        if (self.repo_root / "src").exists():
            env["PYTHONPATH"] = str(self.repo_root / "src")
        else:
            env["PYTHONPATH"] = str(self.repo_root / "ord-plan" / "src")

        try:
            result = subprocess.run(
                ["/usr/bin/git"] + ["python", "-m", "pytest", "tests/", "--tb=short"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=60,
                env=env,
            )

            if result.returncode != 0:
                issues.append("Tests are failing")
                if result.stdout:
                    issues.append(f"Test output: {result.stdout[-200:]}")

        except subprocess.TimeoutExpired:
            issues.append("Tests timed out")
        except Exception as e:
            issues.append(f"Failed to run tests: {e}")

        # Try running linting
        try:
            result = subprocess.run(
                ["/usr/bin/git"] + ["ruff", "check", "."],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                issues.append("Linting issues found")

        except Exception:
            # Ruff might not be available or configured
            pass

        return ValidationResult(
            success=len(issues) == 0,
            message="Functionality validation"
            + (" passed" if not issues else " failed"),
            details={"issues": issues},
        )

    def validate_complete_state(
        self, target_state: RepositoryState
    ) -> List[ValidationResult]:
        """
        Perform comprehensive validation for a target state.

        Args:
            target_state: State to validate

        Returns:
            List of ValidationResult objects
        """
        results = []

        # Detect current state
        current_state = self.detect_current_state()

        # Skip transition validation if current state matches target state
        if current_state != target_state:
            transition_result = self.validate_state_transition(
                current_state, target_state
            )
            results.append(transition_result)

            if not transition_result.success:
                return results

        # Validate file structure
        structure_result = self.validate_file_structure(target_state)
        results.append(structure_result)

        # Validate imports (for states that require it)
        if target_state in [
            RepositoryState.REFERENCES_UPDATED,
            RepositoryState.VALIDATED,
            RepositoryState.COMPLETED,
        ]:
            import_result = self.validate_python_imports(target_state)
            results.append(import_result)

        # Validate functionality (for states that require it)
        if target_state in [RepositoryState.VALIDATED, RepositoryState.COMPLETED]:
            func_result = self.validate_functionality(target_state)
            results.append(func_result)

        # Store validation history
        self.validation_history.append(
            {
                "timestamp": str(
                    subprocess.run(
                        ["/usr/bin/git"] + ["date"], capture_output=True, text=True
                    ).stdout.strip()
                ),
                "current_state": current_state.value,
                "target_state": target_state.value,
                "results": results,
            }
        )

        return results

    def generate_validation_report(self, results: List[ValidationResult]) -> str:
        """
        Generate a human-readable validation report.

        Args:
            results: List of ValidationResult objects

        Returns:
            Formatted report string
        """
        report = []
        report.append("🔍 Repository Validation Report")
        report.append("=" * 50)

        all_passed = all(result.success for result in results)

        for i, result in enumerate(results, 1):
            status = "✅ PASS" if result.success else "❌ FAIL"
            report.append(f"{i}. {result.message}: {status}")

            if not result.success and result.details:
                for _, value in result.details.items():
                    if value:
                        if isinstance(value, list):
                            for item in value:
                                report.append(f"   - {item}")
                        else:
                            report.append(f"   - {value}")

        report.append("=" * 50)
        if all_passed:
            report.append("🎉 All validations passed!")
        else:
            report.append(
                "⚠️  Some validations failed. Please address the issues above."
            )

        return "\n".join(report)


def main():
    """Test repository state validation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate repository state during restructuring"
    )
    parser.add_argument(
        "--target-state",
        choices=[state.value for state in RepositoryState],
        help="Target state to validate against",
    )
    parser.add_argument(
        "--detect", action="store_true", help="Only detect current state"
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    validator = RepositoryStateValidator()

    if args.detect:
        current_state = validator.detect_current_state()
        print(f"📍 Current repository state: {current_state.value}")
        return

    if not args.target_state:
        # Validate current detected state
        current_state = validator.detect_current_state()
        target_state = current_state
    else:
        target_state = RepositoryState(args.target_state)

    print(f"🔍 Validating repository state: {target_state.value}")

    results = validator.validate_complete_state(target_state)
    report = validator.generate_validation_report(results)
    print("\n" + report)

    # Exit with appropriate code
    if any(not result.success for result in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
