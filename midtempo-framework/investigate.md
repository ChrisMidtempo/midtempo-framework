# Investigate: Deep Discovery & Recommendations

## Overview

Investigate unknown problems, unexplained behaviour, or uncertainty through structured dialogue and systematic tracing. Produce concrete recommendations as standalone report files.

**Goal:** Transform unclear situations into actionable, classified recommendations with complete evidence.

**NOT for:**

- Known bugs with clear symptoms → use [bugs.md](bugs.md)
- New feature delivery → use [build.md](build.md)
- Delivered features needing tweaks → use [refine.md](refine.md)
- Code quality concerns → use [refactor.md](refactor.md)

**Outputs:**

- `planning/investigations/[name]-investigation.md` — Main findings and analysis
- `planning/investigations/[name]-rec-[n]-[slug].md` — One file per recommendation (ready for new conversation)

---

## Table of Contents

- [Overview](#overview)
- [The Process](#the-process)
  - [Non-Negotiable Rules](#non-negotiable-rules)
  - [Entry Gate](#entry-gate)
- [Step 1: Gather Context](#step-1-gather-context)
  - [Agent Actions (Silent)](#11-agent-actions-silent)
  - [Present Context Summary](#12-present-context-summary)
- [Step 2: Clarify Concern](#step-2-clarify-concern)
  - [Required Questions](#21-required-questions)
  - [Define Scope](#22-define-scope)
- [Step 3: Trace Evidence](#step-3-trace-evidence)
  - [Code Tracing](#31-code-tracing)
  - [Data Investigation](#32-data-investigation)
  - [Behaviour Discovery](#33-behaviour-discovery)
  - [External Research](#34-external-research)
  - [Present Evidence](#35-present-evidence)
- [Step 4: Analyse & Synthesise](#step-4-analyse--synthesise)
  - [Pattern Recognition](#41-pattern-recognition)
  - [Impact Assessment](#42-impact-assessment)
  - [Present Analysis](#43-present-analysis)
- [Step 5: Propose Recommendations](#step-5-propose-recommendations)
  - [Classification](#51-classification)
    - [Refinement criteria](#511-refinement-criteria)
    - [Refactor criteria](#512-refactor-criteria)
    - [Build criteria](#513-build-criteria)
    - [Investigation criteria](#514-investigation-criteria)
  - [Scope Assessment](#52-scope-assessment)
  - [Priority Ordering](#53-priority-ordering)
  - [Present Proposals](#54-present-proposals)
  - [Refine Proposals](#55-refine-proposals)
- [Step 5U: Synthesise Understanding](#step-5u-synthesise-understanding)
  - [Mechanism](#5u1-mechanism)
  - [Current State](#5u2-current-state)
  - [What Could Happen](#5u3-what-could-happen)
  - [Glossary](#5u4-glossary)
  - [Present Synthesis](#5u5-present-synthesis)
- [Step 6: Write Recommendations](#step-6-write-recommendations)
  - [Recommendation File Template](#61-recommendation-file-template)
  - [Sequential Recommendation Approval](#62-sequential-recommendation-approval)
- [Step 6U: Write Understanding Report](#step-6u-write-understanding-report)
- [Step 7: Write Investigation Report](#step-7-write-investigation-report)
- [Investigation Complete](#investigation-complete)
- [Anti-Patterns](#anti-patterns)

---

## The Process

### Non-Negotiable Rules

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST understand the human's concern through structured dialogue before investigating
- You MUST trace systematically through code, data, and behaviour — never guess
- You MUST provide explicit recommendations with reasoning — never end with "it depends"
- You MUST classify all future work as Bug, Refinement, Refactor, Build, or Investigation
- You MUST read and follow the `/midtempo-framework/rules/writing.md` rules
- You MUST validate findings against evidence — no speculation without proof

</CRITICAL_REQUIREMENT>

---

### ENTRY GATE

```
IF human request is a known bug with clear symptoms
  → INVALID: REDIRECT to `/midtempo-framework/bugs.md`

IF human request is a new feature idea
  → INVALID: REDIRECT to `/midtempo-framework/build.md`

IF human request is tweaking a delivered feature
  → INVALID: REDIRECT to `/midtempo-framework/refine.md`

IF human request is refactoring existing code
  → INVALID: REDIRECT to `/midtempo-framework/refactor.md`

IF not read ALL of `/midtempo-framework/rules/writing.md`
  → INVALID: READ ALL of `/midtempo-framework/rules/writing.md` before proceeding


IF not read ALL of `/midtempo-framework/instructions/purpose.md` # Provides an overview of the goal and capabilities of the service
  → INVALID: STOP - Read ALL of `purpose.md` before proceeding
IF not read ALL of `/midtempo-framework/instructions/architecture.md` # Services architectural structure and design principles
  → INVALID: STOP - Read ALL of `architecture.md` before proceeding


IF human wants to understand something unclear, unexplained, or uncertain
  → SET investigation_path = "understanding"
  → VALID: Continue to Step 1

IF human wants to break a concern into actionable, deliverable work
  → SET investigation_path = "recommendations"
  → VALID: Continue to Step 1

IF intent is unclear or could fit either path
  → ASK: "Investigation intent — understanding the situation, or breaking it into deliverable work?"
  → WAIT for selection
  → SET investigation_path based on answer
  → VALID: Continue to Step 1
```

---

## Step 1: Gather Context

**Do not skip to questions.** Gather context silently first.

### 1.1 Agent Actions (Silent)

```
SCAN codebase:
  - Review areas mentioned by human
  - Search through relevant code structures

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


READ supporting documents:
  - `/midtempo-framework/instructions/purpose.md` # Provides an overview of the goal and capabilities of the service
  - `/midtempo-framework/instructions/architecture.md` # Services architectural structure and design principles

IF investigation involves error handling
  → READ: `/midtempo-framework/instructions/error-handling.md` # Error handling patterns and conventions for the repository

IF investigation involves UI
  → READ: `/midtempo-framework/instructions/frontend-design.md` # Component architecture, composition patterns, and UI organisation
  → READ: `/midtempo-framework/instructions/style-guide.md` # CSS style rules and conventions

IF investigation involves adding a new page
  → READ: `/midtempo-framework/instructions/new-page.md` # How to wire a new page into the UI

```

### 1.2 Present Context Summary

**Output to human:**

```
Context Summary:

Based on analysis:

Areas reviewed:
- [area 1]: [what found]
- [area 2]: [what found]

Relevant documents read:
- [document]: [key points]

Initial observations:
- [observation 1]
- [observation 2]

Does this match your understanding of the situation?
```

**Wait for validation**

**If corrections needed:** Update understanding and re-present

---

## Step 2: Clarify Concern

**Ask one question at a time.** Prefer multiple choice.

### 2.1 Required Questions

**Understanding the concern:**

```
SCAN the user's opening prompt for what they have observed

IF opening prompt describes observations with enough detail to frame an investigation question:
  → Do NOT ask the user to repeat themselves
  → Agent cross-references observations against Step 1 context (silent)

  → Present reflection:

    "Based on what you described and what I found during context gathering:

    What I understand you're seeing: [agent's framing of observed behaviour]
    Related context: [relevant code, docs, or patterns from Step 1]
    Investigation path: [investigation_path] — [one-sentence reason path was set]

    Is this — framing and path — what you want to investigate?"

  IF human confirms → Continue to §2.2 Define Scope
  IF human corrects framing → Revise understanding and re-present
  IF human requests path switch → SET investigation_path = [other path] and re-present

IF opening prompt is vague or partial:
  → Ask ONE focused question based on what is missing:

    IF observations unclear:
      "What behaviour have you observed? (what happens, where, when)"
    IF scope unclear:
      "Which part of the system does this involve? (feature area, component, or workflow)"

  → Wait for answer
  → Agent cross-references against Step 1 context (silent)
  → Present reflection (same format as above)
```

### 2.2 Define Scope

Based on answers, present scope definition:

**Output to human:**

```
Scope Definition:

Investigation name: [kebab-case-identifier]

Investigation path: [investigation_path]

Investigation question: [One-sentence question capturing the concern]

In scope:
- [Component/system 1]
- [Component/system 2]

Out of scope:
- [Explicitly excluded]

Evidence sources to trace:
- Code paths: [files/functions]
- Behaviour: [scenarios to observe]

Supporting documents:
- [document 1] — [why relevant]

Is this scope correct?
```

**Wait for validation**

**If corrections:** Update scope and re-present

**After validation:** CREATE `planning/investigations/[name]-investigation.md` and WRITE:

```markdown
# [Title] Investigation

**Date:** [YYYY-MM-DD]
**Status:** In Progress
**Name:** [kebab-case-name]
**Path:** [investigation_path]

---

## 1. Investigation Question

[Validated question from §2.2]

---

## 2. Scope

**In Scope:**

- [Areas from §2.2]

**Out of Scope:**

- [Exclusions from §2.2]
```

---

## Step 3: Trace Evidence

**Do not speculate.** Trace systematically.

### 3.1 Code Tracing

For each evidence source, trace systematically:

```
TRACE code path:
  1. Entry point — Where does the relevant code path begin?
  2. Data flow — How does data transform through the path?
  3. Decision points — What conditions affect behaviour?
  4. Exit points — Where does the path terminate?

DOCUMENT each trace:

### Trace: [Evidence Source]

**Entry:** `src/path/file.ts:42` — [description]

**Flow:**
1. [Step] at `file.ts:45`
2. [Step] at `other.ts:23`
3. [Step] at `another.ts:88`

**Decision Points:**
- Line 52: [condition] determines [outcome]
- Line 67: [condition] determines [outcome]

**Exit:** `file.ts:95` — [what happens]

**Finding:** [What the trace reveals]
```

### 3.2 Data Investigation

Proceed to "3.3 Behaviour Discovery" - No database in this repo.


### 3.3 Behaviour Discovery

- Run relevant tests to observe behaviour
- Review logs or output
- Trace execution flow


Document observations:

```
### Behaviour: [Scenario]

**Observation:** [What happened]

**Expected:** [What should happen]

**Gap:** [Difference, if any]
```

### 3.4 External Research

**Use external knowledge only when the concern depends on it.**

```
TRIGGER:
  IF concern depends on framework, library, protocol, or vendor semantics
  IF behaviour aligns with known issues, RFCs, or third-party docs
  IF terminology or mechanism is unfamiliar from codebase alone

CHECK-RESOURCES:
  SCAN `planning/assets/` for any curated resource documents relevant to this concern
  IF a relevant resource doc exists → use it as the primary starting point before fetching

FETCH:
  Search authoritative sources (vendor docs, RFCs, official guides)
  CAP: ≤3 sources per concern; each must map to a specific finding
  REJECT: forum posts and blogs unless they corroborate an authoritative source

DOCUMENT each reference:

### Reference: [Source title]

**URL:** https://...
**Authority:** [vendor docs / RFC / official guide / corroborating secondary]

**Excerpt:** [verbatim quote, ≤200 words]

**Finding:** [what this source confirms, contradicts, or clarifies]
```

### 3.5 Present Evidence

**Output to human:**

```
Evidence Gathered:

Code traces:
- [Trace 1]: [finding with file:line references]
- [Trace 2]: [finding with file:line references]

Behaviour observations:
- [Scenario 1]: [observation and gap]
- [Scenario 2]: [observation and gap]

External research:
- [Reference 1]: [authority + finding mapping]
- [Reference 2]: [authority + finding mapping]

All findings backed by evidence — no speculation.

Does this evidence capture the situation?
```

**Wait for validation**

**After validation:** APPEND to `planning/investigations/[name]-investigation.md`:

```markdown
---

## 3. Evidence

### Code Traces

[file:line references and findings from §3.1]

### Data Findings

[query results and implications from §3.2]

### Behaviour Observations

[scenarios, observations, and gaps from §3.3]

### External Research

[references with URL, fetch date, authority, finding mapping from §3.4]

---
```

---

## Step 4: Analyse & Synthesise

**Connect evidence to find patterns and root causes.**

### 4.1 Pattern Recognition

Review evidence and identify:

```
ANALYSE:
  - Patterns — Recurring themes across traces
  - Anomalies — Unexpected behaviour or data
  - Root causes — Underlying reasons for observed behaviour
  - Connections — Links between separate findings
```

### 4.2 Impact Assessment

For each significant finding:

| Finding       | Impact   | Severity               | Affected Areas   |
| ------------- | -------- | ---------------------- | ---------------- |
| [Description] | [Effect] | [blocking/recommended] | [Files/features] |

### 4.3 Present Analysis

**Output to human:**

```
Analysis:

Key discoveries:
1. [Discovery] — Evidence: [file:line or data/behaviour reference]
2. [Discovery] — Evidence: [file:line or data/behaviour reference]

Root causes identified:
- [Cause] — affects [area] because [reason]

Patterns observed:
- [Pattern] — seen in [locations]

Anomalies:
- [Anomaly] — unexpected because [reason]

Impact summary:
- [Blocking issue] — must fix before [work]
- [Recommended action] — improves [aspect]

IF investigation_path == "understanding"
  → "Ready to build understanding?"
IF investigation_path == "recommendations"
  → "Ready to discuss recommendations?"
```

**Wait for validation**

**After validation:** APPEND to `planning/investigations/[name]-investigation.md`:

- §4 Key Findings — discoveries, root causes, patterns, anomalies from the Step 4 output above

---

## Step 5: Propose Recommendations

**Path gate:** Applies when `investigation_path == "recommendations"`.
IF `investigation_path == "understanding"` → SKIP to Step 5U.

**Present proposed recommendations for discussion before writing files.**

### 5.1 Classification

Classify each recommended action:

| Classification    | Criteria                                      | Skill            |
| ----------------- | --------------------------------------------- | ---------------- |
| **Bug**           | Broken behaviour with clear root cause        | bugs.md          |
| **Refinement**     | Small tweak to existing, design exists        | refine.md     |
| **Refactor**      | Restructure existing code, no behaviour change | refactor.md      |
| **Build**    | New capability or significant change          | build.md |
| **Investigation** | Needs evidence, or exceeds build size    | investigate.md   |


#### 5.1.0 Decomposition Principle

Each recommendation MUST be independently actionable — completing it alone produces a working improvement without requiring other recommendations first.

```
IF a recommendation only makes sense when combined with another
  → MERGE them into a single recommendation
  → RE-ASSESS classification against the merged scope

IF merging would exceed Build size limits (§5.1.3)
  → Classify as Investigation (§5.1.4 — decomposition case)

DO NOT split work across recommendations to keep individual sizes small
if the pieces are not independently useful.
```


#### 5.1.1 Refinement criteria

IF original design document does not exist
  → INVALID: STOP - No design doc means no delivered feature. Use build skill for new work.

IF work affects 4+ files
  → INVALID: STOP - Too large for Refine skill. Use Build skill.

IF work adds new UI page
  → INVALID: STOP - New pages require full workflow. Use build skill.

IF work changes database schema (new tables, columns, migrations)
  → INVALID: STOP - Schema changes require full workflow. Use build skill.

IF work introduces new architectural patterns
  → INVALID: STOP - New patterns require full workflow. Use build skill.

IF work has 4+ acceptance criteria
  → INVALID: STOP - Too complex for refine. Use build skill.

IF work is small refinement (≤3 files, ≤3 acceptance criteria, tweaks existing delivered feature)
  → VALID: Use refine skill


#### 5.1.2 Refactor criteria

IF work changes observable behaviour (API contracts, UI output, data formats)
  → INVALID: STOP - Behaviour changes require build skill.

IF work introduces new dependencies or architectural patterns
  → INVALID: STOP - New patterns require build skill.

IF work affects 16+ files
  → INVALID: STOP - Too large for a single refactor. Classify as Investigation.

IF work restructures existing code without changing behaviour (renaming, extracting, reorganising, simplifying)
  → VALID: Use refactor skill


#### 5.1.3 Build criteria

IF work affects 16+ files
  → INVALID: STOP - Too large for a single build. Classify as Investigation.

IF work spans 3+ modules or domains
  → INVALID: STOP - Too large for a single build. Classify as Investigation.

IF work would require an estimated 31+ unit tests
  → INVALID: STOP - Too large for a single build. Classify as Investigation.

IF work introduces 2+ new architectural patterns
  → INVALID: STOP - Too large for a single build. Classify as Investigation.

IF work has 11+ acceptance criteria
  → INVALID: STOP - Too large for a single build. Classify as Investigation.

IF work is a new capability or significant change (≤15 files, ≤2 modules, ≤30 estimated tests, ≤10 acceptance criteria)
  → VALID: Use build skill


#### 5.1.4 Investigation criteria

The work needs a follow-up investigation before actionable recommendations are possible. Two cases trigger this classification:

**Uncertainty:** The sub-area lacks sufficient evidence. A focused investigation must gather evidence and clarify scope before recommending specific work.

**Decomposition:** The work exceeds Build skill size limits. A focused investigation must break it into ordered, build-sized chunks.

Follow-up action: Run a new investigation (`/midtempo-framework/investigate.md`) scoped to the specific need.

The follow-up investigation should produce:
- For uncertainty: evidence gathering, analysis, and actionable recommendations (classified as Bug, Refine, Refactor, or Build)
- For decomposition: one Build recommendation per chunk, with dependency ordering and explicit file/module boundaries


### 5.2 Scope Assessment

For each recommendation:

- **Files affected** — List specific files
- **Estimated tests** — Approximate number of unit tests for the work
- **Modules/domains** — Count of distinct modules or domains touched
- **Complexity** — Low (1-2 files), Medium (3-5 files), High (6+ files)
- **Dependencies** — What must exist or change first
- **Risk** — Low (isolated), Medium (touches shared code), High (affects multiple features)

**Sizing Reference:**

| Signal              | Refine | Refactor | Build | Investigation |
| ------------------- | --------- | -------- | ---------- | ------------- |
| Files affected      | ≤3        | ≤15      | 4–15       | 16+           |
| Estimated tests     | ≤5        | —        | 6–30       | 31+           |
| Modules/domains     | 1         | 1–2      | 1–2        | 3+            |
| New patterns        | None      | None     | ≤1         | 2+            |
| Acceptance criteria | ≤3        | —        | 4–10       | 11+           |

**Classification precedence:**

1. ANY signal exceeding the Build column → Investigation
2. ANY signal exceeding the Refine column → Build (not Refine)
3. ALL signals within Refine column AND §5.1.1 criteria pass → Refine

The §5.1 criteria gates are authoritative. This table is a quick reference — if table and gates disagree, follow the gates.

### 5.2.1 Classification Gate (per recommendation)

For EACH recommendation, complete this checklist before assigning classification:

```
Files affected: [N]
Acceptance criteria: [N]
Estimated tests: [N]
Modules/domains: [N]
New patterns: [N]
Design doc exists: [yes/no]

APPLY §5.1 criteria in order:
  §5.1.1 Refinement: [VALID/INVALID — which rule?]
  §5.1.2 Refactor: [VALID/INVALID — which rule?]
  §5.1.3 Build: [VALID/INVALID — which rule?]
  §5.1.4 Investigation: [VALID/INVALID — which rule?]

APPLY §5.2 precedence:
  Highest signal column: [Refine/Build/Investigation]

Classification: [result]
```

IF classification from §5.1 gates conflicts with §5.2 precedence
  → Use the higher classification (Investigation > Build > Refine)

### 5.3 Priority Ordering

Order recommendations by:

1. **Blocking issues** — Must fix before other work
2. **Dependencies** — Required by other recommendations
3. **Impact** — Higher impact first
4. **Effort** — Lower effort preferred when impact equal

### 5.4 Present Proposals

**Output to human:**

```
Proposed Recommendations:

Based on the analysis, I propose the following actions:

| # | Title | Classification | Est. Tests | Modules | Files | Risk |
|---|-------|---------------|------------|---------|-------|------|
| 1 | [Title] | [Classification] | [N] | [N] | [N] | [Low/Med/High] |
| 2 | [Title] | [Classification] | [N] | [N] | [N] | [Low/Med/High] |

Detail per recommendation:

1. [Title] (Classification: [Classification])
   What: [One-sentence description of what needs to happen]
   Why: [Key finding/evidence that drives this recommendation]
   Scope: [Files/areas affected], [N] estimated tests, [N] modules
   Risk: [Low/Medium/High] — [brief justification]
   Dependencies: [Other recommendations or "None"]

2. [Title] (Classification: [Classification])
   ...

Questions for discussion:
- Should any recommendations be added, removed, or merged?
- Do the classifications feel right?
- Is the priority ordering correct?
```

**Wait for human's response**

### 5.5 Refine Proposals

```
IF human suggests changes:
  → UPDATE proposals based on feedback
  → RE-PRESENT updated proposal table and detail
  → WAIT for validation
  → REPEAT until human approves

IF human approves:
  → VALID: Continue to Step 6 (Write Recommendations)
```

---

## Step 5U: Synthesise Understanding

**Path gate:** Applies when `investigation_path == "understanding"`.
IF `investigation_path == "recommendations"` → use Step 5 above.

**Build the four-part synthesis from the evidence and analysis.**

### 5U.1 Mechanism

Construct the cause-effect chain that explains the observed behaviour.

```
FOR EACH link in the chain:
  - Trigger — file:line, data point, or external reference (§3.1, §3.3, §3.4)
  - Transformation — what happens at this link
  - Output — what the next link receives
  - Evidence — citation for this link

DOCUMENT:

### Link [N]: [Step name]

**Trigger:** `file:line` or `Reference: [source]`
**Transformation:** [what happens]
**Output:** [what's produced]
**Evidence:** [§3.1 trace / §3.3 observation / §3.4 reference]
```

### 5U.2 Current State

State what is observably happening now, with evidence.

```
DOCUMENT:

### Current State

**Behaviour:** [specific behaviour with file:line evidence]
**Effects:** [what the user/system experiences]
**Conditions present:** [what is currently true that drives this behaviour]
```

### 5U.3 What Could Happen

For each significant condition, state the conditional outcome.

```
DOCUMENT (one row per scenario):

| Condition       | Outcome           | Evidence              | Likelihood     |
| --------------- | ----------------- | --------------------- | -------------- |
| [If X happens]  | [Then Y follows]  | [§3.x reference]      | [Low/Med/High] |
```

### 5U.4 Glossary

For each unfamiliar term encountered (especially from external research):

```
DOCUMENT:

**[Term]** — [definition ≤25 words]
Source: [reference path or file:line]
```

### 5U.5 Present Synthesis

**Output to human:**

```
Synthesis:

Mechanism ([N] links):
- Link 1 → Link 2 → Link 3 — [one-line summary chain]

Current State:
- [Behaviour] — [evidence]

What Could Happen:
| Condition | Outcome | Likelihood |
|-----------|---------|------------|
| [...]     | [...]   | [...]      |

Glossary: [N terms defined]

Ready to write the understanding report?
```

**Wait for validation**

```
IF human suggests changes:
  → UPDATE synthesis based on feedback
  → RE-PRESENT
  → WAIT for validation
  → REPEAT until human approves

IF human approves:
  → VALID: Continue to Step 6U (Write Understanding Report)
```

---

## Step 6: Write Recommendations

**Path gate:** Applies when `investigation_path == "recommendations"`.
IF `investigation_path == "understanding"` → SKIP to Step 6U.

**Present each recommendation separately. Wait for validation before writing.**

### 6.1 Recommendation File Template

**File naming:** `planning/investigations/[name]-rec-[n]-[slug].md`
- `[name]` — Investigation name from Step 2
- `[n]` — Priority number (1, 2, 3...)
- `[slug]` — Short kebab-case description

**Template:**

```markdown
# Recommendation: [Title]

**Source:** Investigation `[name]` ([date])
**Classification:** [Bug | Build | Refine | Refactor | Investigation]
**Priority:** [N] of [Total]
**Skill:** `/midtempo-framework/[bugs|build|refine|refactor|investigate].md`

---

## Context

**Investigation Question:** [Original validated question]

**Key Finding:** [The specific finding that led to this recommendation]

**Evidence:**

- [Specific evidence point with file:line references]
- [Specific evidence point with data/behaviour observations]
- [Specific evidence point]

---

## Task

[Clear statement of what needs to happen]

---

## Scope

| Aspect          | Assessment               |
| --------------- | ------------------------ |
| Files           | [List of affected files] |
| Estimated tests | [N]                      |
| Modules/domains | [N]                      |
| Complexity      | [Low/Medium/High]        |
| Dependencies    | [List or "None"]         |
| Risk            | [Low/Medium/High]        |

---

## Acceptance Criteria

- [ ] [Measurable criterion]
- [ ] [Measurable criterion]
- [ ] [Measurable criterion]

---

## Reference

Full investigation: `planning/investigations/[name]-investigation.md`
```

### 6.2 Sequential Recommendation Approval

Present each recommendation separately in priority order. Ask: "Does this recommendation look right?" before writing.

**For each recommendation:**

- Present the full recommendation content following the §6.1 template
- Ask: "Does this recommendation look right?"
- **After validation:** Write to `planning/investigations/[name]-rec-[n]-[slug].md`

<CRITICAL_REQUIREMENT type="MANDATORY">

Write ONE recommendation file at a time. Do NOT batch-write multiple files — long-running writes cause network failures.

</CRITICAL_REQUIREMENT>

**If human asks clarifying questions:** Re-present the recommendation with updates based on any new understanding. Explain what changed and why.

WAIT for human validation before proceeding

Verify recommendation matches agreed proposal from Step 5
IF human approves
  → VALID: Write to `planning/investigations/[name]-rec-[n]-[slug].md` and present next recommendation
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

AFTER all recommendations written:
  → Continue to Step 7

---

## Step 6U: Write Understanding Report

**Path gate:** Applies when `investigation_path == "understanding"`.
IF `investigation_path == "recommendations"` → use Step 6 above.

WRITE the validated synthesis from Step 5U to `planning/investigations/[name]-understanding.md`:

```markdown
# [Title] Understanding

**Source:** Investigation `[name]` ([date])
**Investigation Question:** [Original validated question from §2.2]

---

## 1. Mechanism

[Cause-effect chain from §5U.1 — one ### Link per step, with file:line and reference citations]

---

## 2. Current State

[Observable behaviour from §5U.2 — Behaviour / Effects / Conditions present]

---

## 3. What Could Happen

[Conditional outcomes table from §5U.3]

---

## 4. Glossary

[Term definitions from §5U.4]

---

## Reference

Full investigation: `planning/investigations/[name]-investigation.md`
```

AFTER write:
  DECLARE to human: "Wrote understanding report to `planning/investigations/[name]-understanding.md`."
  → Continue to Step 7

---

## Step 7: Write Investigation Report

**Complete the investigation report at `planning/investigations/[name]-investigation.md`.**

The report already contains §1–§3 from earlier steps. APPEND the remaining sections and update the status.

APPEND to `planning/investigations/[name]-investigation.md`:

IF investigation_path == "recommendations":

```markdown

---

## 5. Recommendations

| Priority | Title   | Classification | File                     |
| -------- | ------- | -------------- | ------------------------ |
| 1        | [Title] | [Classification] | `[name]-rec-1-[slug].md` |
| 2        | [Title] | [Classification] | `[name]-rec-2-[slug].md` |

Full detail in each recommendation file.

---

## 6. Next Steps

Start follow-up work by opening the relevant recommendation file and using it as context for a new conversation with the appropriate skill.

---
```

IF investigation_path == "understanding":

```markdown

---

## 5. Understanding Report

Full understanding: `planning/investigations/[name]-understanding.md`

Sections:
- Mechanism — [one-sentence summary]
- Current State — [one-sentence summary]
- What Could Happen — [one-sentence summary]
- Glossary — [N terms]

---

## 6. Next Steps

Use the understanding report as context for further conversations. If actionable work follows, run a new investigation with `investigation_path = "recommendations"`.

---
```

UPDATE the file header: change `**Status:** In Progress` to `**Status:** Complete`.

DECLARE to human: "Updated `planning/investigations/[name]-investigation.md` — appended §5 and §6, status set to Complete."

---

## Investigation Complete

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output after investigation completes - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
</CRITICAL_REQUIREMENT>

```
---
                     INVESTIGATION COMPLETE: [NAME]

---

Investigation Question:
[Original validated question]

Key Findings:
- [Finding 1] — [Evidence reference]
- [Finding 2] — [Evidence reference]

Root Causes:
- [Cause] — affects [area]

Files Created:

  Investigation Report:
    `planning/investigations/[name]-investigation.md`
```

THEN APPEND, IF investigation_path == "recommendations":

```
  Recommendation Reports:
    `planning/investigations/[name]-rec-1-[slug].md` — [Title] ([Classification])
    `planning/investigations/[name]-rec-2-[slug].md` — [Title] ([Classification])

Recommendations Summary:

| Priority | Title | Classification | Est. Tests | Modules | Risk |
|----------|-------|----------------|------------|---------|------|
| 1 | [Title] | [Classification] | [N] | [N] | [Low/Med/High] |
| 2 | [Title] | [Classification] | [N] | [N] | [Low/Med/High] |

---
Start follow-up work by opening the first recommendation file and using it
as context for a new conversation with the appropriate skill.

---
```

THEN APPEND, IF investigation_path == "understanding":

```
  Understanding Report:
    `planning/investigations/[name]-understanding.md`

Understanding Summary:

| Section            | Key takeaway              |
|--------------------|---------------------------|
| Mechanism          | [one-sentence summary]    |
| Current State      | [one-sentence summary]    |
| What Could Happen  | [one-sentence summary]    |
| Glossary           | [N terms]                 |

---
Open the understanding report for the full context. If actionable work follows,
run a new investigation with `investigation_path = "recommendations"`.

---
```

---

## Anti-Patterns

### Anti-Pattern 1: Speculation Without Evidence

**INVALID:**

```
"This probably happens because..."
"I think the issue might be..."
```

**VALID:** Trace code paths. Query data. Observe behaviour. State findings with evidence.

### Anti-Pattern 2: Vague Recommendations

**INVALID:**

```
"Consider improving error handling"
"Look into the performance"
```

**VALID:** "Fix timeout handling in `src/api/fetch.ts:42` — trace shows 5-second timeout causes silent failures. Classification: Bug."

### Anti-Pattern 3: Symptom Focus

**INVALID:** Document surface-level observations without tracing to root causes.

**VALID:** Follow the trace backward until you find the original trigger. Document the chain.

### Anti-Pattern 4: Jumping Steps

**INVALID:**

```
Step 1 complete → Jump to Step 5 (proposals)
Step 2 complete → Jump to Step 7 (investigation report)
Ask questions → Write recommendations without gathering evidence
Step 4 complete → Jump to Step 6 (write files) without proposing first
```

**VALID:** Complete steps in order — 1 → 2 → 3 → 4 → (5 OR 5U) → (6 OR 6U) → 7. Path is committed in the entry gate; do not switch paths mid-investigation.

---
**END OF DOCUMENT:** Total sections: 7 | Purpose: Deep discovery and actionable recommendations