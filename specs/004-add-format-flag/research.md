# Research: Add Format Flag for Configuration Decoupling

**Feature**: 004-add-format-flag
**Date**: 2025-12-23
**Purpose**: Resolve unknowns and define technical approach for separating format configuration from rules files

## Research Decisions

### Decision 1: Format File Structure and Validation

**Question**: How should format files be structured and validated compared to combined rules files?

**Decision**: Format files will contain only formatting configuration keys (no `events` section). The same validation logic will be reused from `yaml_parser.py` but with relaxed requirements for format files.

**Rationale**:
- Reuses existing validation infrastructure
- Format files are simpler subset of combined files
- Keeps validation logic in one place
- Prevents users from accidentally putting events in format files

**Alternatives Considered**:
- Separate validation logic for format files: Rejected because it duplicates validation code
- Allow events in format files and ignore them: Rejected because it creates confusion about purpose

**Implementation**:
- Add a new method `parse_format_file()` in `YamlParser` that validates only formatting keys
- Reuse existing date format validation from `Configuration.validate_date_formats()`
- New validation rules:
  - Allow empty format files (will use all defaults)
  - Require valid YAML syntax
  - Warn on unknown keys (don't error, for extensibility)
  - No `events` section allowed in format files

---

### Decision 2: Configuration Merging Strategy

**Question**: How should formatting options from format file and rules file be merged with proper precedence?

**Decision**: Add a `merge_format_config()` method to `Configuration` class that performs deep merge with format file taking precedence over rules file values.

**Rationale**:
- Centralizes merging logic in one place
- Type-safe with existing Configuration dataclass
- Easy to test independently
- Clear precedence: format file > rules file > defaults

**Alternatives Considered**:
- Merge in generate.py command handler: Rejected because mixing business logic with CLI code
- Use dictionary merging at parser level: Rejected because loses type safety and validation

**Implementation**:
```python
@classmethod
def merge_format_config(
    cls,
    rules_config: Optional[Dict[str, Any]],
    format_config: Optional[Dict[str, Any]]
) -> "Configuration":
    """Merge formatting configs with format_file taking precedence."""
    merged = {}
    if rules_config:
        merged.update(rules_config)
    if format_config:
        merged.update(format_config)  # Overwrites rules_config keys
    return cls.from_env_and_dict(merged)
```

---

### Decision 3: Edge Case Handling

**Question**: How should the tool handle edge cases for format files?

**Decision**: Specific error handling strategies for each edge case:

| Edge Case | Behavior |
|-----------|----------|
| Empty format file | Use all default values, no error |
| Invalid YAML syntax | Error with file path and YAML error details |
| Unknown formatting key | Warning to stderr, ignore key |
| Duplicate formatting keys in file | Use last value, warning to stderr |
| Invalid file path | Error with clear message about file not found |
| File not readable | Error with clear message and permission hint |
| Neither format nor rules provides option | Use Configuration default values |

**Rationale**:
- Graceful degradation with clear user feedback
- Warnings instead of errors for non-critical issues
- Consistent with existing error handling patterns
- Prevents silent failures while being lenient

**Alternatives Considered**:
- Strict validation (error on unknown keys): Rejected because limits future extensibility
- Silent ignore of all unknown keys: Rejected because hides user mistakes

---

### Decision 4: Default Values for Formatting Options

**Question**: What are the default values when formatting options are not provided?

**Decision**: Use existing Configuration class defaults:
- `reverse_datetree_year_format`: "%Y"
- `reverse_datetree_week_format`: "%Y-W%V"`
- `reverse_datetree_date_format`: "%Y-%m-%d %a"`
- `reverse_datetree_use_week_tree`: true

**Rationale**:
- Maintains backward compatibility
- Existing behavior is tested and documented
- Defaults are sensible for org-mode workflows

**Alternatives Considered**:
- Require all formatting options: Rejected because breaks backward compatibility
- Different defaults for format files vs rules files: Rejected because confusing for users

---

### Decision 5: CLI Flag Integration

**Question**: How should the `--format` flag be integrated into the existing CLI?

**Decision**: Add optional `--format` parameter to `generate()` command using Click's `Path` type, with same validation pattern as `--rules` flag.

**Rationale**:
- Consistent with existing flag patterns
- Click's Path type provides automatic validation
- Keeps changes minimal and focused

**Implementation**:
```python
@click.option(
    "--format",
    type=click.Path(exists=True, readable=True),
    help="""Path to YAML format configuration file.

    Contains only formatting options (REVERSE_DATETREE_WEEK_FORMAT, etc.).
    Format file options take precedence over rules file options."""
)
```

**Alternatives Considered**:
- New `--format-config` flag name: Rejected because longer, `--format` is clear
- Make format flag required: Rejected because breaks backward compatibility

---

### Decision 6: Validation Timing and Error Reporting

**Question**: When should format file be validated and how should errors be reported?

**Decision**: Validate format file immediately after rules file, before any processing. Combine errors from both files in single validation report.

**Rationale**:
- Fails fast on configuration errors
- Provides complete error feedback in one pass
- Consistent with existing validation flow

**Implementation**:
```python
# Parse rules file first
rules_config, rules_errors = YamlParser.parse_and_validate(rules)

# Parse format file if provided
format_config = None
format_errors = []
if format:
    format_config, format_errors = YamlParser.parse_format_file(format)

# Combine and report all errors together
all_errors = rules_errors + format_errors
if all_errors:
    # Report errors
    raise click.Abort()
```

**Alternatives Considered**:
- Validate files independently with separate error reports: Rejected because increases user friction
- Delay format validation until merge time: Rejected because wastes time on invalid config

---

## Architecture Impact

### Components to Modify

1. **`cli/generate.py`**:
   - Add `--format` parameter to `generate()` command
   - Parse format file if provided
   - Merge format config with rules config
   - Validate merged configuration

2. **`cli/config.py`**:
   - Add `merge_format_config()` class method
   - Reuse existing `from_env_and_dict()` and `validate_date_formats()`

3. **`parsers/yaml_parser.py`**:
   - Add `parse_format_file()` method
   - Add `validate_format_schema()` method
   - Reuse existing YAML parsing infrastructure

4. **Test fixtures** (`tests/fixtures/`):
   - Add format file examples (valid, empty, invalid)
   - Add combined rules files for backward compatibility tests
   - Add merged configuration scenario fixtures

### Data Flow Changes

```
Before:
  rules.yaml → YamlParser → Configuration → generate output

After:
  format.yaml → YamlParser.format → \
                                 → merge → Configuration → generate output
  rules.yaml → YamlParser.rules → /
```

## Backward Compatibility

**Ensuring backward compatibility**:
- `--format` flag is optional
- Existing commands without `--format` work unchanged
- Combined rules files continue to work
- No changes to default behavior or output format

**Test strategy**:
- Keep all existing tests passing
- Add new tests for format file scenarios
- Add tests that verify combined files still work
- Add tests for precedence rules (format > rules)

## Open Questions

None. All research decisions made.

## Next Steps

Proceed to Phase 1: Design & Contracts
- Create data-model.md with entity definitions
- Create CLI contract documentation
- Create quickstart.md with usage examples
- Update agent context
