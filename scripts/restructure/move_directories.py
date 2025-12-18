"""
File movement utilities for repository restructuring.

This module provides utilities to safely move files and directories
using git mv operations to preserve history.
"""

import subprocess
import sys
from pathlib import Path
from typing import List
from typing import Optional
from typing import Tuple


class FileMover:
    """Handles file and directory movement using git operations."""

    def __init__(self, repo_root: Optional[Path] = None, dry_run: bool = False):
        """Initialize file mover with repository root and dry-run mode."""
        self.repo_root = repo_root or Path.cwd()
        self.dry_run = dry_run
        self.moved_items = []

    def _run_git_mv(self, source: Path, target: Path) -> Tuple[bool, str]:
        """
        Run git mv command with proper error handling.

        Args:
            source: Source path to move
            target: Target path for move

        Returns:
            Tuple of (success, error_message)
        """
        try:
            cmd = ["git", "mv", str(source), str(target)]

            if self.dry_run:
                print(f"DRY RUN: Would run: {' '.join(cmd)}")
                return True, ""

            result = subprocess.run(
                cmd, cwd=self.repo_root, capture_output=True, text=True, check=True
            )

            print(f"✅ Moved {source} -> {target}")
            self.moved_items.append((source, target))
            return True, ""

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to move {source} -> {target}: {e.stderr}"
            print(f"❌ {error_msg}")
            return False, error_msg

    def move_directory(self, dir_name: str) -> Tuple[bool, str]:
        """
        Move a directory from ord-plan/ to repository root.

        Args:
            dir_name: Name of directory to move (e.g., 'src', 'tests')

        Returns:
            Tuple of (success, error_message)
        """
        source_path = self.repo_root / "ord-plan" / dir_name
        target_path = self.repo_root / dir_name

        if not source_path.exists():
            error_msg = f"Source directory {source_path} does not exist"
            print(f"❌ {error_msg}")
            return False, error_msg

        if target_path.exists():
            error_msg = f"Target {target_path} already exists"
            print(f"❌ {error_msg}")
            return False, error_msg

        return self._run_git_mv(source_path, target_path)

    def move_file(self, file_name: str) -> Tuple[bool, str]:
        """
        Move a file from ord-plan/ to repository root.

        Args:
            file_name: Name of file to move (e.g., 'README.md', 'pyproject.toml')

        Returns:
            Tuple of (success, error_message)
        """
        source_path = self.repo_root / "ord-plan" / file_name
        target_path = self.repo_root / file_name

        if not source_path.exists():
            error_msg = f"Source file {source_path} does not exist"
            print(f"❌ {error_msg}")
            return False, error_msg

        if target_path.exists():
            error_msg = f"Target file {target_path} already exists"
            print(f"❌ {error_msg}")
            return False, error_msg

        return self._run_git_mv(source_path, target_path)

    def move_github_directory(self) -> Tuple[bool, str]:
        """
        Move .github directory contents to repository root .github/.

        Returns:
            Tuple of (success, error_message)
        """
        source_path = self.repo_root / "ord-plan" / ".github"
        target_path = self.repo_root / ".github"

        if not source_path.exists():
            error_msg = f"Source .github directory {source_path} does not exist"
            print(f"❌ {error_msg}")
            return False, error_msg

        # Create target .github if it doesn't exist
        if not target_path.exists():
            if self.dry_run:
                print(f"DRY RUN: Would create directory {target_path}")
            else:
                target_path.mkdir(exist_ok=True)
                print(f"📁 Created directory {target_path}")

        # Move contents, not the directory itself
        try:
            for item in source_path.iterdir():
                target_item = target_path / item.name

                if item.is_file():
                    success, error = self._run_git_mv(item, target_item)
                    if not success:
                        return False, error
                elif item.is_dir():
                    # For subdirectories, we need to move recursively
                    success, error = self._move_directory_recursive(item, target_item)
                    if not success:
                        return False, error

            print("✅ Moved .github contents to repository root .github/")
            return True, ""

        except Exception as e:
            error_msg = f"Failed to move .github contents: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg

    def _move_directory_recursive(self, source: Path, target: Path) -> Tuple[bool, str]:
        """Recursively move directory contents."""
        try:
            if self.dry_run:
                print(f"DRY RUN: Would create directory {target}")
            else:
                target.mkdir(parents=True, exist_ok=True)

            for item in source.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(source)
                    target_file = target / rel_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)

                    success, error = self._run_git_mv(item, target_file)
                    if not success:
                        return False, error

            return True, ""
        except Exception as e:
            return False, f"Failed to move directory recursively: {e}"

    def get_moved_items(self) -> List[Tuple[Path, Path]]:
        """Get list of successfully moved items."""
        return self.moved_items.copy()

    def undo_moves(self) -> Tuple[bool, str]:
        """
        Undo all moves by moving items back to ord-plan/.

        Returns:
            Tuple of (success, error_message)
        """
        if not self.moved_items:
            print("ℹ️  No moves to undo")
            return True, ""

        if self.dry_run:
            print("DRY RUN: Would undo all moves")
            return True, ""

        print("🔄 Undoing moves...")

        for source, target in reversed(self.moved_items):
            # The original target is now at source, and original source is at target
            success, error = self._run_git_mv(source, target)
            if not success:
                return False, f"Failed to undo move {source} -> {target}: {error}"

        self.moved_items.clear()
        print("✅ All moves undone successfully")
        return True, ""


def main():
    """Test the file mover functionality."""
    import argparse

    parser = argparse.ArgumentParser(description="Test file movement operations")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing",
    )
    parser.add_argument(
        "--directories",
        nargs="+",
        default=["src", "tests", "docs"],
        help="Directories to move (default: src tests docs)",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        default=["README.md", "LICENSE", "pyproject.toml", ".gitignore", "AGENTS.md"],
        help="Files to move",
    )
    parser.add_argument(
        "--include-github", action="store_true", help="Move .github directory"
    )

    args = parser.parse_args()

    mover = FileMover(dry_run=args.dry_run)

    print("🚀 Starting file movement operations...")

    # Move directories
    for directory in args.directories:
        print(f"\n📁 Moving directory: {directory}")
        success, error = mover.move_directory(directory)
        if not success:
            print(f"❌ Failed: {error}")
            sys.exit(1)

    # Move files
    for file_name in args.files:
        print(f"\n📄 Moving file: {file_name}")
        success, error = mover.move_file(file_name)
        if not error:  # File might not exist, that's ok for test
            print(f"ℹ️  {file_name} not found or already moved")

    # Move .github if requested
    if args.include_github:
        print("\n📁 Moving .github directory...")
        success, error = mover.move_github_directory()
        if not success:
            print(f"❌ Failed: {error}")
            sys.exit(1)

    print(f"\n📊 Summary: Moved {len(mover.get_moved_items())} items")

    if args.dry_run:
        print("💡 DRY RUN completed - no actual changes made")
    else:
        print(
            "✅ File movements completed. Review with 'git status' and commit when ready."
        )


if __name__ == "__main__":
    main()
