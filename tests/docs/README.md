# Documentation Tests

This directory contains comprehensive unit tests for Architecture Decision Records (ADRs) and Production Runbooks.

## Overview

These tests validate documentation quality, structure, and completeness for the `docs/adr/` and `docs/runbooks/` directories.

## Test Files

- **`test_adr_documentation.py`** (496 lines, 28 tests) - Validates ADR structure, content, and code examples
- **`test_runbook_documentation.py`** (507 lines, 29 tests) - Validates runbook procedures, commands, and operational content

## Running Tests

```bash
# Run all documentation tests
python -m pytest tests/docs/ -v

# Run ADR tests only
python -m pytest tests/docs/test_adr_documentation.py -v

# Run runbook tests only
python -m pytest tests/docs/test_runbook_documentation.py -v

# Run specific test class
python -m pytest tests/docs/test_adr_documentation.py::TestADRStructure -v

# Run with verbose output
python -m pytest tests/docs/ -vv --tb=long
```

## What These Tests Validate

### ADR Tests
- ✅ File structure and naming conventions
- ✅ Required sections (Status, Context, Decision, Consequences)
- ✅ Code block syntax (TypeScript, Bash, YAML)
- ✅ Cross-references and links
- ✅ Content quality and completeness
- ✅ Domain-specific technical content

### Runbook Tests
- ✅ Operational procedures structure
- ✅ Command syntax (kubectl, SQL, Bash)
- ✅ Incident response procedures
- ✅ Severity level definitions
- ✅ Actionable troubleshooting steps
- ✅ Time estimates and detection methods

## Test Coverage

- **Total Tests**: 57 test methods
- **Test Classes**: 13 classes
- **Lines of Code**: 1,004 lines
- **Documentation Covered**: 12 files, 5,514 lines

## Dependencies

- pytest >= 7.2.0 (in requirements.txt)
- Python 3.x

No additional dependencies required.

## Contributing

When adding new documentation:

1. Create your ADR or runbook following existing formats
2. Run the test suite: `python -m pytest tests/docs/ -v`
3. Fix any validation failures
4. Consider adding domain-specific tests for new content

## Related Documentation

- See `../../TEST_DOCUMENTATION_SUMMARY.md` for detailed test descriptions
- See `../../UNIT_TESTS_GENERATED.md` for quick reference guide