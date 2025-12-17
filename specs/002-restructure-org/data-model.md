# Data Model: Repository Restructure

**Date**: 2025-12-17  
**Purpose**: Define entities and validation rules for repository restructuring operations

## Core Entities

### RepositoryStructure
Represents the current and target directory layouts of the repository.

**Attributes:**
- source_root: string = "ord-plan"
- target_root: string = "" (repository root)
- directories_to_move: Directory[]
- files_to_move: File[]
- path_mappings: PathMapping[]

### Directory
Represents a directory that needs to be moved during restructuring.

**Attributes:**
- name: string (e.g., "src", "tests", "docs", ".github")
- source_path: string (e.g., "ord-plan/src")
- target_path: string (e.g., "src")
- preserve_structure: boolean = true
- subdirectories: Directory[]

### File
Represents an individual file that needs to be moved.

**Attributes:**
- name: string (filename)
- source_path: string (full path including ord-plan/)
- target_path: string (path after restructuring)
- file_type: enum {CONFIG, SOURCE, TEST, DOC, METADATA}
- requires_content_update: boolean = false

### PathMapping
Represents old and new path relationships for reference updates.

**Attributes:**
- old_pattern: string (regex pattern to match old paths)
- new_pattern: string (replacement pattern)
- file_types: string[] (extensions to apply this mapping to)
- scope: enum {PYTHON_IMPORTS, CONFIG_FILES, WORKFLOWS, DOCUMENTATION}

## Validation Rules

### Directory Movement Validation
- Source directory must exist in ord-plan/
- Target location must not conflict with existing files
- Directory structure preservation must be maintained
- All required directories (src, tests, docs, .github) must be moved

### File Movement Validation
- All Python package files must be moved (pyproject.toml, README.md, LICENSE, etc.)
- No data loss during file movement
- File permissions must be preserved
- Binary files must remain intact

### Reference Update Validation
- All Python import statements must be updated
- Configuration file paths must be corrected
- Test fixture paths must remain valid
- Documentation links must be functional

### Git History Validation
- All moved files must preserve git history
- Single commit must show all movements
- No orphaned commits should exist
- Tags must remain functional

## State Transitions

### RepositoryState
enum representing repository states during restructuring:

1. INITIAL: Repository in original state with ord-plan/ subdirectory
2. FILES_MOVED: Files moved to root level
3. REFERENCES_UPDATED: All paths and imports updated  
4. VALIDATED: All functionality verified through tests
5. COMPLETED: Restructuring complete and functional

### Transition Rules
- INITIAL → FILES_MOVED: Requires successful git mv operations
- FILES_MOVED → REFERENCES_UPDATED: Requires successful regex replacements
- REFERENCES_UPDATED → VALIDATED: Requires successful test execution
- VALIDATED → COMPLETED: Requires final validation checkpoint

## Constraints

### Technical Constraints
- Must use git mv for history preservation
- All operations must be atomic (single commit)
- No temporary directories allowed
- Must preserve all existing functionality

### Quality Constraints
- 100% test pass rate required after restructuring
- Zero broken links or references allowed
- All development commands must work identically
- Repository must follow Python packaging standards

### Process Constraints
- Must handle absolute and relative paths correctly
- Must update all configuration file references
- Must preserve test fixture structure
- Must not break existing CI/CD workflows