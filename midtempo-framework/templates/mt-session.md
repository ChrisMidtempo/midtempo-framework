# MT Session Template

**Renders to:** `planning/mt-session.md` (working) → `planning/archive/mt-session-<YYYYMMDD-HHMM>.md` (on completion).


---

## Section ownership

| Section | Written by | Read by |
|---|---|---|
| `## Status` | mt.md (running, captured, ready-for-triage); mt-fix.md (triage-in-progress, triage-complete) | Entry Gate of both skills |
| `## Current Batch` | mt.md (init); mt-fix.md (6 per-file update) | Entry Gate of both skills; mt-fix.md (resume detection) |
| `## Kickoff` | mt.md  | mt-fix.md (analysis context) |
| `## Run Results` | mt.md (capture from mutation harness) | mt-fix.md (ratchet computation) |
| `## Surviving Mutants` | mt.md (stubs; pre-pass; clustering; sort); mt-fix.md ( analysis + classification + action) | Both skills, one block at a time |
| `## Discoveries` | mt-fix.md (surface-and-log; per-file review; defensive sweep) | mt-fix.md only |
| `## Ratchet Verdict` | mt-fix.md  | mt-fix.md (emit) |
| `## Open Handoffs` | mt-fix.md (design-doc review prompt; fix-now exits) | mt-fix.md (emit) |

---

## File schema

```
# MT Session — <feature-name or branch>

## Status
ready-for-triage          (or: kickoff | running | captured | triage-in-progress | triage-complete)

## Current Batch
Next: <file path>                                        (or "—" when triage-complete)
  Unclassified clusters in this file: <N>
Progress: <N> of <total> file batches classified
  Equivalents pre-accepted: <N> mutants    (mt.md bulk-accept)
  Borderlines flagged for triage: <B> mutants
  Cluster-level outcomes so far:           (mt-fix.md updates these)
    Real test gaps:   <N>  (fix-now: <N>, ignored: <N>)
    Equivalent:       <N>  (from pre-pass and any overrides)
    Production bugs:  <N>  (bugs-pushed: <N>)
    Discoveries this file: pushed <P>, discarded <D>  (mt-fix.md review)
Remaining files (file-prior desc):
  <file path>  (<N> clusters, max prior <N>)
  <file path>  (<N> clusters, max prior <N>)

## Kickoff
- Started: <YYYY-MM-DD HH:MM>
- Scope choice: <1 design-doc | 2 changed-files | 3 branch | 4 test-path-pattern | 5 since-last-mt>
- Resolved diff: <git SHA range OR space-separated path filter>
- Source design doc: <path or "none">
- Source test manifest: <path or "none">
- Previous session SHA: <SHA or "none — first session">
- Previous-session score: <X% or "none — first session">
- Runtime budget: 2h  (Phase 1 starting point — validate)
- Command: <one of: npm run mutate:diff | npm run mutate>

## Run Results
- Run end: <YYYY-MM-DD HH:MM>
- Mutation score: <X%>
- Killed: <N>
- Survived: <N>
- Runtime actual: <Xh Xm>

## Surviving Mutants

### M<N> — <file:line>
- Mutator: <boundary | conditional | logical | block-removal | string-literal | other>
- Original: `<code>`
- Mutated:  `<code>`
- Likely-equivalent (mt.md 5.0.5): <unset | yes | borderline | no>
- Lightweight rationale (head only, when yes or borderline): <one line>
- Cluster head: M<N>                 (= self for head; an M-ID for linked rows)
- Cluster members (head only): M<N>, M<N>, …       (omit on linked rows)
- Enclosing function (head only): <function name | "(fallback <a|b|c>)">
- Severity-prior (head only): <integer>            (mt.md computed)
- Linked to (linked rows only): M<head-id>
- Context (head only): <2-3 sentences>                    (mt-fix.md 2)
- Observable-behaviour analysis (head only): <YES | NO | SPEC-SILENT> — <evidence>  (mt-fix.md 2)
- Why this matters (head only): <one line>               (mt-fix.md 2)
- Recommendation (head only): <one line>                 (mt-fix.md 2)
- Severity: <blocking | recommended | nit>               (mt-fix.md analysed value; linked inherit)
- Classification: <unclassified | real test gap | equivalent mutant | production bug>
- Sub-class (head only, real-test-gap only): <no-coverage | new-behaviour | strengthen-assertion>
- Rationale (equivalent OR ignore action; head only): <one line>
- Action: <unset | recorded | fix-now | ignored | bug-pushed>
- Fix applied (head only, fix-now only): <test file path edited>
- Verification (head only, fix-now only): <passed | failed-then-ignored>
- Manifest entry (head only, bug-pushed only): MT-<YYYYMMDD>-<seq>          (new entry created this session)
- Manifest link (head only, alternative to Manifest entry): MT-<YYYYMMDD>-<seq>   (extended an existing entry)
- Handoff scope (head only, bug-pushed only): <one line — refined later in bugs.md>
- Telemetry (head only): proposed-vs-accepted summary for classification,
  severity, sub-class, action — each `same` (no override) or
  `<agent's> → <operator's>` (override recorded)

### M<N+1> — <file:line>
…

## Discoveries

Production bugs found at file:lines OTHER than the current cluster's mutant during mt-fix.md per-cluster analysis. Written by mt-fix.md (logged / decided)

### D<N> — <file:line>
- Discovered during: cluster C<N> (M<head-id>) in file <path>
- Conversation: <YYYY-MM-DD HH:MM>
- Proposed severity: <blocking | recommended | nit>
- Problem: <2-3 sentences>
- Why this matters: <one sentence>
- Status: <logged | pushed | discarded>
- Manifest entry (only when Status: pushed): MT-<YYYYMMDD>-<seq>
- Operator decision rationale (only when Status: discarded): <one line>

### D<N+1> — <file:line>
…

## Ratchet Verdict
(written by mt-fix.md 7.4)

- Real-test-gap count: <N>
- Equivalent-mutant count: <N>
- Production-bug count: <N>
- Action counts: fix-now=<N> ignored=<N> bugs-pushed=<N>
- Discovery counts: logged=<N> pushed=<N> discarded=<N>
- Effective score (this session):  <X%>
- Effective score (previous):      <X% or "—">
- Delta:                           <±X pp>
- Verdict:                         <BASELINE | PASS | FAIL>
- Re-baselined:                    <yes (rationale) | no>

## Open Handoffs
(written by mt-fix.md)

- [ ] Design-doc review (if fired): <path>
- (Bug entries are in planning/mt-fix-manifest.md — not duplicated here)
```

---

## State enum

| Status | Set by | Meaning | Next entry routes to |
|---|---|---|---|
| (no file) | — | Fresh start | mt.md |
| `kickoff` | mt.md | Session file written; scope confirmed; run not yet launched | mt.md Step 3 |
| `running` | mt.md | Mutation run in flight | mt.md Step 4 |
| `captured` | mt.md auto-promote | Run Results populated; pre-triage not started | mt.md Step 5 |
| `ready-for-triage` | mt.md | Pre-triage complete; Stage 2 not started | mt-fix.md Step 1 |
| `triage-in-progress` | mt-fix.md | At least one file batch classified | mt-fix.md Step 1 |
| `triage-complete` | mt-fix.md | All file batches classified + ratchet verdict written | mt-fix.md Step 8 (emit + archive) |

Out-of-range statuses redirect to the other skill via a one-line message; see each skill's Entry Gate.

---

## ID conventions

- **`M<N>`** — Mutant ID. Sequential, assigned by mt.md in mutation report order. Lowest M-ID in a cluster is the HEAD.
- **`C<N>`** — Cluster ID. Sequential, assigned by mt.md in heuristic order. The head's M-ID identifies the cluster in cross-references.
- **`D<N>`** — Discovery ID. Sequential, assigned by mt-fix.md in the order discoveries are surfaced.
- **`MT-<YYYYMMDD>-<seq>`** — Fix manifest entry ID. Per-day zero-padded counter starting at `01`. Generated by mt-fix.md when an action requires manifest write (`Action: bug-pushed`, or `Status: pushed` on a Discovery).

---

## Operator manual-edit rules

The session file is hand-editable at any time. Both skills re-read sections on resume, so an edit shapes subsequent behaviour. Common operator edits:

- **Force a state transition.** Edit `## Status` to a different enum value. Re-invoke the appropriate skill.
- **Skip a file.** Edit `## Current Batch`'s `Remaining files` list to remove a file. The skill will not return to it.
- **Re-open a classified cluster.** Edit the cluster head's `Classification:` back to `unclassified` and clear `Action:`. mt-fix.md will re-present it on the next file-batch visit.
- **Discard a discovery without rationale.** Edit a `## Discoveries` entry's `Status: logged` to `Status: discarded` and add a one-line `Operator decision rationale:`. mt-fix.md defensive sweep won't surface it.

The skills do NOT enforce edit validity at read time. Self-inflicted breakage (e.g., promoting `Status: kickoff` to `triage-complete` without doing the work) is the operator's responsibility.

---

**END OF DOCUMENT**