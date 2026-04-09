# Template Authoring Rules

## Table of Contents

- [Working Definition](#working-definition)
- [How Templates Work](#how-templates-work)
- [Tier 1: Syntax Reference](#tier-1-syntax-reference)
  - [R1 — Variables and Expressions](#r1--variables-and-expressions)
  - [R2 — Control Structures](#r2--control-structures)
  - [R3 — Built-in Filters](#r3--built-in-filters)
  - [R4 — Whitespace Control](#r4--whitespace-control)
  - [R5 — Comments and Raw Blocks](#r5--comments-and-raw-blocks)
  - [R6 — Variable Assignment](#r6--variable-assignment)
- [Tier 2: Custom Filters](#tier-2-custom-filters)
  - [F1 — `cmd` Filter](#f1--cmd-filter)
  - [F2 — `category` Filter](#f2--category-filter)
  - [F3 — `instructions` Filter](#f3--instructions-filter)
- [Tier 3: Macros](#tier-3-macros)
  - [M1 — SmartContext](#m1--smartcontext)
  - [M2 — File Reading Macros](#m2--file-reading-macros)
  - [M3 — Test Macros](#m3--test-macros)
  - [M4 — Output Macros](#m4--output-macros)
  - [M5 — Gate Macros](#m5--gate-macros)
  - [M6 — Adding New Macros](#m6--adding-new-macros)
- [Tier 4: Authoring Rules](#tier-4-authoring-rules)
  - [A1 — Use Filters, Not Direct Access](#a1--use-filters-not-direct-access)
  - [A2 — Never Hardcode Scope Names](#a2--never-hardcode-scope-names)
  - [A3 — Prefer Category Filter Over Manual Loops](#a3--prefer-category-filter-over-manual-loops)
  - [A4 — Never Nest Triple Backticks](#a4--never-nest-triple-backticks)
  - [A5 — Guard Instruction References](#a5--guard-instruction-references)
  - [A6 — Multi-Language Awareness](#a6--multi-language-awareness)
- [Compliance Gates](#compliance-gates)
- [Quick-Reference Checklist](#quick-reference-checklist)
- [Process](#process)

---

## Working Definition

```
A correct template produces identical agent instructions
for every project whose config satisfies the same schema.
```

**Falsifiable test:** Generate from two configs with different languages and commands. Does the output contain correct, project-specific values with no Jinja2 artefacts (`{{`, `{%`, `}}`)? Yes → correct. No → revise.

**Three pieces:**

| Piece | Location | Role |
|-------|----------|------|
| **Template** | `.j2` files in `jinja-templates/` | Instructions with placeholders |
| **Config** | `midtempo-framework.yml` per project | Real data for placeholders |
| **Generator** | `scripts/generate_docs.py` | Reads config, fills placeholders, writes output |

---

## How Templates Work

```
Template:  "Run {{ "test" | cmd }}"
Config:    commands.test.command = "pytest"
Output:    "Run `pytest`"
```

- Placeholders: `{{ ... }}`
- Logic: `{% ... %}`
- Comments: `{# ... #}`
- Same template + different config = different output
- **Never edit generated files directly.** Changes are overwritten on next generation.

---

## Tier 1: Syntax Reference

### R1 — Variables and Expressions

```jinja2
{{ repo.title }}                          {# "Example App" #}
{{ repo.language }}                       {# {python: all} #}
{{ repo.language.values()|first }}        {# "all" #}
{{ dateStamp }}                           {# "18/01/2026" (dd/mm/yyyy, UTC) #}
```

**Built-in context variables:**

| Variable | Content |
|----------|---------|
| `repo` | Repository metadata (title, language, purpose) |
| `capabilities` | Feature flags (hasUI, hasDB, hasTypecheck) |
| `commands` | Available commands for this project |
| `instructions` | Custom instruction page references |
| `dateStamp` | Generation date (dd/mm/yyyy, UTC) |

---

### R2 — Control Structures

**Conditionals:**

```jinja2
{% if repo.language|length == 1 %}
  Single language
{% elif repo.language|length == 2 %}
  Two languages
{% else %}
  Multiple languages
{% endif %}
```

**Logical operators:** `is defined`, `!=`, `in`, `is mapping`, `is string`, `and`, `or`, `not`

**Loops:**

```jinja2
{% for lang, scope in repo.language.items() %}
  {{ lang }}: {{ scope }}
{% endfor %}
```

**Loop variables:** `loop.index` (1-based), `loop.index0` (0-based), `loop.first`, `loop.last`

---

### R3 — Built-in Filters

| Filter | Example | Result |
|--------|---------|--------|
| `replace` | `{{ cat\|replace('_', ' ') }}` | `"test unit"` |
| `title` | `{{ cat\|title }}` | `"Test Unit"` |
| `upper` | `{{ cat\|upper }}` | `"TEST"` |
| `default` | `{{ cat\|default('other') }}` | Fallback if undefined |
| `first` / `last` | `{{ list\|first }}` | First/last element |
| `length` | `{{ list\|length }}` | Count |
| `sort` | `{{ dict.items()\|sort }}` | Sort by key |

**Type checks:** `is defined`, `is string`, `is mapping`, `is number`

---

### R4 — Whitespace Control

```jinja2
{% for item in list -%}     {# Strip after tag #}
  {{ item }}
{%- endfor %}                {# Strip before tag #}
```

Result: No blank lines between iterations.

---

### R5 — Comments and Raw Blocks

```jinja2
{# Jinja2 comment — stripped from output #}

{% raw %}
{{ this is literal output, not interpreted }}
{% endraw %}
```

Use `{% raw %}` for code examples containing `{{ }}` (e.g., JSX, React style props).

---

### R6 — Variable Assignment

```jinja2
{% set scope = repo.language.values()|first %}
{% set core = ['test', 'lint', 'typecheck'] %}
```

**Mutable dict (in-place):**

```jinja2
{% set categorised = {} %}
{% set _ = categorised.update({category: []}) %}
{% set _ = categorised[category].append(item) %}
```

`{% set _ = ... %}` discards return value, executes for side effects.

**Namespace (for loop-scoped state):**

```jinja2
{% set ns = namespace(found=false) %}
{% for key, cmd, desc in "test" | category %}
  {% if 'unit' in key %}
    {% set ns.found = true %}
  {% endif %}
{% endfor %}
{% if not ns.found %}
  {{ "test" | cmd }}
{% endif %}
```

`namespace` persists across loop iterations. Plain `{% set %}` inside a loop is scoped to that iteration and invisible outside.

---

## Tier 2: Custom Filters

### F1 — `cmd` Filter

**Purpose:** Extract executable command string from config.

```jinja2
{{ "test" | cmd }}       →  `pytest`
{{ "lint" | cmd }}       →  `ruff check scripts/`
```

- String format: returns the string
- Object format: returns `.command` value
- Missing command: raises `KeyError`

---

### F2 — `category` Filter

**Purpose:** Get commands matching a category for iteration.

```jinja2
{% for key, cmd, desc in "test" | category %}
{{ cmd }}    # {{ desc }}
{% endfor %}
```

Returns: `[(command_key, command_string, description), ...]`

---

### F3 — `instructions` Filter

**Purpose:** Generate formatted path reference for instruction pages.

```jinja2
{{ "architecture" | instructions }}
→  `/midtempo-framework/instructions/architecture.md` # System design and structure
```

- Missing instruction: raises `KeyError`
- **Always guard with existence check** (see rule A5)

---

## Tier 3: Macros

All macros live in `jinja-templates/macros.j2` and are globally available without imports.

### M1 — SmartContext

SmartContext (`this`) gives macros access to filters and config. Pass it as the first parameter.

```jinja2
{% macro my_macro(ctx) -%}
{{ ctx.cmd('test') }}          {# equivalent to "test" | cmd #}
{{ ctx.category('test') }}     {# equivalent to "test" | category #}
{{ ctx.instructions('arch') }} {# equivalent to "arch" | instructions #}
{{ ctx.repo.title }}           {# direct config access #}
{%- endmacro %}

{{ my_macro(this) }}
```

**Methods:** `ctx.cmd()`, `ctx.category()`, `ctx.instructions()`
**Attributes:** `ctx.repo`, `ctx.commands`, `ctx.capabilities`, `ctx.dateStamp`

Direct filter calls (`{{ "test" | cmd }}`) fail inside macros — always use SmartContext methods instead.

---

### M2 — File Reading Macros

| Macro | Purpose | Usage |
|-------|---------|-------|
| `read_file(path, context?)` | Single file read with truncation verification | `{{ read_file('/path/file.md') }}` |
| `require_rules_read(pages)` | Multiple rules file reads | `{{ require_rules_read(['writing', 'testing']) }}` |
| `require_instructions_read(pages, instructions)` | Multiple instruction reads (existence-checked) | `{{ require_instructions_read(['purpose', 'arch'], instructions) }}` |
| `conditional_ui_reads(caps, instructions, include_new_page?)` | UI-specific reads when hasUI=true | `{{ conditional_ui_reads(capabilities, instructions) }}` |
| `conditional_db_reads(caps, instructions)` | DB-specific reads when hasDB=true | `{{ conditional_db_reads(capabilities, instructions) }}` |

---

### M3 — Test Macros

| Macro | Purpose | Usage |
|-------|---------|-------|
| `test_status_check(check_logfile, ctx)` | Verify test status via logfile or direct run | `{{ test_status_check(true, this) }}` |
| `test_gate(ctx)` | Gate check — prefers `test_summary`, falls back to `test` | `{{ test_gate(this) }}` |
| `test_targeted(ctx)` | Single-file TDD run with `<test-file>` placeholder | `{{ test_targeted(this) }}` |
| `test_coverage_report(ctx)` | Coverage run — prefers `test_coverage`, falls back to `test` | `{{ test_coverage_report(this) }}` |

---

### M4 — Output Macros

| Macro | Purpose | Usage |
|-------|---------|-------|
| `completion_box(title)` | Bordered box (79 chars wide) | `{{ completion_box('DONE: Feature') }}` |
| `phase_complete_box(title, documents?, next_step?, prerequisites?, prohibited?)` | Full phase completion block with MANDATORY/PREREQUISITE/PROHIBITED | `{{ phase_complete_box('TESTS WRITTEN', documents=[('path', 'desc')]) }}` |
| `command_block(ctx, category, title?, show_primary?, show_comments?)` | Formatted command display for a category | `{{ command_block(this, 'test') }}` |

---

### M5 — Gate Macros

| Macro | Purpose | Usage |
|-------|---------|-------|
| `entry_gate_reads(ctx, rules?, instructions?)` | Complete entry gate read validation | `{{ entry_gate_reads(this, rules=['writing'], instructions=['arch']) }}` |
| `verify_rules_compliance_gates(rules)` | Exit gate rules verification | `{{ verify_rules_compliance_gates(['testing']) }}` |
| `testing_cg_range()` | Testing gate range string (single source) | `{{ testing_cg_range() }}` |
| `testing_compliance_gates_summary()` | Compact CG-1 through CG-6 summary | `{{ testing_compliance_gates_summary() }}` |

---

### M6 — Adding New Macros

1. Add macro to `jinja-templates/macros.j2` with documentation comment
2. Document in this file
3. Add tests in `tests/test_template_rendering.py`
4. Run: `npm run test:python`

**Rules for macros:**
- Use SmartContext (`ctx`) — never direct filters
- Use `-` whitespace control (`{%-` and `-%}`)
- Provide defaults for optional parameters
- Test with mono-language and multi-language configs

---

## Tier 4: Authoring Rules

### A1 — Use Filters, Not Direct Access

```jinja2
{# INVALID — breaks with object format #}
{{ commands.test }}

{# VALID — handles both string and object formats #}
{{ "test" | cmd }}
```

**Check:** Does every command reference use the `cmd` filter or `ctx.cmd()` method? Yes/No.

---

### A2 — Never Hardcode Scope Names

```jinja2
{# INVALID — assumes scope name "backend" #}
Run {{ "backend_test" | cmd }}

{# VALID — iterates dynamically #}
{% if repo.language|length == 1 %}
  Run {{ "test" | cmd }}
{% else %}
  {% for lang, scope in repo.language.items() %}
  Run {{ scope }}_test for {{ lang }}
  {% endfor %}
{% endif %}
```

Scope names are user-defined. Templates must iterate `repo.language.items()` or use mono-language bare commands.

**Check:** Does the template contain any literal scope names ("backend", "frontend")? If yes → revise.

---

### A3 — Prefer Category Filter Over Manual Loops

```jinja2
{# INVALID — manual filtering #}
{% for key, value in commands.items() %}
  {% if value is mapping and value.category == "test" %}
    {{ value.command }}
  {% endif %}
{% endfor %}

{# VALID — filter handles format checking and unpacking #}
{% for key, cmd, desc in "test" | category %}
  {{ cmd }}    # {{ desc }}
{% endfor %}
```

**Check:** Does any loop manually filter by `.category`? If yes → use `| category` filter instead.

---

### A4 — Never Nest Triple Backticks

Never place ` ``` ` inside a ` ``` ` code block. Use four backticks for the outer block:

````markdown
Here's how to use code blocks:
```python
print("hello")
```
````

**Check:** Does any code block contain nested triple backticks at the same fence level? If yes → revise.

---

### A5 — Guard Instruction References

```jinja2
{# INVALID — KeyError if instruction missing #}
{{ "frontend-design" | instructions }}

{# VALID — guard with existence check #}
{% if "frontend-design" in instructions %}
{{ "frontend-design" | instructions }}
{% endif %}
```

For capability-gated instructions, combine both checks:

```jinja2
{% if capabilities.hasUI and "frontend-design" in instructions %}
  → READ: {{ "frontend-design" | instructions }}
{% endif %}
```

**Check:** Does every `| instructions` call have an existence guard (`in instructions`)? Yes/No.

---

### A6 — Multi-Language Awareness

**Mono-language** (`{python: all}`): scope = `"all"`, bare command names (`test`, `lint`)

**Multi-language** (`{python: backend, typescript: frontend}`): scoped command names (`backend_test`, `frontend_lint`)

**Detection pattern:**

```jinja2
{% if repo.language|length == 1 %}
  {# Simple output, no scope guidance #}
{% else %}
  {# Scoped guidance with iteration #}
  {% for lang, scope in repo.language.items() %}
    {{ lang }} ({{ scope }})
  {% endfor %}
{% endif %}
```

**Check:** Does the template produce correct output for both mono-language and multi-language configs? Yes/No.

---

## Compliance Gates

```
FOR EACH template under review:
  → Run all gates
  → All must pass
  → Any failure → revise before proceeding
```

| Gate | Check |
|------|-------|
| **CG-TA-1** | Every command reference uses `cmd` filter or `ctx.cmd()` — no direct `commands.X` access (A1) |
| **CG-TA-2** | No hardcoded scope names — all scope references iterate `repo.language` dynamically (A2) |
| **CG-TA-3** | Category loops use `\| category` filter — no manual `.category ==` filtering (A3) |
| **CG-TA-4** | No nested triple backticks at the same fence level (A4) |
| **CG-TA-5** | Every `\| instructions` call has an existence guard (A5) |
| **CG-TA-6** | Template produces correct output for both mono-language and multi-language configs (A6) |
| **CG-TA-7** | No Jinja2 artefacts (`{{`, `{%`, `}}`, `{#`) in generated output (except inside code examples wrapped in `{% raw %}`) |
| **CG-TA-8** | Macros use SmartContext (`ctx`) for filter access — no direct filter calls inside macros (M1) |
| **CG-TA-9** | Generated files are never edited directly — all changes made in `.j2` templates |

---

## Quick-Reference Checklist

| ID | Rule | One-Line Check |
|----|------|----------------|
| A1 | Use filters | Every command uses `\| cmd` or `ctx.cmd()` |
| A2 | No hardcoded scopes | Zero literal scope names in template |
| A3 | Category filter | No manual `.category ==` loops |
| A4 | No nested fences | No ` ``` ` inside ` ``` ` |
| A5 | Guard instructions | Every `\| instructions` has `in instructions` guard |
| A6 | Multi-language | Output correct for 1 and 2+ languages |
| M1 | SmartContext in macros | Macros use `ctx.cmd()` not `\| cmd` |

---

## Process

1. Edit the `.j2` template file
2. Run generator: `npm run generate myProject`
3. Check output in `agents/myProject/` directory
4. Validate: no `{{`, `{%`, `}}` in output (except code examples)
5. Test with mono-language and multi-language configs
6. Run template tests: `npm run test:python`

---
**END OF DOCUMENT:** Total sections: 8 | Purpose: Template authoring syntax, filters, macros, and rules for Jinja2 agent templates
