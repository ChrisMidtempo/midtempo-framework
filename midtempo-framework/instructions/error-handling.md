# Agentic Framework Error Handling

## Table of Contents

- [Error Classification](#1-error-classification)
- [Error Handling Patterns](#2-error-handling-patterns)
- [Error Logging & Reporting](#3-error-logging--reporting)
- [Error Testing Patterns](#4-error-testing-patterns)
- [Repo-Specific Anti-Patterns](#5-repo-specific-anti-patterns)
- [File References](#6-file-references)
- [Compliance Gates](#7-compliance-gates)

---

## 1. Error Classification

### 1.1 System

Standard Python exceptions with enhanced error messages. No custom error classes — all errors use built-in exception types, caught and re-raised with contextual detail.

### 1.2 Categories

- **Validation errors** (`ValueError`): Config validation failures, schema violations, scope conflicts, pattern mismatches
- **Template errors** (`UndefinedError`, `TemplateError`): Jinja2 rendering failures, undefined variables, syntax errors, circular inheritance
- **File system errors** (`FileNotFoundError`): Missing config files, language templates, schema files
- **Data format errors** (`KeyError`): Missing commands, instructions, language mappings in configuration
- **Parse errors** (`yaml.YAMLError`): YAML/JSON parsing failures from malformed data

### 1.3 Severity levels

Severity is implicit in exception type:
- `ValueError`: Invalid input or config (user-correctable)
- `ValidationError` (jsonschema): Schema validation failure, caught and re-raised as `ValueError`
- `FileNotFoundError`: Missing required file (user-correctable)
- `KeyError`: Missing required field (configuration issue)
- `UndefinedError`, `TemplateError`: Template rendering failure (template or config issue)
- `RecursionError`: Circular template inheritance (template structure issue)

### 1.4 HTTP mapping

Server layer (`server/app.py`) maps errors to HTTP status codes:

- **422** — Two sources: (1) Pydantic `RequestValidationError` (missing or wrong-type field); custom handler returns `{"error": "<first validation message>"}`, overriding FastAPI's default `{"detail": [...]}` structure. (2) `ValueError` from `validate_config_with_enhanced_errors` (schema-invalid config dict); route handler returns `{"error": str(e)}` before any filesystem work begins. Both represent input validation failures at the server boundary.
- **400** — Business logic rejection (unknown language, `ValueError` from `render_config_string`); route handler returns `{"error": str(e)}`.
- **500** — Unhandled `Exception`; generic handler logs server-side, returns `{"error": "An unexpected error occurred"}`. No stack trace or internal path in response.
- **405** — Method not allowed; explicit `api_route` registration required when `StaticFiles` is mounted at `/`.

All error responses use `{"error": string}` — not `{"detail": ...}` (FastAPI default). This contract applies to all server endpoints.

### 1.5 Error codes

No formal error codes. Errors identified by exception type and message content. Exit codes: 0 (success), 1 (failure).

---

## 2. Error Handling Patterns

### 2.1 Boundaries

- **CLI entry points**: Top-level `_cli_main()` / `main()` functions catch exceptions, print to stderr, return exit code 1
- **Enhanced error handlers**: Catch third-party exceptions (`ValidationError`, `UndefinedError`), enrich with context, re-raise as standard types
- **Worker processes**: Catch all exceptions in `generate_single_repo()`, return error tuples instead of raising
- **Validation layer**: Validates config against JSON Schema before rendering begins — errors halt pipeline

### 2.2 Enhanced error handlers

[scripts/validate_config.py](scripts/validate_config.py)
- Catches `jsonschema.ValidationError`
- Inspects validator type (`required`, `enum`, `pattern`, `additionalProperties`)
- Builds multi-line error messages with field paths and valid options
- Re-raises as `ValueError` with `raise ... from e`

[scripts/generate_docs.py](scripts/generate_docs.py)
- Catches `jinja2.UndefinedError`
- Adds template filename and config suggestion
- Re-raises with file context using `raise ... from e`

### 2.3 Script layer

- Scripts raise typed exceptions (`ValueError`, `FileNotFoundError`, `KeyError`)
- Add context before raising: field names, file paths, valid options
- Preserve exception chain with `raise ... from e`
- Validate early: check preconditions before processing

### 2.4 Parallel processing

[scripts/generate_all.py](scripts/generate_all.py)
- `generate_single_repo()` catches all `Exception` types
- Returns tuple `(repo_path, success, error_message)` instead of raising
- Main thread collects results via `as_completed(futures)`
- Enables partial success in batch operations — one failure does not stop others

### 2.5 Unhandled errors

- No global exception handlers
- Exceptions propagate to Python CLI (traceback printed to stderr)
- pytest catches and reports exceptions during testing

### 2.6 Consistency rules

- Catch third-party exceptions and re-raise with enhanced context (never let raw `ValidationError` or `UndefinedError` propagate)
- Use `raise ValueError(...) from e` to preserve exception chain
- Add actionable guidance to error messages (field paths, valid options, config suggestions)
- Let exceptions propagate to CLI — catch at top level only when adding context
- Return error tuples in worker processes (enable partial success in parallel operations)
- Validate early: check preconditions before processing starts
- Categorise exceptions at CLI entry points: separate handlers for `ValueError`, `TemplateError`, generic `Exception`

---

## 3. Error Logging & Reporting

### 3.1 Logger

**CLI scripts:** No logging library. Use `print()` for all output.

**Server layer (`server/`):** Use `logging.getLogger(__name__)` per module. Log unhandled exceptions with `logger.error("...", exc_info=exc)`. Do not use `print()` in server code.

### 3.2 Log levels

Implicit levels via output destination:
- Success messages: stdout (`print(...)`)
- Error messages: stderr (`print(..., file=sys.stderr)`)

### 3.3 Log format

Plain text messages:
- Success: `✓ <action> (<details>)`
- Error: `Error: <message>` or `<error_type>: <details>`
- Multi-line errors: Enhanced messages with field paths, valid options, suggestions

### 3.4 Destinations

- Success messages → stdout
- Error messages → stderr
- Unhandled exceptions → stderr (Python traceback)
- Test output → pytest framework

### 3.5 Context fields

Error messages include:
- **Field path**: Full dotted path to invalid field (e.g., `repo.language`)
- **Invalid value**: What was provided
- **Valid options**: Enum values, pattern requirements, examples
- **File context**: Template filename, config file path
- **Actionable guidance**: What to check or fix

### 3.6 PII handling

Not applicable — config files contain project metadata only, no user PII.

### 3.7 Client reporting

**CLI layer:** Not applicable.

**Server layer:** All errors return `{"error": string}` JSON. No stack traces or internal paths in responses. The browser renders the `error` field value via `textContent` (not `innerHTML`) to prevent XSS.

### 3.8 External services

None. All output to stdout/stderr.

### 3.9 Consistency rules

- Print success to stdout, errors to stderr (use `file=sys.stderr`)
- Use `✓` symbol for success messages (visually distinct)
- Include counts in summary messages (files generated, repos processed, succeeded/failed)
- Multi-line errors: Use newlines for readability (field path on one line, guidance on next)
- Top-level CLI functions: Catch exceptions, print to stderr, return exit code 1
- Preserve exception traceback (let unhandled exceptions print full traceback for debugging)

---

## 4. Error Testing Patterns

### 4.1 Testing utilities

- [tests/helpers/config_factory.py](tests/helpers/config_factory.py): Factory functions for creating test configs
  - `create_valid_config()`: Minimal valid config
  - `create_invalid_scope_config(value)`: Config with invalid scope for validation testing
  - `create_standard_config(language)`: Full config with commands loaded from language template files
  - `create_config_with_language(mapping)`: Config with specified language mapping and empty commands
- [tests/conftest.py](tests/conftest.py): Reusable fixtures — `complete_python_config`, `complete_typescript_config`

### 4.2 Error mocking

- Create invalid configs using factory functions: `create_invalid_scope_config("Backend123")`
- Write configs to temp files using `tmp_path` fixture: `config_path = tmp_path / ".agentic-framework.yml"`
- Trigger errors by calling validation functions with invalid input
- Use `yaml.dump(config, f)` to write test configs to temporary files

### 4.3 Error assertions

- Use `pytest.raises(ExceptionType)` as context manager to assert exceptions
- Use `match` parameter for inline message checks: `pytest.raises(KeyError, match="not found")`
- Access error message via `exc_info.value`: `error_message = str(exc_info.value)`
- Assert error message content with flexible substring checks:
  - Field paths: `assert "repo.language" in error_message`
  - Keywords: `assert "required" in error_message.lower()`
  - Multiple options: `assert "pattern" in msg.lower() or "lowercase" in msg.lower()`

### 4.4 Temporary files

- Use pytest's built-in `tmp_path` fixture for temporary directories
- Pattern: `config_path = tmp_path / ".agentic-framework.yml"`
- Write configs: `with config_path.open("w") as f: yaml.dump(config, f)`
- Pass path to validation functions for integration testing

### 4.5 CLI testing patterns

- Use `monkeypatch` to mock `sys.argv` for CLI entry points
- Assert exit codes: 0 for success, 1 for failure
- Test both success paths and error paths for each CLI function

### 4.6 Integration patterns

- Test full validation flow: create config → write to file → validate → assert error
- Test worker error handling: parallel processing returns error tuples instead of raising
- Test batch error aggregation: verify mixed success/failure scenarios report correctly
- Test exception enhancement: verify exceptions caught, enriched, and re-raised with context

### 4.7 Test commands

- `npm run test:python`: Run all Python tests (unit + integration)
- `npm run test:python:unit`: Run unit tests only (fast, for TDD workflow)
- `npm run test:python:integration`: Run integration tests only
- `npm run test:python:coverage`: Run tests with coverage report

---

## 5. Repo-Specific Anti-Patterns

### 5.1 Violations

- **Letting third-party exceptions propagate**: Never let `ValidationError` or `UndefinedError` reach CLI. Catch and re-raise with enhanced context using the pattern in [scripts/validate_config.py](scripts/validate_config.py) and [scripts/generate_docs.py](scripts/generate_docs.py).

- **Breaking exception chain**: Never use `raise ValueError(message)` when re-raising. Use `raise ValueError(...) from e` to preserve the original exception for debugging.

- **Vague error messages**: Never raise generic errors like `ValueError("Invalid config")`. Include field paths, invalid values, valid options, and actionable guidance.

- **Printing errors to stdout**: Never use `print(error_message)` for errors. Use `print(error_message, file=sys.stderr)` to separate error output from success messages.

- **Raising in worker processes**: Never let worker functions in parallel processing raise exceptions. Return error tuples `(path, success, error_message)` to enable partial success.

- **Manual test config creation**: Never manually build config dicts in tests. Use factory functions from [tests/helpers/config_factory.py](tests/helpers/config_factory.py) for consistency.

- **Missing pytest.raises**: Never test error conditions without `pytest.raises`. Use the context manager to assert exception type and verify error message content.

### 5.2 Enforcement

- Code review: Check error handlers follow patterns from [scripts/validate_config.py](scripts/validate_config.py) and [scripts/generate_docs.py](scripts/generate_docs.py)
- Test coverage: Verify error paths tested with `pytest.raises`
- Manual verification: Run scripts with invalid input, check errors go to stderr with exit code 1

---

## 6. File References

### 6.1 Error classification

- [scripts/validate_config.py](scripts/validate_config.py) — Enhanced error message transformation for `ValidationError`
- [scripts/init_framework.py](scripts/init_framework.py) — Raises `ValueError`, `FileNotFoundError` with available language lists

### 6.2 Error handling

- [scripts/validate_config.py](scripts/validate_config.py) — Pattern for catching and re-raising with context
- [scripts/generate_docs.py](scripts/generate_docs.py) — Template error handler with file context
- [scripts/generate_all.py](scripts/generate_all.py) — Worker error handling with tuple returns

### 6.3 Logging

- [scripts/validate_templates.py](scripts/validate_templates.py) — CLI error output to stderr
- [scripts/generate_all.py](scripts/generate_all.py) — Summary messages with counts

### 6.4 Testing

- [tests/helpers/config_factory.py](tests/helpers/config_factory.py) — Test config factories
- [tests/conftest.py](tests/conftest.py) — Complete config fixtures

### 6.5 Other rules

- Testing patterns: [agentic-framework/rules/testing.md](agentic-framework/rules/testing.md)
- TDD workflow: [agentic-framework/rules/tdd.md](agentic-framework/rules/tdd.md)
- Writing style: [agentic-framework/rules/writing.md](agentic-framework/rules/writing.md)

### 6.6 Last edited

03/04/2026 (Stage 3)

---

## 7. Compliance Gates

> Delivery and review skills verify these gates. Each gate must pass for code touching this domain.

- [ ] **CG-1:** Third-party exceptions (`ValidationError`, `UndefinedError`) caught and re-raised with enhanced context — never propagated raw (§2.2)
- [ ] **CG-2:** Exception chain preserved — all re-raised exceptions use `raise ... from e` (§2.3)
- [ ] **CG-3:** Error messages include actionable context: field paths, invalid values, valid options (§3.5)
- [ ] **CG-4:** Errors printed to stderr (`file=sys.stderr`), success to stdout (§3.9)
- [ ] **CG-5:** Worker process errors returned as tuples `(path, success, error_message)` — never raised across process boundary (§2.4)
- [ ] **CG-6:** Error paths tested with `pytest.raises` asserting exception type and message content (§4.3)

---
**END OF DOCUMENT:** Total sections: 7 | Purpose: Error handling patterns and framework | Last updated: 15/02/2026
