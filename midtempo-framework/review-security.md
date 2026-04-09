# Security Review Skill

## Overview

Guard security posture: secrets, input handling, authentication, data protection, public hardening. Each analysis section is validated by the human and persisted to file before the next begins.

**Goal:** Produce an incremental review report and a grouped recommendations file with skill routing per finding.

**NOT for:**

- Code correctness → use [review-code.md](review-code.md)
- Test quality → use [review-tests.md](review-tests.md)
- Architecture boundaries → use [review-architecture.md](review-architecture.md)
- E2E reliability → use [review-e2e.md](review-e2e.md)

**Primary references:**

- `security.md`
- `architecture.md`
- Domain: `authentication.md`
- Domain: `input-validation.md`
- Domain: `data-protection.md`
- Domain: `public-hardening.md`
- Domain: `secrets-management.md`

**Outputs:**

- `planning/reviews/security-[date].md` — Review report (written incrementally, one section at a time)
- `planning/reviews/security-[date]-recommendations.md` — Grouped findings with severity and skill routing

---

## Table of Contents

- [Overview](#overview)
- [Non-Negotiable Rules](#non-negotiable-rules)
- [Security Domain Map](#security-domain-map)
- [Entry Gate](#entry-gate)
- [Step 1: Scope & Intent](#step-1-scope--intent)
- [Step 2: Universal Security Gates](#step-2-universal-security-gates)
- [Step 3: Domain Security Compliance](#step-3-domain-security-compliance)
- [Step 4: Security Anti-Patterns](#step-4-security-anti-patterns)
- [Step 5: Compile Recommendations](#step-5-compile-recommendations)
- [Step 6: Complete Review](#step-6-complete-review)
- [Anti-Patterns](#anti-patterns)
- [Severity Taxonomy](#severity-taxonomy)
- [Common Rationalisations](#common-rationalisations-forbidden)
- [Final Rule](#final-rule)

---

## Non-Negotiable Rules

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST review against the universal security compliance gates (CG-S1 – CG-S5) for all work.
- You MUST check domain-specific compliance gates for domains matching both repo capabilities AND scope of work.
- You MUST cite a compliance gate reference and file:line evidence for every finding.
- You MUST include at least one positive observation.
- You MUST label severity: blocking/recommended/nit.
- You MUST read applicable domain security rule files before checking their gates.
- You MUST skip domain checks not relevant to the scope of work, even if the capability is enabled.
- You MUST present each analysis section to the human before writing it to the review file.
- You MUST wait for human validation on sections with findings before appending.
- You MUST write sections with no findings (all PASS) without requiring validation.
- You MUST write each validated section to `planning/reviews/security-[date].md` before starting the next.
- You MUST compile findings into `planning/reviews/security-[date]-recommendations.md` with skill routing per finding.
- You MUST NOT batch multiple sections into a single write.

</CRITICAL_REQUIREMENT>

---

## Security Domain Map

Domains apply when the repo capability is enabled AND the work under review touches that domain. Skip domains outside the scope of work.

| Domain | Capability | Rule File | Applies |
| --- | --- | --- | --- |
| **Secrets Management** | Always | `rules/security/secrets-management.md` | Always |
| **Input Validation** | hasUI or hasDB | `rules/security/input-validation.md` | Yes |
| **Authentication** | hasAuthentication | `rules/security/authentication.md` | Yes |
| **Data Protection** | handlesConfidentialData | `rules/security/data-protection.md` | Yes |
| **Public Hardening** | isPublicFacing | `rules/security/public-hardening.md` | Yes |

**Scoping rule:** A domain row appearing above means the capability is enabled. The agent still checks whether the work under review touches that domain before running its compliance gates.

---

## Entry Gate

```
IF human request is about code correctness
  → REDIRECT to `/midtempo-framework/review-code.md`

IF human request is about test quality
  → REDIRECT to `/midtempo-framework/review-tests.md`

IF human request is about architecture boundaries
  → REDIRECT to `/midtempo-framework/review-architecture.md`

IF human request is about E2E reliability
  → REDIRECT to `/midtempo-framework/review-e2e.md`
```

VERIFY-COMPLETE-READ for EVERY file below:
  CHECK the last line says "END OF DOCUMENT"
  IF CHECK fails → Re-read from offset until true end

READ ALL of `/midtempo-framework/rules/writing.md` → before proceeding
READ ALL of `/midtempo-framework/rules/security.md` → before proceeding
READ ALL of `/midtempo-framework/instructions/purpose.md` → before proceeding
READ ALL of `/midtempo-framework/instructions/architecture.md` → before proceeding


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


VALID: Continue to Step 1

---

## Step 1: Scope & Intent

### 1.1 Establish Scope

ASK the human two questions. WAIT for each answer before continuing.

**Q1 — What are you reviewing?**

| Scope Type | Behaviour |
|------------|-----------|
| Feature/branch | Find planning docs, scope to feature files and surfaces |
| Surface | Scope to that surface's layering path from instruction documents |
| Module/area | Human provides entry point(s), agent maps the boundary |
| Whole system | All surfaces from instruction documents |

**Q2 — What's driving this review?**

| Intent | Effect |
|--------|--------|
| Verify design | Measure findings against planning/design docs |
| Investigate concern | Prioritise concern area, then standard checks |
| Pre-change assessment | Focus on area about to change, frame findings as risks |
| Health check | Standard full run, no bias |

WAIT for both answers before continuing.

### 1.2 Determine Applicable Domains

Based on the scope from Q1, determine which security domains from the Security Domain Map apply to the work under review.

```
FOR EACH domain in Security Domain Map:
  IF capability is enabled AND scope of work touches that domain
    → Mark domain as APPLICABLE
  IF capability is enabled AND scope of work does NOT touch that domain
    → Mark domain as SKIPPED (with reason)
```

### 1.3 Documentation Check

**Based on scope type from Q1:**

```
IF feature/branch → REQUIRED: find and read planning docs. IF not found → STOP.
IF surface or area → OPTIONAL: use if available.
IF whole system → NOT EXPECTED: skip.
```

Search for:
- `/planning/*-plan.md` — Implementation plans
- `/planning/*-design.md` — Design documents

Read and extract:
- Intended architecture and scope
- Security-relevant design decisions
- Integration points and trust boundaries

If no docs exist and scope type requires them → ASK:
> "No planning/design documentation found. Please provide:
> (a) path to relevant docs, or (b) confirmation this is a minor change not requiring docs."

### 1.4 Present Scope

Present scope summary to human:

```
Security Review Scope: [Feature/Target Name]

- Type: [feature / surface / area / whole system]
- Target: [from Q1]
- Intent: [from Q2]
- Planning docs:
  - Design: [path or "not applicable"]
  - Plan: [path or "not applicable"]
- Applicable domains:
  - [domain]: [reason applicable]
  - [domain]: SKIPPED — [reason]
```

WAIT for human validation before proceeding

Review scope, intent, applicable domains, and planning docs for accuracy
IF human approves
  → VALID: CREATE review file and continue to Step 2
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

### 1.5 Create Review File

```markdown
# Security Review: [Feature Name]

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

## Applicable Domains

| Domain | Status | Reason |
| --- | --- | --- |
| [domain] | Applicable | [reason] |
| [domain] | Skipped | [reason] |

---

## Intent Summary

- [Key point from planning docs]
- [Key point from planning docs]
```

Continue to Step 2.

---

## Step 2: Universal Security Gates

Check the universal security compliance gates (CG-S1 – CG-S5) against the code under review. These gates apply to all work regardless of domain.

- CG-S1: No hardcoded secrets in code or version control
- CG-S2: No sensitive data in logs (credentials, tokens, PII)
- CG-S3: Secure defaults (fail closed, not open)
- CG-S4: Input validation at all system boundaries
- CG-S5: Error messages don't leak sensitive information

For each gate, record PASS or FAIL with file:line evidence.

### 2.1 Present Results

**Output to human:**

```
Universal Security Gates: [Feature Name]

| Gate | Result | Evidence |
|------|--------|----------|
| CG-S1 | PASS/FAIL | [file:line if FAIL] |
| CG-S2 | PASS/FAIL | [file:line if FAIL] |
| CG-S3 | PASS/FAIL | [file:line if FAIL] |
| CG-S4 | PASS/FAIL | [file:line if FAIL] |
| CG-S5 | PASS/FAIL | [file:line if FAIL] |
```

### 2.2 Validation Gate

```
IF any gate is FAIL
  → PRESENT results to human
```

WAIT for human validation before proceeding

Review universal security gate results and evidence for accuracy
IF human approves
  → VALID: APPEND to `planning/reviews/security-[date].md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

```
IF all gates PASS
  → STATE: "Universal Security Gates: all PASS"
  → APPEND to `planning/reviews/security-[date].md` without waiting

Continue to Step 3.
```

---

## Step 3: Domain Security Compliance

Check compliance gates for each domain marked APPLICABLE in Step 1. Read the domain rule file, then verify each gate against the code under review.

```
FOR EACH domain marked APPLICABLE in Step 1:
  1. READ the domain's rule file (from Security Domain Map)
  2. LOCATE the "Compliance Gates" section
  3. VERIFY each CG gate against code under review
  4. RECORD PASS or FAIL with file:line evidence
```

### 3.1 Secrets Management

**Always applicable.** Check compliance gates from `rules/security/secrets-management.md`.

- CG-SM1: No hardcoded credentials in source code
- CG-SM2: No secrets in tracked files
- CG-SM3: No credentials in log output
- CG-SM4: Secrets accessed via environment variables or secrets vault only
- CG-SM5: Encryption keys stored separately from protected data
- CG-SM6: Encryption keys not derived from user input without KDF
- CG-SM7: No plaintext export of encryption keys

### 3.2 Input Validation

**Check if scope touches input handling.** Check compliance gates from `rules/security/input-validation.md`.

- CG-IV1: Structured inputs validated against explicit format
- CG-IV2: All inputs enforce maximum length at entry
- CG-IV3: Validation occurs at point of entry
- CG-IV4: No user input in dynamic execution contexts
- CG-IV6: All HTML output uses context-appropriate encoding
- CG-IV7: File uploads validated server-side by content type
- CG-IV8: Validation decisions made once at entry

### 3.3 Authentication

**Check if scope touches authentication or authorisation.** Check compliance gates from `rules/security/authentication.md`.

- CG-AU1: Auth logic isolated in dedicated middleware or service
- CG-AU2: Access control enforced at service boundary
- CG-AU3: Passwords stored using adaptive hashing algorithm
- CG-AU4: Sessions invalidated on logout, regenerated on login
- CG-AU5: Security events logged with timestamp and actor
- CG-AU6: Session cookies set with SameSite attribute
- CG-AU7: State-changing endpoints protected against CSRF
- CG-AU8: Sensitive operations require re-authentication
- CG-AU9: Failed auth attempts rate-limited
- CG-AU10: Privilege escalation attempts logged

### 3.4 Data Protection

**Check if scope touches confidential data handling.** Check compliance gates from `rules/security/data-protection.md`.

Read and verify all CG-DP gates from the domain rule file.

### 3.5 Public Hardening

**Check if scope touches public-facing surfaces.** Check compliance gates from `rules/security/public-hardening.md`.

Read and verify all CG-PH gates from the domain rule file.

### 3.N Present Results

**Output to human:**

```
Domain Security Compliance: [Feature Name]

[For each applicable domain:]

[Domain Name]:
| Gate | Result | Evidence |
|------|--------|----------|
| [CG-XX] | PASS/FAIL | [file:line if FAIL] |
| ... | ... | ... |

Skipped domains:
- [domain]: [reason from Step 1]
```

### 3.N+1 Validation Gate

```
IF any gate is FAIL
  → PRESENT results to human
```

WAIT for human validation before proceeding

Review domain compliance gate results and evidence for accuracy
IF human approves
  → VALID: APPEND to `planning/reviews/security-[date].md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

```
IF all gates PASS across all applicable domains
  → STATE: "Domain Security Compliance: all PASS"
  → APPEND to `planning/reviews/security-[date].md` without waiting

Continue to Step 4.
```

---

## Step 4: Security Anti-Patterns

Check for common security anti-patterns in the code under review. Reference the anti-patterns table (see §Anti-Patterns) and each applicable domain's anti-pattern section.

For each anti-pattern found, record:
- Pattern name
- File:line evidence
- Applicable compliance gate violated
- Concrete security impact

### 4.1 Universal Anti-Patterns

Check all code under review for:

- **Hardcoded credentials** — API keys, passwords, tokens in source code
- **Sensitive data in logs** — credentials, tokens, PII in log statements
- **Fail-open defaults** — permissive defaults, debug mode, wildcard CORS
- **Missing input validation** — unvalidated data at system boundaries
- **Information leakage** — stack traces, paths, credentials in error messages

### 4.2 Input Handling Anti-Patterns

- **String-concatenated queries** — user input interpolated into SQL
- **Unencoded output** — user input rendered in HTML without escaping
- **Downstream-only validation** — validation buried in services, absent at entry point
- **Unbounded input** — no maximum length on strings, files, or payloads

### 4.3 Authentication Anti-Patterns

- **Auth logic in handlers** — auth decisions embedded in route handlers
- **Client-side-only access control** — no server-side enforcement
- **Weak password storage** — plaintext, reversible, or fast-hash storage
- **Session fixation** — session not regenerated on login, not invalidated on logout
- **Missing CSRF protection** — state-changing endpoints without token or origin validation

### 4.N Present Results

**Output to human:**

```
Security Anti-Patterns: [Feature Name]

Findings:
- [PATTERN]: [description] at [file:line] — violates [CG-XX]
- ...

OR

"Security Anti-Patterns: no issues found"
```

### 4.N+1 Validation Gate

```
IF findings exist
  → PRESENT findings to human
```

WAIT for human validation before proceeding

Review security anti-pattern findings for accuracy
IF human approves
  → VALID: APPEND to `planning/reviews/security-[date].md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

```
IF no findings
  → STATE: "Security Anti-Patterns: PASS — no issues found"
  → APPEND to `planning/reviews/security-[date].md` without waiting

Continue to Step 5.
```

---

## Step 5: Compile Recommendations

Compile all findings from Steps 2–4 into a single recommendations file.

### 5.1 Gather Positives

Before compiling findings, record at least one positive observation — a concrete security strength with evidence.

### 5.2 Group Findings

Group findings by severity (see §Severity Taxonomy):

1. **Blocking** — must resolve before further work
2. **Recommended** — should resolve soon
3. **Nit** — minor improvements

For each finding, include:

- **Severity:** blocking / recommended / nit
- **Skill:** `/midtempo-framework/[bugs|refactor|build|refine].md`
- **Evidence:** file:line references
- **Gate:** compliance gate violated (e.g. CG-S1, CG-SM2, CG-AU3)
- **Summary:** one-sentence description
- **Acceptance criteria:** measurable condition for resolution

### 5.3 Present Results

**Output to human:**

```
Recommendations: [Feature Name]

Positives:
- [Strength with evidence]

Blocking:
- [Finding] — Gate: [CG-XX] — Skill: [skill] — Evidence: [file:line]

Recommended:
- [Finding] — Gate: [CG-XX] — Skill: [skill] — Evidence: [file:line]

Nit:
- [Finding] — Gate: [CG-XX] — Skill: [skill] — Evidence: [file:line]

Total: [N] findings ([N] blocking, [N] recommended, [N] nit)
```

### 5.4 Validation Gate

This step always requires validation — it produces the recommendations file.

WAIT for human validation before proceeding

Review grouped recommendations for accuracy, severity, gate references, and skill routing
IF human approves
  → VALID: WRITE to `planning/reviews/security-[date]-recommendations.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

### 5.5 Write Recommendations File

After validation, CREATE `planning/reviews/security-[date]-recommendations.md`:

```markdown
# Security Review Recommendations: [Feature Name]

**Date:** [DD/MM/YYYY]
**Source:** `planning/reviews/security-[date].md`

---

## Positives

- [Strength with evidence]

---

## Blocking

### [Finding Title]

- **Skill:** `/midtempo-framework/[skill].md`
- **Gate:** [CG-XX]
- **Evidence:** [file:line references]
- **Summary:** [one sentence]
- **Acceptance Criteria:**
  - [ ] [measurable criterion]

---

## Recommended

### [Finding Title]

- **Skill:** `/midtempo-framework/[skill].md`
- **Gate:** [CG-XX]
- **Evidence:** [file:line references]
- **Summary:** [one sentence]
- **Acceptance Criteria:**
  - [ ] [measurable criterion]

---

## Nit

### [Finding Title]

- **Skill:** `/midtempo-framework/[skill].md`
- **Gate:** [CG-XX]
- **Evidence:** [file:line references]
- **Summary:** [one sentence]
- **Acceptance Criteria:**
  - [ ] [measurable criterion]
```

```
IF no findings across Steps 2–4
  → SKIP recommendations file
  → STATE: "No findings — no recommendations file needed"

Continue to Step 6.
```

---

## Step 6: Complete Review

### 6.1 Security Checklist

Complete before finishing:

- [ ] Scope declared (type, target, intent, applicable domains)
- [ ] Planning docs consulted or minor change confirmed
- [ ] Universal security gates checked (CG-S1 – CG-S5)
- [ ] Domain compliance gates checked for all applicable domains
- [ ] Inapplicable domains confirmed skipped with reason
- [ ] Security anti-patterns checked
- [ ] Positive observation recorded (at least one)
- [ ] Findings labelled (blocking/recommended/nit)
- [ ] All sections written to `planning/reviews/security-[date].md`
- [ ] Recommendations file written (or no findings confirmed)

### 6.2 Finalise Review File

APPEND completed checklist to `planning/reviews/security-[date].md`.

UPDATE the file header: change `**Status:** In Progress` to `**Status:** Complete`.

### 6.3 Completion Output

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output after review completes - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
</CRITICAL_REQUIREMENT>

```
---
                    SECURITY REVIEW COMPLETE: [FEATURE NAME]                   

---

Scope: [type/target/applicable domains]

Review report:
  `planning/reviews/security-[date].md`

Recommendations:
  `planning/reviews/security-[date]-recommendations.md` — [N] findings ([N] blocking, [N] recommended, [N] nit)

  OR "No findings — no recommendations file created"

Start follow-up work by opening the recommendations file
and using it as context for a new conversation with the
skill specified in each finding.
```

---

## Anti-Patterns

| Pattern | Example | Gate Violated |
| --- | --- | --- |
| **Hardcoded credentials** | API key string literal in source code | CG-S1, CG-SM1 |
| **Secrets in tracked files** | `.env` with real credentials committed | CG-SM2 |
| **Credentials in logs** | Logging auth tokens or request headers | CG-S2, CG-SM3 |
| **Fail-open defaults** | Debug mode enabled, CORS wildcard in config | CG-S3 |
| **Information leakage** | Stack traces or file paths in error responses | CG-S5 |
| **String-concatenated queries** | User input interpolated into SQL string | CG-IV5 |
| **Unbounded input** | No maximum length on text fields or file uploads | CG-IV2 |
| **Downstream-only validation** | Validation in service layer, absent at entry point | CG-IV3 |
| **Unencoded output** | Raw user input inserted into HTML template | CG-IV6 |
| **Auth logic in handlers** | Permission check inside route handler | CG-AU1 |
| **Client-side-only access control** | UI hides button, server performs no check | CG-AU2 |
| **Weak password storage** | MD5, SHA-256, or plaintext password storage | CG-AU3 |
| **Session fixation** | Session ID not regenerated on login | CG-AU4 |
| **Missing CSRF protection** | POST endpoint with no token or origin check | CG-AU7 |
| **Missing SameSite cookie** | Session cookie without explicit SameSite attribute | CG-AU6 |

---

## Severity Taxonomy

### Blocking

- Universal security gate failures (CG-S1 – CG-S5)
- Hardcoded credentials or secrets in tracked files (CG-SM1, CG-SM2)
- SQL injection or unencoded output (CG-IV5, CG-IV6)
- Auth logic outside dedicated middleware (CG-AU1)
- Weak password storage (CG-AU3)
- Data protection gate failures (CG-DP series)

### Recommended

- Credentials in log output (CG-SM3)
- Missing input length limits (CG-IV2)
- Validation not at entry point (CG-IV3)
- Missing security event logging (CG-AU5)
- Session handling gaps (CG-AU4)

### Nit

- Minor improvements to error message content
- Tightening existing validation rules
- Logging format improvements

### Escalation

- **Missing security requirements** → pause, request clarification
- **Systemic security failures** (multiple blocking across domains) → escalate to planning for security architecture review
- **Production exposure risk** → immediate escalation to human partner

---

## Common Rationalisations (FORBIDDEN)

**Agent must refuse these justifications with mandatory counter-responses:**

| User Says | Agent Must Respond |
|-----------|-------------------|
| "It's just a prototype" | "No. Security patterns are cheaper to establish now than to retrofit later." |
| "The endpoint isn't public" | "No. Internal endpoints need access control. Network position is not authorisation." |
| "We check permissions in the frontend" | "No. Client-side checks are not access control. Server-side enforcement required." |
| "We'll add security before go-live" | "No. Fix now. Security bolted on late introduces regressions and gaps." |
| "It's only internal users" | "No. Internal users can be compromised. Role-based access limits blast radius." |
| "The framework handles it" | "Confirm the framework's default behaviour for this specific case. Defaults vary." |
| "The frontend already validates it" | "No. Client-side validation is not a security control. Server-side validation required." |
| "We sanitise the input instead of validating it" | "Sanitisation is not validation. Define what is permitted and reject everything else." |
| "bcrypt is too slow for our use case" | "Confirm the measured latency. If genuinely unacceptable, argon2id or scrypt offer tunable cost. Fast hashes are not an option." |
| "CORS is configured, so CSRF is not a risk" | "No. CORS restricts which origins read responses. CSRF exploits the browser sending cookies automatically — separate attack. SameSite attribute and CSRF tokens are the defences." |

**If user persists after mandatory response:** Add a note to the relevant planning document recording the override and the reason given. Then continue.

---

## Final Rule

If uncertain whether a finding is a security issue, flag it. False positives are reviewed and dismissed; false negatives ship vulnerabilities.

---
**END OF DOCUMENT:** Total sections: 15 | Purpose: Security review skill — scope, universal gates, domain compliance, anti-patterns, and recommendations