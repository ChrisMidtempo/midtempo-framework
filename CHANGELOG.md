# Changelog

All notable changes to the Midtempo Framework are documented here.

---

## [0.5.1] — 28/05/2026

### Root cause synthesis in architecture reviews, coupling assessment in design, two new test rules

**Review-architecture skill - root cause synthesis (new Step 7):**  
A new step, "Synthesise Root Causes", now runs between findings collection (Steps 2–6) and the recommendations file. It clusters findings by the artefact they touch - type, module, implicit convention, or data shape - and where ≥ 2 findings share a single root cause, promotes the root cause into its own finding with the symptoms listed as evidence. If no clusters emerge, all findings remain independent. The former Steps 7 and 8 are now Steps 8 and 9, and the architecture checklist gains a "root cause synthesis pass complete" line.

**Review-architecture and review-code - design doc field per finding:**  
Both review skills now require every recommendation to declare which design doc it relates to: `planning/[path]/[feature]-design.md`, or an explicit `N/A — [reason]` (cross-cutting work, predates design-doc convention, general cleanup, etc.).

**Refactor skill - design doc updates on standalone invocation:**  
A new critical requirement: when the refactor skill runs standalone (not as part of the delivery workflow), it must update the feature design doc with refactor outcomes before producing exit output - and update the recommendation document if one was provided. The extraction step reads the referenced design doc per finding from the recommendation document.

**Write-design and design template - Balanced Coupling assessment:**  
The design template's §3.3 "Integration Points" now carries a "Coupling Assessment" sub-section based on the Balanced Coupling model. Each integration is rated for Strength (contract → model → functional → intrusive), Distance (same module → cross-team), and Volatility (high for Core; low for Supporting/Generic). The balance rule — `BALANCE = (STRENGTH XOR DISTANCE) OR NOT VOLATILITY` — flags distributed-monolith risk (high/high/high) and low-cohesion risk (low/low/low). 

**Testing rules - global state restoration (§9 amendment):**  
The "tests must reset state between runs" rule now explicitly covers global state mutations: clocks, fake timers, locale, environment variables, random seeds, monkey-patches, registered handlers. Mode switches (e.g. fake → real timers) must be paired inside the same scope that opened them - a `beforeEach`/`setUp` in the next test file is not a safe backstop.

**Testing rules - guarded preconditions (new §13):**  
A new violation class: wrapping a test action in a conditional that silently skips when the precondition is unmet (`if button exists: click`) buries the real failure as a downstream timeout. Tests must assert the precondition explicitly, then use it unconditionally. Two new entries are added to the Common Rationalisations table.

---

## [0.5.0] — 25/05/2026

### Investigate skill redesigned, and "reversibility" clarified

**Investigate skill — single-path investigation:**  
The two-path investigation model (understanding vs. recommendations) has been removed - 0.4.9 didn't work as hoped. The skill now follows a single path for all investigations. The four-part synthesis that was previously exclusive to the understanding path — Mechanism, Current State, What Could Happen, and Glossary — is now embedded in Step 4 (Analyse & Synthesise) for every investigation, before proposals are made. Step 5U, Step 6U, and the understanding report file have all been removed.

**Investigate skill — explicit external research opt-in (§2.1.5):**  
External research is no longer auto-triggered based on concern type. Instead, a new step (§2.1.5) is introduced after the framing reflection is confirmed, giving the human an explicit choice: skip external research, use agent-suggested areas (populated from Step 1 context), or specify custom sources. The `research_opt_in` flag set here controls whether §3.4 runs and whether §4.5 (Glossary) is populated.

**Build skill — reversibility classification simplified:**  
The "rollback" option has been removed from the reversibility axis in the impact assessment table and decision cards. Reversibility is now a binary choice — feature-flag or permanent — with clearer definitions: a feature-flag can be toggled off at runtime without a code change; permanent means later code will depend on it and reversing means rework.

**README — templating engine clarification:**  
A prominent note has been added to the top of the README clarifying that this repo is a templating engine for generating repo-specific skills — not the framework itself. An example of the generated framework lives in `midtempo-framework/`.

---

## [0.4.9] — 26/04/2026

### Dual-path investigation skill, external research step, and a new CLAUDE.md

**Investigate skill — two investigation paths:**  
The investigate skill now asks at entry which kind of investigation you're running:

- **Understanding path** — you want to understand how something works or why it behaves the way it does. Produces a structured understanding report (mechanism, current state, conditional outcomes, glossary).
- **Recommendations path** — you want to break a concern into actionable, deliverable work. Produces the existing recommendation files.

If the intent is ambiguous, the skill asks before proceeding. The path is committed at the entry gate and cannot switch mid-investigation. Each path has its own steps: `5U → 6U` for understanding, `5 → 6` for recommendations, with Step 7 adapting its report structure accordingly.

**Investigate skill — external research step (§3.4):**  
A new evidence-gathering step handles cases where the concern depends on framework, library, protocol, or vendor semantics. Before fetching, the step checks `planning/assets/` for curated resource documents relevant to the concern. If none exist, it searches authoritative sources (vendor docs, RFCs, official guides), capped at three per concern. Forum posts and blogs are rejected unless corroborating an authoritative source. References are documented inline in the investigation file.

**Deliver-red — clearer known-pass validation prompt:**  
The known-pass presentation now opens with an explicit instruction explaining that approval updates the test manifest and completes the §4 exit gate — reducing ambiguity about what the human is being asked to confirm.

**Delivery and refactor skills — "Step" → "Phase" terminology:**  
The handover prompts at the end of the GREEN and REFACTOR phases now use "Phase" consistently (`Phase 3`, `Phase 4`) instead of "Step", matching the language used everywhere else in the delivery workflow.

---

## [0.4.8] — 17/04/2026

### Cleaner phase separation in the delivery workflow

The RED → GREEN → REFACTOR phases are now more explicitly enforced in the delivery skills. GREEN phase now carries an explicit rule that you must not refactor or run the linter — those belong to REFACTOR. This prevents agents from jumping ahead and cleaning up code before the core behaviour is even working. A minor clarification was also added to the refine skill around the same boundary.

---

## [0.4.7]

### Phase-aware test reviews and smarter RED phase rules

Two important fixes to how TDD phases are understood:

- The test review skill now detects which phase it's operating in. If a test manifest shows RED status, the reviewer understands that failing tests are expected — a compliance fix that leaves tests still failing is fine, and a fix that suddenly makes a test pass is a signal to stop and ask.
- The RED phase delivery skill now explicitly forbids running coverage or the linter. Both are Phase 3 (REFACTOR) concerns. Running them in RED produces meaningless results and causes confusion.

---

## [0.4.6]

### Smarter build skill and a simpler code review entry

**Build skill — two modes of architecture exploration:**  
The build skill now supports two distinct modes depending on how much is already decided:

- **Mode A** — nothing is decided yet. The skill explores 2–3 genuinely different architectural approaches across multiple axes (pattern, data model, UX, integration).
- **Mode B** — the architecture is already specified. The skill focuses on open design questions within those constraints, resolving them one at a time through impact assessment.

This gives teams flexibility to match their actual decision-making context rather than forcing a one-size-fits-all exploration.

**Code review skill — simplified entry:**  
The review entry process was simplified from a two-question format (scope + intent taxonomy) to a single question: scope, with an optional concern field. The "Intent" taxonomy (pre-merge / investigate / post-delivery) was removed as it added overhead without improving review quality.

---

## [0.4.5.1]

### Documentation patch

Minor cleanup to `SETUP.md` — removed unnecessary instructions and tightened the wording.

---

## [0.4.5]

### Documentation consolidation and expanded test coverage

- Removed the duplicate `CLAUDE.md` from the `midtempo-framework/` directory. The root `CLAUDE.md` is now the single source of truth for agent rules.
- Improved wording in the README for clarity ("procedure" instead of "fixed workflow" etc.).
- Added new test files covering CSS documentation structure, HTML validation, and server call handling — over 100 lines of new test coverage.
- Tightened `.gitignore` to exclude more generated and temporary files.

---

## [0.4.5]

### Test log file skill and a much-improved documentation-fix skill

**New: test log file skill (`fix-log-file`):**  
Adds wrapper scripts that write test output to a persistent log file. Works with pytest, Jest, Vitest, Go, Ruby, and Java. This lets the framework know the current test state across conversations without re-running the full suite every time.

**Expanded: documentation-fix skill:**  
The `fix-docs` skill was rewritten from ~80 lines to over 450. It now supports:
- A "fresh start" gate for first-time use vs. a "continuation" gate for returning to an in-progress session
- Batch processing of documentation issues with a progress file that persists between conversations
- Categorised issue tracking: missing docs, invalid parameters, broken links, type mismatches
- Integration with language-specific documentation tools and writing rules validation

**New: About modal UI tests:**  
Added ~350 lines of tests covering the About modal component — button placement, HTML structure, JavaScript event wiring, keyboard navigation (Escape key), z-index layering, and focus management.

**Documentation rewrite:**  
`INSTALL.md`, `GUIDE.md`, and `README.md` in the framework directory were all rewritten for clarity and completeness.

---

## [0.4.3]

### Minor documentation and config corrections

Small corrections to framework documentation wording and config values. Added a few lines to the test examples. No functional changes.

---

## [0.4.2]

### Removed server, added example planning documents

**Removed:**  
The embedded FastAPI server (`server/`) and its associated build-time validation scripts have been removed. The framework no longer generates dynamic server-based UIs — it is now purely documentation and skill-driven.

**Added:**  
A set of example planning documents has been added to the `planning/` directory:
- `EXAMPLE-decisions.md` — how to document design decisions
- `EXAMPLE-design.md` — how to write an architecture design document  
- `EXAMPLE-plan.md` — how to write a delivery plan
- `EXAMPLE-tests.md` — how to write a test manifest

These serve as templates and reference material for teams using the framework.

**Tests:**  
Expanded UI test coverage for CSS validation and HTML structure; refactored the form wiring tests.

---

## [0.4.1]

### Package and PR template updates

Minor updates to `package.json` and the pull request template. No functional changes.

---

## [0.4.0]

### Structured GitHub issue forms

Converted the GitHub issue templates from freeform markdown to structured YAML forms. Bug reports and feature requests now capture consistent, structured data instead of open text — improving triage and reducing back-and-forth.

---

## [0.3.9]

### Open source community setup

Added the standard set of open source repository files:

- Apache 2.0 license
- Contribution guidelines (`CONTRIBUTING.md`)
- Security policy (`SECURITY.md`)
- `CODEOWNERS` file
- Bug report and feature request issue templates

The framework is now properly set up as a public open source project.

---

## [0.3.8] — Initial public release

The first public release of the Midtempo Framework.

Includes the complete agent rules and workflow documentation (`CLAUDE.md`), the Jinja2 template system for generating language-specific configurations (JavaScript/npm, Kotlin/Maven, Python/Poetry, Python/uv), and initial UI test coverage for form and modal components.

The framework targets Python 3.14+ and uses `pyproject.toml` for package configuration.
