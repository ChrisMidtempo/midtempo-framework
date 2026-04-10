# Midtempo Framework

> You can generate a complete set of framework docs at [midtempo.com](https://midtempo.com) if you'd rather avoid the overhead of installing the repo.

## What this is
A constraint-first framework for LLM-assisted development on real codebases. It assumes the engineer remains responsible for everything that ships, and makes that responsibility sustainable.

### The principles

#### - You stay in control
No agent access to git. Human approval at every phase - design, plan, tests, code. Documentation arrives in digestible sections you sign off on, not walls of text to rubber-stamp afterwards.

#### - External tools do the validating
The agent answers to tools that can't be charmed. Clean lint, clean types, clean tests, every run - no exceptions, no pre-existing noise to hide behind. High coverage thresholds catch unapproved code generated outside the TDD loop.

#### - Process before code
Design → delivery plan → test manifest → implementation. TDD always, no exceptions, no "simple tweaks." Each task starts in a fresh conversation and stops before context compaction degrades instruction fidelity.

#### - Repository-grounded
A structured setup dialogue produces docs describing what this codebase actually is - purpose, architecture, patterns - so every conversation starts grounded. Security gates adapt to the repo's risk profile across five domains: authn/authz, secrets, input validation, data protection, and public hardening. Repository-specific instructions survive regeneration when the framework updates, or org standards evolve.

#### - Work compounds
New tasks review prior planning docs in the same domain; completed work updates them. Decisions, patterns, and lessons carry across fresh conversations rather than being lost.

#### - Universal by design
Pure markdown skills, no executable framework code. Language- and IDE-agnostic. One YAML config drives capabilities, commands, and conditional content. One framework per repository - team standards, not individual preferences.

## Why it exists

LLMs cannot reliably self-regulate. External validation catches errors, process discipline prevents drift, approval gates keep judgement with the engineer, and repository context means nothing is lost between conversations.

The framework enforces what matters. You decide what ships.

---

# This Repo

This environment uses a Jinja2 templating system to generate repository-specific agent instructions. One YAML config produces complete agent skill files tailored to each repository's language, capabilities, and tooling.

#### Templates
The templates are in `jinja-templates/` and there's a grounded framework that works for this repo in `midtempo-framework/`.

#### Examples
Examples of the delivery documents the framework generates are in `planning/EXAMPLE-*.md` (order is: decisions > design > plan > test)

>  The framework docs are markdown. Viewing .md files is much easier in preview mode, or with an extension like "Markdown Preview Github Styling"

## Features

- **Single source of truth** - Update templates once, generate for all repositories
- **Multi-language support** - Python, TypeScript, extensible via `commands/*.yml.j2`
- **Config-driven** - YAML controls conditional content (UI, database, type checking)
- **Validation** - Schema validation, template syntax checking, markdown linting
- **Idempotent** - Same config produces identical output every run

## Prerequisites

See [SETUP.md](/SETUP.md) for installation and environment setup.

---

## Commands

### Create New Framework

Initialise a new config to create a `midtempo-framework.yml` file. This defines the project's language, capabilities (UI, database), and tooling commands. The service then uses this .yml file to generate (and re-generate) the tailored docs for each repo.

```bash
npm run init agents/[repo-name] [language]
```

**Example:**
```bash
npm run init agents/my-service python
```

Creates `agents/my-service/midtempo-framework.yml` with language-specific defaults.

**Supported languages:** In `commands/*.yml.j2` (currently `python`, `typescript`, `typescript-npm`, `go-lang`)

---

### Generate Framework

Generate agent documentation from our config file. This reads the `midtempo-framework.yml` and produces a complete set of agent skills, rules, and templates customised to each repository. 

```bash
npm run generate [repo-name]
```

**Examples:**
```bash
npm run generate my-service
npm run generate midtempo-framework
```

Output writes to `agents/[repo-name]/` with all agent skills, rules, templates, and setup services.

> EXCEPTION
>
> - "midtempo-framework" writes to `/midtempo-framework/`
>
> - This enables instant and self-referential skill updates for this repo as the framework improves

---

### Add Language to Repository 

Add a language to an existing config. Use this when a repository grows to include multiple languages (e.g., adding a TypeScript frontend to a Python backend). The framework handles command scoping automatically - prefixing commands like `test` with scope identifiers like `backend_test` and `frontend_test` to avoid conflicts.

```bash
npm run language:add -- --repo [name] --language [lang] --new-scope [scope] [--existing-scope [scope]]
```

**Single-language → Multi-language:**
```bash
npm run language:add -- --repo my-service --language typescript --new-scope frontend --existing-scope backend
```

Transforms `test` → `backend_test`, adds `frontend_test`.

**Multi-language → Multi-language:**
```bash
npm run language:add -- --repo my-service --language rust --new-scope services
```

Adds scoped commands without modifying existing ones.

---

### Validation

Run validation checks before committing changes. Template validation catches Jinja2 syntax errors early. Markdown linting ensures generated documentation follows consistent formatting. Link checking verifies all internal references resolve correctly.

**Validate template syntax:**
```bash
npm run validate:templates
```

**Validate markdown output:**
```bash
npm run lint:markdown
```

**Check markdown links:**
```bash
npm run check:links
```

**Run all checks:**
```bash
npm run check:all
```

---

### Batch Generation

Generate documentation for multiple repositories in a single operation. Define repositories in a manifest file (`repos-manifest.yml`) with paths to each config and output directory. The framework processes repositories in parallel, making it possible to update dozens or hundreds of projects at once.

```bash
npm run generate:all
```

Uses `repos-manifest.yml` to process repositories in parallel.

---

### Schema Generation

Update the JSON Schema that validates configuration files. The schema is generated from the capability registry in `scripts/capabilities.py`, which defines available capabilities like `hasUI` and `hasDB`. When you add or modify capabilities, regenerate the schema to keep validation rules in sync.

```bash
npm run schema:generate
```

Run after modifying `scripts/capabilities.py` to sync `schema/config.schema.json`.

### Adding a Conditional Template

To gate a `rules/` template on a capability, add one entry to `TEMPLATE_SKIP_RULES` in `scripts/capabilities.py` - no changes to `scripts/generate_docs.py` required.

```python
# scripts/capabilities.py
TEMPLATE_SKIP_RULES: dict[str, str | list[str]] = {
    "rules/my-new-rule": "myCapabilityKey",          # skip if capability is false
    "rules/ui-and-db-rule": ["hasUI", "hasDB"],       # skip if both are false
}
```

Single-key entries skip the template when the named capability is falsy. Multi-key (list) entries skip when all listed capabilities are falsy - the template generates if any one is true.

---

### Testing

Run the test suite to verify template rendering, config validation, and generation logic. The tests cover schema validation, Jinja2 template syntax, markdown output formatting, and end-to-end generation workflows.

```bash
npm run test:python              # Run tests
npm run test:python [fileName]   # Run a single test
npm run test:python:coverage     # Run tests with coverage report
```

Coverage reports write to `htmlcov/`.

---

### Add Language to Framework

Extend the framework to support a new programming language. This differs from "Add Language to Repository" - here you're adding system-wide support so any repository can use the new language. You create a command template that defines language-specific defaults (test commands, linting, type checking) that get applied when someone initialises a project with that language.

1. Create `commands/[language].yml.j2` with command defaults
2. Include `{{ base_config }}` placeholder for schema-required fields
3. Define `commands`, `instructions`, and language-specific settings
4. Test: `npm run init agents/test-project [language]`
5. Verify: `npm run generate test-project`

See existing templates in `commands/` for structure examples.

---

## Documentation

Detailed guides for specific topics. The README covers common operations; these documents provide deeper reference material.

| Document | Purpose |
|----------|---------|
| [SETUP.md](SETUP.md) | Installation and environment setup |
| [jinja-templates/template-authoring.md](jinja-templates/template-authoring.md) | Template syntax, filters, and patterns |
| [schema/config.schema.json](schema/config.schema.json) | Configuration schema reference |
| [README.md](midtempo-framework/README.md) | Example client README -  usage overview |
| [GUIDE.md](midtempo-framework/GUIDE.md) | Example client GUIDE - explanation of the framework's concepts and thinking |
| [INSTALL.md](midtempo-framework/INSTALL.md) | Example client install instructions |

---

## Maintaining Compliance Gates

Rules files (`jinja-templates/rules/*.md.j2`) define compliance gates - numbered CG-N checklists that agents verify during delivery and review. When a rules file's gates change, dependent macros in `jinja-templates/macros.j2` must also be updated.

**Testing gates dependency chain:**

| Source of truth | Compact form | Range string |
|-----------------|-------------|--------------|
| `rules/testing.md.j2` - full CG definitions | `testing_compliance_gates_summary()` in `macros.j2` | `testing_cg_range()` in `macros.j2` |

**When changing testing compliance gates:**

1. Update `jinja-templates/rules/testing.md.j2` (canonical definitions)
2. Update `testing_compliance_gates_summary()` macro (compact form used by 4+ skills)
3. Update `testing_cg_range()` macro (range string, e.g. "CG-1 through CG-7")
4. Regenerate: `npm run generate -- [repo-name]`
5. Run tests: `npm run test:python`

All consuming templates pick up changes automatically through the macros - no further edits needed.

For macro API details, see [template-authoring.md §5.17–5.19](jinja-templates/template-authoring.md#517-verify_rules_compliance_gates-macro--rules-file-exit-gate-verification).

---

## Project Structure

Key directories and their purposes. Templates live in `jinja-templates/`, language defaults in `commands/`, and generation logic in `scripts/`.

```
midtempo.framework/
├── jinja-templates/        # Jinja2 source templates
│   ├── agents/             # Agent skill templates
│   ├── rules/              # Rule templates
│   ├── templates/          # Document templates
│   └── setup-skills/       # Setup stage templates
├── commands/               # Language command defaults
│   ├── python.yml.j2
│   └── typescript.yml.j2
├── scripts/                # Generation and validation
├── server/                 # FastAPI server (config form UI)
│   ├── app.py              # Application, routes, middleware
│   └── models.py           # Pydantic request models
├── schema/                 # JSON Schema definitions
└── tests/                  # Test suite
```

