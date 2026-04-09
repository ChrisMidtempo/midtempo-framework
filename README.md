# Midtempo Framework

> You can generate complete framework docs at [midtempo.com](https://midtempo.com) if you'd rather avoid CLI / the overhead of another repo.

## What does this solve?

**The Problem**
LLMs hallucinate, drift from instructions as context grows, and optimise for task completion rather than correctness. They lose knowledge between conversations and cannot validate their own output. Increasing agent autonomy amplifies these failures.

**The Solution**
A constraint-first framework that contains these failures by enforcing what LLMs cannot do themselves: validating output, maintaining standards, preserving knowledge, and respecting boundaries. The engineer stays responsible. The framework makes that sustainable.

## The Core Principles

### 1. **Developer Sovereignty**
- You own the code - No agent access to git. All commits, pushes, and PRs require explicit human action.
- You approve the work - Human gates at every workflow phase. No autonomous decisions on architecture, approach, or scope.
- You understand the work - Documentation presented in digestible sections requiring approval before proceeding. No massive docs to review after the fact.
 
Understanding is encouraged - designs are presented in small sections (200-300 words) with multiple approaches, trade-off analysis, and devil's advocate checks. 

One framework per repository - not per-user. Team-wide standards, not individual preferences.

### 2. **External Validation**
- LLMs cannot self-validate - Context drift, hallucination, and statistical pattern matching make self-assessment impossible and dangerous.
- Zero tolerance for failures - Unit tests, linting, type checking, and doc generation must run clean (zero errors AND warnings). Any pre-existing issue becomes an excuse for the LLM to ignore rules.
- Coverage enforcement - TDD combined with low coverage metrics indicates the agent generated unapproved code during implementation. High coverage thresholds catch this immediately.
- Mechanical rule enforcement - Linters, type checkers, and test frameworks provide objective, consistent validation every run.

### 3. **Process Discipline**
- Test-Driven Development always - No production code without a failing test first. No exceptions.
- Documentation before implementation - Design → Delivery Plan → Test Manifest → Code. Understanding precedes action.
- Fresh conversations per task - Each task starts in a new conversation to prevent context drift and instruction decay. Stop before compaction/summarisation occurs.
- No instant fixes - Every code change requires prior documentation and TDD workflow, even "simple" tweaks.

### 4. **Universal Design**
- Pure markdown - No executable code in the framework itself. Skills are instructions, not scripts.
- Language agnostic - Python, TypeScript, Go, Rust, Swift. Any language with testing and linting.
- IDE independent - Works with Claude Code, Continue, Cursor, or any LLM interface. No proprietary integrations.
- Config-driven - One YAML file controls capabilities, commands, and conditional content. Idempotent regeneration.
- Organisation and team standards - Regenerate from updated settings or templates whilst preserving repository-specific instructions.

### 5. **Safety by Design**
- Command standardisation - Enforcing auto-approved commands prevents permission fatigue and approval blindness.
- Complexity constraints - Functions ≤75 lines, files ≤500 lines, cyclomatic complexity ≤10. Shorter, simpler code is safer, reviewable code.
- Immutable workflows - Iron laws (TDD, refactor-on-green, root-cause bug fixes) cannot be waived.
- Conversation boundaries - Context compaction destroys instruction fidelity. Stop and restart rather than continue with degraded context.
- Understanding before evaluation - Understanding before evaluation - Code, test, and architecture reviews verify implementation matches documented intent and repo rules, preventing "looks fine" approvals of incorrectly-solved problems.

### 6. **Repository Context**
- Agent grounding - Structured setup dialogue creates repository-specific documentation (purpose, architecture, patterns) that grounds every conversation in what this codebase actually does.
- Contextual security - Security rules adapt to capabilities and risk profile. High-risk services (authentication, confidential data, public-facing) trigger additional domain-specific validation gates.
- Security domain coverage - Five compliance gate sets enforced at delivery: authentication & authorisation, secrets management, input validation & output encoding, data protection, and public hardening. Enhanced gates within each domain activate automatically when confidential data handling or public-facing exposure is configured.
- Preserved knowledge - Repository-specific instructions survive framework regeneration. Update org-wide standards without losing local context.
- Consistent patterns - Organisation-level rules (TDD enforcement, database access patterns, error handling) applied uniformly across all repositories.
- Work builds on work - New tasks review prior planning documentation in the same domain (`planning/`), completed work updates those docs. Context, patterns, decisions, and lessons learned compound across fresh conversations - nothing is ever lost.

## **Why This Matters**

Engineers remain responsible for code quality under all circumstances. This framework makes that responsibility sustainable by solving the self-regulation LLM problem.

External validation catches hallucinations. Process discipline prevents drift and shortcuts. Approval gates maintain control. Repository context compounds knowledge across conversations - nothing is lost.

The result: safe, effective, maintainable LLM-assisted workflow with maximum capability and sustained responsibility. No compromises on velocity or judgement.

**The framework enforces what matters. You decide what ships.**

---

# This Repo

This environment uses a Jinja2 templating system to generate repository-specific agent instructions. One YAML config produces complete agent skill files tailored to each repository's language, capabilities, and tooling.

The templates are in `jinja-templates/` and there's a working version for this service in `midtempo-framework/`.

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

