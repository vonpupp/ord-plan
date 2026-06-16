"""Validation script to verify file movements were successful.

This script validates that all expected files and directories
have been moved from ord-plan/ to repository root.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from validate_state import (  # noqa: E402
    RepositoryState,
    RepositoryStateValidator,
)


def validate_file_moves():
    """Validate that all files were moved correctly."""
    repo_root = Path.cwd()

    print("🔍 Validating file movements...")

    # Check that key directories exist at root
    required_dirs = ["src", "tests", "docs", ".github"]
    for dir_name in required_dirs:
        dir_path = repo_root / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/ exists at repository root")
        else:
            print(f"❌ {dir_name}/ missing from repository root")
            return False

    # Check that key files exist at root
    required_files = [
        "README.md",
        "LICENSE",
        "pyproject.toml",
        "AGENTS.md",
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
        "noxfile.py",
        "conftest.py",
    ]
    for file_name in required_files:
        file_path = repo_root / file_name
        if file_path.exists():
            print(f"✅ {file_name} exists at repository root")
        else:
            print(f"❌ {file_name} missing from repository root")

    # Check that src/ord_plan structure is intact
    cli_path = repo_root / "src/ord_plan/cli"
    models_path = repo_root / "src/ord_plan/models"
    parsers_path = repo_root / "src/ord_plan/parsers"
    services_path = repo_root / "src/ord_plan/services"
    utils_path = repo_root / "src/ord_plan/utils"

    for subdir in [cli_path, models_path, parsers_path, services_path, utils_path]:
        if subdir.exists():
            print(f"✅ src/ord_plan/{subdir.name}/ exists")
        else:
            print(f"❌ src/ord_plan/{subdir.name}/ missing")
            return False

    # Check that tests structure is intact
    test_dirs = ["tests/contract", "tests/integration", "tests/unit", "tests/fixtures"]
    for test_dir in test_dirs:
        dir_path = repo_root / test_dir
        if dir_path.exists():
            print(f"✅ {test_dir}/ exists")
        else:
            print(f"❌ {test_dir}/ missing")
            return False

    # Check that .github workflows were moved
    workflows_dir = repo_root / ".github/workflows"
    if workflows_dir.exists():
        workflow_files = list(workflows_dir.glob("*.yml"))
        print(f"✅ .github/workflows/ contains {len(workflow_files)} workflow files")
    else:
        print("❌ .github/workflows/ missing")
        return False

    return True


def validate_repository_state():
    """Validate current repository state using state validator."""
    print("\n🔍 Validating repository state...")

    validator = RepositoryStateValidator()
    current_state = validator.detect_current_state()
    print(f"📍 Current state: {current_state.value}")

    # Validate structure for FILES_MOVED state
    results = validator.validate_complete_state(RepositoryState.FILES_MOVED)

    success_count = sum(1 for result in results if result.success)
    total_count = len(results)

    print(f"\n📊 Validation Results: {success_count}/{total_count} passed")

    for result in results:
        status = "✅" if result.success else "❌"
        print(f"  {status} {result.message}")

        if not result.success and result.details:
            for key, value in result.details.items():
                if value:
                    print(f"    {key}: {value}")

    return all(result.success for result in results)


def validate_basic_functionality():
    """Validate basic functionality still works."""
    print("\n🔍 Validating basic functionality...")

    repo_root = Path.cwd()

    # Try importing the main module
    try:
        import sys

        sys.path.insert(0, str(repo_root / "src"))

        print("✅ Can import ord_plan.cli")

        print("✅ Can import ord_plan.models")

        print("✅ Can import ord_plan.services")

        print("✅ Can import ord_plan.utils")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    # Check that main script exists
    main_script = repo_root / "src" / "ord_plan" / "__main__.py"
    if main_script.exists():
        print("✅ __main__.py exists")
    else:
        print("❌ __main__.py missing")
        return False

    return True


def main():
    """Run the main validation function."""
    print("🚀 Starting comprehensive file movement validation...")

    # Validate file moves
    files_ok = validate_file_moves()

    # Validate repository state
    state_ok = validate_repository_state()

    # Validate basic functionality
    func_ok = validate_basic_functionality()

    print("\n" + "=" * 50)
    print("📊 FINAL VALIDATION SUMMARY")
    print("=" * 50)

    print(f"File Movements: {'✅ PASS' if files_ok else '❌ FAIL'}")
    print(f"Repository State: {'✅ PASS' if state_ok else '❌ FAIL'}")
    print(f"Basic Functionality: {'✅ PASS' if func_ok else '❌ FAIL'}")

    overall_success = files_ok and state_ok and func_ok
    status_msg = (
        "🎉 ALL VALIDATIONS PASSED" if overall_success else "⚠️  SOME VALIDATIONS FAILED"
    )
    print(f"\nOverall Status: {status_msg}")

    if overall_success:
        print("\n✅ User Story 1 (File Movements) completed successfully!")
        print("📋 Next steps:")
        print("   1. Review changes with 'git status' and 'git diff'")
        print("   2. Commit the file movements")
        print("   3. Proceed with User Story 2 (Reference Updates)")
    else:
        print("\n❌ Validation failed. Please address issues before proceeding.")
        sys.exit(1)


if __name__ == "__main__":
    main()
