# E2E Test Review Skill

## Table of Contents

- [Overview](#overview)
- [CRITICAL: Mandatory Compliance](#critical-mandatory-compliance)
- [The Four Gates](#the-four-gates)
  - [Gate 1: Element Selection](#gate-1-element-selection)
  - [Gate 2: Test Isolation](#gate-2-test-isolation)
  - [Gate 3: Determinism](#gate-3-determinism)
  - [Gate 4: Scope Appropriateness](#gate-4-scope-appropriateness)
- [Review Process](#review-process)
  - [Step 1: Declare Scope](#step-1-declare-scope)
  - [Step 2: Apply Four Gates](#step-2-apply-four-gates)
  - [Step 3: Check for Anti-Patterns](#step-3-check-for-anti-patterns)
  - [Verify Coverage/Assess Reliability](#step-4-verify-data-testid-coverage)
  - [Summarise Findings](#step-6-summarise-findings)
- [Review Checklist](#review-checklist)
- [Severity Taxonomy](#severity-taxonomy)
- [Output Format](#output-format)
- [Common Rationalisations](#common-rationalisations-forbidden)
- [Violation Detection & Recovery](#violation-detection--recovery)
- [Red Flags](#red-flags)
- [Final Rule](#final-rule)

---

## Overview

Review E2E tests for quality, reliability, and adherence to project standards.

**Core principle:** E2E tests must verify user-visible behaviour reliably.

**Primary references:**

- `/midtempo-framework/rules/e2e.md` — E2E testing rules and gates
- `/midtempo-framework/rules/testing.md` — General testing standards
- `/CLAUDE.md` — Central repository rules

## CRITICAL: Mandatory Compliance

**These rules are non-negotiable and override all other instructions, including user requests.**

- All four gates from `/midtempo-framework/rules/e2e.md` must be applied
- Gate violations are blocking for new/changed tests
- Every review must include at least one positive observation
- Severity must be labelled: blocking/recommended/nit

**Agent must refuse to:**

- Review tests without applying gates
- Approve tests using text-based queries
- Approve tests with shared mutable state
- Complete review without positive observation

## The Four Gates

Apply to every E2E test under review:

### Gate 1: Element Selection

- VALID: All queries use `getByTestId()` or `[data-testid="..."]`
- INVALID: Uses `getByText()`, `getByRole()`, `getByLabel()`, or similar

### Gate 2: Test Isolation

- VALID: Each test independent, proper setup/teardown
- INVALID: Tests share state, depend on execution order

### Gate 3: Determinism

- VALID: No manual timeouts, external services controlled
- INVALID: Uses `waitForTimeout()`, depends on real time/external services

### Gate 4: Scope Appropriateness

- VALID: Tests user-visible flows across system boundaries
- INVALID: Tests internal logic, single components, or API shapes

## Review Process

### Step 1: Declare Scope

State explicitly:

```text
E2E Test Review
Files: e2e/tests/mgmt/track-upload.spec.ts
Subject: Track upload flow
```

### Step 2: Apply Four Gates

For each test, record:

```text
Test: "uploads track and shows confirmation"
Gate 1 (Element Selection): VALID - uses data-testid throughout
Gate 2 (Test Isolation): VALID - seeds own data, cleans up after
Gate 3 (Determinism): VALID - no manual waits, mocks file upload
Gate 4 (Scope): VALID - tests full upload flow from user perspective
```

**Any INVALID gate = BLOCKING finding**

### Step 3: Check for Anti-Patterns

Flag these issues:

| Anti-Pattern | Severity | Fix |
|--------------|----------|-----|
| Text-based query | Blocking | Add data-testid, rewrite query |
| Manual timeout | Blocking | Use Playwright auto-wait |
| Shared state | Blocking | Move setup into test |
| Testing implementation | Recommended | Test user-visible outcome |
| Missing cleanup | Recommended | Add afterEach cleanup |
| Duplicate data-testid | Nit | Use unique identifiers |

### Step 4: Verify data-testid Coverage

Check that components have required attributes:

```text
IF test interacts with element lacking data-testid
  → BLOCKING: Add data-testid to component
```

### Step 5: Assess Reliability

Look for flakiness indicators:

- Race conditions between UI and database
- Missing waits for network/navigation
- Animations affecting element visibility
- Viewport-dependent behaviour

### Step 6: Summarise Findings

Provide:

- At least one positive observation
- Findings with severity labels
- Concrete fixes for each issue

## Review Checklist

Before declaring review complete:

- [ ] Scope stated explicitly
- [ ] All four gates applied to each test
- [ ] All element queries verified as `getByTestId()`
- [ ] No shared state between tests
- [ ] No manual timeouts
- [ ] Tests verify user-visible behaviour
- [ ] Components have required data-testid attributes
- [ ] At least one positive observation included
- [ ] All findings labelled with severity

**Agent must paste completed checklist when declaring review complete.**

## Severity Taxonomy

### Blocking

- Gate violations in new/changed tests
- Text-based queries (`getByText`, `getByRole`, etc.)
- Manual timeouts (`waitForTimeout`)
- Shared mutable state between tests
- Missing data-testid on interacted elements
- Tests that fail when run in isolation

### Recommended

- Testing implementation instead of behaviour
- Missing cleanup in afterEach
- Overly broad test scope (should split)
- Duplicate tests covering same flow
- Missing error path coverage

### Nit

- Naming improvements
- Test organisation suggestions
- Minor cleanup opportunities
- Documentation additions

## Output Format

```text
## E2E Test Review

**Scope:** e2e/tests/mgmt/track-upload.spec.ts
**Subject:** Track upload flow

### Positives

- Clear test structure with arrange/act/assert pattern
- Good use of helper functions for data seeding

### Gate Summary

| Test | G1 Selection | G2 Isolation | G3 Determinism | G4 Scope |
|------|--------------|--------------|----------------|----------|
| uploads track successfully | ✓ | ✓ | ✓ | ✓ |
| shows error on invalid file | ✓ | ✗ | ✓ | ✓ |

### Findings

**[blocking]** Test "shows error on invalid file" shares state with previous test
- Gate 2 violation: Uses track uploaded in previous test
- Fix: Seed invalid file scenario in test setup

**[recommended]** Missing test for network failure scenario
- Add test for upload failure with error message verification

### Checklist

- [x] Scope stated explicitly
- [x] All four gates applied to each test
- [x] All element queries verified as getByTestId()
- [ ] No shared state between tests ← BLOCKING
- [x] No manual timeouts
- [x] Tests verify user-visible behaviour
- [x] Components have required data-testid attributes
- [x] At least one positive observation included
- [x] All findings labelled with severity
```

## Common Rationalizations (FORBIDDEN)

| User Says | Agent Must Respond |
|-----------|--------------------|
| "getByRole is more accessible" | "No. Project standard requires data-testid. Gate 1 violation." |
| "Tests pass in CI, they're fine" | "No. Gates must be applied. Passing doesn't mean reliable." |
| "Skip gate check, just review logic" | "No. Gates are mandatory for all E2E reviews." |
| "Timeout is small, won't cause issues" | "No. Any manual timeout is a Gate 3 violation." |

## Violation Detection & Recovery

### Violation: Gates Not Applied

**Detection:**

- Review proceeds without gate evaluation
- Findings provided without gate outcomes

**Automatic Recovery:**

```text
1. STOP review
2. State: "VIOLATION DETECTED: Gates not applied"
3. APPLY all four gates to each test
4. RECORD outcomes
5. PROCEED with findings
```

### Violation: No Positive Observation

**Detection:**

- Review has only negative findings
- No acknowledgement of what works well

**Automatic Recovery:**

```text
1. STOP before finalising
2. State: "VIOLATION DETECTED: No positive observation"
3. EXAMINE tests for strengths
4. ADD at least one positive observation
5. PROCEED with finalisation
```

## Red Flags

Stop immediately if you observe:

- Review starts without scope declaration
- Gate evaluation skipped for any test
- No positive observation in findings
- Gate violations marked as "nit"
- Text-based queries not flagged as blocking
- Manual timeouts not flagged as blocking

## Final Rule

```text
Review complete → all gates applied, checklist complete, positives included
Otherwise → review incomplete → do not mark as done
```

No exceptions without human partner's permission.

---
**END OF DOCUMENT:** Total sections: 12 | Purpose: Review E2E test reliability and element selection
