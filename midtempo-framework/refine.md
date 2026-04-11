# Refine: Post-Delivery Refinement

## Overview

Refine already-delivered features when delivery doesn't quite meet expectations or small tweaks would provide quick wins. Iterate on existing work with documented context.

**Goal:** Make targeted refinements to delivered features while maintaining design continuity and test coverage.

**NOT for:**

- New features → use [build.md](build.md)
- Bug fixes with clear symptoms → use [bugs.md](bugs.md)
- Code quality improvements → use [refactor.md](refactor.md)
- Unknown problems or uncertainty → use [investigate.md](investigate.md)

**Outputs:**

- Updated design document with refinement context
- Doc-comments for changed code
- Delivery following TDD principles

---

## Table of Contents

- [Overview](#overview)
- [The Process](#the-process)
  - [Non-Negotiable Rules](#non-negotiable-rules)
  - [Entry Gate](#entry-gate)
- [Step 1: Locate Design Context](#step-1-locate-design-context)
  - [Agent Actions (Silent)](#11-agent-actions-silent)
  - [Present Design Context](#12-present-design-context)
- [Step 2: Define Refinement](#step-2-define-refinement)
  - [Route by Source](#21-route-by-source)
  - [Present Refinement Definition](#22-present-refinement-definition)
- [Step 3: Verify Test Suite](#step-3-verify-test-suite)
  - [Run Existing Tests](#31-run-existing-tests)
  - [Present Test State](#32-present-test-state)
- [Step 4: Gather Context](#step-4-gather-context)
  - [Required Reading](#41-required-reading)
  - [Confirm Standards Loaded](#42-confirm-standards-loaded)
- [Step 5: RED — Write Failing Tests](#step-5-red--write-failing-tests)
  - [Write Minimal Test](#51-write-minimal-test)
  - [Verify RED State](#52-verify-red-state)
- [Step 6: GREEN — Minimal Implementation](#step-6-green--minimal-implementation)
  - [Implement Refinement](#61-implement-refinement)
  - [Verify GREEN State](#62-verify-green-state)
- [Step 7: REFACTOR (If Needed)](#step-7-refactor-if-needed)
  - [Assess Need](#71-assess-need)
  - [Refactor and Verify](#72-refactor-and-verify)
- [Step 8: Update Documentation](#step-8-update-documentation)
  - [Update Design Document](#81-update-design-document)
  - [Add Doc-Comments](#82-add-doc-comments)
  - [Verify Documentation](#83-verify-documentation)
  - [Present Documentation Updates](#84-present-documentation-updates)
- [Step 9: Final Verification](#step-9-final-verification)
  - [Run Full Check](#91-run-full-check)
  - [Verify Checklist](#92-verify-checklist)
- [Refine Complete](#refine-complete)
- [Anti-Patterns](#anti-patterns)
- [Common Rationalisations](#common-rationalisations-forbidden)
- [Final Rule](#final-rule)

---

## The Process

### Non-Negotiable Rules

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST locate and read the `*-design.md` document — the single source of truth for the feature
- You MUST search `planning/` and `planning/archive/` (including subfolders) — most recent relevant design doc supersedes older ones
- You MUST verify work is small enough (≤3 files, ≤3 acceptance criteria)
- You MUST read all relevant testing standards before writing any tests
- You MUST follow TDD principles: RED → GREEN → REFACTOR
- You MUST update the design document with all refinement context, implementation changes, and understanding gained
- You MUST add Doc-comments for any changed code
- You MUST verify tests are green before and after implementation
- You MUST use the prescribed tooling commands exactly as listed — no substitution, no additional flags, no pipes
- You MUST read and follow `/midtempo-framework/rules/writing.md`
- You MUST use UK English spelling throughout
- You MUST NOT proceed if scope exceeds Refine skill thresholds

</CRITICAL_REQUIREMENT>

---

### ENTRY GATE

```
IF original design document does not exist
  → INVALID: REDIRECT to `/midtempo-framework/build.md` — No design doc means no delivered feature

IF work affects 4+ files
  → INVALID: REDIRECT to `/midtempo-framework/build.md` — Too large for Refine skill

IF work adds new UI page
  → INVALID: REDIRECT to `/midtempo-framework/build.md` — New pages require full workflow
IF work introduces new architectural patterns
  → INVALID: REDIRECT to `/midtempo-framework/build.md` — New patterns require full workflow

IF work has 4+ acceptance criteria
  → INVALID: REDIRECT to `/midtempo-framework/build.md` — Too complex for Refine skill

IF work is small refinement (≤3 files, ≤3 acceptance criteria, tweaks existing delivered feature)
  → VALID: Continue to Step 1
```

---

## Step 1: Locate Design Context

**Do not start refining.** The `*-design.md` document is the single source of truth for every feature. Find it and understand the full history first.

### 1.1 Agent Actions (Silent)

FIND design document:

STEP 1: Check for explicit reference
  IF the user's message or any supporting document contains a `planning/[path]-design.md` path
    → Use that path directly — skip remaining steps

STEP 2: Derive slug and glob
  Determine the most granular noun phrase that captures the exact subject of the request
  (e.g. "avatar-upload" not "avatar", "pagination-offset" not "pagination")
  Glob `planning/**/*[slug]*-design.md`

STEP 3: Resolve
  IF exactly one match → use it
  IF multiple matches → present the list: "I found multiple matching design documents — which applies?"
    → Wait for human to select before proceeding
  IF zero matches
    → STOP: "I could not locate the design document. Please provide the path."
    → Wait for human response before proceeding


```
READ design document completely:
  - Acceptance criteria (original and any subsequent updates)
  - Key decisions, trade-offs, and rationale
  - Implementation approach and any changes made during delivery
  - Previous refinements and implementation learnings

VERIFY-COMPLETE-READ:
  CHECK the last line says "END OF DOCUMENT"
  IF CHECK fails → Re-read from offset until true end

```

### 1.2 Present Design Context

**Output to human:**

```
Design Context:

Design document: `planning/[path]/[feature]-design.md`

Original feature: [Feature name and purpose]

Key decisions from design:
- [Decision 1]: [Rationale]
- [Decision 2]: [Rationale]

Original acceptance criteria:
- [Criterion 1]
- [Criterion 2]

Previous refinements (if any):
- [Date]: [What was refined]

Current implementation files:
- `src/path/to/file.ts`
- `src/path/to/other.ts`

Does this match your understanding of the feature?
```

**Wait for validation**

**If design document not found:** Ask human for location. DO NOT PROCEED until design document is located.

---

## Step 2: Define Refinement

**One question at a time. Wait for each answer before proceeding.**

### 2.1 Route by Source

```
IF supporting document provided (investigation or review recommendation):
  → GOTO "§2.1.1 With Supporting Document"

IF no supporting document:
  → GOTO "§2.1.2 Without Supporting Document"
```

#### 2.1.1 With Supporting Document

```
1. READ the supporting document completely
2. Present the document's recommendation in your own words:

   "The [investigation/review] recommends:

   Problem: [agent's summary of the finding]
   Proposed change: [agent's summary of the recommendation]
   Scope: [files and acceptance criteria from the doc]

   Does this still match what you want to refine?"

IF human confirms → GOTO "§2.2 Present Refinement Definition"
IF human corrects → Update understanding and re-present
```

#### 2.1.2 Without Supporting Document

**Understanding the issue:**

```
SCAN the user's opening prompt for issue description

IF opening prompt describes the issue with enough detail to act on:
  → Do NOT ask the user to repeat themselves
  → Agent performs codebase analysis (silent):
    - Locate relevant code matching the described behaviour
    - Cross-reference against design doc acceptance criteria
    - Identify what the code does vs what the user described

  → Present reflection:

    "Based on what you described and what I found in the codebase:

    Current behaviour: [agent's technical framing of the issue]
    Location: [file:line references where this behaviour originates]
    Design doc context: [relevant acceptance criteria or decisions]

    Is this an accurate read of the problem?"

  IF human confirms → Continue to "Desired behaviour" below
  IF human corrects → Revise understanding and re-present

IF opening prompt is vague or partial:
  → Ask ONE focused question based on what is missing:

    IF behaviour unclear:
      "What happens when you [specific action related to the feature]?"
    IF location unclear:
      "Where in the application do you see this? (page, action, or feature area)"
    IF expectation unclear:
      "What did you expect to happen when [the action they described]?"

  → Wait for answer
  → Agent performs codebase analysis (silent)
  → Present reflection (same format as above)
```

**Desired behaviour:**

```
SCAN conversation so far for desired behaviour

IF user already stated what they want (in opening prompt or previous response):
  → Do NOT re-ask
  → Agent analyses feasibility against codebase (silent):
    - Can the desired behaviour work within existing architecture?
    - Which files need changing?
    - Any trade-offs or constraints?

  → Present reflection:

    "You want: [agent's technical framing of desired behaviour]

    To achieve this:
    - [File 1]: [what changes]
    - [File 2]: [what changes]

    Constraints: [any trade-offs discovered, or "None identified"]

    Does this capture what you're after?"

  IF human confirms → GOTO "§2.2 Present Refinement Definition"
  IF human corrects → Revise and re-present

IF desired behaviour not yet stated:
  → Ask: "What should happen instead when [the specific action/scenario]?"
  → Wait for answer
  → Agent analyses feasibility (same as above)
  → Present reflection (same format)
```

### 2.2 Present Refinement Definition

**Output to human:**

```
Refinement Definition:

Feature: [Original feature name]
Design doc: `planning/[path]/[feature]-design.md`

Refinement goal: [One-sentence description of what needs tweaking]

Current behaviour: [What's happening now]

Desired behaviour: [What should happen instead]

Files to change:
- `src/path/to/file.ts`

Acceptance criteria:
- [ ] [Criterion 1]
- [ ] [Criterion 2]

Scope check:
- Files: [N] (max 3) ✓
- Criteria: [N] (max 3) ✓

Ready to proceed with TDD?
```

**Wait for validation**

**If scope exceeds limits:** STOP — "This exceeds Refine skill scope. Use `/midtempo-framework/build.md` for full workflow."

---

## Prescribed Commands

**Use these exact commands throughout all steps. No substitution, no additional flags, no pipes.**

#### Test
```bash
npm run test:python    # Run all Python tests
npm run test:python:unit    # Run Python unit tests only (fast, no external dependencies)
npm run test:python:integration    # Run Python integration tests only (slower, may use external resources)
npm run test:python:coverage    # Run Python unit tests with coverage report
```

#### Lint
```bash
npm run lint:python    # Run Python linter for code quality
npm run lint:python:fix    # Fix Python linting issues automatically
npm run fix:all    # Auto-fix formatting and linting issues
```

#### Typecheck
```bash
npm run typecheck:python    # Run Python type checker (mypy)
```
---

## Step 3: Verify Test Suite

**Do not write code or tests yet.** Verify current state first.

### 3.1 Run Existing Tests

```bash
npm run test:python    # Verbose — no summary command configured
```

### 3.2 Present Test State

**Output to human:**

```
Test Suite State:

Result: [PASSING / FAILING]

IF PASSING:
  All [N] tests passing. Ready to proceed.

IF FAILING:
  [N] tests failing. Cannot proceed with Refine skill.
  Failing tests:
  - [test name]: [failure reason]

  Please resolve failing tests in a different conversation before continuing.
```

**If tests failing:** STOP — Wait for human to confirm tests are green before proceeding.

**If tests passing:** Continue to Step 4.

---

## Step 4: Gather Context

**Do not write tests yet.** Read all relevant standards first.

### 4.1 Required Reading

VERIFY-COMPLETE-READ for EVERY file below:
  CHECK the last line says "END OF DOCUMENT"
  IF CHECK fails → Re-read from offset until true end

READ ALL of `/midtempo-framework/rules/tdd.md` → before proceeding
READ ALL of `/midtempo-framework/rules/testing.md` → before proceeding
READ ALL of `/midtempo-framework/rules/writing.md` → before proceeding
READ ALL of `/midtempo-framework/instructions/architecture.md` → before proceeding

IF the current task involves UI
READ ALL of `/midtempo-framework/instructions/frontend-design.md` → for UI component patterns
READ ALL of `/midtempo-framework/instructions/style-guide.md` → for styling conventions



### 4.2 Confirm Standards Loaded

**Output to human:**

```
Standards Loaded:
[for each rules/*.md or instructions/*.md, output]
- Read: [folder/file] [Valid | N/A]

Ready to write failing tests.
```

```
Step 4 complete when ALL conditions met:
- [ ] All rules files read completely (tdd.md, testing.md, writing.md)
- [ ] All applicable instruction files read completely
- [ ] Standards loaded output presented to human
```

**Continue to Step 5.**

---

## Step 5: RED — Write Failing Tests

**MUST Follow tdd.md principles.** 

**MUST follow testing.md rules**

### 5.1 Write Minimal Test

Write test that:
- Shows desired refinement behaviour
- Fails for correct reason (behaviour not implemented)
- Has no placeholder assertions (no hardcoded pass/fail values)
- Asserts on real behaviour, not mocks
- Follows all gates from `/midtempo-framework/rules/testing.md`

### 5.2 Verify RED State

```bash
npm run test:python <test-file>    # Verbose — single file for TDD loop
```

**Output to human:**

```
RED State:

Test file: `tests/path/to/test.test.ts`

Test: [Test name]
Status: FAILING ✓

Failure reason: [Why test fails — should be "behaviour not implemented"]

Expected: [What test expects]
Actual: [What currently happens]

Test is failing for correct reason. Ready to implement.
```

**If test passes:** STOP — Test should fail before implementation. Review test logic.

**If test fails for wrong reason:** Fix test before proceeding.

---

## Step 6: GREEN — Minimal Implementation

**Write simplest code to pass the test.** No over-engineering.

### 6.1 Implement Refinement

- Write minimal code to make test pass
- Focus only on making test green
- No additional features beyond the test
- No premature abstraction

### 6.2 Verify GREEN State

```bash
npm run test:python <test-file>     # New test passes
npm run test:python    # Verbose — no summary command configured                 # All tests still pass
npm run lint:python                 # Clean
npm run typecheck:python            # Clean
```

**Output to human:**

```
GREEN State:

New test: PASSING ✓
All tests: PASSING ([N] tests) ✓
Lint: CLEAN ✓
Typecheck: CLEAN ✓
Files changed:
- `src/path/to/file.ts`: [What changed]

Implementation complete. Ready to refactor if needed.
```

**If any check fails:** Fix before proceeding.

---

## Step 7: REFACTOR (If Needed)

**Only if refinement introduced duplication or complexity.**

### 7.1 Assess Need

```
CHECK for refactoring need:
  - Duplication introduced?
  - Complexity increased unnecessarily?
  - Code clarity reduced?

IF no issues found
  → SKIP to Step 8

IF issues found
  → Refactor while keeping tests green
```

### 7.2 Refactor and Verify

If refactoring:

```bash
npm run test:python    # Verbose — no summary command configured    # Tests still green after each change
npm run lint:python    # Still clean
npm run typecheck:python  # Still clean
```

**Output to human (if refactored):**

```
REFACTOR State:

Refactoring applied:
- [What was refactored and why]

All tests: PASSING ✓
Lint: CLEAN ✓
Typecheck: CLEAN ✓
Refactoring complete.
```

---

## Step 8: Update Documentation

**The design document is the single source of truth. Update it with everything learned during this refinement.**

### 8.1 Update Design Document

Add a "Refinement" section to `planning/[feature]-design.md`:

```
Refinement - [refinement name]

[Date] - [Brief description]

Context
[Why refinement was needed]

Changes
- [What was tweaked]
- [What behaviour changed]

Implementation learnings
- [Understanding gained during refinement]
- [Corrections to original assumptions, if any]

Rationale
[Why this approach was chosen]

Testing
[Test files updated/added]
```

The design doc must reflect the current state of the feature. If the refinement revealed that original decisions or acceptance criteria were wrong, update those sections too — do not leave stale information.

### 8.2 Add Doc-Comments

For any modified functions/classes/interfaces:
- Plain UK English following `/midtempo-framework/rules/writing.md`
- Document parameters, return values, and exceptions as needed


### 8.3 Verify Documentation
```
npm run docs:generate    # Generate API documentation
npm run docs:validate    # Validate docstring presence on all public functions and classes
```
Add content so that there are ZERO errors or warnings.

### 8.4 Present Documentation Updates

**Output to human:**

```
Documentation Updated:

Design document: `planning/[path]/[feature]-design.md`
  - Added refinement section with context

Doc-comments added:
- `src/path/to/file.ts`: [N] functions documented

Ready for final verification.
```

```
Step 8 complete when ALL conditions met:
- [ ] Design document updated with refinement section
- [ ] Doc-comments added for all modified functions/classes
- [ ] Documentation commands run clean (if applicable)
- [ ] Documentation updates presented to human
```

---

## Step 9: Final Verification

**Confirm all work is complete.**

### 9.1 Run Full Check

```bash
npm run test:python    # Verbose — no summary command configured    # All tests passing
npm run lint:python    # Clean
npm run typecheck:python  # Clean
npm run docs:generate    # Clean
```

### 9.2 Compliance Gate Verification

```
IF delivery scope touches architecture AND '/midtempo-framework/instructions/architecture.md "Compliance Gates"' not verified
  → STOP. "Verify all architecture compliance gates before proceeding."
IF delivery scope touches error handling AND '/midtempo-framework/instructions/error-handling.md "Compliance Gates"' not verified
  → STOP. "Verify all error-handling compliance gates before proceeding."
IF delivery scope touches new page creation AND '/midtempo-framework/instructions/new-page.md "Compliance Gates"' not verified
  → STOP. "Verify all new-page compliance gates before proceeding."

IF delivery scope touches UI components AND '/midtempo-framework/instructions/frontend-design.md "Compliance Gates"' not verified
  → STOP. "Verify all frontend-design compliance gates before proceeding."
IF delivery scope touches styling AND '/midtempo-framework/instructions/style-guide.md "Compliance Gates"' not verified
  → STOP. "Verify all style-guide compliance gates before proceeding."


IF '/midtempo-framework/rules/testing.md "Compliance Gates"' not verified
  → STOP. "Verify all testing compliance gates before proceeding."


VALID: Continue to "§9.3 Verify Checklist"
```

### 9.3 Verify Checklist

```
VERIFY completion:
  - [ ] Original design document read
  - [ ] Refinement goal met
  - [ ] Tests written following TDD (RED → GREEN → REFACTOR)
  - [ ] Design document updated with refinement context
  - [ ] Doc-comments added for changed code
```

---

## Refine Complete

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output after Exit Gate passes - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
- You MUST verify refinement goal is met and tests followed TDD before producing this output
</CRITICAL_REQUIREMENT>

```
---
                         REFINEMENT COMPLETE

---

Original feature: [feature name]
Design doc: `planning/[path]/[feature]-design.md`

Refinement: [what was tweaked and why]

Files changed:
- `src/path/to/file.ts`
- `tests/path/to/test.test.ts`

Tests added: [N] tests in [test-file]
All tests passing. Lint/typecheck clean.

Documentation updated:
- Design doc updated with refinement context
- Doc-comments added for [N] changed exports

Commit

[feat | fix]: [title of change]

[3 sentences describing problem and what was changed].

---
Review refinement and commit.

---
```

---

## Anti-Patterns

### Anti-Pattern 1: Skipping Design Doc

**INVALID:**

```
Human: "Tweak the playlist creation flow"
Agent: *starts coding without reading design doc*
```

**VALID:** Read `planning/[feature]-design.md` first to understand original decisions.

### Anti-Pattern 2: Scope Creep

**INVALID:** "While I'm here, let me also add sorting, filtering, and export..."

**VALID:** Stick to stated refinement goal. Additional features → full workflow.

### Anti-Pattern 3: Code-First

**INVALID:** Write refinement code, then add tests after.

**VALID:** RED → GREEN → REFACTOR. Watch test fail first.

### Anti-Pattern 4: Forgetting Future Context

**INVALID:** Make refinement, don't update design doc.

**VALID:** Update design doc so future maintainers understand why refinement was needed.

### Anti-Pattern 5: "Refine" Means "Skip Tests"

**INVALID:** "It's just a small tweak, I'll skip tests."

**VALID:** "Refine" follows TDD. Small tweaks break. Write the test.

### Anti-Pattern 6: Writing Tests Without Reading Standards

**INVALID:** Start writing tests without reading `/midtempo-framework/rules/testing.md`.

**VALID:** Read all relevant testing standards (Step 4) before writing any tests.

### Anti-Pattern 7: Multiple Questions at Once

**INVALID:**

```
"What's wrong? What should happen? Which files are affected?"
```

**VALID:** Ask one question. Wait for answer. Then ask next question.

### Anti-Pattern 8: Jumping Steps

**INVALID:**

```
Step 1 complete → Jump to Step 6 (implementation)
Step 2 complete → Skip Step 4 (standards loading)
```

**VALID:** Complete steps in order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9. No skipping.

---

## Common Rationalisations (FORBIDDEN)

| Human Says                            | Agent Must Respond                                                                 |
| ------------------------------------- | ---------------------------------------------------------------------------------- |
| "It's too small for a design doc"     | "Design doc already exists for the feature. I must update it with context."        |
| "Skip TDD just this once"             | "No. Refine follows TDD. Writing failing test first."                           |
| "Just make it work, we'll test later" | "No. Tests written after prove nothing. Writing test now."                         |
| "While you're there, also add..."     | "That exceeds Refine skill scope. Use full workflow for additional features."         |
| "Don't bother updating design doc"    | "No. Future maintainers need context. Updating design doc."                        |
| "Skip reading testing.md, I know TDD" | "No. Step 4 is mandatory. Reading `/midtempo-framework/rules/testing.md` before proceeding." |
| "Just tell me what to change"         | "I must understand the design context first. Locating design document."            |

---

## Final Rule

```
REFINEMENT = SMALL POST-DELIVERY REFINEMENT
REQUIRES: Design doc exists, ≤3 files, ≤3 criteria, follows TDD
PHASES: Context → Define → Verify → Standards → RED → GREEN → REFACTOR → Document → Verify
UPDATES: Design doc with context for future maintainers
```

Never skip steps. Never exceed scope limits. Never bypass TDD.

No exceptions without human partner's permission.

---
**END OF DOCUMENT:** Total sections: 7 | Purpose: Refine delivered features with targeted tweaks