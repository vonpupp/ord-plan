"""Path mapping system for reference updates using regex patterns.

This module provides utilities to update file references, import statements,
and path references during repository restructuring.
"""

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from typing import List
from typing import Tuple


@dataclass
class PathMapping:
    """Represents a path mapping for reference updates."""

    old_pattern: str
    new_pattern: str
    file_types: List[str]
    description: str
    scope: str


class PathMapper:
    """Handles path mapping and reference updates."""

    def __init__(self, repo_root: Path = None, dry_run: bool = False):
        """Initialize path mapper with repository root and dry-run mode."""
        self.repo_root = repo_root or Path.cwd()
        self.dry_run = dry_run
        self.updated_files = []

        # Define path mappings for repository restructuring
        self.mappings = [
            # Python import statements
            PathMapping(
                old_pattern=r"from ord_plan\.",
                new_pattern="from ",
                file_types=[".py"],
                description="Remove ord_plan prefix from import statements",
                scope="python_imports",
            ),
            PathMapping(
                old_pattern=r"import ord_plan\.",
                new_pattern="import ",
                file_types=[".py"],
                description="Remove ord_plan prefix from import statements",
                scope="python_imports",
            ),
            # Configuration file path references
            PathMapping(
                old_pattern=r"ord-plan/",
                new_pattern="",
                file_types=[".toml", ".yaml", ".yml", ".json", ".cfg", ".ini"],
                description="Remove ord-plan/ prefix from config file paths",
                scope="config_files",
            ),
            PathMapping(
                old_pattern=r"src/",
                new_pattern="",
                file_types=[".toml", ".yaml", ".yml", ".json"],
                description="Remove src/ prefix from path references",
                scope="config_files",
            ),
            # Documentation references
            PathMapping(
                old_pattern=r"ord-plan/",
                new_pattern="",
                file_types=[".md", ".rst", ".txt"],
                description="Update documentation path references",
                scope="documentation",
            ),
            # GitHub Actions workflow paths
            PathMapping(
                old_pattern=r"ord-plan/",
                new_pattern="",
                file_types=[".yml", ".yaml"],
                description="Update CI/CD workflow paths",
                scope="workflows",
            ),
            PathMapping(
                old_pattern=r"working-directory: ord-plan",
                new_pattern="working-directory: .",
                file_types=[".yml", ".yaml"],
                description="Remove working-directory references",
                scope="workflows",
            ),
            # Test file references
            PathMapping(
                old_pattern=r"ord_plan/",
                new_pattern="",
                file_types=[".py"],
                description="Remove ord_plan/ from test paths",
                scope="test_files",
            ),
        ]

    def find_files_to_update(self, file_types: List[str]) -> List[Path]:
        """Find all files of specified types to update.

        Args:
            file_types: List of file extensions to include

        Returns:
            List of file paths to update
        """
        files_to_update = []

        for ext in file_types:
            # Use find command for efficient file discovery
            try:
                cmd = ["find", str(self.repo_root), "-type", "f", "-name", f"*{ext}"]
                result = subprocess.run(
                    ["/usr/bin/git"] + cmd, capture_output=True, text=True, check=True
                )

                if result.stdout.strip():
                    files = [
                        Path(line.strip())
                        for line in result.stdout.strip().split("\n")
                        if line.strip()
                    ]
                    files_to_update.extend(files)

            except subprocess.CalledProcessError:
                print(f"⚠️  Could not find files with extension {ext}")

        # Filter out files that shouldn't be modified
        filtered_files = []
        for file_path in files_to_update:
            relative_path = file_path.relative_to(self.repo_root)

            # Skip files in .git, node_modules, or other ignored directories
            if any(part.startswith(".") for part in relative_path.parts):
                continue

            # Skip files in specs/ directory (these are documentation)
            if "specs" in relative_path.parts:
                continue

            # Skip files in scripts/restructure (our own scripts)
            if "scripts/restructure" in str(relative_path):
                continue

            filtered_files.append(file_path)

        return filtered_files

    def update_file(
        self, file_path: Path, mappings: List[PathMapping]
    ) -> Tuple[bool, str]:
        """Update a single file using provided mappings.

        Args:
            file_path: Path to file to update
            mappings: List of mappings to apply

        Returns:
            Tuple of (success, error_message)
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Apply each mapping
            for mapping in mappings:
                pattern = re.compile(mapping.old_pattern)
                if pattern.search(content):
                    content = pattern.sub(mapping.new_pattern, content)
                    print(f"  📝 Applied {mapping.description}")

            # Only write if content changed
            if content != original_content:
                if self.dry_run:
                    print(f"    DRY RUN: Would update {file_path}")
                else:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"  ✅ Updated {file_path}")

                self.updated_files.append(file_path)
            else:
                print(f"  ℹ️  No changes needed for {file_path}")

            return True, ""

        except Exception as e:
            error_msg = f"Failed to update {file_path}: {e}"
            print(f"  ❌ {error_msg}")
            return False, error_msg

    def update_by_scope(self, scope: str) -> Tuple[bool, str]:
        """Update all files for a specific scope.

        Args:
            scope: Scope to update (e.g., 'python_imports', 'config_files')

        Returns:
            Tuple of (success, error_message)
        """
        # Filter mappings by scope
        scope_mappings = [m for m in self.mappings if m.scope == scope]

        if not scope_mappings:
            return False, f"No mappings found for scope: {scope}"

        print(f"🔄 Updating files for scope: {scope}")

        # Get all file types for this scope
        file_types = set()
        for mapping in scope_mappings:
            file_types.update(mapping.file_types)

        # Find files to update
        files_to_update = self.find_files_to_update(list(file_types))

        if not files_to_update:
            print(f"ℹ️  No files found for scope {scope}")
            return True, ""

        print(f"📁 Found {len(files_to_update)} files to update")

        # Update each file
        for file_path in files_to_update:
            print(f"\n📄 Processing {file_path.relative_to(self.repo_root)}:")
            success, error = self.update_file(file_path, scope_mappings)
            if not success:
                return False, error

        return True, ""

    def update_all(self) -> Tuple[bool, str]:
        """Update all files using all mappings."""
        print("🚀 Starting comprehensive path mapping updates...")

        # Group mappings by scope to avoid processing files multiple times
        scopes = {mapping.scope for mapping in self.mappings}

        for scope in scopes:
            success, error = self.update_by_scope(scope)
            if not success:
                return False, error

        return True, ""

    def get_updated_files(self) -> List[Path]:
        """Get list of successfully updated files."""
        return self.updated_files.copy()

    def preview_changes(self) -> Dict[str, List[str]]:
        """Preview what changes would be made without applying them.

        Returns:
            Dictionary mapping scopes to lists of files that would be updated
        """
        self.dry_run = True
        original_updated = self.updated_files.copy()
        self.updated_files.clear()

        preview = {}
        scopes = {mapping.scope for mapping in self.mappings}

        for scope in scopes:
            scope_mappings = [m for m in self.mappings if m.scope == scope]
            file_types = set()
            for mapping in scope_mappings:
                file_types.update(mapping.file_types)

            files_to_update = self.find_files_to_update(list(file_types))
            preview[scope] = [
                str(f.relative_to(self.repo_root)) for f in files_to_update
            ]

        # Restore original state
        self.dry_run = False
        self.updated_files = original_updated

        return preview


def main():
    """Test path mapping functionality."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Update file references after restructuring"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without applying",
    )
    parser.add_argument(
        "--scope",
        choices=[
            "python_imports",
            "config_files",
            "documentation",
            "workflows",
            "test_files",
        ],
        help="Update only specific scope (default: all)",
    )
    parser.add_argument("--preview", action="store_true", help="Preview changes only")

    args = parser.parse_args()

    mapper = PathMapper(dry_run=args.dry_run or args.preview)

    if args.preview:
        print("🔍 Preview of changes to be made:")
        preview = mapper.preview_changes()

        for scope, files in preview.items():
            print(f"\n📁 Scope: {scope}")
            if files:
                for file_path in files[:10]:  # Show first 10
                    print(f"  📄 {file_path}")
                if len(files) > 10:
                    print(f"  ... and {len(files) - 10} more files")
            else:
                print("  ℹ️  No files found")

        print("\n💡 Use --dry-run to see actual changes, or run without flags to apply")
        return

    print("🚀 Starting path mapping updates...")

    if args.scope:
        success, error = mapper.update_by_scope(args.scope)
    else:
        success, error = mapper.update_all()

    if not success:
        print(f"❌ Failed: {error}")
        sys.exit(1)

    updated_files = mapper.get_updated_files()
    print(f"\n📊 Summary: Updated {len(updated_files)} files")

    if args.dry_run:
        print("💡 DRY RUN completed - no actual changes made")
    else:
        print(
            "✅ Path mapping completed. Review with 'git diff' and commit when ready."
        )


if __name__ == "__main__":
    main()
