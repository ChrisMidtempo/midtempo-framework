# Refactoring & Code Health Skill

## Overview

Refactoring improves the internal structure of the code **without changing its externally observable behaviour**. It is the primary mechanism for controlling technical debt, improving readability, and keeping the codebase scalable as features grow.

**Goal:** Transform code into cleaner, more maintainable structure while preserving all existing behaviour, adhering to all relevant rules and instructions.

**NOT for:**

- New feature delivery → use [build.md](build.md)
- Known bugs with clear symptoms → use [bugs.md](bugs.md)
- Delivered features needing tweaks → use [refine.md](refine.md)
- Unknown problems or uncertainty → use [investigate.md](investigate.md)

**Outputs:**

- Refactor Report (presented to human for approval)
- Incremental commits with passing tests

**Workflow integration:** This skill is used as either:
 - a sub-skill in **Phase 4: Refactor** of `deliver.md`
 - run as a stand-alone skill.

---

## Table of Contents

- [Overview](#overview)
- [The Process](#the-process)
  - [Non-Negotiable Rules](#non-negotiable-rules)
  - [Entry Gate](#entry-gate)
- [Step 1: Discovery](#step-1-discovery)
  - [1.1 Open Discovery](#11-open-discovery)
  - [1.2 Targeted Discovery](#12-targeted-discovery)
- [Step 2: Design Principles & Architecture](#step-2-design-principles--architecture)
  - [2.1 DRY (Don't Repeat Yourself)](#21-dry-dont-repeat-yourself)
  - [2.2 SRP (Single Responsibility Principle)](#22-srp-single-responsibility-principle)
  - [2.3 OCP (Open/Closed Principle)](#23-ocp-openclosed-principle)
  - [2.4 KISS (Keep It Simple)](#24-kiss-keep-it-simple)
  - [2.5 LoD (Law of Demeter)](#25-lod-law-of-demeter)
  - [2.6 Architectural Violations](#26-architectural-violations)
  - [2.7 Incomplete Implementation](#27-incomplete-implementation)
- [Step 3: Report & Approval](#step-3-report--approval)
  - [3.1 Compile Report](#31-compile-report)
  - [3.2 Pre-Output Self-Check](#32-pre-output-self-check)
  - [3.3 Human Approval](#33-human-approval)
- [Step 4: Execute Approved Refactors](#step-4-execute-approved-refactors)
  - [4.1 Step Boundaries](#41-step-boundaries)
  - [4.2 Execution Loop](#42-execution-loop)
  - [4.3 Bug Discovery Protocol](#43-bug-discovery-protocol)
  - [4.4 Execution Checklist](#44-execution-checklist)
- [Step 5: Verify Post-Refactor Stability](#step-5-verify-post-refactor-stability)
  - [5.1 Full Verification](#51-full-verification)
  - [5.2 Verify Instruction Compliance Gates](#52-verify-instruction-compliance-gates)
  - [5.3 Final Checklist](#53-final-checklist)
  - [5.4 Refactor Complete](#54-refactor-complete)
  - [5.5 Refactor Skipped](#55-refactor-skipped)
- [Anti-Patterns](#anti-patterns)
- [Common Rationalisations](#common-rationalisations-forbidden)
- [Design Principles Reference](#design-principles-reference)
- [Approved Refactoring Patterns](#approved-refactoring-patterns)
- [Final Rule](#final-rule)

---

## The Process

### Non-Negotiable Rules

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST run `npm run lint:python` FIRST to discover refactoring targets — warnings and errors are important metrics
- You MUST NOT estimate metrics (complexity, function length) — always use lint output
- You MUST systematically check design principles (DRY, SRP, OCP, KISS, LoD) and architecture
- You MUST confirm tests are green before refactoring
- You MUST check coverage on refactor targets before refactoring — low coverage means behaviour drift risk
- You MUST NOT change behaviour without a test proving behaviour changed
- You MUST perform refactors in **small, reversible steps** (see §4.1 Step Boundaries)
- You MUST update existing Doc-Comments if renaming or moving code
- You MUST NOT introduce new abstractions unless demanded by duplication or complexity
- You MUST ensure architectural, UI, and import-layer rules remain valid after refactor
- You MUST provide at least one positive observation in any Refactor Report output
- You MUST present refactor report to human and await approval before executing

</CRITICAL_REQUIREMENT>

---

### ENTRY GATE

**Output to human:**

```
Refactor Entry Gate — verifying preconditions:

1. Checking test suite status...
2. Reading instruction docs (purpose, architecture, error-handling)...
3. Reading planning docs (design, plan)...
4. Checking coverage on refactor targets...
```

```
IF test suite is failing
  → INVALID: STOP - Refactor forbidden until green

VERIFY-COMPLETE-READ for EVERY file below:
  CHECK the last line says "END OF DOCUMENT"
  IF CHECK fails → Re-read from offset until true end

READ ALL of `/midtempo-framework/instructions/purpose.md` → before proceeding
READ ALL of `/midtempo-framework/instructions/architecture.md` → before proceeding
READ ALL of `/midtempo-framework/instructions/error-handling.md` → before proceeding

READ ALL of `/planning/[feature-name]-design.md` → to understand feature intent
READ ALL of `/planning/[feature-name]-plan.md` → to understand delivery approach

IF the current task involves UI
READ ALL of `/midtempo-framework/instructions/frontend-design.md` → for UI component patterns
READ ALL of `/midtempo-framework/instructions/style-guide.md` → for styling conventions

IF the current task includes a new page/screen
READ ALL of `/midtempo-framework/instructions/new-page.md` → for page wiring instructions

VERIFY-COMPLETE-READ for EVERY file below:
  CHECK the last line says "END OF DOCUMENT"
  IF CHECK fails → Re-read from offset until true end

IF the current task involves secrets management
READ ALL of `/midtempo-framework/rules/security/secrets-management.md` → for secrets-management rules

IF the current task involves input validation
READ ALL of `/midtempo-framework/rules/security/input-validation.md` → for input-validation rules

IF the current task involves authentication
READ ALL of `/midtempo-framework/rules/security/authentication.md` → for authentication rules

IF the current task involves data protection
READ ALL of `/midtempo-framework/rules/security/data-protection.md` → for data-protection rules

IF the current task involves public-facing security
READ ALL of `/midtempo-framework/rules/security/public-hardening.md` → for public-hardening rules


IF coverage command available:
  RUN npm run test:python:coverage    # Coverage — metrics + pass/fail
  IF coverage < 70% branches on target files
    → WARN human: "Low coverage on refactor targets. Behaviour drift risk."
    → RECOMMEND: "Strengthen tests before refactoring"
    → WAIT for human decision: proceed or strengthen tests first

IF NO recommendation document provided (planning/investigations/*-rec-*.md)
  → GOTO "Step 1: Discovery" §1.1 Open Discovery

ELSE
  → READ ALL of the recommendation document for task
  → READ ALL of the recommendation parent document for context
  → GOTO "Step 1: Discovery" §1.2 Targeted Discovery
```

---

## Step 1: Discovery

**Do not skip or estimate. Lint output is mandatory.**

### 1.1 Open Discovery

**Output to human:** "Running format, tests, lint, and typecheck — gathering refactoring metrics..."

**Use this path when NO recommendation document is provided.**

**Format code before refactoring:**

```bash
npm run format:python                     # Auto-format all code
```

Formatting first ensures refactoring diffs show logic changes, not style changes.

**Run verification and gather metrics:**

```bash
npm run test:python    # Verbose — no summary command configured
npm run lint:python:fix           # GET METRICS — this is the source of refactoring targets
npm run typecheck:python      # Verify clean
```
**Check file lengths (linter does not enforce file-length limits):**

Count lines for every source file in the refactor scope. Any source file exceeding 500 lines is a **blocking** refactoring target. Measure with `wc -l` or equivalent — do not estimate.

**Categorise lint findings by type:**

From the lint output, list each warning:

| Lint Rule | Type | Target |
|-----------|------|--------|
| `complexity` > 10 | Complexity | Must fix |
| `max-lines-per-function` > 75 | Function length | Must fix |
| `file-length` > 500 | File length | Must fix |
| `no-nested-ternary` | Readability | Must fix |
| Other warnings | Style | Must fix |

Zero tolerance for lint errors or warnings. All findings enter the refactor report.

```
VALID: Continue to "Step 2: Design Principles & Architecture"
```

---

### 1.2 Targeted Discovery

**Use this path when a recommendation document IS provided.**

```
EXTRACT from recommendation document:
  - Targets: files and specific issues identified
  - Scope: files affected, complexity, risk
  - Acceptance criteria: measurable outcomes
  - Evidence: file:line references from investigation

READ each targeted file completely.
```

```bash
npm run format:python                     # Auto-format before refactoring
```
```bash
npm run lint:python:fix                   # Fix auto-fixable lint issues
```

```bash
npm run test:python    # Verbose — no summary command configured
npm run lint:python           # Gather current metrics for targeted files
npm run typecheck:python      # Verify clean
```

Review lint output for targeted files. Record current metrics.

```
VALID: Continue to "Step 2: Design Principles & Architecture"
```

---

## Step 2: Design Principles & Architecture

**Output to human:** "Checking design principles (DRY, SRP, OCP, KISS, LoD) and architecture — analysing code structure..."

**This step is mandatory for both discovery paths.** Systematically check for violations that lint does not catch.

### 2.1 DRY (Don't Repeat Yourself)

- [ ] Search for duplicated logic patterns across files
- [ ] Perform **side-by-side comparison** before dismissing duplication
- [ ] Check for similar function signatures with different names
- [ ] Look for copied validation, transformation, or formatting logic

**Evidence required:** If claiming "not duplicated", provide side-by-side comparison showing actual differences.

### 2.2 SRP (Single Responsibility Principle)

- [ ] Check if functions/modules mix unrelated responsibilities
- [ ] Look for methods handling validation + IO + transformation together
- [ ] Identify low cohesion (unrelated operations in same module)

### 2.3 OCP (Open/Closed Principle)

- [ ] Identify switch statements that require modification to extend
- [ ] Look for if/else chains that grow with new cases
- [ ] Check for hardcoded type checks instead of polymorphism

### 2.4 KISS (Keep It Simple)

- [ ] Spot unnecessarily complex implementations
- [ ] Find metaprogramming/reflection where simple loops/conditionals suffice
- [ ] Identify over-engineered solutions to simple problems

### 2.5 LoD (Law of Demeter)

- [ ] Search for method chains: `a.b().c().d()`
- [ ] Look for code reaching through multiple layers
- [ ] Check for direct access to nested properties

### 2.6 Architectural Violations

- [ ] **Cross-layer imports:** Verify imports respect the architectural boundaries defined in `/midtempo-framework/instructions/architecture.md` # Services architectural structure and design principles §5.2 "Dependency Rules" (no upward or sideways dependencies)
- [ ] **Layer skipping:** Ensure each layer only calls the layer directly beneath it — no bypassing intermediate layers
- [ ] **Public/internal boundaries:** Ensure module boundaries respected — internal implementation details not leaked to consumers
- [ ] **Higher-level reimplementation:** Higher-level modules must compose lower-level modules, not reimplement their logic

**Check for:**

- Lower-level modules importing from higher-level modules (dependency inversion violations)
- Layers bypassing intermediate layers
- Higher-level modules with 30+ lines of logic that parallels existing lower-level module functionality
- Custom implementations that duplicate capabilities already provided by existing modules

### 2.7 Incomplete Implementation

- [ ] **Placeholder comments:** Search for `// Additional`, `// TODO: add remaining`, `// See ... for`
- [ ] **Incomplete interfaces:** Compare interfaces against their source of truth (schema, API docs)
- [ ] **Deferred work:** No comments implying "more to come" — implement fully or remove

```
VALID: Continue to "Step 3: Report & Approval"
```

---

## Step 3: Report & Approval

**This is the first human touchpoint. Combine all findings into a single report.**

### 3.1 Compile Report

**For Open Discovery path:**

```text
## Refactor Report

### Findings

| Type | Issue | File:Line | Current Metric |
|------|-------|-----------|----------------|
| Complexity | ... | ... | ... |
| Function length | ... | ... | ... |
| File length | ... | ... | ... |
| Readability | ... | ... | ... |
| Style | ... | ... | ... |

### Design Analysis

DRY violations:
- [Finding with file:line references or "None found"]

SRP violations:
- [Finding with file:line references or "None found"]

OCP violations:
- [Finding with file:line references or "None found"]

KISS violations:
- [Finding with file:line references or "None found"]

LoD violations:
- [Finding with file:line references or "None found"]

Architectural violations:
- [Finding with file:line references or "None found"]

Incomplete implementation:
- [Finding with file:line references or "None found"]

### Proposed Changes

1. [Change description] — [Files affected] — [Risk: low/medium/high]
2. [Change description] — [Files affected] — [Risk: low/medium/high]

### Measured Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Max function length | X lines | ≤75 | ✓/✗ |
| Max file length | X lines | ≤500 | ✓/✗ |
| Cyclomatic complexity | X | ≤10 | ✓/✗ |

### Positives

- [At least one concrete positive observation]
- [Another positive if applicable]
```

**For Targeted Discovery path:**

```text
## Refactor Report (from Recommendation)

### Source

- Recommendation: [rec doc filename]
- Investigation: [source investigation]

### Targets

| # | File | Issue (from rec doc) | Current Metric |
|---|------|----------------------|----------------|
| 1 | [file] | [issue] | [from lint] |

### Design Analysis

[Same design analysis sections as Open Discovery — populated from Step 2]

### Proposed Changes

1. [Change] — [Files] — [Risk: low/medium/high]

### Acceptance Criteria (from rec doc)

- [ ] [criterion from rec doc]

### Positives

- [At least one concrete positive observation]
```

### 3.2 Pre-Output Self-Check

Before presenting the report, verify each criterion against the report artefact:

1. Every file path in Findings references a real file in the codebase (not invented)
2. Every metric in Measured Metrics matches lint output values (not estimated or rounded)
3. Every finding includes file:line evidence from lint output or codebase inspection
4. Positives section contains at least one concrete observation
5. Design Analysis populated from Step 2 checks (not skipped)
6. No section contains placeholder text ("[TODO]", "[TBD]", "...")

IF any check fails → Fix the report before presenting. Do not present output with known violations.

### 3.3 Human Approval

Lint errors and warnings are mandatory — zero tolerance, no human approval needed.

```
IF design analysis findings exist
  → Present to human:

    HUMAN DECISION REQUIRED

    Lint remediation: [N] issues — all will be fixed (mandatory).

    Design analysis findings require your decision:
      - Proceed with all design findings
      - Proceed with selected findings only
      - Skip design refactoring
      - Request more detail

    Awaiting human selection...

IF no design analysis findings
  → State: "No design principle issues found."
  → IF lint findings exist → Continue to Step 4 (lint remediation only)
  → IF no findings at all → GOTO "§5.5 Refactor Skipped"

IF design options presented AND human has not responded
  → INVALID: STOP - Await human decision

IF human selected skip
  → IF lint findings exist → Continue to Step 4 (lint remediation only)
  → IF no lint findings
    IF sub-skill of deliver.md → GOTO `/midtempo-framework/deliver.md` "§6.4 Step 3 Skipped Output"
    IF standalone → GOTO "§5.5 Refactor Skipped"

IF human requested more detail
  → Provide requested detail, re-present options

IF human selected a scope
  → Continue to Step 4 with lint remediation + selected design findings
```

**Wait for validation**

---

## Step 4: Execute Approved Refactors

**Small steps only. Each change must be individually testable.**

### 4.1 Step Boundaries

One step = ONE of:

- Extract a single function/method
- Rename a single symbol (and update all references)
- Move a function/class to a different file
- Inline a single abstraction
- Replace a single pattern (e.g., nested ternary → if/else)
- Remove a single instance of duplication

NOT one step:

- Extract AND rename in the same change
- Move AND restructure in the same change
- Multiple unrelated fixes in one pass

### 4.2 Execution Loop

For each approved change:

```
1. Make single change (see §4.1 boundaries)

2. Run tests:
   npm run test:python <test-file>    # Verify green
3. Run lint:
   npm run lint:python:fix               # Verify clean
4. Run typecheck:
   npm run typecheck:python          # Verify clean
5. If renaming, update existing Doc-Comments to match new names
6. Move to the next change

IF step breaks behaviour
  → STOP → Rollback → Adjust plan
```

### 4.3 Bug Discovery Protocol

```
IF refactoring reveals a bug (logic error, dead code, unreachable branch):
  → DO NOT fix the bug within the refactor skill
  → APPEND to planning/[feature-name]-design.md under "## Bug Report" section:
    - Date: [date]
    - File: [file:line]
    - Description: [what the bug is]
    - Evidence: [how it was discovered during refactor]
    - Severity: [blocking/non-blocking for refactor]
  → Report to human: "Bug logged in design doc — route through bugs.md skill"
  → Continue refactoring unless bug makes refactor unsafe

IF bug makes refactor unsafe (refactored code depends on buggy behaviour):
  → STOP → Report to human with evidence
  → WAIT for human decision: fix bug first or abort refactor
```

### 4.4 Execution Checklist

During each refactor step:

- [ ] Step is minimal and individually test-safe (§4.1)
- [ ] Naming improved
- [ ] Responsibilities clarified
- [ ] No behavioural changes detected
- [ ] Architecture boundaries preserved
- [ ] Design principles preserved (DRY, SRP, OCP, KISS, YAGNI, LoD)
- [ ] Existing Doc-Comments updated if names changed
- [ ] No placeholder comments implying incomplete code

---

## Step 5: Verify Post-Refactor Stability

**Confirm all quality gates pass after refactoring.**

### 5.1 Full Verification

```bash
npm run test:python    # Verbose — no summary command configured
npm run lint:python:fix           # Clean lint
npm run typecheck:python      # Clean types
```

IF any command fails
  → STOP: Fix failures before proceeding to checklist

### 5.2 Verify Instruction Compliance Gates

```
IF delivery scope touches architecture AND '/midtempo-framework/instructions/architecture.md "Compliance Gates"' not verified
  → STOP. "Verify all architecture compliance gates before proceeding."
IF delivery scope touches error handling AND '/midtempo-framework/instructions/error-handling.md "Compliance Gates"' not verified
  → STOP. "Verify all error-handling compliance gates before proceeding."


IF delivery scope touches UI components AND '/midtempo-framework/instructions/frontend-design.md "Compliance Gates"' not verified
  → STOP. "Verify all frontend-design compliance gates before proceeding."
IF delivery scope touches styling AND '/midtempo-framework/instructions/style-guide.md "Compliance Gates"' not verified
  → STOP. "Verify all style-guide compliance gates before proceeding."

IF delivery scope touches secrets management AND '/midtempo-framework/rules/security/secrets-management.md "Compliance Gates"' not verified
  → STOP. "Verify all secrets-management compliance gates before proceeding."
IF delivery scope touches input validation AND '/midtempo-framework/rules/security/input-validation.md "Compliance Gates"' not verified
  → STOP. "Verify all input-validation compliance gates before proceeding."
IF delivery scope touches authentication AND '/midtempo-framework/rules/security/authentication.md "Compliance Gates"' not verified
  → STOP. "Verify all authentication compliance gates before proceeding."
IF delivery scope touches data protection AND '/midtempo-framework/rules/security/data-protection.md "Compliance Gates"' not verified
  → STOP. "Verify all data-protection compliance gates before proceeding."
IF delivery scope touches public hardening AND '/midtempo-framework/rules/security/public-hardening.md "Compliance Gates"' not verified
  → STOP. "Verify all public-hardening compliance gates before proceeding."

FOR EACH applicable compliance gate from instruction documents read at the entry gate:
  → VERIFY gate against the refactored code
  → Record PASS or FAIL with file:line evidence
  → CITE gate number in findings

IF any gate fails
  → STOP: Fix violation before proceeding to final checklist
```

### 5.3 Final Checklist

- [ ] Coverage not reduced
- [ ] Complexity score decreased (or unchanged if already good)
- [ ] No new TODOs or commented-out code

IF §5.3 Final Checklist all complete
  → VALID: GOTO "§5.4 Refactor Complete"

### 5.4 Refactor Complete

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output after Exit Gate passes - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
- You MUST verify tests pass, coverage is not reduced, and no new TODOs exist before producing this output
</CRITICAL_REQUIREMENT>

```
---
                          REFACTOR COMPLETE

---

Changes made:
- [Specific refactor: extraction, split, rename]
- [Specific refactor: complexity reduction]
- [Specific refactor: duplication removal]

Tests still green. Lint/typecheck clean.

Commit

refactor: [feature name]

[3 lines describing (1) primary structural change, (2) secondary improvement, (3) metric improvement]

---
Review refactors and commit.

[If refactor was called as a sub-skill of deliver.md]
 Run `/midtempo-framework/review-code.md` on /planning/[feature-name]-plan.md to review delivery before documentation

 Or start a new conversation with:

 Step 4 - use /midtempo-framework/deliver.md with /planning/[feature-name]-plan.md. Run Step 4.

---
```

### 5.5 Refactor Skipped

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output after Exit Gate passes - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
</CRITICAL_REQUIREMENT>

```
---
                          REFACTOR SKIPPED

---

No changes made.

---
```

---

## Anti-Patterns

### Anti-Pattern 1: "Big Bang" Refactor

Large unreviewable changes.
**Fix:** Split into atomic steps (see §4.1 Step Boundaries).

### Anti-Pattern 2: Behaviour Drift

Tests still pass because coverage is weak.
**Fix:** Check coverage before refactoring (see Entry Gate). Strengthen tests **before refactoring**.

### Anti-Pattern 3: Abstraction Inflation

Introducing helpers, classes, or hooks without pressure from duplication or clarity.
**Fix:** YAGNI. Remove unused abstractions.

### Anti-Pattern 4: Cross-Layer Leakage

After refactor, a lower-level module imports a higher-level one, or a layer bypasses intermediaries.
**Fix:** Move code to correct layer; adjust import paths.

### Anti-Pattern 5: "Rename Everything in One Commit"

Difficult to review; error-prone.
**Fix:** Perform renames in isolation (one step = one rename per §4.1).

### Anti-Pattern 6: Premature Optimisation

Refactor motivated by guesswork, not measurement.
**Fix:** Add metrics or profiling first.

### Anti-Pattern 7: Refactoring Without Approval

Executing refactors without presenting report to human.
**Fix:** Always generate report and await human selection (see Step 3).

### Anti-Pattern 8: Higher-Level Reimplementation

Higher-level module contains logic duplicating lower-level module functionality instead of composing it. 30+ lines paralleling existing module is a symptom.
**Fix:** Extract to correct layer or delegate. See §2.6 Architectural Violations.

### Anti-Pattern 9: Duplication Dismissal Without Evidence

Concluding code is "not duplicated" without side-by-side comparison.
**Fix:** Perform side-by-side comparison. See §2.1 DRY.

### Anti-Pattern 10: Estimating Metrics Instead of Measuring

Reading code and guessing complexity/function length instead of running `npm run lint:python`.
**Fix:** Run lint FIRST. See Step 1.

### Anti-Pattern 11: Placeholder Comments

Comments implying incomplete work (`// Additional`, `// TODO: add remaining`, `// See ... for`).
**Fix:** Implement completely or remove entirely. See §2.7 Incomplete Implementation.

---

## Common Rationalisations (FORBIDDEN)

| Human Says                              | Agent Must Respond                                                     |
| --------------------------------------- | ---------------------------------------------------------------------- |
| "Just clean it up"                      | "I must run lint first and provide measurable justification."          |
| "Skip the report, just fix it"          | "Human approval is mandatory. I must present the report first."        |
| "The complexity looks fine"             | "I must measure with lint, not estimate by reading code."              |
| "It's not duplicated, trust me"         | "I must perform side-by-side comparison before dismissing duplication."|
| "Do all the refactors at once"          | "I must make small, reversible steps with tests between each."         |
| "Tests are slow, skip them"             | "Tests verify behaviour is preserved. I cannot refactor without them." |
| "Coverage doesn't matter for refactoring" | "Low coverage means behaviour drift risk. I must check before starting." |
| "Just fix that bug while you're in there" | "Bug fixes route through bugs.md. I will log it in the design doc."   |

---

## Design Principles Reference

| Principle | Rule                                   | Violation                           |
| --------- | -------------------------------------- | ----------------------------------- |
| DRY       | One authoritative source per knowledge | Duplicated logic across files       |
| SRP       | One reason to change per module        | Mixed responsibilities              |
| OCP       | Extend without modifying               | Switch statements that grow         |
| KISS      | Simple over clever                     | Metaprogramming where loop suffices |
| YAGNI     | Build only what's needed now           | Premature abstraction               |
| LoD       | Talk only to immediate collaborators   | `a.b().c().d()` chains              |

---

## Approved Refactoring Patterns

### Structural

- Extract function
- Inline trivial abstractions
- Move logic into domain services
- Split large modules

### Readability

- Rename for clarity
- Simplify branching
- Replace magic numbers with constants

### Cohesion

- Group related logic
- Remove unrelated responsibilities

### Complexity Reduction

- Reduce nesting
- Break long functions
- Introduce early returns

### Duplication Removal

- Extract shared helper
- Consolidate test fixture factories

---

## Final Rule

```
MUST MEASURE FIRST. MUST REPORT SECOND. MUST AWAIT APPROVAL. MUST EXECUTE IN SMALL STEPS.
```

Never estimate what can be measured. Never execute without approval. Never make large changes in single commits.

No exceptions without human partner's permission.

---
**END OF DOCUMENT:** Total sections: 14 | Purpose: Improve code structure while preserving behaviour