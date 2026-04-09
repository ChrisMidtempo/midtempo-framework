# Agentic Framework Purpose

## Table of Contents

- [System Identity](#1-system-identity)
  - [Overview](#11-overview)
  - [Core Mechanism](#12-core-mechanism)
  - [Output](#13-output)
- [What This System Does](#2-what-this-system-does)
  - [Primary Capabilities](#21-primary-capabilities)
  - [Inputs](#22-inputs)
  - [Outputs](#23-outputs)
- [How It Works](#3-how-it-works)
  - [Process Flow](#31-process-flow)
  - [Key Components](#32-key-components)
- [System Boundaries](#4-system-boundaries)
  - [The System DOES](#41-the-system-does)
  - [The System Does NOT](#42-the-system-does-not)
---

## 1. System Identity

### 1.1 Overview

Agentic Framework is a Jinja2 templating system that generates repository-specific AI agent workflow documentation. A single YAML configuration produces a complete set of agent skill files tailored to a repository's language, capabilities, and tooling.

**Scope of this document:** This purpose document covers the **generation engine** — Python scripts (`scripts/`), JSON Schema (`schema/`), and configuration validation. Template files (`.j2`) are managed through separate instruction skills: `instructions/template-editing.md` for editing existing templates and `instructions/new-template.md` for creating new ones.

### 1.2 Core mechanism

Jinja2 templating + YAML configuration + Python generation scripts + JSON Schema validation + centralised macro library

### 1.3 Output

Complete agent workflow documentation — skill files, rules, setup stages, and document templates — written to namespaced directories with generation metadata

---

## 2. What This System Does

### 2.1 Primary capabilities

- Generate agent workflow documentation from Jinja2 templates with conditional inclusion based on repository capabilities (UI, database, type checking)
- Validate configurations against JSON Schema and template syntax before generation
- Initialise new project configurations with language-specific command defaults (Python, TypeScript, Go, Swift)
- Add languages to existing configurations with automatic command scoping (single→multi or multi→multi)
- Process multiple repositories in parallel via batch generation with configurable workers
- Centralise reusable patterns through a macro library consumed by all skill templates

### 2.2 Inputs

`agentic-framework.yml` configuration files, Jinja2 templates (`agents/`, `rules/`, `templates/`, `setup-skills/`), language command defaults (`commands/*.yml.j2`), JSON Schema (`schema/config.schema.json`)

### 2.3 Outputs

Namespaced documentation directories containing agent skill files, rule documents, setup stage guides, document templates, and regeneration metadata

---

## 3. How It Works

### 3.1 Process flow

1. Load YAML configuration and validate against JSON Schema
2. Validate Jinja2 template syntax and detect unused variables
3. Load language-specific command defaults and merge with configuration
4. Render templates with configuration context, applying conditional inclusion (hasUI, hasDB, hasTypecheck)
5. Write output to namespaced directory with generation metadata
6. Validate generated markdown for syntax correctness

### 3.2 Key components

- **jinja-templates/**: Template source files organised by category — agents (21 skills), rules (5), setup-skills (11), document templates (4), and a centralised macro library (`macros.j2`)
- **scripts/**: Python generation, validation, initialisation, and batch processing orchestrators (13 files, ~2,900 LOC)
- **schema/**: JSON Schema definition for configuration validation
- **commands/**: Language-specific command default templates (5 languages)

---

## 4. System Boundaries

### 4.1 The system DOES

- Generate documentation files from Jinja2 templates
- Validate configuration and template syntax before generation
- Ensure markdown correctness in generated output
- Track generation metadata for idempotent regeneration
- Process multiple repositories in parallel
- Initialise and configure new projects with language defaults
- Centralise compliance gate definitions and template patterns via macros

### 4.2 The system does NOT

- Modify source code (generates documentation only)
- Manage dependencies (repository responsibility)
- Handle deployment or execution (out of scope)
- Store runtime state (idempotent generation)
- Execute tests or run repository code
- Manage git operations or version control
- Overwrite instruction files in `/agentic-framework/instructions/` (preserved across regeneration)

---
**END OF DOCUMENT:** Total sections: 4 | Purpose: System purpose and boundaries | Last updated: 15/02/2026
