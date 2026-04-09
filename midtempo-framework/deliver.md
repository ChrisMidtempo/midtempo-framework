# Delivery Orchestrator

## Table of Contents

- [Overview](#1-overview)
- [Iron Laws](#2-iron-laws)
- [Command Rules (MANDATORY)](#3-command-rules-mandatory)
- [Execution Plan](#4-execution-plan)
  - [Phase Sequence](#41-phase-sequence)
- [Phase 1: Red State](#5-phase-1-red-state)
  - [Entry Gate](#51-entry-gate)
  - [Sub-skill Execution](#52-sub-skill-execution)
  - [Exit Gate](#53-exit-gate)
- [Phase 2: Green State](#6-phase-2-green-state)
  - [Entry Gate](#61-entry-gate)
  - [Sub-skill Execution](#62-sub-skill-execution)
  - [Exit Gate](#63-exit-gate)
- [Phase 3: Refactor](#7-phase-3-refactor)
  - [Sub-skill Execution](#71-sub-skill-execution)
  - [Exit Gate](#72-exit-gate)
- [Phase 4: Documentation](#8-phase-4-documentation)
  - [Sub-skill Execution](#81-sub-skill-execution)
  - [Exit Gate](#82-exit-gate)
- [Recovery Protocol](#9-recovery-protocol)
- [Phase Summary](#10-phase-summary)
- [Pre-Output Self-Check](#11-pre-output-self-check)

---

## 1. Overview

This orchestrator coordinates the delivery process through a sequence of sub-skills. Each phase executes in order with human approval gates between phases.

**Inputs:** 
 - Delivery plan (`planning/[feature-name]-plan.md`)
 - Test manifest (`planning/[feature-name]-tests.md`)

**Context:** The delivery plan and test manifest describes WHAT to build. This orchestrator coordinates HOW to execute the plan by invoking specialised sub-skills.

---

## 2. Iron Laws

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST NOT write production code without a failing test first
- You MUST NOT abbreviate or leave any phase incomplete
- You MUST end every phase with its Phase Complete Script — no exceptions
- You MUST execute phases in order — no skipping ahead
- You MUST NOT modify commands (no pipes, redirections, or extra flags)

</CRITICAL_REQUIREMENT>

---

## 3. Command Rules (MANDATORY)

**Run commands EXACTLY as shown. No modifications.**

#### Testing
```bash
npm run test:python    # Run all Python tests
npm run test:python:unit    # Run Python unit tests only (fast, no external dependencies)
npm run test:python:integration    # Run Python integration tests only (slower, may use external resources)
npm run test:python:coverage    # Run Python unit tests with coverage report
```

#### Linting
```bash
npm run lint:python    # Run Python linter for code quality
npm run lint:python:fix    # Fix Python linting issues automatically
npm run fix:all    # Auto-fix formatting and linting issues
```

#### Type Checking
```bash
npm run typecheck:python    # Run Python type checker (mypy)
```

**Tests are automatically saved to the log file:**

```bash
# Check previous unit test results:
tail -5 /planning/last-test-ran.log
```

---

## 4. Execution Plan

> **Core principle:** Each phase delegates to a sub-skill. The orchestrator manages sequencing and common rules.
> **Phase Activation:** Human provides Phase # in prompt. If not specified, start at Phase 1.
> **Recovery:** After each sub-skill completes, human begins next Phase in a new conversation.

### 4.1 Phase Sequence

```
Phase 1: Red State         → Sub-skill: deliver-red.md
Phase 2: Green State       → Sub-skill: deliver-green.md
Phase 3: Refactor          → Sub-skill: refactor.md
Phase 4: Documentation     → Sub-skill: documentation.md
Complete: Feature ready for merge
```

**To Start a Phase:** Human will provide "Phase [N] - use /midtempo-framework/deliver.md with /planning/[feature-name]-plan.md. Run Phase [N]."

**Restart protocol:** After completing a phase, provide to human the prompt for the next step: "Phase [N+1] - use /midtempo-framework/deliver.md with /planning/[feature-name]-plan.md. Run Phase [N+1]"

---

## 5. Phase 1: Red State

**Goal:** All scenarios from the approved manifest exist as tests and are failing for the correct reasons.

### 5.1 Entry Gate

```
IF Human has not provided plan document in prompt
  → ASK: "Which planning document are we working on"
  → WAIT: for human response before proceeding

IF Human has not provided Phase # in prompt
  → ASK: "Which phase? Phase 1 (Red), Phase 2 (Green), Phase 3 (Refactor), Phase 4 (Documentation)"
  → WAIT: for human response before proceeding

IF not read ALL of `/planning/[feature-name]-plan.md`
  → STOP: READ ALL of `/planning/[feature-name]-plan.md` before proceeding.

IF not read ALL of `/planning/[feature-name]-tests.md`
  → STOP: READ ALL of `/planning/[feature-name]-tests.md` before proceeding.

VALID: Run sub-skill `/midtempo-framework/deliver-red.md`
```

### 5.2 Sub-skill Execution

**MANDATORY:** Run the sub-skill `/midtempo-framework/deliver-red.md` process exactly.

The sub-skill handles:
- Reading instruction documents
- Test creation checklist
- Running tests and verifying RED state
- Exit gate validation
- Phase Complete Script


### 5.3 Exit Gate

```
IF sub-skill `/midtempo-framework/deliver-red.md` not completed
  → STOP: "Phase 1 incomplete. Complete Red State before proceeding."

IF sub-skill did not display "Red State Complete Script"
  → GOTO: `/midtempo-framework/deliver-red.md` and display "Red State Complete Script"

```

---

## 6. Phase 2: Green State

**Goal:** Make all tests pass with minimal production code, whilst adhering to our rules/*.md and instructions/*.md


### 6.1 Entry Gate

````
**Check test status using the log file**

```bash
tail -5 /planning/last-test-ran.log
```


IF not read ALL of `/planning/[feature-name]-tests.md`
  → STOP: READ ALL of `/planning/[feature-name]-tests.md` before proceeding.

COUNT "number of tests" in `/planning/[feature-name]-tests.md`
COUNT "number of failing tests" from unit tests

IF "number of failing tests" < "number of tests" 
  → STOP: "Red Phase incomplete. All tests should be in red state first."
  → ASK: human how to proceed.

VALID: Run sub-skill `/midtempo-framework/deliver-green.md`
````

### 6.2 Sub-skill Execution

**MANDATORY:** Run the sub-skill `/midtempo-framework/deliver-green.md` process exactly.

The sub-skill handles:
- Reading instruction documents
- Implementation process
- Running tests and verifying GREEN state
- Lint and typecheck validation
- Coverage validation
- Exit gate validation
- Phase Complete Script

### 6.3 Exit Gate

````
**Check test status **

**Check test status using the log file**

```bash
tail -5 /planning/last-test-ran.log
```


IF ANY FAILING TESTS 
  → STOP: "Green State is incomplete. Complete Phase 2 before proceeding."

IF sub-skill did not display "Green Stage Complete Script"
  → GOTO: `/midtempo-framework/deliver-green.md` and display "Green Stage Complete Script"

````

---

## 7. Phase 3: Refactor

**Goal:** Improve code structure and quality while keeping all tests green.

### 7.1 Sub-skill Execution

**MANDATORY:** Run the sub-skill `/midtempo-framework/refactor.md` process exactly.

The sub-skill handles:
- Metrics discovery
- Refactoring opportunities identification
- Human approval for refactoring decisions
- Refactoring execution
- Exit gate validation
- Phase Complete Script (or Skipped Output)

### 7.2 Exit Gate

````
**Check test status using the log file**

```bash
tail -5 /planning/last-test-ran.log
```

npm run lint:python
npm run typecheck:python
IF ANY unit test errors
IF ANY linting errors or warnings
IF ANY type checking errors or warnings  → STOP: "Refactor is incomplete. Complete Refactor before proceeding."

IF sub-skill did not produce "Refactor Complete Script"
  → GOTO: `/midtempo-framework/refactor.md` and output "Refactor Complete Script"

````

---

## 8. Phase 4: Documentation

**Goal:** Document the work and mark feature complete.

### 8.1 Sub-skill Execution

**MANDATORY:** Run the sub-skill `/midtempo-framework/documentation.md` process exactly.

The sub-skill handles:
- Reading writing rules
- Instruction document updates
- Planning document updates
- Doc comments validation
- README updates
- Exit gate validation
- Phase Complete Script


### 8.2 Exit Gate

```
IF sub-skill `/midtempo-framework/documentation.md` not completed
  → STOP: "Phase 4 incomplete. Complete sub-skill before proceeding."

IF sub-skill did not display Documentation Complete Script
  → GOTO: `/midtempo-framework/documentation.md` and display "Documentation Complete Script"

```

---

## 9. Recovery Protocol

**When a phase fails:**

1. Orchestrator identifies failure point
2. Sub-skill guides human to fix issue
3. Sub-skill completes with success message
4. Human runs delivery again in a **new conversation** starting at current phase
5. Example: "Run Phase 2 - `/midtempo-framework/delivery.md` for `/planning/[featureName]-plan.md"

**Why new conversation:**
- Avoids context problems with compact/summarisation
- Framework provides full understanding at each conversation start
- Clear progress tracking

**Progress tracking:**
- Each phase output shows what passed
- Human knows exactly where to resume
- No ambiguity about state

---

## 10. Phase Summary

| Phase | Name          | Sub-skill              | Human        | Commit      |
| ----- | ------------- | ---------------------- | ------------ | ----------- |
| 1     | Red State     | deliver-red.md        | **Review**   | `test:`     |
| 2     | Green State   | deliver-green.md      | **Review**   | `feat:`     |
| 3     | Refactor      | refactor.md            | **Decision** | `refactor:` |
| 4     | Documentation | documentation.md       | **Sign-off** | `docs:`     |

**Human involvement at every phase exit is mandatory.** No phase completes without human confirmation.

**Invocation:** "Phase [N] - use /midtempo-framework/deliver.md with /planning/[feature-name]-plan.md. Run Phase [N]."

---

## 11. Pre-Output Self-Check

Before presenting phase completion, verify:

1. The sub-skill's Phase Complete Script was displayed
2. All exit gate criteria for this phase evaluated to true
3. No phase was skipped or executed out of order
4. The next phase prompt was provided to the human
5. Human approved the phase output before proceeding

IF any check fails → Fix before presenting phase completion. Do not present output with known violations.

---

---
**END OF DOCUMENT:** Total sections: 11 | Purpose: Delivery orchestrator with phase coordination