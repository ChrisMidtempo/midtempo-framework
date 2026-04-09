# Writing Test Manifests

## Overview

The test manifest is THE CORE document that governs delivery. Everything else — decisions, design, planning — exists to gather the information needed for this document.

**The test manifest defines what gets built.** The plan provides context; the test manifest provides the contract. Delivery steps verify against the test manifest, not the plan.

**Outputs:**

- `planning/[feature-name]-tests.md` — The authoritative test manifest

**Template:** `/midtempo-framework/templates/test.md`

**Input:** Plan document (`planning/[feature-name]-plan.md`)

**Invocation:** "Write test manifest" or "Create test manifest for [feature]"

---

## Table of Contents

- [Overview](#overview)
- [Non-Negotiable Rules](#non-negotiable-rules)
- [Entry Gate](#entry-gate)
- [Step 1: Context Extraction](#step-1-context-extraction)
  - [Agent Actions (Silent)](#11-agent-actions-silent)
  - [Present Behaviour Inventory](#12-present-behaviour-inventory)
  - [Exit Gate — Context Extraction](#13-exit-gate--context-extraction)
- [Step 2: Test Scenario Creation](#step-2-test-scenario-creation)
  - [Process](#21-process)
  - [Scenario Structure](#22-scenario-structure)
  - [Complexity Ratings](#221-complexity-ratings)
  - [Coverage Requirements](#23-coverage-requirements)
  - [Present Draft Manifest](#24-present-draft-manifest)
  - [Exit Gate — Test Scenario Creation](#25-exit-gate--test-scenario-creation)
- [Step 3: Validation](#step-3-validation)
  - [Traceability Check](#31-traceability-check)
  - [Duplication Check](#32-duplication-check)
  - [Rules Alignment Check](#33-rules-alignment-check)
  - [Exit Gate — Validation](#34-exit-gate--validation)
- [Integration Test Scenarios](#section-1-integration-test-scenarios-service-dependent)
- [Error/Exception Scenarios](#section-2-errorexception-scenarios)
- [Security Test Scenarios](#section-3-security-test-scenarios)
- [Notes for Implementation](#section-4-notes-for-implementation)
- [Validation](#section-5-validation)
- [Step Complete Output](#step-4-step-complete-output)
- [Common Test Gaps to Check](#common-test-gaps-to-check)
- [Violation Recovery](#violation-recovery)
- [What NOT to Do](#what-not-to-do)

---

## Non-Negotiable Rules

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST have a plan document at `planning/[feature-name]-plan.md` before creating a test manifest
- You MUST read all required rules and instructions before proceeding
- You MUST create bidirectional traceability between plan behaviours and test scenarios
- You MUST detect and flag semantic duplicates for human decision
- You MUST identify omissions from the plan document
- You MUST verify alignment with testing rules
- You MUST propose fixes when issues found and re-present for validation
- You MUST obtain human approval before the manifest is complete
- You MUST use UK English spelling throughout

</CRITICAL_REQUIREMENT>

---

## Entry Gate

```
IF plan document does not exist at planning/[feature-name]-plan.md
  → INVALID: STOP - Run write-plan skill first

VERIFY-COMPLETE-READ for EVERY file below:
  CHECK the last line says "END OF DOCUMENT"
  IF CHECK fails → Re-read from offset until true end

READ ALL of `/midtempo-framework/rules/testing.md` → before proceeding
READ ALL of `/midtempo-framework/rules/writing.md` → before proceeding
READ ALL of `/midtempo-framework/instructions/architecture.md` → before proceeding
READ ALL of `/midtempo-framework/instructions/error-handling.md` → before proceeding
READ ALL of `/midtempo-framework/instructions/db.md` → before proceeding


READ ALL of `/midtempo-framework/templates/test.md` → for test manifest document structure

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


Present to human before proceeding:
  "Security domain files read: [list files read above]
   Security domain files skipped: [list domains not applicable]"

VALID: Continue to Step 1
```

---

## Step 1: Context Extraction

**Goal:** Extract all testable behaviours from the plan document.

### 1.1 Agent Actions (Silent)

```
READ plan document:
  - Extract objective (what problem this solves)
  - Extract all in-scope behaviours from Section 2
  - Extract module-capability table from Section 3 (Test Strategy: Module Distillation)
  - Extract Concerns column from Section 3 module-capability table (risks each module must address)
  - Extract implementation approach from Section 4 (architecture, data flow, integration points)
  - Extract test infrastructure from Section 3 "Test Infrastructure" (factories, fixtures, helpers, mocks)
  - Note implementation guidance items (setup requirements, test utilities, known challenges)
  - Note out-of-scope items (must NOT have tests)
  - Identify modules/components mentioned

BUILD behaviour inventory:
  - Assign unique ID to each in-scope behaviour (B1, B2, B3...)
  - Use §3 module-capability table for module-to-behaviour mapping
  - Use §4 architecture for implementation context and cross-module dependencies
  - Flag behaviours that span multiple modules
```

### 1.2 Present Behaviour Inventory

**Output to human:**

```
Behaviour Inventory (extracted from plan):

| ID | Behaviour | Module | Plan Section |
|----|-----------|--------|--------------|
| B1 | [behaviour description] | [module path] | §2.1 |
| B2 | [behaviour description] | [module path] | §2.2 |
| ... | ... | ... | ... |

Total: [N] behaviours requiring test coverage

Test Infrastructure (from plan §3):

[Insert test infrastructure summary extracted from plan, or "No relevant test utilities found" if plan §3 states none]

Out of scope (must NOT have tests):
- [out of scope item 1]
- [out of scope item 2]

Does this capture all testable behaviours and existing test infrastructure?
```

WAIT for human validation before proceeding

IF human approves
  → VALID: Write behaviour inventory to `planning/[feature-name]-tests.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

**After validation approved, write to file:**

Create `planning/[feature-name]-tests.md` using `/midtempo-framework/templates/test.md` as the document structure:

1. Copy the template header: `# [Feature Name] Test Specification`, planning doc reference, status
2. Copy `## Pre-Approval Checklist` from the template verbatim (including Progress Gate)
3. For `## Coverage Target`, insert the approved behaviour inventory table
4. Add the `## Test Scenarios` heading with `Progress: Not Started`

Stop after the Test Scenarios heading. Module subsections are added in Step 2.

### 1.3 Exit Gate — Context Extraction

```
IF behaviour inventory not validated by human
  → STOP. Wait for validation.

IF any in-scope behaviour missing from inventory
  → STOP. Add missing behaviours.

VALID: Continue to Step 2
```

---

## Step 2: Test Scenario Creation

**Goal:** Create test scenarios with explicit plan references for every behaviour.

### 2.1 Process

For each behaviour in the inventory:

1. **Identify test file** — Where tests for this module belong
2. **Create scenarios** — Success path, error conditions, edge cases
3. **Link to plan** — Each scenario references behaviour ID
4. **Classify dependencies** — Set `**Dependencies:**` per scenario: `none` (no external dependencies), `database`, `network`, `filesystem`, or `external API`. Classify by what the test needs to run, not by runtime speed
5. **Apply testing compliance gates** — Verify against `/midtempo-framework/rules/testing.md` "Compliance Gates" (CG-1 through CG-8)

### 2.2 Scenario Structure

Each test scenario MUST include:

```markdown
#### Test [M.N]: [Descriptive name in plain English]

**Plan Reference:** B[X] — [Behaviour description from inventory]

**Concern:** [Risk from plan §3 Concerns column this test addresses, or "—" if pure happy-path]

**Dependencies:** [none | database | network | filesystem | external API] — classify by dependency, not runtime

**Complexity:** [Low | Medium | High] — [one-line justification]

**Description:** [What behaviour is being tested]

**GIVEN:**
- [Precondition — reference discovered factory/fixture/helper by full path if applicable]
- [Mock/stub configuration]

**WHEN:**
- [Parameter or action]

**THEN:**
- [Expected return value or state change]
- [Side effect that should occur]
```

### 2.2.1 Complexity Ratings

Assign one rating per scenario:

| Rating | Criteria |
|--------|----------|
| Low | Single unit, straightforward assertion, minimal setup |
| Medium | Multiple dependencies, mocking required, or multi-step setup |
| High | Integration-level, complex state, async flows, or multiple interacting systems |

The human reviews and amends ratings before approval. Include a one-line justification with each rating.

### 2.3 Coverage Requirements

For each behaviour, ensure:

- [ ] At least one success path scenario
- [ ] Error conditions tested (if behaviour can fail)
- [ ] Boundary conditions tested (null, empty, max, min)
- [ ] No scenarios for out-of-scope behaviours
- [ ] Security scenarios included (when work touches security domains):
  - Secret handling tested (when work uses credentials/tokens)
  - Auth boundaries tested (when work involves authentication)
  - Input validation tested (when work accepts user input)
### 2.4 Present Draft Manifest

**Output to human:**

Present ONE module's test scenarios at a time. Do NOT draft or present scenarios for subsequent modules until the current module is approved and appended to the file. Batching multiple modules into a single approval is a violation.

```
Module: [module path]
Test file: [test file path]

[Test scenarios for this module]

Plan coverage for this module:

| Scenario | Behaviour | Dependencies | Complexity | Description |
|----------|-----------|--------------|------------|-------------|
| T1.1     | B1        | none         | Low        | [brief description] |
| T1.2     | B1        | database     | High       | [brief description] |
| T1.3     | B3        | none         | Medium     | [brief description] |

Review complexity ratings (see §2.2.1 for criteria). Amend if needed.
Does this coverage look correct for [module]?
```

WAIT for human validation before proceeding

IF human approves
  → VALID: Append approved scenarios to `planning/[feature-name]-tests.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

**After validation approved, append to file:**

Append to `planning/[feature-name]-tests.md` as a subsection under `## Test Scenarios`:

### Module: `[module path]`

**Test file:** `[test file path]`

[Insert all approved test scenarios for this module]

**Repeat for each module before proceeding to exit gate.**

### 2.5 Exit Gate — Test Scenario Creation

```
IF any module's scenarios not validated
  → STOP. Wait for validation.

IF any behaviour has zero test scenarios
  → STOP. Add missing scenarios.

VALID: Continue to Step 3
```

---

## Step 3: Validation

**Goal:** Verify traceability, detect duplicates, check rules alignment. Fix issues interactively.

### 3.1 Traceability Check

Build coverage matrix:

```
Coverage Matrix:

| Behaviour | Scenarios  | Complexity       | Status    |
|-----------|------------|------------------|-----------|
| B1        | T1.1, T1.2 | 1 Low, 1 High    | ✓ Covered |
| B2        | T2.1       | 1 Medium         | ✓ Covered |
| B3        | —          | —                | ✗ MISSING |

Complexity summary: [N] Low, [N] Medium, [N] High

Orphan scenarios (no plan reference):
- T4.1 — No matching behaviour in plan

Concern Coverage:

| Concern (from plan §3) | Module | Scenarios | Status    |
|------------------------|--------|-----------|-----------|
| [concern text]         | [path] | T1.2, T2.3 | ✓ Covered |
| [concern text]         | [path] | —          | ✗ MISSING |

Concerns with no test coverage must be addressed before proceeding.
```

**Output to human:**

Present the coverage matrix regardless of outcome.

**If issues found:**

1. List missing coverage and orphan scenarios
2. Propose fixes (add scenarios for uncovered behaviours, remove or reassign orphans)
3. Present proposed fixes for human approval
4. Apply approved fixes
5. Re-present coverage matrix
6. Loop until clean

**If no issues found:**

State: "Coverage matrix clean — all behaviours covered, no orphans."

### 3.2 Duplication Check

Detect semantic overlaps:

- Tests covering the same behaviour with different wording
- Tests with identical Setup + Input + Expected Output
- Tests in different modules testing the same code path

```
Potential duplicates detected:

1. T1.2 and T3.1 — Both test [behaviour] with [same setup]
   Recommendation: [merge / keep both with justification / remove one]

2. T2.3 and T2.4 — Identical expected output for different inputs
   Recommendation: [consolidate into parameterised test / keep separate]
```

**Output to human:**

Present duplication check results regardless of outcome.

**If duplicates found:**

Present each pair to human for decision. Do not auto-resolve duplicates.

**If no duplicates found:**

State: "No semantic duplicates detected."

### 3.3 Rules Alignment Check

Verify against `/midtempo-framework/rules/testing.md`:

- [ ] All assertions test real behaviour, not mock existence
- [ ] No placeholder assertions (expect(true).toBe(false))
- [ ] No test-only methods required in production code
- [ ] Each test is isolated and order-independent
- [ ] Coverage scope complete (success, error, boundary)
- [ ] No hard-coded collection sizes or full value enumeration — assert entry presence and format
- [ ] All element queries will use data-testid attributes
- [ ] Security compliance gates verified (CG-S1 – CG-S5):
  - No hardcoded secrets in test scenarios
  - No sensitive data in test assertions
  - Auth boundaries properly tested
  - Input validation scenarios included

IF no violations found:
  → State: "Rules alignment clean — no violations detected."
  → Continue to §3.4 Exit Gate

IF violations found:
  1. List each violation with scenario reference
  2. Propose correction
  3. Present proposed corrections for human approval:

WAIT for human validation before proceeding

Re-present corrected scenarios for review.
IF human approves
  → VALID: Apply approved fixes and continue to §3.4 Exit Gate
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

### 3.4 Exit Gate — Validation

```
IF coverage matrix shows missing behaviours
  → STOP. Fix coverage gaps.

IF orphan scenarios exist without justification
  → STOP. Resolve orphans.

IF duplicates flagged but not resolved by human
  → STOP. Wait for human decision.

IF rules alignment check has failures
  → STOP. Fix violations.

VALID: Continue to write validation section
```

**After exit gate passes, draft and present Section 1 below. Do not list or preview upcoming sections.**

Each section follows: draft content → present to human → approve → append to `planning/[feature-name]-tests.md` → then draft the next section. Each appended section is a recovery checkpoint. Never combine multiple sections into a single approval.

Sections 1–3 reorganise the approved Step 2 scenarios into cross-cutting views (by dependency, error handling, and security). They reference existing scenarios — not create new ones. The human reviews these sections to confirm the cross-cutting groupings are complete and correctly categorised.

**Section 1: Integration Test Scenarios (Service-Dependent)**

Collect scenarios from Step 2 where `**Dependencies:**` is not `none`. Group by dependency type (database, network, filesystem, external API). Reference each scenario by ID (e.g. T1.2, T3.1). If no scenarios have external dependencies, state "No integration scenarios — all tests classify as `Dependencies: none`".

WAIT for human validation before proceeding

Present drafted Integration Test Scenarios section.
IF human approves
  → VALID: Append `## Integration Test Scenarios (Service-Dependent)` to `planning/[feature-name]-tests.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

**Section 2: Error/Exception Scenarios**

Collect error and exception scenarios from Step 2. Reference each by scenario ID. If error scenarios are already fully covered in module test sections, state which scenarios cover error paths rather than duplicating content.

WAIT for human validation before proceeding

Present drafted Error/Exception Scenarios section.
IF human approves
  → VALID: Append `## Error/Exception Scenarios` to `planning/[feature-name]-tests.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

**Section 3: Security Test Scenarios**

Collect security-specific test scenarios from Step 2 when work touches security domains. Reference each by scenario ID:
- Secret handling tests (no hardcoded credentials, secure storage verification)
- Auth boundary tests (login/logout, session expiry, permission checks)
- Input validation tests (SQL injection, XSS, command injection prevention)
- Data protection tests (encryption at rest/transit, PII handling)
- Public-facing hardening tests (security headers, CORS, rate limiting)

WAIT for human validation before proceeding

Present drafted Security Test Scenarios section.
IF human approves
  → VALID: Append `## Security Test Scenarios` to `planning/[feature-name]-tests.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

**Section 4: Notes for Implementation**

Draft implementation guidance: special setup requirements, shared test utilities, mock data sources, known challenges.

WAIT for human validation before proceeding

Present drafted Notes for Implementation section.
IF human approves
  → VALID: Append `## Notes for Implementation` to `planning/[feature-name]-tests.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

**Section 5: Validation**

Draft the Validation section with three subsections:

### Coverage Matrix

[Insert the final coverage matrix from section 3.1]

### Duplicate Resolution

[Insert duplicate resolution outcomes from section 3.2]

### Rules Alignment

[Insert rules alignment check results from section 3.3]

WAIT for human validation before proceeding

Present drafted Validation section.
IF human approves
  → VALID: Append `## Validation` to `planning/[feature-name]-tests.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

---

Before presenting the Step Complete Output, verify:
1. No section contains placeholder text ("[TODO]", "[TBD]", "...")

IF any check fails → Fix before presenting. Do not present output with known violations.

---

## Step 4: Step Complete Output

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output after exit gates pass - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
- You MUST verify coverage matrix has zero MISSING entries and document contains no placeholders before producing this output
</CRITICAL_REQUIREMENT>

```
═══════════════════════════════════════════════════════════════════════════════
                    TEST MANIFEST COMPLETE: [FEATURE-NAME]
═══════════════════════════════════════════════════════════════════════════════

Document created:
- `planning/[feature-name]-tests.md`

Coverage:
- [N] behaviours from plan document
- [M] test scenarios across [X] modules

Complexity:
- Low: [N] scenarios
- Medium: [N] scenarios
- High: [N] scenarios

Traceability:
- All behaviours mapped to scenarios ✓
- No orphan scenarios ✓
- Coverage matrix included in document ✓

Validation:
- Duplicates: [none / N resolved]
- Rules alignment: passed ✓


───────────────────────────────────────────────────────────────────────────────
Review test manifest. Start new conversation with:

Phase 1 - use /midtempo-framework/deliver.md with /planning/[feature-name]-plan.md. Run Phase 1.
───────────────────────────────────────────────────────────────────────────────
```

---

## Common Test Gaps to Check

Before requesting approval, verify these patterns:

- **Multiple required fields**: If schema/type has required=[A, B, C], do you have tests for missing A, missing B, missing C?
- **Symmetric operations**: If code validates both directions (to/from, encode/decode, serialize/deserialize), are both tested?
- **Collection operations**: If code handles empty/single/multiple items, are all three cases tested?
- **Error boundaries**: Every documented error condition has a test expecting that error
- **State transitions**: If behaviour depends on state, test each valid transition

---

## Violation Recovery

Agent must detect violations and execute recovery automatically. All recovery follows present-before-apply: propose fix → human approves → apply → re-validate.

### Missing Plan Reference

**Detection:** Test scenario lacks "Plan Reference" field

**Recovery:**
1. STOP at this scenario
2. State: "VIOLATION: Test scenario has no plan reference"
3. IDENTIFY which behaviour this tests
4. ADD Plan Reference field
5. IF no matching behaviour → flag as potential orphan

### Coverage Gap / Orphan Scenario / Semantic Duplicate

These violations are detected and resolved by the inline recovery procedures in Step 3:

- **Coverage gaps and orphan scenarios** → §3.1 Traceability Check "If issues found" recovery
- **Semantic duplicates** → §3.2 Duplication Check — present to human for decision

---

## What NOT to Do

- ❌ Create test manifest without a plan document
- ❌ Write test scenarios without plan references
- ❌ Skip traceability validation
- ❌ Auto-resolve duplicate scenarios without human decision
- ❌ Proceed with missing behaviour coverage
- ❌ Include scenarios for out-of-scope behaviours
- ❌ Use placeholder assertions in scenario expectations
- ❌ Skip rules alignment check
- ❌ Batch multiple modules into a single approval — present and append one module at a time
- ❌ Draft scenarios for the next module before the current module is approved and appended

---

---
**END OF DOCUMENT:** Total sections: 7 | Purpose: Write test manifests from implementation plans