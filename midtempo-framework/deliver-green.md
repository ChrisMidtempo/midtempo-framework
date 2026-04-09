# Deliver - GREEN State

## Overview

**Goal:** Make all failing tests pass with minimal production code whilst adhering to the repo's rules and instructions. No refactoring in this task.

**Inputs:**
 - Approved delivery plan (`planning/[feature-name]-plan.md`)
 - Approved test manifest (`planning/[feature-name]-tests.md`)
 - TDD Red State — all tests failing for the correct reason 

**Outputs:**
 - Production code that makes every test pass
 - Clean typecheck status
 - Coverage meeting thresholds

**Workflow integration:**
 - This skill is ONLY run as a `deliver.md` sub-skill
 - It is NEVER run as a stand-alone skill

---

## Table of Contents

- [Overview](#overview)
- [Goal](#1-goal)
- [Entry Gate](#2-entry-gate)
- [Process](#3-process)
  - [Anti-Patterns](#31-anti-patterns)
  - [Checklist](#32-checklist)
- [Exit Gate](#4-exit-gate)
  - [Criteria for Valid](#41-criteria-for-valid)
- [Complete Script](#5-complete-script)

---

## 1. Goal

All tests pass with minimal production code. No refactoring in this task.

## 2. Entry Gate

**Verify RED state:**

**Check test status using the log file**

```bash
tail -5 /planning/last-test-ran.log
```


```
READ `planning/[feature-name]-tests.md` Status field

IF Status field does not start with "Red"
  → STOP. "Test manifest status is not Red. Complete deliver-red first."

PARSE test counts from Status field (total, failing, known-pass if present)

COMPARE against test status check output above:
  IF failure count ≠ Status failing count
    → STOP. "Test state mismatch: test output shows [N] failures, manifest status claims [N]. Resolve before proceeding."
  IF total test count ≠ Status total count
    → STOP. "Test count mismatch: test output shows [N] tests, manifest status claims [N]. Resolve before proceeding."

VALID: Red state verified — counts match between manifest status and test output.

VERIFY-COMPLETE-READ for EVERY file below:
  CHECK the last line says "END OF DOCUMENT"
  IF CHECK fails → Re-read from offset until true end

READ ALL of `/midtempo-framework/instructions/purpose.md` → before proceeding
READ ALL of `/midtempo-framework/instructions/architecture.md` → before proceeding
READ ALL of `/midtempo-framework/instructions/error-handling.md` → before proceeding


READ ALL of `/planning/[feature-name]-plan.md` → to understand delivery scope

IF "delivery scope" involves UI
 READ ALL of `/midtempo-framework/instructions/frontend-design.md` → before proceeding
 READ ALL of `/midtempo-framework/instructions/style-guide.md` → before proceeding
IF "delivery scope" includes adding a new page/screen
  READ ALL of `/midtempo-framework/instructions/new-page.md` → before proceeding

VALID: Continue with `§3. Process`.
```

## 3. Process

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST complete deliver-green with failures = 0 — no exceptions
- You MUST write the smallest code to pass each test AND adhere to this repo's instructions and rules documents
- You MUST only run targeted file tests (`npm run test:python <test-file>`) during implementation — full suite and coverage runs are for the exit gate only
- You MUST NOT rationalise failures as "acceptable", "follow-up work", or "integration only" — the exit gate (§4) handles integration test classification, not you
- You MUST NOT skip failing tests without human approval
- You MUST NOT complete deliver-green (Phase 2 in deliver.md) with failures > 0 for any reason
- You MUST NOT add behaviour beyond what the test requires
- You MUST NOT refactor (that happens later)
- You MUST NOT optimise prematurely or add "nice to have" code

</CRITICAL_REQUIREMENT>

For each failing test:

1. **Write minimal implementation** — Smallest code to pass the test AND adhere to the repo's rules/instructions
2. **Verify GREEN** — Run `npm run test:python <test-file>    # Verbose — single file for TDD loop`
3. **Move to next test** — Do not refactor.

**If you cannot make a test pass after 3 implementation approaches (3 distinct code changes — not 3 test runs of the same code):**
- Stop working on implementation
- Ask question to escalate to human
- Provide test name, failure reason, attempts made, recommendation
- Wait for human decision

**Commands (during implementation):**

```bash
npm run test:python    # Run all Python tests
npm run test:python:unit    # Run Python unit tests only (fast, no external dependencies)
npm run test:python:integration    # Run Python integration tests only (slower, may use external resources)
npm run test:python:coverage    # Run Python unit tests with coverage report
npm run typecheck:python    # Type errors signal incorrect code — catch while writing
```

### 3.1 Anti-Patterns

INVALID:
  "3 tests are failing but they're integration tests — they'll pass
  in the full environment. Completing deliver-green."
  Why invalid: Broken code does not become acceptable because the tests are integration tests.

INVALID:
  "This test fails due to an external dependency. Marking as
  follow-up work and continuing."
  Why invalid: Self-approving deferrals. Escalate to human — do not self-classify and continue.

VALID:
  "Integration test `test_create_user` fails with ConnectionRefusedError.
  Exit gate classified as service unavailability — recorded as deferred."
  Why valid: The exit gate (§4) classifies integration failures. Service unavailability
  is deferred there — not self-approved during implementation.

VALID:
  "3 tests failing. Escalating to human with test names, failure
  reasons, and recommendations. Awaiting decision."

### 3.2 Checklist

**Output to human:**

- [ ] All tests from `[feature-name]-tests.md` passing
- [ ] No production methods exist without test coverage
- [ ] No "test-only" methods in production code
- [ ] No placeholder comments implying incomplete implementation:
  - [ ] No `// Additional ... as defined in ...`
  - [ ] No `// TODO: add remaining ...`
  - [ ] No `// See ... for full definition`
  - [ ] All interfaces/types fully defined with real properties
- [ ] No file has < 80% coverage (low coverage = code added outside test manifest)

**Exit gate commands (run ONCE before human review):**

```bash
npm run test:python:unit                     # Unit tests — must all pass
npm run test:python:integration              # Integration tests — must pass or defer
npm run typecheck:python          # Type check - verify no warnings or errors
```

## 4. Exit Gate

**PROHIBITED: Self-approving failed tests or rationalising failures.**

```
IF `npm run test:python:unit` shows failures > 0
  → STOP. "Unit tests failing: [count]. Fix implementation."
IF `npm run test:python:integration` shows failures > 0
  → Classify each failure:
    IF failure is a connection/service error (timeout, refused, unavailable)
      → Record as "deferred — services unavailable" with test name and actual error message
    IF failure is a code error (assertion, logic, type)
      → STOP. "Integration test failing: [test name]. Fix implementation."
  → **Output to human:**
    "Integration test classification:
    - [test name]: [DEFERRED — service unavailable / FAILING — code error]
      Error: [actual error message]
    Approve this classification?"
  → WAIT for human approval before proceeding

IF you cannot fix a failing test after 3 implementation attempts
  → ESCALATE TO HUMAN:
    • Test name and file path
    • Expected behaviour
    • Current failure message
    • Implementation attempts (list 3 approaches tried)
    • Recommendation (skip test / modify test / change approach)
  → Human decides. You must not skip tests without approval.

IF `npm run typecheck:python` has errors
  → STOP. "Type errors: [count]. Fix before proceeding."

IF Coverage fails thresholds (< 90% overall)
  → STOP. "VIOLATION: Overall coverage below threshold."
  → Required: ≥ 90% (lines, functions, branches)
  → 89% is not 90%. Threshold is strict.
  → ANALYSE and REPORT to human:
    • Current coverage percentages (lines, functions, branches)
    • Which areas are uncovered (from coverage report)
    • What the uncovered code does
    • Is this functionality in test manifest? (YES/NO + explanation)
  → ASK human: "Overall coverage [X]% (threshold: 90%). Uncovered: [describe code].
    [Is/Is not] in test manifest: [explain].
    **TDD violation**: This code has no tests.

    Options:
    [A] Delete uncovered code, return to test manifest, add missing tests, re-run RED→GREEN (proper TDD cycle)
    [B] Accept as-is (violates TDD - requires justification)"
  → Wait for human decision.
  → If [A] chosen:
    1. Delete uncovered code
    2. Add a "## Stage 2 — Coverage Gaps" section to `planning/[feature-name]-tests.md` listing each uncovered area and the code it covers
    3. Stop Step 2
    4. Tell human to start a new conversation with:

    `Run /midtempo-framework/write-tests.md on planning/[feature-name]-plan.md — TDD in progress, coverage gaps. Add tests to resolve gaps in Stage 2 — Coverage Gaps section.`
  → If [B] chosen: Continue to §5 Complete Script.

IF any file has < 80% coverage
  → STOP. "Per-file coverage violation: [file] at [X]% (threshold: 80%). Low coverage indicates code added outside the test manifest."
  → Report file name, coverage percentage, and uncovered lines to human
  → ASK human: "Add tests for this file or accept as-is?"
  → WAIT for human decision.

IF `npm run format:python` not run
  → STOP. "Code not formatted. Run `npm run format:python` to auto-fix."

IF code contains placeholder comments
  → STOP. "Incomplete code. No '// Additional columns...', '// TODO: add remaining...', '// See X for full definition'. Complete or remove."

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

IF '/midtempo-framework/rules/testing.md "Compliance Gates"' not verified
  → STOP. "Verify all testing compliance gates before proceeding."


VALID: Output "§5.5 Step 2 Complete Output"
```

---

### 4.1 Criteria for VALID

```
- Unit test failures = 0 (log confirms 100% passing)
- Integration test failures = 0 OR deferred (services unavailable)
- Deferred integration tests listed with service-dependency reason
- Type errors = 0
- Test coverage ≥ 90%
- No file with < 80% coverage (indicates code outside test manifest)
- Format clean (if format_check exists)
```

If criteria fail → fix issues or escalate to human. Deliver-green CAN NEVER complete with red unit tests.

**Update test manifest status:**

```
COUNT total tests from test run output
COUNT passing tests from test run output
COUNT deferred tests (services unavailable) from test run output
OPEN `planning/[feature-name]-tests.md`
IF deferred > 0
  → SET Status to: Green ([total] tests, [passing] passing, [deferred] deferred)
ELSE
  → SET Status to: Green ([total] tests passing)
SAVE the file
```

## 5. Complete Script

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output after Exit Gate passes - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
- You MUST verify tests are green, coverage meets threshold, and type errors are zero before producing this output
</CRITICAL_REQUIREMENT>

---
                         GREEN STATE COMPLETE

---

Files created:
- `src/path/to/file.ts`
- `src/components/layer/Component/index.tsx`

Files modified:
- `src/path/to/existing.ts`

[N] tests passing. [D] deferred (services unavailable). Coverage: [X]% lines, [Y]% functions, [Z]% branches.
Deferred integration tests (if any):
- [test name]: [service dependency] — "deferred — services unavailable"
Escalation decisions (if any):
- [test name]: [SKIPPED / MODIFIED / DEFERRED] — human decision: "[reason]"

Compliance gates: [ALL PASSED / list any that required human override]

Commit

feat: [feature name]

[2 lines describing (1) primary capability, (2) key technical approach]

---
Review implementation and commit. Start new conversation with:

Step 3 - use midtempo-framework/deliver.md with planning/[feature-name]-plan.md. Run Step 3.

---

---

---
**END OF DOCUMENT:** Total sections: 5 | Purpose: Execute TDD Green State — make all failing tests pass with minimal production code whilst adhering to repo instructions and rules