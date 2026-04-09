# Test Review Skill

## Overview

Review test quality file-by-file: apply compliance gates, fix issues inline, record outcomes. Each file is reviewed, fixed if needed, and persisted before the next begins.

**Goal:** Review tests against compliance gates, fix violations inline, and produce a record of findings and resolutions.

**Two modes:**

| Mode | Trigger | Output target |
|------|---------|---------------|
| **Manifest review** | Test manifest file provided in prompt | Annotate the manifest with review status per test |
| **Scope discovery** | No file provided | `planning/reviews/tests-[date].md` — section per file reviewed |

**NOT for:**

- Architecture boundaries → use [review-architecture.md](review-architecture.md)
- Code correctness → use [review-code.md](review-code.md)
- E2E reliability → use [review-e2e.md](review-e2e.md)

**Outputs:**

- Test manifest (annotated) OR `planning/reviews/tests-[date].md` — review record written incrementally
- `planning/reviews/tests-[date]-recommendations.md` — unresolved items only (created only if needed)

---

## Table of Contents

- [Overview](#overview)
- [Non-Negotiable Rules](#non-negotiable-rules)
- [Entry Gate](#entry-gate)
- [Step 1: Establish Scope](#step-1-establish-scope)
- [Step 2: Review + Fix Loop](#step-2-review--fix-loop)
- [Step 3: Compile Unresolved](#step-3-compile-unresolved)
- [Step 4: Complete Review](#step-4-complete-review)
- [Anti-Patterns](#anti-patterns)
- [Severity Taxonomy](#severity-taxonomy)
- [Common Rationalisations](#common-rationalisations-forbidden)
- [Final Rule](#final-rule)

---

## Non-Negotiable Rules

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST apply all compliance gates (see §2.2) to every test file reviewed
- You MUST fix violations inline — do not defer to other skills when a fix is straightforward
- You MUST present each file's findings to the human with clear explanation, example, and solution before fixing
- You MUST write each file's review outcome to the output target before starting the next file
- You MUST NOT batch multiple file reviews into a single write
- You MUST NOT skip files already identified in scope
- You MUST run the targeted test command after every fix to verify the fix works
- You MUST record unresolved items (design decisions, new files needed) separately — do not silently skip them
- You MUST use UK English throughout

</CRITICAL_REQUIREMENT>

---

## Entry Gate

```
IF human request is about architecture boundaries
  → REDIRECT to `/midtempo-framework/review-architecture.md`

IF human request is about code correctness
  → REDIRECT to `/midtempo-framework/review-code.md`

IF human request is about E2E reliability
  → REDIRECT to `/midtempo-framework/review-e2e.md`
```

VERIFY-COMPLETE-READ for EVERY file below:
  CHECK the last line says "END OF DOCUMENT"
  IF CHECK fails → Re-read from offset until true end

READ ALL of `/midtempo-framework/rules/writing.md` → before proceeding
READ ALL of `/midtempo-framework/rules/testing.md` → before proceeding
READ ALL of `/midtempo-framework/instructions/purpose.md` → before proceeding
READ ALL of `/midtempo-framework/instructions/architecture.md` → before proceeding


```
IF file path provided AND file does not exist
  → STOP: Manifest file not found at [path]. Ask the human to confirm the correct path.
    (If no manifest exists, the human can re-invoke without a file path to use Scope Discovery mode.)

IF file path provided in prompt
  → MODE: Manifest Review
  → READ the provided file completely
  → Extract test file list from manifest

IF no file path provided
  → MODE: Scope Discovery
  → Continue to Step 1 for scope questions

VALID: Continue to Step 1
```

---

## Step 1: Establish Scope

### 1.1 Determine Mode

```
IF MODE = Manifest Review (file provided):
  1. READ the manifest file completely
  2. Extract the list of test files and their descriptions
  3. COUNT total tests declared
  4. SET output target = the manifest file path

IF MODE = Scope Discovery (no file provided):
  ASK: "What test files should I review?"

  | Scope Type | Behaviour |
  |------------|-----------|
  | Feature/branch | Find test files related to feature from planning docs |
  | Directory | All test files in specified directory |
  | Specific files | Review listed files only |
  | Full suite | All test files in project |

  WAIT for answer.

  SET output target = `planning/reviews/tests-[date].md`
```

### 1.2 Gather Planning Context

Search for planning docs related to the scope:

- `/planning/*-plan.md` — implementation plan
- `/planning/*-design.md` — design document
- `/planning/*-tests.md` — test manifest

```
IF planning docs found
  → READ and extract: intended behaviour, edge cases, error handling requirements
IF no planning docs found
  → ASK: "No planning docs found. Provide path or confirm this is a minor review."
```

### 1.3 Build File List

```
IF MODE = Manifest Review:
  → File list comes from manifest entries
IF MODE = Scope Discovery:
  → Scan scope for test files
  → List each file with its source file under test
```

### 1.4 Present Scope

```
Test Review Scope:

Mode: [Manifest Review / Scope Discovery]
Output target: [manifest path / planning/reviews/tests-[date].md]

Planning docs:
  - Plan: [path or "none"]
  - Design: [path or "none"]
  - Manifest: [path or "none"]

Files to review ([N] total):
  1. [test file path] → tests [source file path]
  2. [test file path] → tests [source file path]
  ...
```

WAIT for human validation before proceeding

Review scope, file list, and output target for accuracy
IF human approves
  → VALID: Create output file (if scope discovery mode) and continue to Step 2
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

### 1.5 Create Output File (Scope Discovery Only)

```
IF MODE = Scope Discovery:
 
  CREATE `planning/reviews/tests-[date].md` with:

  # Test Review: [Scope Description]

  **Date:** [DD/MM/YYYY]
  **Status:** In Progress
  **Mode:** Scope Discovery

  ---

  ## Files to Review

  | # | Test File | Source File | Status |
  |---|-----------|-------------|--------|
  | 1 | [path] | [path] | Pending |
  | 2 | [path] | [path] | Pending |
  ...

IF MODE = Manifest Review:
  → Output target already exists (the manifest file)
  → No file creation needed

Continue to Step 2.
```

---

## Step 2: Review + Fix Loop

Process each test file sequentially. Review, fix, verify, persist — then move to the next file.

### 2.1 Per-File Process

```
FOR EACH test file in the remaining file list:

  1. READ the test file completely
  2. READ the source file under test
  3. Apply compliance gates (§2.2)
  4. CLASSIFY each finding severity (see Severity Taxonomy). IF recommended or nit → present options (fix now / defer / skip) to human. IF deferred → flag as UNRESOLVED.
  5. IF violations found:
     → Present findings (§2.3)
     → WAIT for human validation
     → Fix violations
     → Run targeted test to verify fix:
       ```bash
       npm run test:python <test-file>    # Verbose — single file for TDD loop
       ```
     → PRESENT test result to human: "[N] tests passed — fix verified"
     → IF test fails after fix → ASK human for guidance
  6. IF no violations:
     → STATE: "[file path]: PASS — all gates satisfied"
  7. Write outcome to output target (§2.4)
  8. Continue to next file
```

### 2.2 Compliance Gates

Apply all gates from `/midtempo-framework/rules/testing.md` to each test file:

- CG-1: Real behaviour assertions — no mock existence or placeholders
- CG-2: No test-only methods in production — utilities in repo-specific locations per architecture.md §7.3
- CG-3: Mocks at IO/network level only — never mock business logic test depends on
- CG-4: Mock mirrors complete real API structure — all documented fields
- CG-5: Test isolation — self-contained, no shared state, order-independent
- CG-6: Coverage scope — happy path, error paths, boundary conditions
- CG-7: Shared test data uses factories or helpers — no duplicated inline construction across files

State each gate outcome explicitly per file:

```
[test file path]:
  CG-1: [PASS / FAIL — description]
  CG-2: [PASS / FAIL — description]
  CG-3: [PASS / FAIL — description]
  CG-4: [PASS / FAIL — description]
  CG-5: [PASS / FAIL — description]
  CG-6: [PASS / FAIL — description]
```

### 2.3 Finding Presentation Format

For each violation, present with enough context for the human to understand the problem and the fix:

```
File: [test file path]
Gate: [CG-N] — [gate name]
Status: FAIL

Problem:
  [Clear description of what is wrong]

Current code:
  [The specific code that violates the gate — file:line reference]

Why this matters:
  [One sentence explaining the impact]

Fix:
  [Exact code change or approach to resolve the violation]

Recommendation:
  [Any additional context — alternative approaches, related patterns]
```

WAIT for human validation before proceeding

Review findings, examples, and proposed fixes for accuracy
IF human approves
  → VALID: Apply fixes and run targeted test to verify
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

### 2.4 Write Outcome to Output Target

After each file is reviewed (and fixed if needed):

```
IF MODE = Manifest Review:
  → FIND the module section in the manifest where **Test file:** matches the reviewed file → ANNOTATE the module section header
  → ANNOTATE with:
    Status (pick one):
      - PASS: "✓ Reviewed — all gates passed"
      - FIXED: "✓ Reviewed — [N] violations fixed: [brief summary]"
      - UNRESOLVED: "⚠ Reviewed — [N] items need human decision: [brief summary]"

IF MODE = Scope Discovery:
  → APPEND section to `planning/reviews/tests-[date].md`:

  ### [test file path]

  **Source:** [source file path]
  **Result:** [PASS / FIXED / UNRESOLVED]

  Gates:
    CG-1: [PASS/FIXED] CG-2: [PASS/FIXED] CG-3: [PASS/FIXED]
    CG-4: [PASS/FIXED] CG-5: [PASS/FIXED] CG-6: [PASS/FIXED]

  [IF FIXED:]
  Fixes applied:
  - [Gate]: [what was changed]

  [IF UNRESOLVED:]
  Unresolved:
  - [description — requires human decision]

  → UPDATE the Files to Review table: change Status from "Pending" to "Done"
```

---

## Step 3: Compile Unresolved

Gather any items not fixed inline during Step 2. Create a recommendations file only if unresolved items exist.

### 3.1 Collect Unresolved Items

```
FOR EACH file reviewed in Step 2:
  → CHECK for UNRESOLVED outcomes
  → ADD to unresolved list with context
```

### 3.2 Present Results

```
IF unresolved items exist:

  Unresolved Items: [N] total

  Needs human decision:
  - [description] — [file:line or context]

IF no unresolved items:
  → STATE: "All issues resolved inline. No recommendations file needed."
  → Continue to Step 4.
```

```
IF unresolved items exist
  → Present to human
```

WAIT for human validation before proceeding

Review unresolved items for accuracy and completeness
IF human approves
  → VALID: Write recommendations file
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

### 3.3 Write Recommendations File

```
IF unresolved items exist:
  
  CREATE `planning/reviews/tests-[date]-recommendations.md` with:

  # Test Review Recommendations: [Scope Description]

  **Date:** [DD/MM/YYYY]
  **Source:** [output target path]

  ---

  ## Needs Human Decision

  ### [Item Title]

  - **File:** [test file path]
  - **Context:** [what needs deciding]
  - **Options:** [if applicable]

IF no unresolved items:
  → SKIP recommendations file

Continue to Step 4.
```

---

## Step 4: Complete Review

### 4.1 Review Checklist

Before presenting completion output, verify:

```
- [ ] All files in scope reviewed (none skipped)
- [ ] Compliance gates (CG-1 through CG-6) applied to every file
- [ ] All straightforward violations fixed inline
- [ ] Targeted test run after every fix (all passing)
- [ ] Each file's outcome written to output target
- [ ] Unresolved items compiled (or confirmed none)
- [ ] Recommendations file written (or confirmed not needed)
```

### 4.2 Finalise Output File

```
IF MODE = Scope Discovery:
  → UPDATE `planning/reviews/tests-[date].md` header:
    Change `**Status:** In Progress` to `**Status:** Complete`

IF MODE = Manifest Review:
  → No header update needed (manifest is annotated in place)
```

### 4.3 Completion Output

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output after review completes - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
</CRITICAL_REQUIREMENT>

````
---
                   TEST REVIEW COMPLETE: [SCOPE DESCRIPTION]                   

---

Mode: [Manifest Review / Scope Discovery]
Files reviewed: [N]
Results: [N] PASS, [N] FIXED, [N] UNRESOLVED

Output target:
  [output target path]

Recommendations:
  `planning/reviews/tests-[date]-recommendations.md` — [N] unresolved items

  OR "No unresolved items — no recommendations file created"

IF MODE = Manifest Review:
  Provide next step prompt to human:
  ```
  In a new conversation run
  "Phase 2 — use midtempo-framework/deliver.md with planning/[feature-name]-plan.md. Run Phase 2."
  ```
  Replace [feature-name] with the actual plan document name from planning context.
  (Phase 2 = GREEN phase — writing passing tests.)

IF MODE = Scope Discovery AND unresolved items exist:
  Tell human to open the recommendations file as context for a new conversation:
  ```
  In a new conversation run
  open planning/reviews/tests-[date]-recommendations.md
  ```

IF MODE = Scope Discovery AND no unresolved items:
  STATE: "Review complete. No follow-up actions outstanding."
````

---

## Anti-Patterns

### Anti-Pattern 1: Batch Reviewing

**INVALID:**

```
"Here are findings for all 8 test files..."
```

**VALID:** Review one file at a time. Present findings. Fix. Verify. Write to output. Then move to next file.

### Anti-Pattern 2: Findings Without Examples

**INVALID:**

```
"CG-3 violation found in test_api.py"
```

**VALID:**

```
File: tests/test_api.py:42
Gate: CG-3 — Mocks at IO/network level only
Status: FAIL

Problem:
  Test mocks the business logic function `calculate_total()` instead of the
  external API call. The test verifies the mock was called, not the behaviour.

Current code:
  mock_calculate = mocker.patch('services.calculate_total')
  result = process_order(order)
  mock_calculate.assert_called_once()

Why this matters:
  If calculate_total changes its return type, this test still passes — it
  protects the mock, not the behaviour.

Fix:
  Mock the external API call instead. Assert on the return value of process_order:
  mock_api = mocker.patch('services.external_api.fetch_prices')
  mock_api.return_value = {'item_a': 10.00}
  result = process_order(order)
  assert result.total == 10.00
```

### Anti-Pattern 3: Skipping the Fix

**INVALID:**

```
"CG-1 violation found. Adding to recommendations for later."
```

**VALID:** Fix straightforward violations inline. Run targeted test. Verify. Only defer items that need human design decisions.

### Anti-Pattern 4: Silent Resolution

**INVALID:**

```
[Agent fixes test without showing the human what was wrong or why]
```

**VALID:** Present the finding with problem, example, and fix. Wait for human validation. Then apply the fix.

---

## Severity Taxonomy

| Severity | Criteria | Action |
|----------|----------|--------|
| **Blocking** | Gate violation that changes test behaviour if left unfixed | Fix inline — present finding, fix, verify |
| **Recommended** | Improvement that strengthens test quality but does not change pass/fail | Present to human with trade-offs. Human decides: fix now, defer, or skip |
| **Nit** | Cosmetic or naming improvement | Present to human with trade-offs. Human decides: fix now, defer, or skip |

```
IF finding is blocking:
  → Fix inline (mandatory)
IF finding is recommended or nit:
  → Present options to human:

  | Option | Effect |
  |--------|--------|
  | Fix now | Apply fix inline, run targeted test, record as FIXED |
  | Defer | Record in recommendations file for follow-up |
  | Skip | Note in file outcome, no further action |

  → WAIT for human decision
```

---

## Common Rationalisations (FORBIDDEN)

| Human Says | Agent Must Respond |
|---|---|
| "Skip the gates, the tests are fine" | "No. Gates are mandatory for every file. Applying now." |
| "Just list the findings, don't fix them" | "No. Blocking violations are fixed inline. Presenting finding and fix now." |
| "Review all files at once, it's faster" | "No. Files are reviewed one at a time with findings written before the next." |
| "Mock assertions are fine for this case" | "No. CG-1 requires behaviour assertions. Presenting the fix." |
| "Don't bother with the output file" | "No. Each file's outcome is written to the output target before the next file." |
| "Mark it as recommended, not blocking" | "No. Severity follows the taxonomy. Gate violations are blocking." |

---

## Final Rule

```
REVIEW = GATE CHECK + FIX + VERIFY + PERSIST
SCOPE: One file at a time, findings written before the next
MODES: Manifest provided → annotate manifest. No file → create review file.
RESUME: Output on disk signals progress. Re-invoke to continue.
NEVER: Batch review, skip gates, fix silently, defer blocking violations
```

No exceptions without human partner's permission.

---
**END OF DOCUMENT:** Total sections: 12 | Purpose: Review test quality file-by-file with inline fixes and incremental persistence
