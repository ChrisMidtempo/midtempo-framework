# Improve Coverage Skill

## Overview

This skill improves test coverage incrementally. It analyses coverage output, identifies gaps, and writes tests in priority order.

**Execution:** One batch per conversation. Progress tracked in `planning/coverage-progress.md`.

**Prerequisite:** Test suite must pass. Route failing tests through `/midtempo-framework/bugs.md`.

**Bootstrap Acknowledgement:** Only on first use. Don't show once batch execution begins.

---

## Table of Contents

- [Overview](#overview)
- [Bootstrap Use Only](#bootstrap-use-only-only-if-human-isnt-in-batch-delivery)
- [Non-Negotiable Rules](#non-negotiable-rules)
- [Test Priority System](#test-priority-system)
  - [Coverage-Complexity Matrix](#coverage-complexity-matrix)
  - [Complexity Scoring](#complexity-scoring)
  - [Priority Decision Gate](#priority-decision-gate)
  - [Incremental Layer Strategy](#incremental-layer-strategy)
- [ENTRY GATE](#entry-gate)
- [Fresh Start Entry Gate](#1-fresh-start-entry-gate)
  - [Read Testing Rules](#11-read-testing-rules)
  - [Assess Coverage State](#12-assess-coverage-state)
  - [Create Progress File](#13-create-progress-file)
- [Continuation Entry Gate](#2-continuation-entry-gate)
- [Execute Batch](#3-execute-batch)
  - [Select Batch Scope](#31-select-batch-scope)
  - [Execute Coverage Work](#32-execute-coverage-work)
  - [Verify Batch](#33-verify-batch)
- [Batch Complete](#4-batch-complete)
  - [Update Progress File](#41-update-progress-file)
  - [Check Completion Status](#42-check-completion-status)
  - [Batch Complete Output](#43-batch-complete-output)
- [All Complete Output](#5-all-complete-output)
- [Quick Reference](#quick-reference)

---

## Bootstrap Acknowledgement

IF `planning/coverage-progress.md` exists
  → SKIP: Batch in progress. Bootstrap acknowledgement not required.
  → Continue to Non-Negotiable Rules

IF `planning/coverage-progress.md` does NOT exist
  → Read and apply the acknowledgement below.

Writing tests after implementation with an LLM is not recommended. Tests written retroactively verify what the code does, not what it should do. This produces brittle tests coupled to implementation details.

This skill exists because the framework require high test coverage to function reliably. When coverage is low, the agent can ignore poor results. Bootstrapping coverage for legacy code is a pragmatic compromise.

Once baseline coverage exists, I'd recommend not using this skill. ANY agent-generated code with low coverage is a sign the LLM wasn't following instructions and has created code that you've not been aware of. 

**Human must confirm before proceeding:**

> "I understand this skill is to bootstrap coverage only."

WAIT for human acknowledgement.

---

## Non-Negotiable Rules

<CRITICAL_REQUIREMENT type="MANDATORY">

**CORE PRINCIPLE: Improve coverage. No production code changes.**

- You MUST verify existing tests pass before starting
- You MUST read coverage output from the tool (no assumed metrics)
- You MUST follow `/midtempo-framework/rules/testing.md` for all test changes
- You MUST update progress file after each batch
- You MUST start a new conversation for each batch
- You MUST NOT modify production code (route needed changes to bugs.md, refine.md, or refactor.md)
- You MUST NOT disable tests to "improve" coverage
- You MUST NOT add tests that test mock behaviour
- You MUST NOT skip steps or offer "skip" options

**Production code issues:** Log in progress file under "Production Issues" section. Human routes these through bugs|refine|build|refactor skills.

**End state:** Coverage improved to plateau or human-specified target.

</CRITICAL_REQUIREMENT>

---

## Test Priority System

**Core Principle:** Maximise coverage gained per unit of complexity. Never write complex tests for marginal gains.

### Coverage-Complexity Matrix

```
                     │ HIGH COVERAGE IMPACT      │ LOW COVERAGE IMPACT
                     │ (large uncovered area)    │ (small uncovered area)
─────────────────────┼───────────────────────────┼─────────────────────────
LOW COMPLEXITY       │ ★★★★ PRIORITY 1          │ ✗ SKIP
(no mocks,           │ "Refine"              │ "Diminishing Returns"
 direct I/O,         │ → Write immediately       │ → Only if near target
 single assertion)   │                           │
─────────────────────┼───────────────────────────┼─────────────────────────
MEDIUM COMPLEXITY    │ ★★★ PRIORITY 2           │ ★ PRIORITY 4
(1-2 mocks,          │ "Essential Coverage"      │ "Fill Later"
 moderate setup)     │ → Write after refine  │ → Only to reach target
                     │                           │
─────────────────────┼───────────────────────────┼─────────────────────────
HIGH COMPLEXITY      │ ★★ PRIORITY 3            │ ✗ AVOID
(many mocks,         │ "Justified Complexity"    │ "Effort Sink"
 fixtures,           │ → Only if critical path   │ → Never write these
 external deps)      │   has no simpler option   │
```

### Complexity Scoring

| Score | Level | Characteristics |
|-------|-------|-----------------|
| 1-2 | Simple | No mocks, direct input/output, single assertion |
| 3-4 | Medium | 1-2 mocks, some setup, clear test boundary |
| 5+ | Complex | Multiple mocks, fixtures, async chains, state management |

### Priority Decision Gate

Before writing ANY test, apply this gate:

```
CALCULATE:
  coverage_gain = estimated lines/paths covered by this test
  complexity    = mocks + setup_steps + (2 if external_deps)

DECISION:
  IF large coverage gain AND complexity ≤ 2
    → WRITE IMMEDIATELY (Priority 1 - Quick Win)

  IF moderate coverage gain AND complexity ≤ 4
    → WRITE (Priority 2 - Essential)

  IF small coverage gain AND complexity ≤ 4 AND file has major gaps
    → WRITE (Priority 3 - Gap Filler)

  IF minimal coverage gain OR complexity > 4
    → SKIP unless file cannot reach target otherwise
    → If must write, document justification
```

INVALID:
  Test: "config parser raises error on malformed input"
  coverage_gain = 3 lines
  complexity    = 5 (mocks external file system, async loader, state reset)
  Decision: WRITE — it covers a gap
  → Violates: complexity > 4 with small gain — this is an "Effort Sink". SKIP.

VALID:
  Test: "config parser raises error on malformed input"
  coverage_gain = 3 lines
  complexity    = 1 (pass malformed string directly, assert raises)
  Decision: IF small gain AND complexity ≤ 4 AND file has major gaps → WRITE (Priority 3)
  → Complexity ≤ 4. Check file gaps before deciding.

### Incremental Layer Strategy

For each file, work in layers. **STOP when the file's coverage gain from the completed layer is < 5%** (measured from the full test suite coverage report, not individual test file runs).

| Layer | What to Test | Complexity Limit |
|-------|--------------|------------------|
| 1. Happy Path | Main success scenarios, primary function behaviour | Simple (1-2) |
| 2. Error Boundaries | Explicit throws, null guards, validation failures | Simple-Medium (1-3) |
| 3. Branch Filling | Conditional branches, early returns, switch cases | Medium (2-4) |
| 4. Edge Cases | Only for critical business logic if still needed | As needed |

**Layer Rules:**
- Complete Layer 1 for ALL files before starting Layer 2
- After each layer, re-run coverage to measure gains
- Skip to next file when current file's layer gain < 5% (from full suite report)
- Never proceed to Layer 4 for utility/helper files

INVALID:
  File: `utils/parser.py` — Layer 1 complete
  Coverage before: 60% → after: 62% (gain: 2%)
  Decision: Continue to Layer 2 (error boundaries) for this file
  → Violates: gain < 5% — STOP. Mark done for this layer, move to next file.

VALID:
  File: `utils/parser.py` — Layer 1 complete
  Coverage before: 60% → after: 62% (gain: 2%)
  Decision: Mark `utils/parser.py` done for Layer 1. Move to next file.
  → Complete Layer 1 for ALL files before re-running coverage and starting Layer 2.

---

## ENTRY GATE

```
RUN: npm run test:python    # Verbose — no summary command configured

IF tests fail
  → STOP: "Test suite must pass before improving coverage.
    Route failing tests through /midtempo-framework/bugs.md"
  → END

IF tests pass
  → CHECK if `planning/coverage-progress.md` exists

IF progress file exists
  → READ ALL of `planning/coverage-progress.md`
  → GOTO "§2. Continuation Entry Gate"

IF progress file does NOT exist
  → GOTO "§1. Fresh Start Entry Gate"
```

---

## 1. Fresh Start Entry Gate

**First time running this skill.**

### 1.1 Read Testing Rules

```
READ ALL of `/midtempo-framework/rules/testing.md`

This skill follows testing.md for all test changes. Understand:
  - Gate enforcement (all 6 gates)
  - Anti-patterns and auto-recovery
  - Agent checklist requirements

OUTPUT declaration verbatim:
"I have read testing.md - all tests must pass 6 gates, no mock-behaviour testing, no test-only production methods"
```

### 1.2 Assess Coverage State

```
1. RUN: npm run test:python:coverage    # Coverage — metrics + pass/fail

2. READ the coverage output completely.

3. EXTRACT whatever metrics the tool provides:
   - Overall coverage percentage (if available)
   - Per-file coverage percentages (if available)
   - Line/branch/function breakdown (if available)
   - Uncovered files list (if available)

   Do NOT assume specific metrics exist. Work with what the tool reports.

4. IDENTIFY:
   - Files with lowest coverage
   - Files with zero coverage
   - Large files with coverage gaps

5. PRESENT coverage assessment:

**COVERAGE STATE ASSESSMENT**

**Tool output format:** [describe what metrics are available]

**Current coverage:**
[List whatever metrics the tool reported]

**Files with lowest coverage:**
- [file 1]: [X]%
- [file 2]: [X]%
- [file 3]: [X]%
...

**Files with zero coverage:**
- [file 1]
- [file 2]
...

6. CONTINUE to §1.3
```

### 1.3 Create Progress File

```
CREATE `planning/coverage-progress.md` with:

# Coverage Improvement Progress

## Status
- **Current batch:** 1
- **Current layer:** 1 (Happy Path)
- **Started:** [DD/MM/YYYY]

## Baseline Metrics
[Record whatever metrics the coverage tool provides]

## Current Metrics
[Same as baseline initially]

## Files by Priority

### Priority 1: Refine (low coverage + low complexity)
| File | Coverage | Status |
|------|----------|--------|
| `[file]` | [X]% | pending |
...

### Priority 2: Essential (moderate coverage + medium complexity)
| File | Coverage | Status |
|------|----------|--------|
...

### Priority 3: Gap Fillers (needs more work)
| File | Coverage | Status |
|------|----------|--------|
...

### Skipped (complexity too high for gains)
| File | Reason |
|------|--------|
...

## Production Issues (route to bugs|refine|refactor)
[None yet]

## Completed Batches
[None yet]

---

PROCEED to §3. Execute Batch.
```

<CRITICAL_REQUIREMENT type="EXIT_GATE">

**§1 Fresh Start is complete when ALL conditions are met:**

- [ ] Testing rules read (testing.md declaration produced)
- [ ] Coverage state assessed (metrics extracted from tool output)
- [ ] Progress file created with baseline metrics and prioritised file list
- [ ] Human reviewed coverage assessment

IF any condition is not met → STOP. Complete the missing step before proceeding.

</CRITICAL_REQUIREMENT>

---

## 2. Continuation Entry Gate

**Returning to continue from previous batch.**

```
1. READ ALL of `planning/coverage-progress.md`

2. READ ALL of `/midtempo-framework/rules/testing.md`

3. OUTPUT declaration verbatim:
   "I have read testing.md - all tests must pass 6 testing gates, no mock-behaviour testing, no test-only production methods"

4. EXTRACT:
   - Current batch number
   - Current layer
   - Remaining work items
   - Previous coverage metrics

5. VERIFY current state:
   RUN: npm run test:python:coverage    # Coverage — metrics + pass/fail
   COMPARE with progress file metrics

   IF metrics improved since last batch
     → UPDATE progress file with current metrics
     → INFORM human of improvement

6. PRESENT continuation summary:

**CONTINUING COVERAGE IMPROVEMENT**

Batch: [N]
Layer: [1-Happy Path | 2-Error | 3-Branch | 4-Edge]

**Progress since last batch:**
[Coverage delta]

**Remaining this layer:** [count] files

Ready to proceed with batch [N]?

WAIT for human confirmation.

7. VALID: Proceed to §3. Execute Batch.
```

<CRITICAL_REQUIREMENT type="EXIT_GATE">

**§2 Continuation is complete when ALL conditions are met:**

- [ ] Progress file read (batch number and layer extracted)
- [ ] Testing rules read (testing.md declaration produced)
- [ ] Current coverage verified against progress file metrics
- [ ] Human confirmed continuation summary

IF any condition is not met → STOP. Complete the missing step before proceeding.

</CRITICAL_REQUIREMENT>

---

## 3. Execute Batch

### 3.1 Select Batch Scope

```
DETERMINE current layer from progress file

FOR current layer:
  SELECT 3-5 files based on priority:
    - Priority 1 files first (refine)
    - Then Priority 2 files
    - Then Priority 3 files if needed

  BATCH CONSTRAINT:
    - Total estimated complexity ≤ 15 per batch
    - Sum complexity scores of planned tests
    - If batch would exceed 15, reduce file count

PRESENT batch to human:

**BATCH [N] - LAYER: [layer name]**

Scope: [count] files

**Files:**
1. `[file 1]` - [X]% coverage - [reason for selection]
2. `[file 2]` - [X]% coverage - [reason for selection]
...

Proceed with this batch?

WAIT for approval.

IF human approves
  → VALID: Proceed to §3.2 Execute Coverage Work.
IF human rejects or requests changes
  → REVISE: Adjust file selection and re-present.
```

### 3.2 Execute Coverage Work

```
FOR each file in batch:

  1. CHECK current file coverage
     IF file coverage acceptable for current layer
       → SKIP this file
       → CONTINUE to next file

  2. READ the source file completely

  3. IDENTIFY test candidates for current layer:

     LAYER 1 (Happy Path):
       - Main function success scenarios
       - Primary exported behaviour
       - Core business logic paths
       - Complexity limit: 1-2 (no mocks if possible)

     LAYER 2 (Error Boundaries):
       - Explicit error throws
       - Null/undefined guards
       - Validation failures
       - Try/catch blocks
       - Complexity limit: 1-3

     LAYER 3 (Branch Filling):
       - Conditional branches (if/else)
       - Early returns
       - Switch cases
       - Ternary operators
       - Complexity limit: 2-4

     LAYER 4 (Edge Cases - critical files only):
       - Boundary conditions
       - Race conditions
       - Complex state transitions
       - Complexity limit: as needed (document justification)

  4. APPLY Priority Decision Gate for each test:
     CALCULATE coverage_gain and complexity
     IF test fails gate → SKIP and try simpler approach
     IF no simpler approach → document in progress file

  5. APPLY testing.md compliance gates:
     - CG-1: Real behaviour assertions — no mock existence or placeholders
     - CG-2: No test-only methods in production — utilities in repo-specific locations per architecture.md §7.3
     - CG-3: Mocks at IO/network level only — never mock business logic test depends on
     - CG-4: Mock mirrors complete real API structure — all documented fields
     - CG-5: Test isolation — self-contained, no shared state, order-independent
     - CG-6: Coverage scope — happy path, error paths, boundary conditions
     - CG-7: Shared test data uses factories or helpers — no duplicated inline construction across files

  6. WRITE tests following TDD principles:
     - Test describes expected behaviour
     - Assertions on real behaviour
     - No placeholder assertions
     - Prefer simple over comprehensive

  7. VERIFY after each test:
     RUN: npm run test:python:unit <test-file>
     - Test passes
     - Coverage improved
     - Complexity within layer limit

  8. RE-CHECK file coverage:
     RUN: npm run test:python:coverage    # Coverage — metrics + pass/fail
     IF per-test gain < 2% (from full suite report, not individual test run)
       → MARK file done for this layer
       → CONTINUE to next file

  9. IF production code issue discovered:
     - DO NOT modify production code
     - LOG in progress file "Production Issues" section
     - INFORM human: "Found production issue in [file]: [description]. Route through bugs|refine|refactor skill."
     - CONTINUE with test work
```

### 3.3 Verify Batch

```
AFTER all batch work complete:

RUN: npm run test:python    # Verbose — no summary command configured
RUN: npm run test:python:coverage    # Coverage — metrics + pass/fail
VERIFY:
  - All tests pass
  - No new failures introduced
  - Coverage metrics improved

IF tests fail:
  → FIX immediately
  → Tests MUST pass before proceeding

IF coverage decreased:
  → INVESTIGATE cause
  → FIX before proceeding
```

---

## 4. Batch Complete

### 4.1 Update Progress File

```
UPDATE `planning/coverage-progress.md`:

1. UPDATE current metrics
2. MARK completed files
3. ADD to Completed Batches:

### Batch [N] - [DD/MM/YYYY]
- Layer: [layer name]
- Files completed: [count]
- Coverage: [before] → [after]
- Tests: passing
```

### 4.2 Check Completion Status

```
RUN: npm run test:python:coverage    # Coverage — metrics + pass/fail

CHECK completion criteria:
  - All Priority 1 files done?
  - All Priority 2 files done?
  - Coverage gains plateauing? (< 1% improvement per batch)
  - Human-specified target met? (if provided)

IF coverage plateau reached OR target met:
  → GOTO §5. All Complete Output

IF more work remains:
  → GOTO §4.3 Batch Complete Output
```

### 4.3 Batch Complete Output

Before presenting batch complete output, verify:

```
SELF-CHECK:

1. Coverage values match the coverage report output from §4.2
2. All files listed under "Files modified" appear in `planning/coverage-progress.md` as updated
3. Batch number matches the current batch in `planning/coverage-progress.md`
4. "Tests: passing" confirmed by §3.3 Verify Batch result

IF any check fails → Fix before presenting.
```

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output for next conversation - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
- You MUST verify coverage values match the coverage report before producing this output
</CRITICAL_REQUIREMENT>

```
**BATCH [N] COMPLETE**

Layer: [layer name]
Files completed: [count]
Tests skipped (priority gate): [count]

**Coverage:**
[Before] → [After]

**Files modified:**
- [file 1]
- [file 2]

Tests: passing

Progress file updated: planning/coverage-progress.md

---

**PRODUCTION ISSUES FOUND (route separately)**

[None OR list issues to route through bugs|refine|refactor skills]

---

**COMMIT**

test: improve coverage batch [N]

- [Primary change description]
- Coverage: [before] → [after]

---

**NEXT BATCH**

Start a NEW conversation with:

> Continue coverage improvement using /midtempo-framework/improve-coverage.md
```

§4.3 is complete when ALL conditions met:
- [ ] SELF-CHECK passed (all 4 criteria verified against artefacts)
- [ ] Batch complete output produced with all required fields populated
- [ ] Coverage delta matches §4.2 coverage report values
- [ ] Next batch instructions included

<CRITICAL_REQUIREMENT type="EXIT_GATE">

**§4 Batch Complete is complete when ALL conditions are met:**

- [ ] Progress file updated with current metrics and completed files
- [ ] Completion status checked (plateau or target evaluated)
- [ ] All tests passing
- [ ] Batch complete output produced with coverage delta

IF any condition is not met → STOP. Complete the missing step before proceeding.

</CRITICAL_REQUIREMENT>

---

## 5. All Complete Output

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output when coverage target achieved - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
</CRITICAL_REQUIREMENT>

Before presenting all complete output, verify:

```
SELF-CHECK:

1. Final coverage values match the coverage report output from §4.2
2. Baseline values match the baseline recorded in `planning/coverage-progress.md`
3. Batches completed count matches the number of entries under "Completed Batches" in progress file
4. All production issues listed match those logged in progress file

IF any check fails → Fix before presenting.
```

```
**COVERAGE IMPROVEMENT COMPLETE**

**Final coverage:**
[List all available metrics]

**Improvement:**
[Baseline] → [Final]

**Summary:**
- Batches completed: [N]
- Files improved: [count]
- Tests added: [count]

---

**PRODUCTION ISSUES TO ADDRESS**

[List any production issues found - route through proper skills]

---

**CLEANUP**

Archive progress file:
`mv planning/coverage-progress.md planning/archive/`

---

COMMIT MESSAGE (copy/paste):
─────────────────────────────────────────────────────────────────

test: improve coverage to [X]%

Coverage improvement:
- [Baseline] → [Final]
- Files improved: [count]
- Tests added: [count]

Batches completed: [N]

─────────────────────────────────────────────────────────────────
```

---

## Quick Reference

### Invocation

**Fresh start:**
```
Improve coverage using /midtempo-framework/improve-coverage.md
```

**Continue batch:**
```
Continue coverage improvement using /midtempo-framework/improve-coverage.md
```

### Commands

```bash
npm run test:python              # Run all tests
npm run test:python:unit         # Run unit tests only
npm run test:python:coverage     # Run with coverage report
```

### Progress File Location

`planning/coverage-progress.md`

### Layers

1. **Happy Path:** Main success scenarios (complexity 1-2)
2. **Error Boundaries:** Error handling paths (complexity 1-3)
3. **Branch Filling:** Conditional coverage (complexity 2-4)
4. **Edge Cases:** Critical files only, as needed

### Testing Compliance Gates

From `/midtempo-framework/rules/testing.md` "Compliance Gates" section:
- CG-1: Real behaviour assertions — no mock existence or placeholders
- CG-2: No test-only methods in production — utilities in repo-specific locations per architecture.md §7.3
- CG-3: Mocks at IO/network level only — never mock business logic test depends on
- CG-4: Mock mirrors complete real API structure — all documented fields
- CG-5: Test isolation — self-contained, no shared state, order-independent
- CG-6: Coverage scope — happy path, error paths, boundary conditions
- CG-7: Shared test data uses factories or helpers — no duplicated inline construction across files

### Production Code Constraint

**NEVER modify production code in this skill.**

If production issues found:
1. Log in progress file "Production Issues" section
2. Inform human
3. Human routes through bugs|refine|refactor skill
4. Continue with test work only

---

---
**END OF DOCUMENT:** Total sections: 9 | Purpose: Improve test coverage incrementally