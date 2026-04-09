"""Shared test fixtures for template validation tests."""

import pytest


@pytest.fixture
def complete_python_config():
    """
    Complete config fixture with all common commands for Python projects.

    This prevents spurious validation failures when templates reference
    commands that minimal test configs don't include.
    """
    return {
        "name": "test-repo",
        "repo": {
            "name": "TestRepo",
            "language": "python",
            "description": "Test repository",
        },
        "capabilities": {
            "hasUI": False,
            "hasDB": False,
        },
        "commands": {
            # Testing commands
            "test": {
                "command": "pytest",
                "description": "Run all tests",
                "category": "test",
            },
            "test_unit": {
                "command": "pytest tests/unit/",
                "description": "Run unit tests only",
                "category": "test",
            },
            "test_integration": {
                "command": "pytest tests/integration/",
                "description": "Run integration tests only",
                "category": "test",
            },
            "test_coverage": {
                "command": "pytest --cov=scripts",
                "description": "Run tests with coverage report",
                "category": "test",
            },
            # Quality commands
            "lint": {
                "command": "ruff check scripts/ tests/",
                "description": "Run linter for code quality",
                "category": "quality",
            },
            "lint_fix": {
                "command": "ruff check scripts/ tests/ --fix",
                "description": "Auto-fix linting issues",
                "category": "quality",
            },
            "lint_markdown": {
                "command": "markdownlint *.md",
                "description": "Lint Markdown files",
                "category": "quality",
            },
            "typecheck": {
                "command": "mypy scripts/ tests/",
                "description": "Run type checker",
                "category": "quality",
            },
            "format": {
                "command": "black scripts/ tests/",
                "description": "Format Python code",
                "category": "format",
            },
            "format_check": {
                "command": "black --check scripts/ tests/",
                "description": "Check Python code formatting",
                "category": "format",
            },
            # Combined commands
            "check_all": {
                "command": "npm run test && npm run lint && npm run typecheck",
                "description": "Run all quality checks",
                "category": "utilities",
            },
            "fix_all": {
                "command": "npm run format && npm run lint:fix",
                "description": "Auto-fix all issues",
                "category": "utilities",
            },
            "check_links": {
                "command": "markdown-link-check *.md",
                "description": "Check Markdown links",
                "category": "utilities",
            },
            # Build and delivery
            "build": {
                "command": "python -m build",
                "description": "Build Python package",
                "category": "build",
            },
            "docs": {
                "command": "python scripts/generate_docs.py",
                "description": "Generate documentation",
                "category": "documentation",
            },
        },
        "metadata": {
            "framework_version": "1.0.0",
            "generated_at": "2026-01-10T00:00:00Z",
        },
    }


@pytest.fixture
def complete_typescript_config():
    """
    Complete config fixture with all common commands for TypeScript projects.

    This prevents spurious validation failures when templates reference
    commands that minimal test configs don't include.
    """
    return {
        "name": "test-repo",
        "repo": {
            "name": "TestRepo",
            "language": "typescript",
            "description": "Test repository",
        },
        "capabilities": {
            "hasUI": True,
            "hasDB": False,
        },
        "commands": {
            # Testing commands
            "test": {
                "command": "npm test",
                "description": "Run all tests",
                "category": "test",
            },
            "test_unit": {
                "command": "npm run test:unit",
                "description": "Run unit tests only",
                "category": "test",
            },
            "test_integration": {
                "command": "npm run test:integration",
                "description": "Run integration tests only",
                "category": "test",
            },
            "test_coverage": {
                "command": "npm run test:coverage",
                "description": "Run tests with coverage report",
                "category": "test",
            },
            # Quality commands
            "lint": {
                "command": "eslint src/",
                "description": "Run linter for code quality",
                "category": "quality",
            },
            "lint_fix": {
                "command": "eslint src/ --fix",
                "description": "Auto-fix linting issues",
                "category": "quality",
            },
            "lint_markdown": {
                "command": "markdownlint *.md",
                "description": "Lint Markdown files",
                "category": "quality",
            },
            "typecheck": {
                "command": "tsc --noEmit",
                "description": "Run type checker",
                "category": "quality",
            },
            "format": {
                "command": "prettier --write src/",
                "description": "Format TypeScript code",
                "category": "format",
            },
            "format_check": {
                "command": "prettier --check src/",
                "description": "Check TypeScript code formatting",
                "category": "format",
            },
            # Combined commands
            "check_all": {
                "command": "npm run test && npm run lint && npm run typecheck",
                "description": "Run all quality checks",
                "category": "utilities",
            },
            "fix_all": {
                "command": "npm run format && npm run lint:fix",
                "description": "Auto-fix all issues",
                "category": "utilities",
            },
            "check_links": {
                "command": "markdown-link-check *.md",
                "description": "Check Markdown links",
                "category": "utilities",
            },
            # Build and delivery
            "build": {
                "command": "npm run build",
                "description": "Build TypeScript project",
                "category": "build",
            },
            "dev": {
                "command": "npm run dev",
                "description": "Start development server",
                "category": "development",
            },
            "docs": {
                "command": "npm run docs:generate",
                "description": "Generate documentation",
                "category": "documentation",
            },
        },
        "metadata": {
            "framework_version": "1.0.0",
            "generated_at": "2026-01-10T00:00:00Z",
        },
    }
