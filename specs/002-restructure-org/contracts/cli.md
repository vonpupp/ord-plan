# CLI Documentation: Repository Restructure Reference

**Date**: 2025-12-17  
**Purpose**: Document CLI behavior that must be preserved after repository refactoring

## CLI Requirements for Refactoring

**Note**: This is documentation of existing CLI behavior that MUST be preserved after the repository refactoring. No new CLI commands are being implemented.

### Existing CLI Commands
The existing ord-plan CLI commands MUST continue to work identically after refactoring:

```bash
# Existing generate command must still work
ord-plan generate [OPTIONS]

# All existing options and behavior preserved
ord-plan generate --help
ord-plan generate input.yaml --output.org
```

### CLI Preservation Requirements

| Requirement | Description |
|-------------|-------------|
| Command Discovery | All existing CLI commands must remain discoverable |
| Option Handling | All existing options must work identically |
| Output Formats | Org-mode and JSON output must be unchanged |
| Error Handling | Error messages and exit codes must be preserved |
| Help System | All help text and examples must remain accurate |

## Refactoring Validation for CLI

### CLI Functionality Tests
After refactoring, the following CLI behaviors MUST be validated:

```bash
# Test command discovery works
ord-plan --help

# Test existing generate command works
ord-plan generate --help

# Test file operations work
ord-plan generate input.yaml --output.org

# Test error handling preserved
ord-plan generate nonexistent.yaml
```

### CLI Preservation Validation

| Test | Expected Result |
|------|-----------------|
| Help command | Shows all existing commands |
| Generate command | Works with all existing options |
| Error handling | Same error messages and exit codes |
| Output formats | Org-mode and JSON output unchanged |
| Configuration | All config file handling preserved |