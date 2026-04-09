# Agentic Framework Architecture

## Table of Contents

- [Architectural Approach](#1-architectural-approach)
  - [Overview](#11-overview)
  - [Key Characteristics](#12-key-characteristics)
  - [Architectural Style](#13-architectural-style)
  - [Primary Goals](#14-primary-goals)
- [Module Structure](#2-module-structure)
- [Design Patterns](#3-design-patterns)
- [Code Organisation](#4-code-organisation)
- [Architectural Constraints](#5-architectural-constraints)
- [Communication Patterns](#6-communication-patterns)
- [Testing Framework](#7-testing-framework)
- [Examples](#8-examples)
- [File References](#9-file-references)
- [Compliance Gates](#10-compliance-gates)

---

## 1. Architectural Approach

### 1.1 Overview

Agentic Framework follows a configuration-driven template generation pipeline. A single YAML configuration file validates against JSON Schema, enriches with language-specific command defaults, renders through Jinja2 templates with custom filters, and produces namespaced documentation sets tailored to each repository's language, capabilities, and tooling.

### 1.2 Key Characteristics

- **Configuration-driven**: One YAML file per repository controls all generation behaviour
- **Template-based**: 44 Jinja2 templates with conditional logic for language and capability variations
- **Three-layer validation**: Configuration schema → template syntax → generated markdown
- **Namespace isolation**: Output separated into repository-specific directories (`agents/{name}/`)
- **Idempotent generation**: Metadata tracking enables safe regeneration without state corruption
- **Multi-language support**: Language defaults from `commands/*.yml.j2` merged with repository configuration, supporting scoped command naming
- **Self-referential**: The framework generates its own skill files from its own templates

### 1.3 Architectural Style

Pipeline architecture with clear separation between configuration, validation, enrichment, rendering, and output stages

### 1.4 Primary Goals

- **Consistency**: Identical configuration produces identical output on every run
- **Early error detection**: Three validation layers catch errors before output generation
- **Flexibility**: Support 5 languages (Python, TypeScript, TypeScript-npm, Go, Swift) and 3 capability flags (hasUI, hasDB, hasTypecheck)
- **Maintainability**: Centralised templates and macro library; repository-specific configuration
- **Idempotency**: Safe to regenerate — old output cleaned, `instructions/` preserved

---

## 2. Module Structure

### 2.1 Overview

The system organises into five distinct layers with unidirectional dependency flow: Template Source, Configuration & Validation, Generation Orchestration, Filter & Enrichment, and Utilities.

### 2.2 Template Source Layer

**Location:** `jinja-templates/`

**Responsibility:** Source templates organised by category for conditional rendering. Pure input — no code dependencies.

**Key components:**
- `agents/` (21 templates) — Workflow skill files (brainstorming, deliver, review-*, write-*)
- `base/` (3 templates) — Reusable fragments via template inheritance (never generated directly)
- `rules/` (5 templates) — Domain rules (tdd, testing, writing, db, e2e)
- `setup-skills/` (8 templates) — Setup stage sub-skills
- `templates/` (4 templates) — Planning document templates (design, plan, test, decisions)
- `macros.j2` — Global macro library consumed by all templates

### 2.3 Configuration & Validation Layer

**Location:** `schema/`, `scripts/validate_*.py`

**Responsibility:** Validate configuration, template syntax, and generated output before and after rendering

**Dependencies:** Utilities (paths, constants)

**Key components:**
- `schema/config.schema.json` — JSON Schema defining valid configuration structure
- `scripts/validate_config.py` — YAML configuration validation against schema
- `scripts/validate_templates.py` — Template syntax and undeclared variable detection
- `scripts/validate_markdown.py` — Post-generation markdown validation (code block tags, syntax leaks)

### 2.4 Generation Orchestration Layer

**Location:** `scripts/generate_*.py`, `scripts/init_*.py`

**Responsibility:** Coordinate template rendering, merge configurations, write namespaced output

**Dependencies:** Configuration & Validation → Filter & Enrichment → Template Source → Utilities

**Key components:**
- `scripts/generate_docs.py` — Main orchestrator: loads config, sets up Jinja2 Environment, renders templates, writes output
- `scripts/generate_all.py` — Parallel batch generation across multiple repositories using `concurrent.futures`
- `scripts/generate_schema.py` — Generates JSON Schema from instruction registry
- `scripts/generate_schema_capabilities.py` — Generates JSON Schema from capability registry
- `scripts/init_framework.py` — New project initialiser with language defaults
- `scripts/add_language.py` — Adds language support to existing configurations
- `scripts/diff_changes.py` — Preview changes before regeneration

### 2.5 Filter & Enrichment Layer

**Location:** `scripts/filters.py`, `scripts/language_config.py`

**Responsibility:** Custom Jinja2 filters and configuration enrichment that bridge templates and configuration

**Dependencies:** Utilities (capabilities, instructions)

**Key components:**
- `scripts/filters.py` — `SmartContext` class wrapping config context; `_cmd_filter`, `_category_filter`, `_instructions_filter` for template variable resolution
- `scripts/language_config.py` — Language configuration utilities, scope validation, config file generation from `commands/*.yml.j2`

### 2.6 Utilities Layer

**Location:** `scripts/paths.py`, `scripts/capabilities.py`, `scripts/instructions.py`

**Responsibility:** Shared constants and registry data. No internal dependencies (leaf modules).

**Key components:**
- `scripts/paths.py` — Centralised path constants (`PROJECT_ROOT`, `TEMPLATE_DIR`, `SCHEMA_DIR`, `CONFIG_SCHEMA_PATH`, `COMMANDS_DIR`)
- `scripts/capabilities.py` — Capability registry, defaults, and template skip rules (`CAPABILITIES`, `DEFAULT_CAPABILITIES`, `TEMPLATE_SKIP_RULES`)
- `scripts/instructions.py` — Instruction registry (`INSTRUCTIONS`)

### 2.7 Server Layer

**Location:** `server/`

**Responsibility:** FastAPI HTTP application for the static config form UI. Exposes `POST /api/init` and `POST /api/generate`, serves `ui/` as static files, enforces security headers and CORS on all responses.

**Dependencies:** Generation Orchestration (`scripts/init_framework.render_config_string`, `scripts/generate_docs.generate_documentation_with_timing`), Configuration & Validation (`scripts/validate_config.validate_config_with_enhanced_errors`), Utilities (`scripts/paths.PROJECT_ROOT`)

**Key components:**
- `server/app.py` — `create_app(ui_dir=None)` factory; `SecurityHeadersMiddleware`; `CORSMiddleware` with explicit allowlist; custom `RequestValidationError` and `Exception` handlers; `POST /api/init` route; `POST /api/generate` route; static file mount at `/`
- `server/models.py` — `InitRequest(name, language)` and `GenerateRequest(config: dict)` Pydantic models
- `server/__init__.py` — Python package init; empty

**Patterns agents must follow:**

- **`create_app()` factory** — all FastAPI apps that mount a `StaticFiles` directory must use a factory function accepting an optional `ui_dir` parameter. This allows tests to override the directory without patching module state.
- **Explicit 405 route** — when `StaticFiles` is mounted at `/`, register an explicit `api_route` for all non-target HTTP methods on each API path. `StaticFiles` intercepts unmatched routes before FastAPI's default 405 handler fires.
- **`{"error": string}` contract** — all server error responses return `{"error": "<message>"}`. Override `RequestValidationError` to suppress FastAPI's default `{"detail": [...]}` structure. Generic `Exception` handler must log server-side and return a safe message with no internal detail.
- **CORS explicit allowlist** — register `CORSMiddleware` with a hardcoded origins list (no wildcard `*`), `allow_methods` restricted to the methods the endpoints accept, `allow_credentials` omitted (defaults `False`). Store origins as a module-level constant (`CORS_ORIGINS`) so tests and the app share the same list.
- **Two-directory temp lifecycle** — when a route needs two `TemporaryDirectory` instances, create both before the `try` block and call `.cleanup()` on each in the `finally` block. Do not use context managers for two directories — explicit cleanup gives independent control and matches the Decision 2 constraint that both dirs are deleted regardless of outcome.

### 2.8 Dependency Flow

Utilities → Filter & Enrichment → Generation Orchestration ← Configuration & Validation ← Template Source
Server Layer → Generation Orchestration (imports `render_config_string`, `generate_documentation_with_timing`) + Configuration & Validation (imports `validate_config_with_enhanced_errors`) + Utilities (imports `PROJECT_ROOT`)

**Direction:** Utilities provide constants (no dependencies). Filters use registries. Orchestration uses validated config + filters + templates to produce output. Validation reads templates and schema. Template Source is input-only. Server imports from Orchestration, Validation, and Utilities — it does not import from Filter layer.

---

## 3. Design Patterns

### 3.1 Overview

The engine employs four key patterns that define how configuration validates, enriches, and transforms into generated output.

### 3.2 Three-Layer Validation Pipeline

**Usage:** `scripts/validate_config.py`, `scripts/validate_templates.py`, `scripts/validate_markdown.py` run sequentially before and after generation

**Purpose:** Catch errors at the earliest possible stage — invalid config never reaches rendering, syntax errors never produce output, generated markdown verified for leaks

**Impact:** Validation failures halt generation with file-context error messages. No partial output.

**Example:**
1. `validate_config.py` checks YAML against `schema/config.schema.json` — catches missing fields, invalid types
2. `validate_templates.py` parses Jinja2 syntax and detects undeclared variables with file:line context
3. `validate_markdown.py` checks generated output for syntax leaks and malformed code blocks

### 3.3 SmartContext Filter Abstraction

**Usage:** `scripts/filters.py` defines `SmartContext` class and three custom Jinja2 filters registered to the Environment in `scripts/generate_docs.py`

**Purpose:** Decouple rendering from configuration structure. Filters handle scoping, lookups, and formatting so the rendering engine resolves commands transparently across mono-language and multi-language configurations.

**Impact:** Adding new configuration fields requires filter changes in `filters.py`, not changes across the rendering pipeline. `SmartContext` wraps the config dict and exposes `.cmd()`, `.category()`, `.instructions()` methods.

**Example:**
- `_cmd_filter` resolves a command key to its string, handling scope automatically (mono-language `test` vs multi-language `backend_test`)
- `_category_filter` returns all commands matching a category
- `_instructions_filter` formats instruction page references

### 3.4 Registry-Driven Schema Generation

**Usage:** `scripts/generate_schema.py` and `scripts/generate_schema_capabilities.py` generate JSON Schema properties from Python registry constants in `scripts/instructions.py` and `scripts/capabilities.py`

**Purpose:** Single source of truth for available capabilities and instructions. Registries define options; schema generation propagates them to validation.

**Impact:** Adding a new capability or instruction requires updating one registry constant. Running `npm run schema:generate` updates `config.schema.json` automatically.

**Example:** Adding `hasGraphQL` to `CAPABILITIES` in `capabilities.py` → regenerate schema → validation accepts the new property

### 3.5 Configuration Merging with Scope-Aware Naming

**Usage:** `scripts/language_config.py` merges language defaults from `commands/*.yml.j2` with repository configuration during initialisation

**Purpose:** Support both mono-language (scope: `all`) and multi-language (scope: `backend`, `frontend`) repositories with automatic command name scoping

**Impact:** `scripts/init_framework.py` and `scripts/add_language.py` use scope validation to prevent conflicts. Single-language repos get simple names (`test`); multi-language repos get prefixed names (`backend_test`, `frontend_test`).

---

## 4. Code Organisation

### 4.1 Overview

The engine code follows consistent conventions for file placement, naming, and responsibility boundaries.

### 4.2 Key Conventions

**File Naming:**
- Scripts use snake_case: `generate_docs.py`, `validate_templates.py`, `init_framework.py`
- One script per concern: generation, validation, initialisation, schema generation each in separate files
- Prefix groups related scripts: `generate_*.py` (generation), `validate_*.py` (validation), `init_*.py` (initialisation)

**Script Responsibility:**
- `generate_*.py` — Produce output (docs, schema, batch)
- `validate_*.py` — Check correctness (config, templates, markdown)
- `init_*.py` — Set up new projects
- Single-purpose utilities — `paths.py`, `capabilities.py`, `instructions.py`, `filters.py`, `language_config.py`

**Import Pattern:**
- All internal imports use `from scripts.{module}` (absolute, never relative)
- Tests import from `scripts.` treating the package as an external module

### 4.3 Directory Layout

```
scripts/                      # Engine code (16 files, ~2,900 LOC)
├── generate_docs.py          # Main rendering orchestrator
├── generate_all.py           # Parallel batch generation
├── generate_schema.py        # Schema from instruction registry
├── generate_schema_capabilities.py  # Schema from capability registry
├── validate_config.py        # YAML config validation
├── validate_templates.py     # Template syntax validation
├── validate_markdown.py      # Generated output validation
├── init_framework.py         # New project initialiser
├── add_language.py           # Multi-language support
├── diff_changes.py           # Change preview utility
├── filters.py                # SmartContext + Jinja2 filters
├── language_config.py        # Language config utilities
├── paths.py                  # Centralised path constants
├── capabilities.py           # Capability registry
├── instructions.py           # Instruction registry
└── __init__.py               # Package init

schema/                       # Validation schema
└── config.schema.json        # JSON Schema (single source)

commands/                     # Language command defaults
├── python.yml.j2
├── typescript.yml.j2
├── typescript-npm.yml.j2
├── go.yml.j2
└── swift.yml.j2

build-scripts/                # Build utilities
└── validate_docs.py          # Documentation validation

server/                       # FastAPI HTTP server (config form)
├── app.py                    # Application factory, middleware, routes
├── models.py                 # Pydantic request models
└── __init__.py               # Package init

ui/                           # Static files served by server/app.py
└── languages.json            # Built by scripts/build_ui_manifest.py
```

---

## 5. Architectural Constraints

### 5.1 Overview

Constraints and conventions that engine code must follow to maintain system integrity.

### 5.2 Dependency Rules

- Scripts import utilities using `from scripts.{module}` pattern — no relative imports
- Generation scripts depend on validation layer (validate before rendering)
- Utilities have no internal dependencies (leaf modules)
- Tests import from `scripts.` (treat as external package)
- No circular dependencies between modules

### 5.3 Boundary Rules

- Generated output isolated to namespaced directories (`agentic-framework/` or `agents/{name}/`)
- `instructions/` subfolder never regenerated — client-maintained, preserved across regeneration
- `base/` templates never generated directly — inheritance only
- Configuration validation occurs before rendering begins

### 5.4 Error Handling

Fail fast with specific exceptions and clear error messages indicating fix location.

**Patterns:**
- `ValueError` — Invalid configuration or constraint violations (scope conflicts, missing sections)
- `KeyError` — Missing required keys (commands, instructions, language mappings)
- `FileNotFoundError` — Missing files (config, language defaults)
- `UndefinedError` — Undefined template variables (with file context and config hint)
- `TemplateError` — Template syntax errors (with line numbers)

### 5.5 Configuration

All configuration accessed through validated `.agentic-framework.yml` — no environment variables, no hard-coded values.

**Rules:**
- JSON Schema validation before use
- Defaults merged from `scripts/capabilities.py` for missing capability flags
- Language defaults merged from `commands/{language}.yml.j2` during initialisation
- Configuration never mutated after validation (read-only after load)

### 5.6 Idempotency

Generation must be repeatable without side effects.

**Rules:**
- Old `.md` files removed before generation (clean slate)
- `instructions/` preserved (never regenerated)
- Metadata updated in config file after generation (timestamp, version)
- Same config + same templates = identical output

---

## 6. Communication Patterns

### 6.1 Overview

The engine uses synchronous, file-based communication. Configuration flows through validation into rendering, producing markdown files as output. All inter-module communication uses direct function calls with explicit imports.

### 6.2 Generation Pipeline Flow

**Description:** YAML configuration drives all generation through a sequential pipeline

**Flow:**
1. User runs `npm run generate -- {repo-name}`
2. npm script invokes Python: `venv/bin/python scripts/generate_docs.py`
3. `generate_docs.py` loads and validates config against JSON Schema
4. Language defaults merged with config (initialisation only)
5. Jinja2 Environment created with `StrictUndefined` and custom filters from `filters.py`
6. Templates rendered with config context, capability conditionals applied
7. Markdown files written to namespaced output directory
8. Metadata appended to config file (timestamp, framework version)

### 6.3 Module Communication

**Description:** Python modules communicate through direct function calls with `from scripts.{module}` imports

**Patterns:**
- `generate_docs.py` calls `validate_config()` → receives validated dict
- `generate_docs.py` imports `SmartContext` from `filters.py` → wraps config for filter access
- `generate_docs.py` imports constants from `paths.py` → `TEMPLATE_DIR`, `CONFIG_SCHEMA_PATH`
- Functions return values synchronously — no callbacks, no async, no event emitters
- Type hints document contracts (`Path`, `dict`, `Environment`)

### 6.4 CLI Interface via npm Scripts

**Description:** npm scripts provide the user-facing interface, delegating to Python scripts via shell

**Flow:**
1. User runs npm command (e.g. `npm run generate -- agentic-framework`)
2. npm invokes bash script with arguments
3. Bash script calls Python with `PYTHONPATH=.` and appropriate flags
4. Python script returns exit code (0 success, 1 failure)
5. Output displayed to terminal (validation errors, generation summary)

### 6.5 Batch Generation via Worker Pool

**Description:** `scripts/generate_all.py` processes multiple repositories in parallel using `concurrent.futures`

**Flow:**
1. Reads manifest file listing repository configs
2. Creates `ProcessPoolExecutor` with configurable workers
3. Each worker calls `generate_single_repo()` independently
4. Workers return error tuples instead of raising exceptions
5. Orchestrator collects results and reports summary

---

## 7. Testing Framework

### 7.1 Overview

pytest with unit and integration test coverage. Tests verify configuration validation, rendering, CLI entry points, and error handling across the engine code.

### 7.2 Test Organisation

**Unit tests:** `tests/` (root level) and `tests/scripts/` — test individual functions and modules in isolation. Run with `npm run test:python:unit`. Tests without `@pytest.mark.integration` marker.

**Integration tests:** Mixed with unit tests, marked with `@pytest.mark.integration` — test full generation pipeline with real templates and file I/O. Run with `npm run test:python:integration`.

Test files mirror script structure: `tests/scripts/test_add_language.py` tests `scripts/add_language.py`.

### 7.3 Test Utilities

**Factories:** `tests/helpers/config_factory.py` — creates valid/invalid test configurations programmatically. Key functions: `create_standard_config(language)`, `create_valid_config()`, `_build_instructions_for_capabilities()`.

**Fixtures:** `tests/conftest.py` — reusable test data. Key fixtures: `complete_python_config`, `complete_typescript_config`, `tmp_path` (pytest built-in for temporary directories).

### 7.4 Testing Patterns

**CLI testing:** Use `monkeypatch` to mock `sys.argv` and test CLI entry points. Return exit codes, not exceptions.

**Error path testing:** Use `pytest.raises` to assert exceptions and verify error messages contain fix-location context.

**Parallel processing testing:** Worker functions return error tuples instead of raising exceptions. Tests verify mixed success/failure batch scenarios.

### 7.5 Coverage Requirements

- Line coverage: ≥90%
- Function coverage: ≥90%
- Branch coverage: ≥70%
- Coverage report: `npm run test:python:coverage`
- Configuration in `pyproject.toml`

---

## 10. Compliance Gates

> Delivery and review skills verify these gates. Each gate must pass for code touching this domain.

- [ ] **CG-1:** Same configuration produces identical output on every run — engine changes must preserve idempotent generation (§1.4, §5.6)
- [ ] **CG-2:** New configuration fields require corresponding JSON Schema updates via registry constants — schema generated from `capabilities.py` and `instructions.py` (§3.4)
- [ ] **CG-3:** Engine code never writes to or overwrites files in `instructions/` — client-maintained, preserved across regeneration (§5.3)
- [ ] **CG-4:** Generated output writes only to the target namespace directory — no files outside `agentic-framework/` or `agents/{name}/` (§5.3)
- [ ] **CG-5:** Engine generates documentation only — no modification of repository source code (§1.1)
- [ ] **CG-6:** Scripts import utilities using `from scripts.{module}` pattern — no relative imports, no circular dependencies (§5.2)
- [ ] **CG-7:** Configuration validated against JSON Schema before template rendering begins — no rendering of unvalidated config (§3.2, §5.5)

---

## 8. Examples

### 8.1 Adding a New Capability Flag

1. Add entry to `CAPABILITIES` dict in `scripts/capabilities.py`
2. Run `npm run schema:generate` — updates `schema/config.schema.json`
3. Templates can now use `{% if capabilities.newFlag %}` conditionals
4. To gate a `rules/` template on the new capability, add an entry to `TEMPLATE_SKIP_RULES` in `scripts/capabilities.py` — no changes to `scripts/generate_docs.py` required

**Decision points:** Should capability default to `true` or `false`? Which templates need conditional sections?

### 8.2 Adding a New Language

1. Create `commands/{language}.yml.j2` with core commands (test, lint, typecheck)
2. Run `npm run language:add` — merges defaults into target config
3. Scope validation in `scripts/language_config.py` prevents naming conflicts
4. Multi-language configs get prefixed commands automatically

**Decision points:** Which commands are core vs optional? What scope identifier to use?

### 8.3 Adding a New Validation Rule

1. Update `schema/config.schema.json` with new constraints (or regenerate from registries)
2. Add validation logic to `scripts/validate_config.py` if schema insufficient
3. Run `npm run validate:templates -- --strict` to verify
4. Failed validation halts generation — error messages include fix location

**Decision points:** Can constraint be expressed in JSON Schema, or requires custom Python validation? Should violation be error (halt) or warning?

---

## 9. File References

### 9.1 Entry Points

- [scripts/generate_docs.py](scripts/generate_docs.py) — Main generation orchestrator. Start here to understand the rendering pipeline.
- [scripts/init_framework.py](scripts/init_framework.py) — Project initialisation. Demonstrates config creation and language merging.
- [package.json](package.json) — npm scripts interface. Shows all available commands.

### 9.2 Core Configuration

- [schema/config.schema.json](schema/config.schema.json) — JSON Schema defining valid configuration structure
- [commands/python.yml.j2](commands/python.yml.j2) — Representative language defaults file

### 9.3 Validation Pipeline

- [scripts/validate_config.py](scripts/validate_config.py) — Configuration validation against JSON Schema
- [scripts/validate_templates.py](scripts/validate_templates.py) — Template syntax and variable validation
- [scripts/validate_markdown.py](scripts/validate_markdown.py) — Generated output validation

### 9.4 Filter System

- [scripts/filters.py](scripts/filters.py) — SmartContext class and custom Jinja2 filters
- [scripts/language_config.py](scripts/language_config.py) — Language configuration and scope utilities

### 9.5 Registries

- [scripts/capabilities.py](scripts/capabilities.py) — Capability registry, defaults, and template skip rules
- [scripts/instructions.py](scripts/instructions.py) — Instruction registry
- [scripts/paths.py](scripts/paths.py) — Centralised path constants

### 9.6 Testing

- [tests/helpers/config_factory.py](tests/helpers/config_factory.py) — Test configuration factories
- [tests/conftest.py](tests/conftest.py) — Shared fixtures
- [pyproject.toml](pyproject.toml) — Pytest configuration, markers, coverage settings

---
**END OF DOCUMENT:** Total sections: 10 | Purpose: Repository architecture and design patterns | Last updated: 03/04/2026 (Stage 3)
