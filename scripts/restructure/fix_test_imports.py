#!/usr/bin/env python3
"""Fix test imports to use proper ord_plan package structure."""

import re
from pathlib import Path


def fix_test_imports():
    """Fix imports in test files to use ord_plan package."""
    test_files = [
        "tests/unit/test_file_service.py",
        "tests/unit/test_validators.py",
        "tests/unit/test_date_protection_unit.py",
        "tests/unit/test_date_service.py",
        "tests/contract/test_generate_command.py",
        "tests/integration/test_date_ranges.py",
        "tests/integration/test_file_preservation.py",
        "tests/integration/test_date_protection.py",
        "tests/integration/test_performance.py",
        "tests/integration/test_error_handling.py",
    ]

    for test_file in test_files:
        file_path = Path(test_file)
        if not file_path.exists():
            continue

        print(f"Fixing imports in {test_file}")

        with open(file_path) as f:
            content = f.read()

        # Fix imports to use ord_plan package
        original_content = content

        # Pattern 1: "from cli import" -> "from ord_plan.cli import"
        content = re.sub(
            r"^from cli import", "from ord_plan.cli import", content, flags=re.MULTILINE
        )

        # Pattern 2: "from models import" -> "from ord_plan.models import"
        content = re.sub(
            r"^from models import",
            "from ord_plan.models import",
            content,
            flags=re.MULTILINE,
        )

        # Pattern 3: "from services import" -> "from ord_plan.services import"
        content = re.sub(
            r"^from services import",
            "from ord_plan.services import",
            content,
            flags=re.MULTILINE,
        )

        # Pattern 4: "from utils import" -> "from ord_plan.utils import"
        content = re.sub(
            r"^from utils import",
            "from ord_plan.utils import",
            content,
            flags=re.MULTILINE,
        )

        if content != original_content:
            with open(file_path, "w") as f:
                f.write(content)
            print(f"  ✅ Fixed imports in {test_file}")
        else:
            print(f"  ℹ️  No changes needed in {test_file}")


if __name__ == "__main__":
    fix_test_imports()
