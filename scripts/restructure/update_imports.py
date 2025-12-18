"""Import statement parsing and update utilities for Python code.

This module provides specialized tools for analyzing and updating Python
import statements during repository restructuring.
"""

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple


class ImportInfo(NamedTuple):
    """Information about a Python import statement."""

    module_name: str
    alias: Optional[str]
    lineno: int
    col_offset: int
    import_type: str  # 'import' or 'from'
    from_module: Optional[str] = None


@dataclass
class ImportUpdate:
    """Represents an import update to be made."""

    file_path: Path
    original_import: str
    updated_import: str
    lineno: int
    reason: str


class ImportParser:
    """Parses and analyzes Python import statements."""

    def __init__(self, target_prefix: str = "ord_plan"):
        """Initialize parser with target prefix to remove."""
        self.target_prefix = target_prefix

    def parse_file_imports(self, file_path: Path) -> List[ImportInfo]:
        """Parse all import statements from a Python file.

        Args:
            file_path: Path to Python file

        Returns:
            List of ImportInfo objects
        """
        imports = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST to extract imports
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(
                            ImportInfo(
                                module_name=alias.name,
                                alias=alias.asname,
                                lineno=node.lineno,
                                col_offset=node.col_offset,
                                import_type="import",
                            )
                        )

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(
                            ImportInfo(
                                module_name=node.module,
                                alias=None,
                                lineno=node.lineno,
                                col_offset=node.col_offset,
                                import_type="from",
                                from_module=node.module,
                            )
                        )

        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"⚠️  Could not parse {file_path}: {e}")

        return imports

    def find_target_imports(self, imports: List[ImportInfo]) -> List[ImportInfo]:
        """Find imports that need updating (those with target prefix).

        Args:
            imports: List of ImportInfo objects

        Returns:
            List of ImportInfo objects that need updating
        """
        target_imports = []

        for imp in imports:
            if imp.import_type == "import":
                # Check for 'import ord_plan.module' or
                # 'import ord_plan.module as alias'
                if imp.module_name.startswith(f"{self.target_prefix}."):
                    target_imports.append(imp)

            elif imp.import_type == "from":
                # Check for 'from ord_plan.module import ...'
                if imp.from_module and imp.from_module.startswith(
                    f"{self.target_prefix}."
                ):
                    target_imports.append(imp)

        return target_imports

    def generate_updated_import(self, imp: ImportInfo) -> str:
        """Generate the updated import statement without target prefix.

        Args:
            imp: ImportInfo object

        Returns:
            Updated import string
        """
        if imp.import_type == "import":
            # Remove ord_plan. prefix
            new_module = imp.module_name.replace(f"{self.target_prefix}.", "", 1)

            if imp.alias:
                return f"import {new_module} as {imp.alias}"
            else:
                return f"import {new_module}"

        elif imp.import_type == "from":
            # Remove ord_plan. prefix from from module
            new_from_module = imp.from_module.replace(f"{self.target_prefix}.", "", 1)
            return f"from {new_from_module} import"

        return ""  # Should not reach here


class ImportUpdater:
    """Updates Python import statements in files."""

    def __init__(
        self, repo_root: Path, target_prefix: str = "ord_plan", dry_run: bool = False
    ):
        """Initialize updater with repository root and settings."""
        self.repo_root = repo_root
        self.parser = ImportParser(target_prefix)
        self.dry_run = dry_run
        self.updates = []

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the repository.

        Returns:
            List of Python file paths
        """
        python_files = []

        for pattern in ["**/*.py"]:
            for file_path in self.repo_root.glob(pattern):
                # Skip files in certain directories
                relative_path = file_path.relative_to(self.repo_root)
                skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv"}

                if any(part in skip_dirs for part in relative_path.parts):
                    continue

                # Skip our own scripts during the update process
                if "scripts/restructure" in str(relative_path):
                    continue

                python_files.append(file_path)

        return python_files

    def analyze_file(self, file_path: Path) -> List[ImportUpdate]:
        """Analyze a Python file and determine what imports need updating.

        Args:
            file_path: Path to Python file

        Returns:
            List of ImportUpdate objects
        """
        updates = []

        # Parse all imports
        imports = self.parser.parse_file_imports(file_path)

        # Find target imports that need updating
        target_imports = self.parser.find_target_imports(imports)

        # Generate updates for each target import
        for imp in target_imports:
            original_line = self._get_original_line(file_path, imp.lineno)
            updated_import = self.parser.generate_updated_import(imp)

            # Generate complete updated line
            updated_line = original_line
            if imp.import_type == "import":
                updated_line = re.sub(
                    rf"import\s+{re.escape(imp.module_name)}(\s+as\s+\w+)?",
                    f"import {updated_import.split(' ', 1)[1]}",
                    original_line,
                )
            elif imp.import_type == "from":
                updated_line = re.sub(
                    rf"from\s+{re.escape(imp.from_module)}\s+import",
                    f"from {updated_import.split(' ', 2)[1]} import",
                    original_line,
                )

            updates.append(
                ImportUpdate(
                    file_path=file_path,
                    original_import=original_line.strip(),
                    updated_import=updated_line.strip(),
                    lineno=imp.lineno,
                    reason=f"Remove {self.parser.target_prefix}. prefix",
                )
            )

        return updates

    def _get_original_line(self, file_path: Path, lineno: int) -> str:
        """Get the original line from file at given line number."""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
                if 1 <= lineno <= len(lines):
                    return lines[lineno - 1]
        except Exception:
            pass
        return ""

    def update_file(self, file_path: Path, updates: List[ImportUpdate]) -> bool:
        """Apply import updates to a file.

        Args:
            file_path: Path to file to update
            updates: List of ImportUpdate objects to apply

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            # Apply updates (work backwards to avoid line number issues)
            for update in sorted(updates, key=lambda u: u.lineno, reverse=True):
                if 1 <= update.lineno <= len(lines):
                    lines[update.lineno - 1] = update.updated_import + "\n"

            if not self.dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)

            return True

        except Exception as e:
            print(f"❌ Failed to update {file_path}: {e}")
            return False

    def update_all_files(self) -> Tuple[int, List[str]]:
        """Update all Python files in the repository.

        Returns:
            Tuple of (number_of_files_updated, list_of_errors)
        """
        python_files = self.find_python_files()
        files_updated = 0
        errors = []

        print(f"📁 Found {len(python_files)} Python files to analyze")

        for file_path in python_files:
            relative_path = file_path.relative_to(self.repo_root)
            print(f"\n📄 Analyzing {relative_path}")

            # Analyze file for needed updates
            updates = self.analyze_file(file_path)

            if updates:
                print(f"  🔄 Found {len(updates)} imports to update:")
                for update in updates:
                    print(
                        f"    Line {update.lineno}: {update.original_import} → "
                        f"{update.updated_import}"
                    )

                # Apply updates
                if self.dry_run:
                    print(f"  💡 DRY RUN: Would update {relative_path}")
                    files_updated += 1
                else:
                    success = self.update_file(file_path, updates)
                    if success:
                        print(f"  ✅ Updated {relative_path}")
                        files_updated += 1
                        self.updates.extend(updates)
                    else:
                        errors.append(f"Failed to update {relative_path}")
            else:
                print("  ℹ️  No import updates needed")

        return files_updated, errors

    def get_update_summary(self) -> Dict[str, int]:
        """Get summary of all updates performed."""
        summary = {
            "files_updated": len({update.file_path for update in self.updates}),
            "total_updates": len(self.updates),
            "import_updates": len(
                [u for u in self.updates if "import" in u.original_import]
            ),
            "from_import_updates": len(
                [u for u in self.updates if "from" in u.original_import]
            ),
        }
        return summary

    def verify_updates(self) -> Tuple[int, List[str]]:
        """Verify that all imports were correctly updated.

        Returns:
            Tuple of (number_of_remaining_issues, list_of_issue_files)
        """
        python_files = self.find_python_files()
        remaining_issues = []

        for file_path in python_files:
            imports = self.parser.parse_file_imports(file_path)
            target_imports = self.parser.find_target_imports(imports)

            if target_imports:
                relative_path = file_path.relative_to(self.repo_root)
                remaining_issues.append(str(relative_path))
                print(
                    f"⚠️  {relative_path} still has {len(target_imports)} "
                    f"ord_plan imports"
                )

        return len(remaining_issues), remaining_issues


def main():
    """Test import update functionality."""
    import argparse

    parser = argparse.ArgumentParser(description="Update Python import statements")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without applying",
    )
    parser.add_argument(
        "--verify", action="store_true", help="Verify imports were updated correctly"
    )
    parser.add_argument(
        "--target-prefix", default="ord_plan", help="Target prefix to remove"
    )

    args = parser.parse_args()

    repo_root = Path.cwd()
    updater = ImportUpdater(repo_root, args.target_prefix, args.dry_run)

    if args.verify:
        print("🔍 Verifying import updates...")
        remaining_issues, issue_files = updater.verify_updates()

        if remaining_issues == 0:
            print("✅ All imports have been correctly updated!")
        else:
            print(f"❌ Found {remaining_issues} files with remaining issues:")
            for file_path in issue_files:
                print(f"  📄 {file_path}")
            sys.exit(1)

        return

    print("🚀 Starting import statement updates...")

    # Update all files
    files_updated, errors = updater.update_all_files()

    if errors:
        print(f"\n❌ Encountered {len(errors)} errors:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)

    # Show summary
    summary = updater.get_update_summary()
    print("\n📊 Update Summary:")
    print(f"  📁 Files updated: {summary['files_updated']}")
    print(f"  🔄 Total updates: {summary['total_updates']}")
    print(f"  📦 Import updates: {summary['import_updates']}")
    print(f"  📋 From-import updates: {summary['from_import_updates']}")

    if args.dry_run:
        print("\n💡 DRY RUN completed - no actual changes made")
    else:
        print("\n✅ Import updates completed. Run with --verify to check results.")


if __name__ == "__main__":
    main()
