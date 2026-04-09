# Security Rules

## Table of Contents

- [Overview](#overview)
- [Compliance Gates](#compliance-gates)
- [Domain-Specific Security](#domain-specific-security)
- [Anti-Patterns](#anti-patterns)
- [Common Rationalisations](#common-rationalisations-forbidden)
- [Enforcement Summary](#enforcement-summary)

---

## Overview

Security compliance has two layers: universal gates that apply to all work, and domain-specific rules that apply when work involves that domain.

**Core principle:** Always match security checks to work scope: authentication work → auth rules, database work → DB security. If in doubt, always check.

**Role in workflow:** These rules are mandatory security standards and are always applied.

## Compliance Gates

> Delivery and review skills verify these gates. Each gate must pass for work touching security concerns.

- [ ] **CG-S1:** No hardcoded secrets in code or version control
- [ ] **CG-S2:** No sensitive data in logs (credentials, tokens, PII)
- [ ] **CG-S3:** Secure defaults (fail closed, not open)
- [ ] **CG-S4:** Input validation at all system boundaries
- [ ] **CG-S5:** Error messages don't leak sensitive information (stack traces, paths, credentials)

## Domain-Specific Security

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


## Anti-Patterns

**Agent must detect and refuse these violations:**

1. **Hardcoded credentials** — API keys, passwords, tokens in source code or committed files
2. **Logging sensitive data** — Credentials, tokens, PII in log statements
3. **Client-side only validation** — Security validation must happen server-side
4. **Generic error messages in production** — Stack traces, file paths, SQL queries exposed to users
5. **Overly permissive defaults** — Open access, debug mode enabled, CORS wildcards in production

## Common Rationalisations (FORBIDDEN)

**Agent must refuse these justifications with mandatory counter-responses:**

| User Says | Agent Must Respond |
|-----------|-------------------|
| "It's just for development/testing" | "No. Security rules apply to all environments. Fixing now." |
| "We'll fix it before production" | "No. Fix security issues immediately. Temporary insecure code becomes permanent." |
| "This is an internal tool" | "No. Internal tools need security too. Insider threats are real." |
| "The API key can be in the code temporarily" | "No. Secrets must never be in version control. Using environment variables." |
| "We can validate on the client side" | "No. Client-side validation is UX only. Security validation happens server-side." |

## Enforcement Summary

**Agent operates under these non-negotiable constraints:**

1. **Compliance gate verification** — All CG-S gates must pass before security-related work is complete.
2. **Domain-specific rules** — Only read and verify rules for domains relevant to current work scope.
3. **Mandatory refusal** — Agent uses mandatory counter-responses to rationalisations.

**Termination condition (agent stops work):**
- Uncertainty about security rule application (escalate to human partner)

**Agent does NOT stop for:**

- Moving secrets to environment variables
- Adding server-side validation alongside client-side
- Implementing secure defaults
- Sanitising error messages for production

---
**END OF DOCUMENT:** Total sections: 6 | Purpose: Security - primary compliance gates and security orchestrator