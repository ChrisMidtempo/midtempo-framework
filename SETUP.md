# Development Setup Guide

## ⛔ Preliminary Gate: AGENTS.md/CLAUDE.md Check

**STOP. Before proceeding with setup:**

1. **Check if AGENTS.md/CLAUDE.md exists in the root directory** of this repository
2. **Verify it contains the framework rules** (starts with "# Agent Rules" and includes sections for Pre-Action Gate, Iron Laws, Workflow, Skill Router, etc.)

---

## Prerequisites

- Python 3.9 or higher
- Node.js and npm
- Git

### Why both Python and Node?

Python is the primary language for the templating system. All core functionality is Python-based:

- Jinja2 templating for document generation (scripts/generate_docs.py)
- Config validation 
- Batch generation for multiple repos

npm also provides markdown quality tools:

"devDependencies": {
  "markdownlint-cli": "^0.39.0",
  "markdown-link-check": "^3.12.0"
}

These are used via npm scripts to validate the output of the templating system (checking markdown syntax and validating links).

**Why This Approach?**

I wanted to test multi-lingual agent configurations AND use npm on a python repo as a "context canary" - when the agent starts calling mypy or pytest, I know it's losing fidelity and/or the instructions aren't strong enough.

## Initial Setup

### 1. Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Node Dependencies

```bash
npm install
```

## Development Workflow

### Linting and Formatting

```bash
# Format Python code
npm run format:python

# Check Python formatting (without modifying files)
npm run format:python:check

# Lint Python code
npm run lint:python

# Auto-fix Python linting issues
npm run lint:python:fix

# Type check Python code
npm run typecheck:python

# Lint Markdown files
npm run lint:markdown

# Check Markdown links
npm run check:links
```

### Testing

```bash
# Run all tests
npm run test:python

# Run tests with coverage report
npm run test:python:coverage
```

### Quality Gates (Run Before Commit)

```bash
# Run all checks (format, lint, typecheck, test, markdown)
npm run check:all

# Auto-fix issues where possible
npm run fix:all
```

## Tool Configuration

All tool configurations are in [pyproject.toml](pyproject.toml):

- **Black**: Code formatter (line length: 100)
- **Ruff**: Fast Python linter (replaces flake8, isort, etc.)
- **mypy**: Static type checker (strict mode enabled)
- **pytest**: Test runner with coverage

## Pre-commit Checklist

Before committing code, ensure:

1. [ ] `npm run format:python` - Code is formatted
2. [ ] `npm run lint:python` - No linting errors
3. [ ] `npm run typecheck:python` - No type errors
4. [ ] `npm run test:python` - All tests passing
5. [ ] `npm run lint:markdown` - Documentation is valid

Or simply run: `npm run check:all`

## Troubleshooting

### Virtual environment not activated

If you see "command not found" errors for Python tools, activate the virtual environment:

```bash
source venv/bin/activate
```

### Missing dependencies

If you see import errors, reinstall dependencies:

```bash
pip install -r requirements.txt
```

### Type checking errors for third-party libraries

If mypy complains about missing stubs for a library, add the type stubs package:

```bash
pip install types-<library-name>
```
