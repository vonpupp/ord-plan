"""Comprehensive validation script for reference updates.

This script validates that all reference updates were successful
and repository is in a consistent state after User Story 2.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from update_imports import ImportUpdater  # noqa: E402
from validate_state import (  # noqa: E402
    RepositoryState,
    RepositoryStateValidator,
)


def validate_python_imports():
    """Validate that Python imports were correctly updated."""
    print("🔍 Validating Python import updates...")

    repo_root = Path.cwd()
    updater = ImportUpdater(repo_root, dry_run=True)

    remaining_issues, issue_files = updater.verify_updates()

    if remaining_issues == 0:
        print("✅ All Python imports correctly updated")
        return True
    else:
        print(f"❌ Found {remaining_issues} files with remaining ord_plan imports:")
        for file_path in issue_files:
            print(f"  📄 {file_path}")
        return False


def validate_repository_state():
    """Validate that repository is in REFERENCES_UPDATED state."""
    print("\n🔍 Validating repository state...")

    validator = RepositoryStateValidator()
    current_state = validator.detect_current_state()
    print(f"📍 Current state: {current_state.value}")

    # Validate against REFERENCES_UPDATED state
    results = validator.validate_complete_state(RepositoryState.REFERENCES_UPDATED)

    success_count = sum(1 for result in results if result.success)
    total_count = len(results)

    print(f"📊 State Validation: {success_count}/{total_count} passed")

    all_passed = all(result.success for result in results)
    if all_passed:
        print("✅ Repository state validation passed")
    else:
        print("❌ Repository state validation failed:")
        for result in results:
            if not result.success:
                print(f"  ❌ {result.message}")

    return all_passed


def validate_functionality():
    """Validate that basic functionality works after reference updates."""
    print("\n🔍 Validating functionality...")

    repo_root = Path.cwd()

    try:
        import os
        import subprocess

        # Set correct PYTHONPATH for new structure
        env = os.environ.copy()
        env["PYTHONPATH"] = str(repo_root / "src")

        # Test that tests can run with new import structure
        result = subprocess.run(
            ["/usr/bin/git"]
            + [
                "python",
                "-m",
                "pytest",
                "tests/test_main.py",
                "-k",
                "test_main_succeeds",
                "-v",
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )

        if result.returncode == 0:
            print("✅ Import functionality test passed")
            return True
        else:
            print(f"❌ Import functionality test failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False


def validate_configuration_files():
    """Validate that configuration files don't contain ord-plan references."""
    print("\n🔍 Validating configuration files...")

    repo_root = Path.cwd()
    config_files = [
        "pyproject.toml",
        ".github/workflows/tests.yml",
        ".github/workflows/release.yml",
    ]

    issues = []

    for config_file in config_files:
        file_path = repo_root / config_file
        if file_path.exists():
            try:
                with open(file_path) as f:
                    content = f.read()

                # Check for ord-plan path references (not package name or URLs)
                lines = content.split("\n")
                for line in lines:
                    # Skip lines that are package metadata or URLs
                    if any(
                        keyword in line
                        for keyword in [
                            "name = ",
                            "homepage = ",
                            "repository = ",
                            "documentation = ",
                        ]
                    ):
                        continue
                    # Check for actual path references
                    if "ord-plan/" in line and "://" not in line:
                        issues.append(
                            f"{config_file} contains ord-plan/ path references"
                        )
                        break

            except Exception as e:
                issues.append(f"Could not read {config_file}: {e}")

    if not issues:
        print("✅ Configuration files validation passed")
        return True
    else:
        print("❌ Configuration files validation failed:")
        for issue in issues:
            print(f"  ❌ {issue}")
        return False


def validate_documentation():
    """Validate that documentation references are correct."""
    print("\n🔍 Validating documentation...")

    repo_root = Path.cwd()
    doc_files = ["README.md", "CONTRIBUTING.md", "docs/index.md", "docs/usage.md"]

    issues = []

    for doc_file in doc_files:
        file_path = repo_root / doc_file
        if file_path.exists():
            try:
                with open(file_path) as f:
                    content = f.read()

                # Check for ord-plan path references
                if "ord-plan/" in content:
                    issues.append(f"{doc_file} contains ord-plan/ path references")

            except Exception as e:
                issues.append(f"Could not read {doc_file}: {e}")

    if not issues:
        print("✅ Documentation validation passed")
        return True
    else:
        print("❌ Documentation validation failed:")
        for issue in issues:
            print(f"  ❌ {issue}")
        return False


def main():
    """Run the main validation function for User Story 2 completion."""
    print("🚀 Starting comprehensive reference update validation...")

    # Run all validation checks
    imports_ok = validate_python_imports()
    state_ok = validate_repository_state()
    func_ok = validate_functionality()
    config_ok = validate_configuration_files()
    docs_ok = validate_documentation()

    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE VALIDATION SUMMARY")
    print("=" * 60)

    print(f"Python Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Repository State: {'✅ PASS' if state_ok else '❌ FAIL'}")
    print(f"Functionality: {'✅ PASS' if func_ok else '❌ FAIL'}")
    print(f"Configuration Files: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Documentation: {'✅ PASS' if docs_ok else '❌ FAIL'}")

    overall_success = all([imports_ok, state_ok, func_ok, config_ok, docs_ok])
    status_msg = (
        "🎉 ALL VALIDATIONS PASSED" if overall_success else "⚠️  SOME VALIDATIONS FAILED"
    )
    print(f"\nOverall Status: {status_msg}")

    if overall_success:
        print("\n✅ User Story 2 (Reference Updates) completed successfully!")
        print("📋 Summary of changes:")
        print("   - Updated Python import statements to remove ord_plan prefix")
        print("   - Updated pyproject.toml path references")
        print("   - Updated documentation cross-references")
        print("   - All repository references now work with new structure")
        print("\n🎯 Repository ready for User Story 3 (Workflow Validation)")
    else:
        print("\n❌ Validation failed. Please address issues before proceeding.")
        sys.exit(1)


if __name__ == "__main__":
    main()
