# Code Review Skill

## Overview

Review code for fitness-for-purpose, instruction compliance, and security compliance. Each analysis section is validated by the human and persisted to file before the next begins.

**Goal:** Produce an incremental review report and a grouped recommendations file with skill routing per finding.

**NOT for:**

- Architecture boundaries, layering, design principles → use [review-architecture.md](review-architecture.md)
- Test quality → use [review-tests.md](review-tests.md)
- E2E reliability → use [review-e2e.md](review-e2e.md)
- Maintainability, readability, DRY, SRP → use [refactor.md](refactor.md)

**Outputs:**

- `planning/reviews/code-[date].md` — Review report (written incrementally, one section at a time)
- `planning/reviews/code-[date]-recommendations.md` — Grouped findings with severity and skill routing

---

## Table of Contents

- [Overview](#overview)
- [Non-Negotiable Rules](#non-negotiable-rules)
- [Severity Taxonomy](#severity-taxonomy)
- [Entry Gate](#entry-gate)
- [Step 1: Scope & Intent](#step-1-scope--intent)
- [Step 2: Fitness-for-Purpose](#step-2-fitness-for-purpose)
- [Step 3: Instruction Compliance](#step-3-instruction-compliance)
- [Step 4: Security Compliance](#step-4-security-compliance)
- [Step 5: Compile Recommendations](#step-5-compile-recommendations)
- [Step 6: Complete Review](#step-6-complete-review)
- [Anti-Patterns](#anti-patterns)
- [Common Rationalisations](#common-rationalisations-forbidden)
- [Final Rule](#final-rule)

---

## Non-Negotiable Rules

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST verify code implements the design and plan documents before checking compliance
- You MUST verify each applicable compliance gate (CG-N) with PASS/FAIL and file:line evidence
- You MUST cite the instruction or rule source for every finding
- You MUST include at least one positive observation
- You MUST label severity: blocking/recommended/nit
- You MUST assume linting, type checks, test coverage, and architecture boundaries are handled elsewhere
- You MUST present each analysis section to the human before writing it to the review file
- You MUST wait for human validation on sections with findings before appending
- You MUST write sections with no findings (all PASS) without requiring validation
- You MUST write each validated section to `planning/reviews/code-[date].md` before starting the next
- You MUST compile findings into `planning/reviews/code-[date]-recommendations.md` with skill routing per finding
- You MUST NOT batch multiple sections into a single write
- You MUST NOT make inline code fixes — observe and recommend only

</CRITICAL_REQUIREMENT>

---

## Severity Taxonomy

### Blocking

- Code does not implement design/plan — acceptance criteria unmet, missing edge cases
- Instruction compliance gate (CG-N) violation
- Design deviation without documented justification

### Recommended

- Partial compliance — gate intent met but implementation incomplete
- Missing error context or inconsistent error handling
- Edge case gaps identified in plan but not fully addressed

### Nit

- Minor improvements within scope that do not affect correctness or compliance

### Escalation

- **Missing intent/requirements** → pause, request clarification
- **Repeated policy failures** (systemic issues) → escalate to planning for RFC

---

## Entry Gate

```
IF human request is about architecture boundaries
  → REDIRECT to `/midtempo-framework/review-architecture.md`

IF human request is about test quality
  → REDIRECT to `/midtempo-framework/review-tests.md`

IF human request is about E2E reliability
  → REDIRECT to `/midtempo-framework/review-e2e.md`
```

VERIFY-COMPLETE-READ for EVERY file below:
  CHECK the last line says "END OF DOCUMENT"
  IF CHECK fails → Re-read from offset until true end

READ ALL of `/midtempo-framework/rules/writing.md` → before proceeding
READ ALL of `/midtempo-framework/instructions/purpose.md` → before proceeding
READ ALL of `/midtempo-framework/instructions/architecture.md` → before proceeding
READ ALL of `/midtempo-framework/instructions/error-handling.md` → before proceeding


IF the current task involves UI
READ ALL of `/midtempo-framework/instructions/frontend-design.md` → for UI component patterns
READ ALL of `/midtempo-framework/instructions/style-guide.md` → for styling conventions





```
VALID: Continue to Step 1
```

---

## Step 1: Scope & Intent

### 1.1 Establish Scope

ASK the human two questions. WAIT for each answer before continuing.

**Q1 — What are you reviewing?**

| Scope Type | Behaviour |
|------------|-----------|
| Feature/branch | Find planning docs, scope to feature files |
| Specific files | Human provides file list |
| PR/diff | Scope to changed files in the diff |

**Q2 — What's driving this review?**

| Intent | Effect |
|--------|--------|
| Pre-merge check | Standard full review against instructions and plan |
| Investigate concern | Prioritise concern area, then standard checks |
| Post-delivery verification | Focus on design compliance and acceptance criteria |

### 1.2 Documentation Check

```
IF feature/branch → REQUIRED: find and read planning docs. IF not found → STOP.
IF specific files → OPTIONAL: use planning docs if available.
IF PR/diff → REQUIRED: find planning docs from branch name or PR description.
```

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
    → NOTE: No design document found — continuing without design context


Also search for `/planning/*-plan.md` — extract intended behaviour and acceptance criteria.

Read and extract:
- Intended behaviour and acceptance criteria
- Edge cases and error handling requirements

### 1.3 Present Scope

Present scope summary to human:

```
Review Scope: [Feature/Target Name]

- Type: [feature / files / PR]
- Target: [from Q1]
- Intent: [from Q2]
- Planning docs:
  - Design: [path or "not applicable"]
  - Plan: [path or "not applicable"]
- Files: [list]
- Required instructions: [derived from entry gate reads + applicable conditional reads]
```

WAIT for human validation before proceeding

Review scope, intent, and planning docs for accuracy
IF human approves
  → VALID: CREATE review file and continue to '§1.4 Create Review File'
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

### 1.4 Create Review File

CREATE `planning/reviews/code-[date].md` with:

```markdown
# Code Review: [Feature Name]

**Date:** [DD/MM/YYYY]
**Status:** In Progress

---

## Review Scope

- **Type:** [from Q1]
- **Target:** [from Q1]
- **Intent:** [from Q2]
- **Planning docs:**
  - Design: [path or "not applicable"]
  - Plan: [path or "not applicable"]

---

## Files Under Review

- [file list]
```

```
IF Review File created → VALID: Continue to Step 2
```

---

## Step 2: Fitness-for-Purpose

Compare code against design and plan documents. Check intent before compliance — does the code do what the plan says?

```
IF resuming this review:
  READ `planning/reviews/code-[date].md`
  IDENTIFY which sections are already written
  CONTINUE from the first section not yet appended to the file
```

### 2.1 Compare Against Design

```
IF planning docs exist:
  1. COMPARE code against design document
  2. VERIFY all acceptance criteria addressed
  3. CHECK edge cases from plan are handled
  4. CHECK error paths match the plan
  5. FLAG any deviation from intended behaviour

IF code deviates from design without documented reason
  → RECORD as blocking finding

IF code matches design OR deviations justified
  → VALID: Continue

IF design doc absent:
  → STATE: "No design doc — skipping design comparison"
  → APPEND note to review file: "Fitness-for-Purpose: not checked (no design doc)"
  → VALID: Continue to §2.2
```

### 2.2 Present Results

**Output to human:**

**Finding format** (use for every finding in this review):

`[severity] Summary (source: "doc.md: quoted requirement or gate rule")`

```
Fitness-for-Purpose: [Feature Name]

Design alignment: [PASS | FAIL with details]
Acceptance criteria: [X/Y satisfied]
Edge cases: [handled | gaps identified]
Error paths: [match plan | deviations found]

Findings:
- [finding using format above] OR "No deviations found"
```

### 2.3 Validation Gate

```
IF findings exist
  → PRESENT results to human
```

WAIT for human validation before proceeding

Review fitness-for-purpose findings for accuracy
IF human approves
  → VALID: APPEND to `planning/reviews/code-[date].md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

```
IF no findings (design alignment PASS)
  → STATE: "Fitness-for-Purpose: PASS — code matches design"
  → APPEND to `planning/reviews/code-[date].md` without waiting

Continue to Step 3.
```

---

## Step 3: Instruction Compliance

Verify code against compliance gates from each instruction document read at the entry gate. Read the "Compliance Gates" section from each applicable instruction, then check each gate against the code under review.

### 3.1 Gather Applicable Gates

```
FOR EACH instruction document read at the entry gate:
  1. REFERENCE the "Compliance Gates" section from your entry gate read — do not re-read the full document
  2. RECORD each CG-N gate applicable to the files under review
  3. SKIP gates that do not apply to the files in scope
```

**Always applicable:**

- `/midtempo-framework/instructions/architecture.md` # Services architectural structure and design principles — "Compliance Gates" section
- `/midtempo-framework/instructions/error-handling.md` # Error handling patterns and conventions for the repository — "Compliance Gates" section

**When UI files in scope:**

- `/midtempo-framework/instructions/frontend-design.md` # Component architecture, composition patterns, and UI organisation — "Compliance Gates" section
- `/midtempo-framework/instructions/style-guide.md` # CSS style rules and conventions — "Compliance Gates" section

### 3.2 Verify Each Gate

```
FOR EACH compliance gate recorded:
  → VERIFY gate against code under review
  → Record PASS or FAIL with file:line evidence
  → CITE gate number in findings (e.g., "architecture CG-3")
```

### 3.3 Present Results

**Output to human:**

Use the finding format from §2.2 for every FAIL entry.

```
Instruction Compliance: [Feature Name]

architecture.md:
  CG-1: [PASS | FAIL — file:line evidence]
  CG-2: [PASS | FAIL — file:line evidence]

error-handling.md:
  CG-1: [PASS | FAIL — file:line evidence]
  CG-2: [PASS | FAIL — file:line evidence]

[additional instruction docs as applicable]

Summary: [N] gates checked, [N] PASS, [N] FAIL
```

### 3.4 Validation Gate

```
IF any gate is FAIL
  → PRESENT results to human
```

WAIT for human validation before proceeding

Review instruction compliance gate results for accuracy
IF human approves
  → VALID: APPEND to `planning/reviews/code-[date].md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

```
IF all gates PASS
  → STATE: "Instruction Compliance: all PASS"
  → APPEND to `planning/reviews/code-[date].md` without waiting

Continue to Step 4.
```

---

## Step 4: Security Compliance

```
SKIP: No security domains configured. Continue to Step 5.
```

---

## Step 5: Compile Recommendations

Compile all findings from Steps 2–4 into a single recommendations file.

### 5.1 Gather Positives

Note positives as you encounter them in Steps 2–4. §5.1 collects what you found — it does not generate new observations.

Before compiling findings, record at least one positive observation — a concrete code strength with file:line evidence.

### 5.2 Group Findings

Group findings by severity (see §Severity Taxonomy):

1. **Blocking** — must resolve before merge
2. **Recommended** — should resolve soon
3. **Nit** — minor improvements

For each finding, include:

- **Severity:** blocking / recommended / nit
- **Skill:** route to the most appropriate skill:
  - Incorrect behaviour → `bugs.md`
  - Structural issue → `refactor.md`
  - Missing or incomplete feature → `refine.md`
  - Design gap or new capability needed → `build.md`
  - None of the above → ASK human: "Which skill applies to this finding?"
- **Evidence:** file:line references
- **Summary:** one-sentence description
- **Source:** instruction/rule citation
- **Acceptance criteria:** measurable condition for resolution

### 5.3 Present Results

Steps 2–4 approved the findings. This step adds skill routing and acceptance criteria — present these for human review before writing the recommendations file.

**Output to human:**

```
Recommendations: [Feature Name]

Positives:
- [Strength with file:line evidence]

Blocking:
- [Finding] — Skill: [skill] — Source: [citation] — Evidence: [file:line]

Recommended:
- [Finding] — Skill: [skill] — Source: [citation] — Evidence: [file:line]

Nit:
- [Finding] — Skill: [skill] — Source: [citation] — Evidence: [file:line]

Total: [N] findings ([N] blocking, [N] recommended, [N] nit)
```

### 5.4 Validation Gate

This step always requires validation — it produces the recommendations file.

WAIT for human validation before proceeding

Review grouped recommendations for accuracy, severity, and skill routing
IF human approves
  → VALID: WRITE to `planning/reviews/code-[date]-recommendations.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

### 5.5 Write Recommendations File

After validation, CREATE `planning/reviews/code-[date]-recommendations.md`:

```markdown
# Code Review Recommendations: [Feature Name]

**Date:** [DD/MM/YYYY]
**Source:** `planning/reviews/code-[date].md`

---

## Positives

- [Strength with file:line evidence]

---

## Blocking

### [Finding Title]

- **Skill:** `/midtempo-framework/[skill].md`
- **Source:** [instruction/rule citation]
- **Evidence:** [file:line references]
- **Summary:** [one sentence]
- **Acceptance Criteria:**
  - [ ] [measurable criterion — observable pass/fail, scoped to this finding, verifiable by the cited skill]

---

## Recommended

### [Finding Title]

- **Skill:** `/midtempo-framework/[skill].md`
- **Source:** [instruction/rule citation]
- **Evidence:** [file:line references]
- **Summary:** [one sentence]
- **Acceptance Criteria:**
  - [ ] [measurable criterion — observable pass/fail, scoped to this finding, verifiable by the cited skill]

---

## Nit

### [Finding Title]

- **Skill:** `/midtempo-framework/[skill].md`
- **Source:** [instruction/rule citation]
- **Evidence:** [file:line references]
- **Summary:** [one sentence]
- **Acceptance Criteria:**
  - [ ] [measurable criterion — observable pass/fail, scoped to this finding, verifiable by the cited skill]
```

```
IF no findings across Steps 2–4
  → SKIP recommendations file
  → STATE: "No findings — no recommendations file needed"

Continue to Step 6.
```

---

## Step 6: Complete Review

### 6.1 Review Checklist

Before completing, verify every item:

```
[ ] Step 1: Scope established, planning docs found, review file created
[ ] Step 2: Fitness-for-purpose checked against design/plan
[ ] Step 3: All applicable instruction compliance gates verified with PASS/FAIL
[ ] Step 4: Skipped (no security domains configured)
[ ] Step 5: Findings compiled with severity and skill routing (or no findings confirmed)
[ ] At least one positive observation recorded
[ ] Every finding cites instruction/rule source with file:line evidence
[ ] Each section written to review file before starting the next
[ ] Recommendations file written (if findings exist)
```

### 6.2 Finalise Review File

UPDATE `planning/reviews/code-[date].md`:

```
1. APPEND the completed checklist
2. UPDATE the file header: **Status:** In Progress → **Status:** Complete
```

### 6.3 Completion Output

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output after review completes - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
</CRITICAL_REQUIREMENT>

```
CODE REVIEW SUMMARY

Review: [Feature Name]
Date: [DD/MM/YYYY]
Status: Complete

Results:
  Fitness-for-Purpose: [PASS | FAIL]
  Instruction Compliance: [N] gates — [N] PASS, [N] FAIL
Findings: [N] total ([N] blocking, [N] recommended, [N] nit)

Files:
  Review: planning/reviews/code-[date].md
  Recommendations: planning/reviews/code-[date]-recommendations.md (or "none")
```

---
                      CODE REVIEW COMPLETE: [FEATURE NAME]                     

---

---

## Anti-Patterns

### 1. Reviewing Without Planning Docs

| | Example |
|---|---|
| **INVALID** | Jump straight to code and check against general best practices |
| **VALID** | Find planning docs first, extract acceptance criteria and edge cases, then review code against those specific requirements |

**Why it matters:** Without planning docs, fitness-for-purpose checks become subjective opinion rather than verifiable compliance.

### 2. Findings Without Citations

| | Example |
|---|---|
| **INVALID** | `[blocking] This function is too complex` |
| **VALID** | `[blocking] Summary of violation (instruction-doc.md CG-N: "quoted gate rule text")` |

**Why it matters:** Uncited findings are unverifiable and indistinguishable from personal preference.

### 3. Skipping Compliance Gates

| | Example |
|---|---|
| **INVALID** | Skim instruction docs and report "looks compliant" |
| **VALID** | Read each CG-N gate, verify against code with PASS/FAIL and file:line evidence |

**Why it matters:** Compliance gates exist to catch systematic violations. Skipping them defeats the purpose of gate-based review.

### 4. Batching Sections

| | Example |
|---|---|
| **INVALID** | Complete all steps, then present everything at once for validation |
| **VALID** | Present each step's findings, wait for validation on sections with findings, write to file, then proceed to next step |

**Why it matters:** Incremental validation catches misunderstandings early. Batched reviews waste effort when early findings invalidate later analysis.

---

## Common Rationalisations (FORBIDDEN)

| Rationalisation | Agent Response |
|----------------|----------------|
| "The code works, so it's fine" | Working code can still violate compliance gates and miss edge cases |
| "That gate doesn't apply here" | If the gate scope does not match the files under review, SKIP per §3.1 step 3. Do not record it as PASS. |
| "No planning docs, so skip fitness check" | ASK human for docs or confirmation — do not skip silently |

If user persists: add a note to the relevant planning document recording the override and the reason given. Then continue.

---

## Final Rule

```
Review completion → scope established, fitness checked, compliance gates verified,
  checklist complete, review file written, recommendations compiled
Otherwise → review incomplete → do not mark as done
```

No exceptions without human partner's permission.

---
**END OF DOCUMENT:** Total sections: 16 | Purpose: Code review for fitness-for-purpose, instruction compliance, and security compliance with incremental sectional output