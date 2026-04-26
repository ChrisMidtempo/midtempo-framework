# Changelog

All notable changes to the Midtempo Framework are documented here.

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

## [0.4.7] — In development

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
