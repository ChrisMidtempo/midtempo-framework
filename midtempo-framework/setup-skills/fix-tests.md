# Fix Tests Skill

## Overview

This skill establishes a robust testing baseline. It fixes broken tests, separates unit from integration tests, and ensures test infrastructure works correctly.

**Goal:** Green test suite, unit/integration tests classified by dependency type, coverage reporting configured.

**Execution:** Test fixes follow `/midtempo-framework/rules/testing.md` gates. Each batch runs in a separate conversation.

**Progress file:** `planning/test-fix-progress.md` tracks state between conversations.

**Coverage improvement:** After completing this skill, run `/midtempo-framework/improve-coverage.md` to improve coverage.

---

## The Process

### Non-Negotiable Rules

<CRITICAL_REQUIREMENT type="MANDATORY">

**CORE PRINCIPLE: Fix test infrastructure. No production code changes.**

- You MUST make all tests pass
- You MUST separate unit tests from integration tests based on dependencies (not runtime)
- You MUST configure coverage reporting
- You MUST follow `/midtempo-framework/rules/testing.md` for all test changes
- You MUST update progress file after each batch
- You MUST start a new conversation for each batch
- You MUST NOT modify production code (route to bugs|refine|build skills)
- You MUST NOT disable tests to "fix" them
- You MUST NOT add tests that test mock behaviour
- You MUST NOT skip any step or offer "skip" options

**Production code issues:** Log in progress file under "Production Issues" section. Human routes these through bugs|refine|build skills.

**End state:** Green test suite, properly classified unit/integration tests, coverage reporting configured.

**Next step:** Run `/midtempo-framework/improve-coverage.md` for coverage improvement.

</CRITICAL_REQUIREMENT>

---

## Test Classification Criteria

Tests are classified by their **dependencies**, not their runtime.

| Classification | Criteria | Suite |
|----------------|----------|-------|
| Unit test | No external dependencies (network, DB, filesystem, real timers) | Unit |
| Integration test | Uses real network, database, filesystem, or unpredictable timing | Integration |
| Timing test | Tests timing logic with **mocked** timers | Unit |
| Timing test | Tests timing logic with **real** timers/delays | Integration |

**Principle:** Classification is deterministic from reading the code. Runtime is irrelevant.

---

## ENTRY GATE

```
CHECK if `planning/test-fix-progress.md` exists

IF progress file exists
  → READ ALL of `planning/test-fix-progress.md`
  → EXTRACT: phase, batch number, remaining issues
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

### 1.2 Assess Test Infrastructure

```
CHECK `/midtempo-framework/midtempo-framework.yml` for repo.language field
IDENTIFY the primary language(s) used in this repository
SEARCH for test configuration files appropriate for that language

READ configuration completely

CHECK test organisation:
  - Where are unit tests?
  - Where are integration tests?
  - Are they separated?
  - How are they run separately?

CHECK midtempo-framework.yml for test commands:
  - Unit test command exists?
  - Integration test command exists?
  - Coverage command exists?

CHECK test output verbosity:
  - Run the test command and observe output
  - Does it print each test name individually? (verbose — bad for large suites)
  - Does it print summary only with failure detail? (quiet — good)
  - Framework-specific quiet flags:
    - pytest: `-q --tb=short` (dots + summary + short tracebacks on failure)
    - jest: default (no `--verbose` flag) or `--silent` for console suppression
    - vitest: `--reporter=dot`
    - go test: default (no `-v` flag)
    - mocha: `--reporter dot` or `--reporter min`
  - Coverage commands: quiet test output, full coverage table
    - pytest: `-q` with `--cov-report=term-missing`

PRESENT infrastructure assessment:

**TEST INFRASTRUCTURE ASSESSMENT**

Framework: [framework name]
Config location: [path]

**Test organisation:**
- Unit tests: [location or "not separated"]
- Integration tests: [location or "not separated"]
- Separation: [yes/no]

**Commands in midtempo-framework.yml:**
- test: [exists/missing] - [command if exists]
- test:unit: [exists/missing]
- test:integration: [exists/missing]
- test:coverage: [exists/missing]

**Test output verbosity:**
- test command: [quiet/verbose] - [flags present or missing]
- coverage command: [quiet/verbose] - [flags present or missing]
- Recommendation: [flags to add, if any]

**Issues found:**
- [issue 1]
- [issue 2]

**Recommendations:**
- [recommendation 1]
- [recommendation 2]

WAIT for human to confirm infrastructure changes (if any).

CONTINUE to §1.3
```

### 1.3 Assess Coverage State

```
RUN: npm run test:python:coverage    # Coverage — metrics + pass/fail

CAPTURE coverage report:
  - Line coverage percentage
  - Function coverage percentage
  - Branch coverage percentage
  - Files with <90% coverage
  - Files with 0% coverage (no tests)

PRESENT coverage assessment:

**COVERAGE STATE ASSESSMENT**

**Current coverage:**
- Lines: [X]% (target: 90%)
- Functions: [X]% (target: 90%)
- Branches: [X]% (target: 70%)

**Gap to target:**
- Lines: [+/-X]%
- Functions: [+/-X]%
- Branches: [+/-X]%

Files with 0% coverage (no tests): [count]
Files with <90% coverage: [count]

Estimated batches: ~[X]

CONTINUE to §1.4
```

### 1.4 Check Source/Test File Matching

```
LIST all source files (excluding tests, configs, types):
  - src/**/*.ts (not *.test.ts, *.spec.ts)
  - src/**/*.py (not test_*.py, *_test.py)
  - Adapt pattern for project structure

LIST all test files:
  - **/*.test.ts, **/*.spec.ts
  - **/test_*.py, **/*_test.py
  - Adapt pattern for project structure

MATCH source files to test files:
  - src/utils/parser.ts → src/utils/parser.test.ts ✓
  - src/services/auth.ts → [no matching test] ✗

IDENTIFY:
  - Source files WITHOUT matching test files
  - Test files WITHOUT matching source files (orphaned tests)
  - Test files testing multiple source files (review needed)

PRESENT matching assessment:

**SOURCE/TEST FILE MATCHING**

Source files: [count]
Test files: [count]
Matched: [count] ([X]%)

**Source files without tests:**
- [file 1]
- [file 2]
...

**Orphaned test files (no matching source):**
- [file 1] - [investigate/delete?]
...

Should I create test stubs for uncovered source files?

WAIT for human decision on:
  - Creating test stubs
  - Handling orphaned tests
  - Priority order for coverage work
```

### 1.5 Create Progress File

```
CREATE `planning/test-fix-progress.md` with:

# Test Fix Progress

## Status
- **Current phase:** [infrastructure | coverage | cleanup]
- **Current batch:** 1
- **Started:** [DD/MM/YYYY]

## Infrastructure
- **Framework:** [name]
- **Unit/integration separated:** [yes/no]
- **Commands configured:** [list]
- **Tests passing:** [yes/no]

## Summary
- **Failing tests:** [count]
- **Tests needing classification:** [count]
- **Orphaned tests:** [count]

## Phases

### Phase 1: Infrastructure [pending/in-progress/complete]
- [ ] All tests passing
- [ ] Unit/integration test separation
- [ ] Test commands in midtempo-framework.yml
- [ ] Coverage reporting configured

### Phase 2: Cleanup [pending/in-progress/complete]
- [ ] Remove orphaned tests
- [ ] Fix flaky tests
- [ ] Final verification

### Next Step (after this skill)
Run `/midtempo-framework/improve-coverage.md` for coverage improvement.

## Tests Requiring Classification (move to integration)
Tests with external dependencies that should be in integration suite:
- [ ] `[file:test]` - [dependency: network/database/filesystem/real-timers]
- [ ] `[file:test]` - [dependency: ...]
...

## Production Issues (route to bugs|build|refine|refactor skills)
[None yet]

## Completed Batches
[None yet]

---

PROCEED to §3. Execute Batch.
```

---

## 2. Continuation Entry Gate

**Returning to continue from previous batch.**

```
READ ALL of `planning/test-fix-progress.md`

READ ALL of `/midtempo-framework/rules/testing.md`

OUTPUT declaration verbatim:
"I have read testing.md - all tests must pass 6 gates, no mock-behaviour testing, no test-only production methods"

EXTRACT:
  - Current phase
  - Current batch number
  - Remaining work items
  - Coverage metrics

VERIFY current state:
  RUN: npm run test:python:coverage    # Coverage — metrics + pass/fail
  COMPARE with progress file metrics

IF metrics differ from progress file
  → UPDATE progress file with current state
  → INFORM human of change

PRESENT continuation summary:

**CONTINUING TEST FIX**

Phase: [phase name]
Batch: [N]

**Status:**
- Tests passing: [yes/no]
- Remaining items: [count]

Ready to proceed with batch [N]?

WAIT for human confirmation.

VALID: Proceed to §3. Execute Batch.
```

---

## 3. Execute Batch

### 3.1 Select Batch Scope

```
BASED ON current phase:

IF Phase 1 (Infrastructure):
  SELECT infrastructure tasks (max 3 per batch):
    - Fix failing tests
    - Separate unit/integration tests
    - Configure test commands
    - Set up coverage reporting

IF Phase 2 (Cleanup):
  SELECT cleanup tasks (max 5 per batch):
    - Orphaned test removal
    - Flaky test fixes

PRESENT batch to human:

**BATCH [N] - PHASE: [phase name]**

Scope: [count] items

**Items:**
1. [item description]
2. [item description]
...

Proceed with this batch?

WAIT for approval.
```

### 3.2 Execute Based on Phase

#### Phase 1: Infrastructure

```
FOR each infrastructure task:

  IF separating unit/integration tests:
    - Identify tests with external dependencies (network, database, filesystem)
    - Create integration test directory if needed
    - Move integration tests to separate location
    - Update test configuration
    - Add separate run commands

  IF configuring test commands:
    - Add test:unit command (runs fast tests only)
    - Add test:integration command (runs slow tests)
    - Add test:coverage command
    - Update midtempo-framework.yml

  IF configuring test output verbosity:
    - Add quiet flags to ALL test commands (test, test_unit, test_integration)
    - Quiet output: summary line + failure detail only
    - Verbose per-test names waste context in large suites
    - Coverage command: quiet test output, full coverage table
    - Single-file runs (e.g. `test <file>`) remain readable with quiet flags
      because the test count per file is small
    - Verify: run full suite, confirm output shows pass/fail counts
      without printing each test name

  VERIFY after each change:
    - Unit tests run separately
    - Integration tests run separately
    - Coverage reports generate
    - Full suite output shows summary + failures only (no per-test names)
```

#### Phase 2: Cleanup

```
FOR each cleanup item:

  IF orphaned test:
    - Verify no matching source file
    - Check if tests utility functions (keep in test-utils)
    - Remove if truly orphaned

  IF flaky test:
    - Identify flakiness cause (timing, order dependency, shared state)
    - Fix root cause
    - Verify passes 5+ times consecutively

  VERIFY after each change:
    - All tests pass
    - No regressions
```

### 3.3 Verify Batch

```
AFTER all batch work complete:

RUN: npm run test:python    # Verbose — no summary command configured

VERIFY:
  - All tests pass
  - No new failures introduced
  - No new lint errors

IF tests fail:
  → FIX immediately
  → Tests MUST pass before proceeding
```

---

## 4. Batch Complete

### 4.1 Update Progress File

```
UPDATE `planning/test-fix-progress.md`:

1. MARK completed items with [x]
2. ADD to Completed Batches:

### Batch [N] - [DD/MM/YYYY]
- Phase: [phase name]
- Items completed: [count]
- Tests: passing
```

### 4.2 Check Phase/Completion Status

```
CHECK phase completion:

IF current phase complete AND more phases remain:
  → UPDATE phase status to "complete"
  → SET next phase to "in-progress"
  → INFORM human of phase transition

RUN: npm run test:python

CHECK all targets:
  - All tests passing?
  - Unit/integration tests properly classified?
  - No orphaned tests?
  - Coverage reporting configured?

IF ALL targets met:
  → GOTO §5. All Complete Output

IF targets NOT met:
  → GOTO §4.3 Batch Complete Output
```

### 4.3 Batch Complete Output

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output for next conversation - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
</CRITICAL_REQUIREMENT>

**BATCH [N] COMPLETE**

Phase: [phase name]
Items completed: [count]

**Files modified:**
- [file 1]
- [file 2]

Tests: passing

Progress file updated: planning/test-fix-progress.md

---

**PRODUCTION ISSUES FOUND (route separately)**

[None OR list issues to route through bugs|refactor|refine|build skills]

---

**COMMIT**

test: [phase] batch [N]

- [Primary change description]

---

**NEXT BATCH**

Start a NEW conversation with:

> Continue fix-tests batch [N+1] using /midtempo-framework/setup-skills/fix-tests.md

---

## 5. All Complete Output

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output when all targets achieved - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
</CRITICAL_REQUIREMENT>

**TEST INFRASTRUCTURE COMPLETE**

All targets achieved ✓

**Test status:**
- All tests passing ✓
- Unit/integration tests classified ✓
- Coverage reporting configured ✓

**Test classification:**
- Unit tests: [count] (no external dependencies)
- Integration tests: [count] (network/DB/filesystem/real-timers)

Batches completed: [N]

---

**PRODUCTION ISSUES TO ADDRESS**

[List any production issues found - route through proper skills]

---

**CLEANUP**

Archive progress file:
`mv planning/test-fix-progress.md planning/archive/`

---

**INFRASTRUCTURE ESTABLISHED ✓**

**Next step:** Run `/midtempo-framework/improve-coverage.md` to improve test coverage.

**Future enforcement:**
- Unit tests run on every commit
- Integration tests run on PR/merge

COMMIT MESSAGE (copy/paste):
─────────────────────────────────────────────────────────────────

test: establish test infrastructure baseline

- All tests passing
- Unit and integration tests separated by dependency type
- Coverage reporting configured

Batches completed: [N]

─────────────────────────────────────────────────────────────────
```

---

## Quick Reference

### Invocation

**Fresh start:**
```
Fix tests using /midtempo-framework/setup-skills/fix-tests.md
```

**Continue batch:**
```
Continue fix-tests batch [N] using /midtempo-framework/setup-skills/fix-tests.md
```

### Commands

```bash
npm run test:python              # Run all tests
npm run test:python:unit         # Run unit tests only
npm run test:python:integration  # Run integration tests
npm run test:python:coverage     # Run with coverage report
```

### Progress File Location

`planning/test-fix-progress.md`

### Phases

1. **Infrastructure:** Fix failing tests, separate unit/integration by dependency type, configure commands
2. **Cleanup:** Remove orphaned tests, fix flaky tests

**Next step:** Run `/midtempo-framework/improve-coverage.md` for coverage improvement

### Testing Compliance Gates

From `/midtempo-framework/rules/testing.md`:
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
3. Human routes through bugs|refine|build|refactor skill
4. Continue with test work only

---