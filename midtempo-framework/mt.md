# Mutation Testing — Pre-Triage (mt.md)

**Operating pattern:** diff-scoped + incremental + filtered.
**Skill scope:** Pre-triage only — define scope, run the mutation command, capture results, equivalent pre-pass, cluster by enclosing function, sort by severity-prior. Hands off to `mt-fix.md` for triage + inline fix + ratchet + complete.

**Companion skill:** `/midtempo-framework/mt-fix.md` (triage + fix + ratchet + complete).

---

## Overview

This skill runs the **pre-triage** half of an MT session:

1. Human picks scope.
2. Skill writes the session file + runs the mutation command.
3. Human returns when the run completes; skill captures results.
4. Equivalent pre-pass (lightweight per-mutant equivalence check; bulk-accept prompt with borderline list).
5. Cluster non-equivalents by enclosing function.
6. Severity-prior sort + Current Batch pointer init.
7. Exit with `Status: ready-for-triage` and a hand-off line directing the human to invoke `mt-fix.md` in a new conversation.

No per-cluster analysis, no inline fixes, no manifest writes — those live in `mt-fix.md`.

**Outputs:**

- `planning/mt-session.md` populated up to `Status: ready-for-triage`
- Human-visible progress lines between sub-steps
- A hand-off line at exit

**Not produced by this skill:**

- Changes to production code, test code, mutation-tool configuration, package manifests, or CI configuration
- Manifest entries (`mt-fix.md` writes those when a production bug is pushed)
- Ratchet verdict (Step 7 in `mt-fix.md`)

---

## Table of Contents

- [Non-Negotiable Rules](#non-negotiable-rules)
- [Entry Gate](#entry-gate)
- [Step 1 — Kickoff: Ask Scope Question](#step-1--kickoff-ask-scope-question)
- [Step 2 — Kickoff: Confirm Resolved Scope](#step-2--kickoff-confirm-resolved-scope)
- [Step 3 — Kickoff: Write Session + Run Command](#step-3--kickoff-write-session--run-command)
- [Step 4 — Run Completion + Capture](#step-4--run-completion--capture)
- [Step 5 — Pre-Triage: Stub Load + Pre-pass + Cluster + Sort](#step-5--pre-triage-stub-load--pre-pass--cluster--sort)
- [Session File Template](#session-file-template)
- [Severity-prior Heuristic](#severity-prior-heuristic)
- [Quick Reference](#quick-reference)

---

## Non-Negotiable Rules

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST NOT change production code, test code, mutation-tool configuration, package manifests, or CI configuration in this skill. Test edits and manifest writes are `mt-fix.md`'s responsibility.
- You MUST process every Step-5 sub-step as `Read → think → Edit → next` loops on disk. Each sub-step (5.2 pre-pass / 5.4 clustering / 5.5 sort) iterates one mutant or one cluster at a time, writing back to `planning/mt-session.md` before advancing. Step 5.0 stub load exception: write at most twice — once per ~50-mutant chunk if the report is large, or once total. Conversation context holds AT MOST one mutant or cluster block during a loop. Never hold the full surviving-mutant list in reasoning context.
- You MUST emit exactly ONE progress line to the human after each sub-step. Progress lines are counts-only surface narration; they do NOT contain prompts and they do NOT wait for input. Human can stop the conversation at any progress line; resume reads the session file.
- You MUST NOT recount, re-cluster, or re-sort silently after writing. Compute once, write once. If the count or cluster boundary is wrong, the human catches it at the equivalent-batch prompt (5.3) or at first Stage 2 cluster presentation in `mt-fix.md`; `review` and `split` are the human's correction paths.
- You MUST run the equivalent pre-pass (Step 5.2) BEFORE clustering. The lightweight 5-line check applies at mutant level for mutator-weight ≤ 2. The check produces THREE values — `yes` (likely-equivalent), `borderline` (rationale non-trivial; defer to human), `no` (carry to clustering). Borderlines surface in the 5.3 prompt as a separate list — agent never resolves borderlines alone.
- You MUST cluster non-equivalent mutants by enclosing function (Step 5.4): same file + same enclosing function. Different mutators on the same line cluster. Distant lines in the same function cluster. Fall back to ±10 lines + same mutator family, then to same line, then to singleton — in that order — when enclosing-function extraction fails. Each cluster has a HEAD and zero or more LINKED members; downstream analysis (in `mt-fix.md`) runs on the head only; linked members inherit.
- You MUST compute the Severity-prior heuristic (Step 5.5) and write the `## Current Batch` pointer at the top of the session file. Files are sorted by max cluster prior, descending.
- You MUST run only the exact commands `npm run mutate:diff`, `npm run mutate:targeted -- "<paths>"`, and `npm run mutate`. The path arguments are human-supplied or session-resolved scope data, not agent-invented flags.
- You MUST update `## Status` at every transition (Step 3 → running; Step 4 → captured; Step 5.6 → ready-for-triage).
- You MUST NOT continue into triage in this conversation. After Step 5.6 emits the handoff, STOP.
- You MUST NOT use "[enter] to accept" or any keystroke-based convention. Every confirmation prompt uses explicit polarity: `yes` accepts, typing an override changes the proposed value.

</CRITICAL_REQUIREMENT>

---

## Entry Gate

State drives mode. Reads are **targeted by section** — do NOT load `## Surviving Mutants` in full at the gate.

```
TARGETED READ planning/mt-session.md sections `## Status` and `## Current Batch`
  (file may not exist — that is fresh-start)

IF file does not exist
  → State: fresh-start
  → GOTO Step 1 (Kickoff: Ask Scope Question)

ELSE read the `## Status` field

  IF Status: kickoff
    → GOTO Step 3 (Kickoff: Write Session + Run Command)

  IF Status: running
    → TARGETED READ the `## Run Results` section only
    IF Run Results is populated (has a non-empty `Mutation score:` line)
      → Auto-promote Status → captured (write the file)
      → Emit: "Run results captured — proceeding to pre-triage."
      → TARGETED READ the first mutant stub from `## Surviving Mutants`
      IF `Severity-prior:` field present     → GOTO Step 5.5
      IF `Cluster head:` field present       → GOTO Step 5.4
      IF `Likely-equivalent:` not `unset`    → GOTO Step 5.2
      ELSE                                   → GOTO Step 5.1
    ELSE
      → GOTO Step 4 recovery branch (wait | declare-crashed)

  IF Status: captured
    → TARGETED READ `## Run Results` (Survived count) and first stub from `## Surviving Mutants`
    IF stubs exist → Emit: "Resuming pre-triage — <N> mutants in session file."
    IF `Severity-prior:` field present     → GOTO Step 5.5
    IF `Cluster head:` field present       → GOTO Step 5.4
    IF `Likely-equivalent:` not `unset`    → GOTO Step 5.2
    ELSE                                   → GOTO Step 5.1

  IF Status: ready-for-triage | triage-in-progress | triage-complete
    → REDIRECT — emit one line and STOP:

      "Session has already finished pre-triage (Status: <status>).
       Continue in a new conversation with:
         Run mutation testing using /midtempo-framework/mt-fix.md"
```

---

## Step 1 — Kickoff: Ask Scope Question

**Goal:** Get the human's scope intent in one prompt, then load only what they name. No broad scanning.

### 1.1 Ask Scope question

```
Select mutation testing scope:

1. Design doc        Mutates production code in modules named by a design
                     doc. Reply `1 <path>` (e.g. `1 planning/foo-design.md`).

2. Changed files     Mutates production code in current git changes (staged
                     + unstaged in the working tree). Reply `2`.

3. Branch            Mutates production code changed on the current branch
                     vs `main`. Reply `3`.

4. Test-path pattern Mutates production code covered by test files matching
                     a glob. Reply `4 <glob>` (e.g. `4 tests/api/**`).

{ IF planning/archive/mt-session-*.md exists }
5. Since last MT     Mutates production code changed since the previous MT
                     session (uses the stored previous SHA). Reply `5`.
{ ENDIF — hide on first session }
```

WAIT for the human's reply. Validate the form; if `1` or `4` is supplied without the required argument, prompt once for the argument and retry.

### 1.2 Narrow reads (silent — targeted sections only)

```
IF choice = 1 (Design doc)
  IF the named design doc does not exist → STOP: "Design doc not found at <path>. Correct the path and retry."
  → TARGETED READ the named design doc:
      - Table of Contents (always — small)
      - § "3. Architecture & Data" only — used for module list + file mapping
      - Do NOT read §1 Problem, §2 Solution, §4 UX, §5 Constraints at this stage.
        `mt-fix.md` Step 2 loads the section covering the cluster's file on demand.
  → Look for the paired test manifest: same basename, `-tests.md` suffix.
    IF present:
      - TARGETED READ its Table of Contents only.
      - Capture the file→behaviour index (which behaviours name which production
        files). `mt-fix.md` Step 2 loads specific behaviours on demand.

(Choices 2, 3, 4, 5 do not load a design doc or test manifest. `mt-fix.md`'s
triage defaults to test-gap classification on SPEC-SILENT mutants.)

ALWAYS:
- TARGETED READ planning/mt-fix-manifest.md `## Open` section:
  - The count
  - Per-entry metadata only: MT-ID + `Cluster head:` file:line + `Cluster
    members:` list + `Classification:`. (Do NOT load full bodies.)
- TARGETED READ the most recent planning/archive/mt-session-*.md:
  ONLY the `## Kickoff` and `## Ratchet Verdict` sections — extract the
  last "Resolved diff:" SHA and the last "Effective score:".
  IF no archive file exists → Previous SHA: none; Previous-session score: none (first session).
```

### Step 1 exit criteria

Scope choice captured (one of 1-5); for choice 1, named design doc + paired test manifest loaded (or paired manifest = "none"); fix-manifest Open-count loaded; previous SHA + previous-session score loaded (or `none — first session`).

---

## Step 2 — Kickoff: Confirm Resolved Scope

**HUMAN DECISION REQUIRED.** Step 1's answers resolve the scope; Step 2 verifies the resolution before write.

### 2.1 Resolve

```
Scope type derived from Step 1 choice:
  1 (Design doc)        → paths from design doc §3 stated modules
                          command = npm run mutate:targeted -- "<paths>"
  2 (Changed files)     → paths from `git diff HEAD --name-only` plus
                          `git diff --staged --name-only`
                          command = npm run mutate:targeted -- "<paths>"
  3 (Branch)            → range = main..HEAD
                          command = mutate_diff
  4 (Test-path pattern) → resolve test files matching the glob; for each,
                          strip the test suffix/directory to derive the
                          production path (e.g. foo.test.<ext> → foo.<ext>,
                          tests/foo.<ext> → src/foo.<ext>); note ambiguous
                          derivations.
                          command = npm run mutate:targeted -- "<paths>"
  5 (Since last MT)     → range = <previous-SHA>..HEAD
                          command = mutate_diff
```

### 2.2 Present the resolved scope

```
SCOPE CONFIRMATION

Choice:                  <1 | 2 | 3 | 4 | 5> — <one-line restatement>
Design doc:              <path or "none — choice does not load one">
Test manifest:           <path or "none — choice does not load one">
Previous session SHA:    <SHA or "none">
Previous-session score:  <X% or "none">
Fix-manifest open count: <N or 0>  (unresolved items from prior sessions — reviewed during mt-fix.md triage)

Resolved scope:
  Detail:  <range or paths string>
  Command: <npm run mutate:diff | npm run mutate:targeted -- "<paths>" | npm run mutate>

Confirm?
  yes                  accept the resolved scope
  back                 return to Step 1.1 (change scope choice)
  rebaseline           force `npm run mutate` (full-suite run; ignores resolved scope paths — use to regenerate a complete baseline)
```

WAIT for the human's response.

### Step 2 exit criteria

Resolved scope confirmed (type, detail, command); no precondition/wiring change requested.

---

## Step 3 — Kickoff: Write Session + Run Command

### 3.1 Write the session file

READ `/midtempo-framework/templates/mt-session.md` (field definitions, section ordering, state enum, ID conventions) before writing.

IF `planning/mt-session.md` exists AND `## Kickoff` is already populated (re-kickoff after crash)
  → Update `## Status: kickoff`; preserve existing Kickoff data; proceed to Step 3.2.

Use the [Session File Template](#session-file-template). Populate Kickoff from Step 1 + Step 2 (include the design doc path AND the test manifest path; both are referenced during `mt-fix.md`'s triage).

Status starts as `kickoff`; Run Results is left empty.

Write `planning/mt-session.md` to disk immediately.

### 3.2 Set Status: running

Update `## Status` from `kickoff` to `running`. Write the file again.

### 3.3 Invoke the run

Run exactly one of:

```
npm run mutate:diff                     # default — diff against resolved range
npm run mutate:targeted -- "<paths>"    # path-filter mode
npm run mutate                          # re-baseline only (explicit re-baseline)
```

The exact command was decided in Step 2 and recorded in the session file's `Command:` line. Do not vary it here.

> **Runtime budget.** Starting point: **2 hours** on a representative scope (~10 changed files). If the run exceeds the budget, the recovery branch in Step 4 fires.

The skill does not run the command in the background or attach to its output. Before exiting, emit:

  "Session file written. Mutation run started. Exit and re-invoke mt.md once the run completes."

Exit the Claude Code session — the human returns later and re-invokes mt.md. The Entry Gate's state machine routes them to Step 4.

### 3.4 Recovery on invocation failure

```
IF the command fails to start (non-zero exit before mutation starts)
  → Status remains `running` in the file (do not auto-rewind)
  → Output: "Run failed to start. Edit `## Status` to `kickoff` to re-attempt,
            or delete the file to reset to fresh-start. See command output above."
  → STOP
```

### Step 3 exit criteria

Session file written with Kickoff populated (design-doc path + test-manifest path included); Status: running; exact command from Step 2 invoked.

---

## Step 4 — Run Completion + Capture

The human re-invokes the skill after the run. Entry Gate routes here when Status: running.

### 4.1 Check completion

```
READ `## Run Results` section in `planning/mt-session.md`

IF the section is empty (no `Mutation score:` line)
  → GOTO 4.2 Recovery
IF the section is populated
  → Auto-promote Status → captured
  → GOTO Step 5
```

The mutation tool is expected to populate Run Results on completion via the human's pre-configured post-run hook. If the hook is not wired, the human pastes the score and surviving-mutant list manually before re-invoking.

### 4.2 Recovery — HUMAN DECISION REQUIRED

TARGETED READ `## Kickoff` from `planning/mt-session.md` to extract scope choice, resolved detail, and command.

Present:

```
RUN STATUS UNCERTAIN

Status: running
Run Results: empty (no Mutation score recorded)
Time since kickoff: <delta>
Prior scope (choice <N>): <resolved detail>
Prior command: <command>

Action options:
  wait     exit without changes; re-invoke later
  crashed  declare run dead. Sub-options:
             r  re-kickoff with the same scope
             n  re-kickoff with a narrower scope (return to Step 1)
             x  abandon session — type `confirm-delete` at the next prompt to confirm

Confirm choice (type `wait` or `crashed r`/`crashed n`/`crashed x`):
```

WAIT. The `wait` option exits the skill without modifying the file.

For `crashed`, update `## Status` accordingly:

- `r` → reset Status to `kickoff`; Emit: "Resetting to kickoff — re-entering Step 3 with same scope."; re-enter Step 3
- `n` → discard the file; re-enter Step 1
- `x` → Prompt: "Type `confirm-delete` to delete `planning/mt-session.md` and reset to fresh-start,
         or any other input to cancel."
         WAIT for response.
         IF `confirm-delete` → delete the file; STOP
         ELSE → return to the Step 4.2 prompt

### Step 4 exit criteria

Either Run Results populated and Status: captured (continue to Step 5), or human chose `wait`, or human chose `crashed` + sub-action.

---

## Step 5 — Pre-Triage: Stub Load + Pre-pass + Cluster + Sort

Entry condition: `Status: captured`.

**Discipline (applies to every sub-step):**

- **Disk is the work primitive.** Each sub-step is a `Read → think → Edit → next` loop, processing one mutant or one cluster at a time.
- **One progress emission per sub-step.** Counts only; no prompts mid-sub-step.
- **Compute once, write once.** No silent recounting or re-sorting.

### 5.1 Stub load — read mutation report → write per-mutant stubs

```
1. Read `reports/mutation.json` (mutation-tool output) if present;
   fall back to the human-supplied per-file Survived/NoCoverage
   list from Step 4's Run Results.
2. For each surviving mutant, append a STUB block to `## Surviving Mutants`
   in planning/mt-session.md:

   ### M<N> — <file:line>
   - Mutator: <kind>
   - Original: `<code>`
   - Mutated:  `<code>`
   - Likely-equivalent: unset
   - Classification: unclassified
   - Action: unset

   Write the file at most twice during this sub-step — once per ~50-mutant
   chunk if the report is large, or once total. Do NOT analyse, classify,
   or cluster yet — stubs only.

3. Progress (one line):

   "Loaded <N> mutants into planning/mt-session.md"
```

### 5.2 Equivalent pre-pass — per-mutant loop on disk

For mutants with mutator-weight ≤ 2 (block-removal, string-literal, other), apply a lightweight equivalence check. Mutator-weight ≥ 3 (boundary, conditional, logical) skips this sub-step — they almost always carry semantic weight.

```
FOR EACH mutant M with mutator-weight ≤ 2 (one at a time):

  1. Read M's stub block from planning/mt-session.md (one block).
  2. Read 5 lines around M's <file:line> in the production file.
     (No design doc; no test manifest.)
  3. Classify equivalence (three values, NOT two):

     LIKELY-EQUIVALENT — confidently yes, bulk-accept candidate:
       - Mutated branch unreachable from surrounding control flow
       - Mutated variable unused, or used only inside a log/console call
       - Removed line was a pure log/console/print statement
       - String-literal in a constant that has no comparator upstream

     BORDERLINE — agent declines to classify alone:
       - Value is written to a file or persisted (even if no test covers
         the path)
       - Return value flows to a comparator but the literal never matches
         (you'd have to assert it really never matches)
       - Removed line both logs AND mutates state
       - Any other case where the rationale is "probably equivalent but
         the assumption is non-trivial"

     NOT-EQUIVALENT — fall through to clustering (default for anything
     not matching the two patterns above).

  4. Edit M's stub block — set Likely-equivalent: <yes|borderline|no>
     and (if yes or borderline) add a one-line `Lightweight rationale:`.

  5. Continue to the next mutant.

Progress (one line):

  "Pre-pass: <N> likely-equivalent / <B> borderline / <K> carrying to clustering"
```

### 5.3 Equivalent-batch prompt — surface bulk + borderlines

Read each Likely-equivalent and Borderline mutant block from the session file (targeted reads) and present once:

```
EQUIVALENT-BATCH PRE-PASS

Clear equivalents (lightweight rationale shown — bulk-accept candidates):
  <path>/logger.<ext>:42          M3    log-line removal
  <path>/format.<ext>:88,89,91    M12, M13, M14   string-literal in non-asserted constant
  <path>/cache.<ext>:155          M27   unused-var assignment
  …
  Total: <N> mutants

Borderline (human decides — pre-pass declines to bulk-classify):
  <path>/fileWriter.<ext>:161  M36
    "unknown" → "" in writeErrorToFile — observable file content, but
    no test coverage on this path
  <path>/fileWriter.<ext>:83   M27
    return "" → "<marker>" — compared against an expected value upstream;
    neither matches, so behaviour identical IF the comparison is the only
    consumer
  …
  Total: <B> mutants

Bulk-accept the clear equivalents?
  yes                       accept all clear; borderlines carry forward
                            to triage in mt-fix.md (flagged)
  yes-all                   accept clear AND borderlines as equivalent
                            (use only if you reviewed the borderlines)
  review                    bring all (clear + borderline) into normal
                            clustering instead
  split M<id> M<id>         accept the remaining clear equivalents; the listed
                            mutants go to clustering; borderlines continue
                            per yes/yes-all
```

WAIT for the human's reply.

On `yes` / `yes-all`: for each accepted mutant, Edit its session-file block to set Classification: equivalent mutant, Action: recorded, rename `Lightweight rationale:` to `Rationale:` (in-place field rename). Each accepted mutant becomes a singleton cluster.

For Borderlines NOT accepted by `yes-all`: loop them into 5.4 (clustering) treated as NOT-EQUIVALENT, but the `Likely-equivalent: borderline` field persists so `mt-fix.md`'s 5.3 presentation can surface the borderline flag.

On `review`: for each clear-equivalent mutant (those with `Likely-equivalent: yes`), reset the field to `Likely-equivalent: no` before entering clustering at Step 5.4. Borderlines carry forward unchanged.

Progress:

  "Equivalents recorded: <N> bulk-accepted, <B> borderlines carried forward, <K> non-equivalents going to clustering"

### 5.4 Clustering — per-file loop on disk

Group non-equivalent mutants into clusters by file + enclosing function.

```
FOR EACH FILE with non-equivalent mutants:

  1. Read all of this file's non-equivalent mutant stubs from
     planning/mt-session.md (targeted file read, just these blocks).
  2. For each block, extract the enclosing function by reading backward
     from the mutant's line in the production file until you hit a
     function declaration. Cache the read — one production-file open
     per file batch.
  3. Group blocks by enclosing function. Apply fallbacks in order when
     extraction is ambiguous:
       a. Same file AND line difference ≤ 10 AND same mutator family
          (comparison: boundary + conditional; boolean: logical;
           structural: block-removal + string-literal + other)
       b. Same file AND same line (different mutators)
       c. Singleton
  4. For each cluster, pick the HEAD (lowest M-ID); LINKED = rest.
  5. Edit each mutant block to add:
       Cluster head:        M<head-id>
       Enclosing function:  <name | "(fallback <a|b|c>)">     (head only)
       Cluster members:     M<head-id>, M<id>, …               (head only)
       Linked to:           M<head-id>                         (linked only)

Progress (one line):

  "Clustering: <C> clusters across <F> files (avg <X> members/cluster)"
```

### 5.5 Severity-prior + Current Batch pointer — per-cluster loop on disk

```
FOR EACH cluster HEAD:

  1. Read the head's block (one block; mutator + file path are enough).
  2. Compute Severity-prior from the rules table (see Severity-prior
     Heuristic below) — no file reads, no LLM.
  3. Edit the head's block to add `Severity-prior: <N>`.

THEN:

4. Group clusters by file; compute file-level Severity-prior = max
   cluster prior per file.
5. Sort files by file Severity-prior descending; tie-break by lowest
   head M-ID.
6. Initialise `## Current Batch` at the top of the session file:

   ## Current Batch
   Next: <file path>   (<N> unclassified clusters)
   Progress: 0 of <total> files classified
     Equivalents pre-accepted: <N> mutants
     Borderlines flagged for triage: <B> mutants
     Total clusters: <N>     (non-equivalent)
   Remaining files (file-prior desc):
     <file path>  (<N> clusters, max prior <N>)
     <file path>  (<N> clusters, max prior <N>)
     …

Progress (one line):

  "Sort complete; Current Batch initialised — <C> clusters across <F> files ready for triage"
```

### 5.6 Pre-triage complete — promote Status, exit, hand off

```
1. Set `## Status: ready-for-triage` in the session file.
2. Emit the handoff message:
```

```
═══════════════════════════════════════════════════════════════════════════════
                    PRE-TRIAGE COMPLETE — READY FOR mt-fix.md
═══════════════════════════════════════════════════════════════════════════════

Run scope: <scope summary>
Total mutants: <N>
  Likely-equivalents pre-accepted: <N>  (from 5.3 batch)
  Borderlines flagged for triage:  <B>  (human chose not to bulk-accept)
  Non-equivalents going to triage: <K>

Clusters: <C> across <F> files (heuristic order — file-prior desc):
  <file path>  (<N> clusters, max prior <N>)
  <file path>  (<N> clusters, max prior <N>)
  …

Status: ready-for-triage
Session file: planning/mt-session.md

───────────────────────────────────────────────────────────────────────────────
Start triage in a new conversation with:

  Run mutation testing using /midtempo-framework/mt-fix.md

mt-fix.md detects Status: ready-for-triage and resumes at the first file batch.
Triage can be done in one session (if context allows) or across multiple
sessions — the Current Batch pointer is the resume signal.
───────────────────────────────────────────────────────────────────────────────
```

Then STOP. Do not continue into triage in this conversation.

### Step 5 exit criteria

`## Surviving Mutants` populated with stub + clustering + severity-prior fields for every surviving mutant; `## Current Batch` written; Status: ready-for-triage; handoff line emitted.

---

## Session File Template

`planning/mt-session.md` is the primary data structure shared with `mt-fix.md`. Both skills target sections; neither loads the whole file.

**Schema:** see [`/midtempo-framework/templates/mt-session.md`](templates/mt-session.md). The template is authoritative for field definitions, section ordering, state enum, ID conventions, and human manual-edit rules.

**Sections this skill (mt.md) writes:**

| Section | Step | What lands |
|---|---|---|
| `## Status` | 3.2, 4.1, 5.6 | `kickoff` → `running` → `captured` → `ready-for-triage` |
| `## Current Batch` | 5.5 | Init: Next file, Remaining files (file-prior desc), Equivalents pre-accepted count, Borderlines count |
| `## Kickoff` | 3.1 | Scope choice, resolved diff, source design doc + test manifest paths, previous SHA + score, command |
| `## Run Results` | 4.1 capture | Mutation score, Killed, Survived, Runtime actual |
| `## Surviving Mutants` | 5.1 → 5.5 | Per-mutant stubs; pre-pass fields; clustering fields; Severity-prior |

`mt-fix.md` writes everything else (Surviving Mutants triage fields, `## Discoveries`, `## Ratchet Verdict`, `## Open Handoffs`).

---

## Severity-prior Heuristic

This rules table is the authoritative copy. `mt-fix.md` cross-references it (no duplication).

```
mutator-weight (max across cluster members):
  boundary           4
  conditional        4
  logical            3
  block-removal      2
  string-literal     1
  other              2

path-weight (head file's path):
  High-criticality paths (business logic, APIs, services)        +3
  Medium-criticality paths (utilities, helpers, shared libs)     +2
  Low-criticality paths (UI, presentation, configuration)        +1
  logging files                                                  -2
  tests/, scripts/                                               -1
  other                                                           0

Severity-prior = mutator-weight + path-weight       (sort descending; tie-break by head M-ID)
```

Before computing path-weight scores, run a one-time survey of the
repository's top-level directory structure (list root dirs only) and map
them to the High/Medium/Low/logging/tests categories above. Do this once
per session; do not re-survey per cluster.

Equivalent pre-pass (5.2) operates at mutant level for mutator-weight ≤ 2.

---

## Quick Reference

### Invocation

```
Run mutation testing using /midtempo-framework/mt.md
```

Detects mode from `planning/mt-session.md` Status.

### Commands

```
npm run mutate:diff                     # diff-scoped (scope choices 3, 5)
npm run mutate:targeted -- "<paths>"    # path-filter (scope choices 1, 2, 4)
npm run mutate                          # full re-baseline (explicit only)
```

### Files

```
planning/mt-session.md                          — working session (shared with mt-fix.md)
planning/archive/mt-session-*.md                — completed sessions
planning/mt-fix-manifest.md                     — production bugs queued for bugs.md
planning/<feature>-design.md                    — developer intent (read at Step 1)
planning/<feature>-tests.md                     — described behaviour (read at Step 1)
/midtempo-framework/templates/mt-session.md     — session-file schema (authoritative)
```

### State transitions handled by mt.md

```
fresh-start → kickoff (Steps 1+2+3)
            → running (Step 3 launches; Step 4 captures)
            → captured (Step 4 promote; Step 5 entry)
            → ready-for-triage (Step 5.6 exit; HANDOFF to mt-fix.md)

Out-of-range statuses (ready-for-triage / triage-in-progress / triage-complete):
  → Entry Gate redirects human to mt-fix.md (one line) and STOPs.
```

### Substep walkthrough

```
5.1    Stub load — Read report → Edit stubs into mt-session.md
       → progress: "Loaded N mutants"
5.2    Equivalent pre-pass — per-mutant loop on disk; classify yes/borderline/no
       → progress: "Pre-pass: N equiv / B borderline / K clustering"
5.3    Equivalent-batch prompt (clear + borderline lists)
       human: yes / yes-all / review / split
       → progress: "Equivalents recorded: N bulk, B borderlines carried, K to clustering"
5.4    Clustering — per-file loop; enclosing-function extraction; Edit head/linked/members
       → progress: "Clustering: C clusters across F files"
5.5    Severity-prior — per-cluster-head loop; Edit Severity-prior; init Current Batch
       → progress: "Sort complete; Current Batch initialised"
5.6    Pre-triage complete handoff → exit; Status: ready-for-triage
```

### Iron Law

This skill never edits production code, test code, or the fix manifest. All write paths target `planning/mt-session.md` only. Triage, test edits, and bug-push live in `mt-fix.md`.

---

**END OF DOCUMENT** Purpose: Pre-triage half (run + equivalent pre-pass + cluster + sort) of a mutation-testing session. Hands off to `mt-fix.md` for triage + inline fix + ratchet + complete.