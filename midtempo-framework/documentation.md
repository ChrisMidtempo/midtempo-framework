# Phase 4: Documentation

## Table of Contents

- [Overview](#1-overview)
- [Process](#2-process)
  - [Non-Negotiable Rules](#21-non-negotiable-rules)
  - [Entry Gate](#entry-gate)
- [Documentation Criteria](#3-documentation-criteria)
  - [Instruction Document Update Criteria](#31-instruction-document-update-criteria)
  - [Document Update Rules](#32-document-update-rules)
  - [What to Capture in the Design Document](#33-what-to-capture-in-the-design-document)
- [Checklist](#4-checklist)
- [Exit Gate](#5-exit-gate)
- [Complete Script](#6-complete-script)

---

## 1. Overview

This sub-skill guides the agent through documenting the work and marking the feature complete.

**Goal:** Document the work and mark feature complete.

---

## 2. Process

### 2.1 Non-Negotiable Rules

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST verify tests are green before documenting
- You MUST read `/midtempo-framework/rules/writing.md` before proceeding
- You MUST update the design document with implementation context, deviations, and understanding gained
- You MUST add doc comments for all public exports
- You MUST update instruction documents ONLY when implementation introduced significant reusable patterns
- You MUST update README with important new behaviour
- You MUST set design document and test manifest status to "Completed"
- You MUST produce the "§6. Complete Script" when the skill is complete

</CRITICAL_REQUIREMENT>

---

### 2.2 Entry Gate

````

**Check test status using the log file**

```bash
tail -5 /planning/last-test-ran.log
```


IF Unit Tests are not GREEN
  → STOP. "Tests not green"
  → ASK human how to proceed.

READ ALL of `/midtempo-framework/rules/writing.md` → before proceeding

VALID: Continue to "§3. Documentation Criteria".
````

---

## 3. Documentation Criteria

### 3.1 Instruction Document Update Criteria

Only update instruction documents (`/midtempo-framework/instructions/*.md`) when implementation introduces **reusable patterns** or **structural decisions** that future agents must follow.

**Do NOT update for:**
- Feature-specific implementation details (those belong in design docs)
- One-off solutions or isolated fixes
- Obvious or standard patterns already implied
- Minor variations on existing documented patterns
- Examples of how to use existing patterns
- Catalogs or inventories of individual components, tables, classes, or functions
- Individual entities (components, tables, functions) created for this feature

**DO update when implementation establishes foundational patterns that future agents must follow:**
- A new architectural boundary or layer is established
- A new pattern becomes the standard approach for the repo
- Existing documented patterns are superseded or contradicted
- Core structural assumptions change
- New error handling strategy emerges as best practice
- New testing pattern emerges as best practice
- Database schema or access patterns are established
- UI component patterns or composition approaches are formalised

**Ask:** "Will future agents building different features need to follow this pattern?" If no → design doc only.

### 3.2 Document Update Rules

- **Design doc** (`/planning/*-design.md`): Single source of truth. All implementation context flows here.

Update **design doc** (`/planning/*-design.md`) with:
- "Completed" Status
- Implementation decisions and rationale
- Deviations from original design (what changed and why)
- New trade-offs or constraints discovered
- Patterns or approaches introduced during development
- File paths or modifications that differed from plan
- Context for future work

---

## 4. Checklist

- [ ] Design document updated (`/planning/*-design.md`) — single source of truth:
  - [ ] Status: Completed
  - [ ] Implementation decisions and rationale captured
  - [ ] Deviations from original design documented with reasons
  - [ ] New patterns or approaches introduced during development
  - [ ] Known limitations or trade-offs discovered
  - [ ] File paths or modifications that differed from plan
  - [ ] Context for future work preserved
- [ ] Instruction documents updated (only if implementation introduced significant reusable patterns):
  - [ ] `/midtempo-framework/instructions/architecture.md` # Services architectural structure and design principles — Update if implementation added:
    - [ ] New architectural layers or module boundaries
    - [ ] New service patterns or component organisation approaches
    - [ ] Significant structural patterns agents must follow
    - [ ] Changes to dependency rules or communication patterns
    - [ ] New code organisation conventions
    - [ ] High level Testing framework changes
  - [ ] `/midtempo-framework/instructions/error-handling.md` # Error handling patterns and conventions for the repository — Update if implementation added:
    - [ ] New error types or error classification
    - [ ] New error handling patterns or strategies
    - [ ] New error boundary implementations
    - [ ] Changes to error reporting, logging, or testing approaches
  - [ ] `/midtempo-framework/instructions/frontend-design.md` # Component architecture, composition patterns, and UI organisation — Update if implementation added:
    - [ ] New component hierarchy or composition patterns
    - [ ] New state management approaches
    - [ ] New data flow patterns or UI architectural decisions
    - [ ] Component organisation or directory structure conventions
  - [ ] `/midtempo-framework/instructions/style-guide.md` # CSS style rules and conventions — Update if implementation added:
    - [ ] New component styling patterns or approaches
    - [ ] New CSS naming conventions or organisation
    - [ ] New layout or responsive design patterns
    - [ ] Changes to styling tool usage (CSS-in-JS, Tailwind, etc.)
  - [ ] `/midtempo-framework/instructions/purpose.md` # Provides an overview of the goal and capabilities of the service — Update if implementation:
    - [ ] Added new major capabilities that redefine repo scope
    - [ ] Changed core functionality or system boundaries
    - [ ] Modified primary use cases or system identity
- [ ] Doc comments added for all public exports in plain UK English (following `/midtempo-framework/rules/writing.md`)
- [ ] `npm run docs:generate` runs successfully without warnings or errors (fix all warnings, including pre-existing)
- [ ] Updated `README.md` with important new behaviour that the human must know. Keep high-level and user-focused. Write in plain English, using clear examples for each significant point. Do not let README.md get bloated! Include:
  - Usage examples
  - Configuration or environment variables

- [ ] Updated plan document:
  - [ ] Set **Status** to `Completed`
- [ ] Updated test manifest:
  - [ ] Set **Status** to `Completed`

---

## 5. Exit Gate

```
IF design document (`/planning/*-design.md`) not updated with implementation context
  → STOP. "Design document must capture implementation decisions, deviations, and context for future work."

IF implementation introduced new architectural patterns/layers not documented in architecture.md
  → STOP. "Update `/midtempo-framework/instructions/architecture.md` # Services architectural structure and design principles with new structural patterns that agents must follow."

IF implementation introduced new error handling patterns not documented in error-handling.md
  → STOP. "Update `/midtempo-framework/instructions/error-handling.md` # Error handling patterns and conventions for the repository with new error approach or classification."


IF implementation introduced new UI component/state patterns not documented in frontend-design.md
  → STOP. "Update `/midtempo-framework/instructions/frontend-design.md` # Component architecture, composition patterns, and UI organisation with new component or architectural approach."

IF implementation introduced new styling patterns not documented in style-guide.md
  → STOP. "Update `/midtempo-framework/instructions/style-guide.md` # CSS style rules and conventions with new styling conventions or approaches."

IF implementation changed core functionality requiring purpose.md update
  → STOP. "Update `/midtempo-framework/instructions/purpose.md` # Provides an overview of the goal and capabilities of the service with capability or boundary changes."


IF `npm run docs:generate` has warnings or errors (current or pre-existing)
  → STOP
  → FIX ALL: "Doc-comments must run cleanly. Fix all errors AND warnings before proceeding."

IF plan document status is not "Completed"
  → STOP. "Update plan document status."

IF test manifest status is not "Completed"
  → STOP. "Update test manifest status."

VALID: Continue to  "§5.1 Exit Checklist"
```

**Get coverage numbers for the Complete Script:**

````
CHECK logfile for coverage data (lines, functions, branches percentages)

IF coverage data found in logfile
  → Use those numbers
IF coverage data NOT found in logfile
  → RUN ONCE:
    ```bash
    npm run test:python:coverage    # Coverage — metrics + pass/fail
    ```
  → Extract lines, functions, and branches percentages from this single run
  → Do NOT run the test suite again
````

Before presenting "§6. Complete Script", verify:
- [ ] Every file path in the output references a real file (not invented)
- [ ] Design document status is "Completed" in the actual file
- [ ] Plan document and test manifest statuses are "Completed" in the actual files
- [ ] Instruction doc updates listed match what was actually changed (or "none" if no new patterns)
- [ ] Coverage numbers are from a real coverage run (not invented)

IF any check fails → Fix before presenting. Do not present output with known violations.

VALID: Continue to "§6. Complete Script"

---

## 6. Complete Script

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output after Exit Gate passes - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
- You MUST verify plan and test manifest status are both Completed before producing this output
</CRITICAL_REQUIREMENT>

```
---
                       PHASE 4 COMPLETE: DOCUMENTATION

---

Feature summary: [what was built]

Files created: [list]
Files modified: [list]

Test count: [N] tests across [M] files
Coverage: [X]% lines, [Y]% functions, [Z]% branches

Documentation:
- Doc comments for [N] exports
- README updated with [section]
- Design doc updated with implementation context
- Instruction docs updated: [list which ones, or "none (no new patterns)"]

Status updated:
- `planning/[feature-name]-design.md` → ✅ Completed
- `planning/[feature-name]-plan.md` → ✅ Completed
- `planning/[feature-name]-tests.md` → ✅ Completed

Commit

docs: [feature name]
[3 lines describing (1) documentation added, (2) design doc updates, (3) "Feature complete."]

---
Review documentation and commit.

Before merge, consider running:
- /midtempo-framework/review-code.md for final code review
- /midtempo-framework/review-tests.md for test quality check
- /midtempo-framework/review-architecture.md for overall structure check

FEATURE COMPLETE ✅

---
```

---
**END OF DOCUMENT:** Total sections: 6 | Purpose: Document work and mark features complete