# Write Design Document from Decisions

## Overview

Transforms validated decisions into a structured design document.

**Prerequisites:**
- Completed Decisions doc with validated decisions in `/planning/[feature-name]-decisions.md`
- All conflicts resolved in decisions document

**Output:**
- `/planning/[feature-name]-design.md` — Final design document following template structure

**Template:**
- `/midtempo-framework/templates/design.md` — Design document structure

---

## Table of Contents

- [Overview](#overview)
- [Non-Negotiable Rules](#non-negotiable-rules)
- [Entry Gate](#entry-gate)
- [Step 1 - Write Design Document](#1-step-1---write-design-document)
  - [Write Design](#11-write-design)
  - [Exit Gate — Write Design](#12-exit-gate--write-design)
- [Step 2 - Alignment Check](#2-step-2---alignment-check)
  - [Verify Design Coherence](#21-verify-design-coherence)
  - [Present Findings](#22-present-findings)
  - [Write Deferred Sections](#23-write-deferred-sections)
- [Step 3 - Output to Human](#3-step-3---output-to-human)
  - [Design Complete Output](#31-design-complete-output)
- [What NOT to Do](#what-not-to-do)

---

## Non-Negotiable Rules

<CRITICAL_REQUIREMENT type="MANDATORY">

⚠️ FILE PATH CRITICAL ⚠️

You are writing to: `/planning/[feature-name]-design.md` (DESIGN FILE)
You are NOT writing to: `/planning/[feature-name]-decisions.md` (decisions file - already complete)

- You MUST write ONE section at a time — batch writes cause network failures
- You MUST follow the design template EXACTLY
- You MUST map decisions.md content to design.md sections
- You MUST use UK English spelling throughout

</CRITICAL_REQUIREMENT>

---

### ENTRY GATE

```
IF decisions document does not exist at `/planning/[feature-name]-decisions.md`
  → INVALID: STOP - Run build skill first

IF decisions document has unresolved conflicts or omissions
  → INVALID: Decisions doc not valid 
  → ASK: human what to do

READ ALL of `/midtempo-framework/rules/writing.md` → before proceeding
  → INVALID: STOP - Read writing rules before proceeding

READ ALL of `/planning/[feature-name]-decisions.md` → input — your source material

READ ALL of `/midtempo-framework/templates/design.md` → template — your structure

VALID: Continue to Step 1
```

---

## 1. Step 1 - Write Design Document

### 1.1 Write Design

⚠️ TARGET FILE: `/planning/[feature-name]-design.md` ⚠️

Write the design document adhering to the design template:
   - Map decisions from decisions.md to template sections
   - Use the design template EXACTLY - no deviations, additions, or omissions
   - Format decisions in Section 3.2 as Decision Cards: Category, Choice, Rationale, Rejected, Plan Hand-off
   - Complete all sections or mark N/A with justification

<CRITICAL_REQUIREMENT type="MANDATORY">

Write ONE section of the design document at a time. Do NOT batch-write the entire document in a single step — long-running writes cause network failures.

</CRITICAL_REQUIREMENT>

**Write sections in design template order. Apply these routing rules:**

```
IF current section is 1 (Problem Statement) through 3.8 (Performance Mitigations)
  → INDIVIDUAL APPROVAL: follow "Individual Approval Cycle" below

IF current section is 4 (Dependencies & Constraints)
  → BATCH APPROVAL: draft sections 4, 5, and 6 together
  → Follow "Batch Approval Cycle" below

IF current section is 7 (Open Questions), 8 (References), or Approval
  → SKIP: deferred to "§2.3 Write Deferred Sections" after alignment check
```

**Individual Approval Cycle** (sections 1–3.8):

```
PRESENT section to human
ASK: "Does this section look right?"
WAIT for human's response

IF human approves
  → WRITE approved section to `/planning/[feature-name]-design.md`
  → CONTINUE to next section

IF human queries or corrects
  → UPDATE section based on feedback
  → RE-PRESENT the updated section for approval
  → WAIT for human's response
  → REPEAT until approved
  → WRITE approved section to `/planning/[feature-name]-design.md`
  → CONTINUE to next section
```

**Batch Approval Cycle** (sections 4–6):

```
DRAFT sections: Dependencies & Constraints, Testing Strategy Principles, Migration
PRESENT all three sections together to human
ASK: "Do these supporting sections look right?"
WAIT for human's response

IF human approves
  → WRITE all three sections to `/planning/[feature-name]-design.md`

IF human queries or corrects
  → UPDATE affected sections based on feedback
  → RE-PRESENT updated sections for approval
  → REPEAT until approved
  → WRITE approved sections to `/planning/[feature-name]-design.md`
```

### 1.2 Exit Gate — Write Design

```
IF Design document has missing sections, placeholders, or TODO's
  → INVALID: STOP
  → ASK: human how to proceed

If Design document sections contain conflicts
  → INVALID: STOP
  → ASK: human how to proceed

If Design document does not adhere to the design template EXACTLY
  → INVALID: make sure it follows the template exactly

If Design document does not adhere to the writing rules - `/midtempo-framework/rules/writing.md`
  → INVALID: make sure it follows the writing rules

VALID → proceed to "§2. Step 2 - Alignment Check"
```

---

## 2. Step 2 - Alignment Check

### 2.1 Verify Design Coherence

**Read the complete design document and verify coherence:**

Human clarifications during "Step 1" can introduce conflicts between sections. This check catches them before the design is finalised.

1. **Check for conflicts** — Decisions in one section must not contradict another
2. **Check for omissions** — Re-read the Decisions file in full. Extract every discrete agreed requirement. For each requirement, confirm it appears in the design document. Flag any that do not.
3. **Check terminology** — Same concepts must use same names throughout
4. **Check scope consistency** — In-scope items have coverage; out-of-scope items are only described in "out of scope"

### 2.2 Present Findings

IF ANY issues found:
   → LIST any conflicts found
   → LIST any omissions from decisions file
   → LIST any terminology inconsistencies
   → RECOMMEND fixes
   → WAIT for human's response

   IF human asks questions:
      → ANSWER question
      → RE-PRESENT current issues with updated understanding

   IF human says fix:
      → RESOLVE issues in the design document

IF NO issues found OR issues resolved:
   → CONTINUE to "§2.3 Write Deferred Sections"

### 2.3 Write Deferred Sections

Write Tier 3 sections now that all design content is complete and aligned:

```
WRITE "Open Questions" section:
  - Capture unresolved questions surfaced during writing or alignment check
  - If none remain, write "No open questions — all resolved during design."

WRITE "References" section:
  - Link to Decisions document
  - Add any external references cited in Decisions doc

WRITE "Approval" section:
  - Standard checklist from design template

VALID: proceed to "§3. Step 3 - Output to Human"
```

---

## 3. Step 3 - Output to Human

### 3.1 Design Complete Output

Before presenting the completion output, verify:
1. Every file path in the output references a real file (not invented)
2. Decision table entries match decisions actually made during the session
3. Alignment check results reflect actual Step 2 findings (not assumed "none")
4. No section contains placeholder text ("[TODO]", "[TBD]", "...")

IF any check fails → Fix before presenting. Do not present output with known violations.

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output after exit gates pass - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
- You MUST verify all file paths reference real files and alignment check results are actual before producing this output
</CRITICAL_REQUIREMENT>

```
---
                        DESIGN COMPLETE: [FEATURE-NAME]

---

Document created:
- `planning/[feature-name]-design.md` — Final design

Gate — Design Written: ✅
- [ ] Design document created
- [ ] All template sections completed

Gate — Design Alignment: ✅
- [ ] No conflicts between design sections
- [ ] No omissions from decisions file
- [ ] Terminology consistent throughout

## Summary of Key Decisions

| Decision | Choice |
|----------|--------|
| [decision area] | [choice made] |
| [decision area] | [choice made] |

## New Components

- [ComponentName] ([atomic level])
- [ComponentName] ([atomic level])

## Alignment Check Results

- Conflicts: [none / list]
- Omissions: [none / list]
- Terminology: [consistent / fixes applied]

## Deferred

- [Item deferred and reason]

## Commit

docs: [feature name] design
[2-3 lines describing the design decisions and scope of the feature.]

---
Review design and commit. Start new conversation with:

Plan - use /midtempo-framework/write-plan.md for /planning/[feature-name]-design.md

---
```

---

## What NOT to do

- ❌ Write to decisions.md (that file is complete - write to design.md)
- ❌ Batch-write multiple sections at once
- ❌ Skip section validation before writing
- ❌ Deviate from design template structure
- ❌ Add features beyond decisions document content

---

---
**END OF DOCUMENT:** Total sections: 7 | Purpose: Transform decisions into structured design documents