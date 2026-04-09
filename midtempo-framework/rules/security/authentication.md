# Authentication & Authorisation

## Table of Contents

- [Overview](#overview)
- [Compliance Gates](#compliance-gates)
- [Enhanced Rules: Confidential Data](#enhanced-rules-confidential-data)
- [Anti-patterns and Auto-recovery](#anti-patterns-and-auto-recovery)
- [Common Rationalisations](#common-rationalisations-forbidden)
- [Enforcement Summary](#enforcement-summary)

---

## Overview

Authentication verifies identity. Authorisation controls what an authenticated identity can do. Failures in either layer expose sensitive data, enable privilege escalation, and create audit gaps that cannot be closed retroactively.

**Core principle:** Auth logic belongs in dedicated middleware or services — not embedded in request-handling or business logic code. Callers cannot be trusted to enforce access control.

**Role in workflow:** These rules apply to all work that creates, modifies, or calls authentication or access control logic. Agent verifies all compliance gates before declaring auth-related work complete.

## Compliance Gates

> Delivery and review skills verify these gates. Each gate must pass for work touching authentication or authorisation.

- [ ] **CG-AU1:** Authentication and authorisation logic isolated in dedicated middleware or service — no auth decisions in request handlers or business logic
- [ ] **CG-AU2:** Access control enforced at the service boundary — not delegated to the caller or client
- [ ] **CG-AU3:** Passwords stored using an adaptive password hashing algorithm (bcrypt, argon2id, or scrypt) — no plaintext, reversible encryption, or fast hashes (MD5, SHA-family, unsalted digests)
- [ ] **CG-AU4:** Sessions invalidated on logout and session token regenerated on login — no session fixation risk
- [ ] **CG-AU5:** Security events logged — failed authentication attempts, authorisation failures, and session invalidations captured with timestamp, actor (user ID or IP), and event type — no PII in log values (see CG-DP5)
- [ ] **CG-AU6:** Session cookies set with `SameSite=Strict` or `SameSite=Lax` — no session cookie without an explicit SameSite attribute
- [ ] **CG-AU7:** State-changing endpoints protected against forged cross-origin requests — CSRF token validated or Origin header verified for all POST, PUT, PATCH, and DELETE routes

## Enhanced Rules: Confidential Data

These gates apply when the repository handles confidential data (PII, financial records, health data, or similarly sensitive material).

- [ ] **CG-AU8:** Sensitive operations (password change, account deletion, payment modifications) require re-authentication before execution
- [ ] **CG-AU9:** Failed authentication attempts rate-limited or throttled — brute force not possible via the API
- [ ] **CG-AU10:** Privilege escalation attempts logged — role grants, permission changes, and administrative operations recorded with actor, target resource, and outcome

## Anti-patterns and Auto-recovery

**Agent must detect violations, present the proposed fix, and wait for human approval before making any changes.**

### 1. Auth Logic in Request Handlers

**Detection:** Authentication or access control decisions (token validation, permission checks, role comparisons) written directly in a route handler, controller action, or view function.

**INVALID:**
```python
@app.route("/admin/users")
def list_users():
    if request.headers.get("X-Role") != "admin":
        return 403
    return User.query.all()
```

**Recovery steps:**
1. State: "VIOLATION: Auth logic in handler — `[file]:[line]`"
2. Identify all auth decisions in the handler
3. Prepare extraction to a dedicated auth middleware or decorator

**Proposed fix:**
```python
@app.route("/admin/users")
@require_role("admin")
def list_users():
    return User.query.all()
```

WAIT for human validation before proceeding

Present violation location and proposed fix
IF human approves
  → VALID: Extract auth logic to middleware or decorator
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

---

### 2. Client-side-only Access Control

**Detection:** Access control enforced only by hiding UI elements, checking a flag on the client, or relying on the caller to skip restricted calls — no server-side enforcement.

**INVALID:**
```javascript
// Client hides button — server performs no check
if (user.role === "admin") {
    showAdminPanel();
}
```

**Recovery steps:**
1. State: "VIOLATION: Access control client-side only — `[endpoint]`"
2. Identify the unprotected server endpoint
3. Prepare server-side access check at the service boundary

WAIT for human validation before proceeding

Present unprotected endpoint and proposed server-side check
IF human approves
  → VALID: Add access control check at service boundary
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

---

### 3. Weak Password Storage

**Detection:** Password stored as plaintext, with a reversible cipher, or hashed with a fast algorithm (MD5, SHA-1, SHA-256, unsalted digest).

**INVALID:**
```python
user.password = request.form["password"]                           # plaintext
user.password = hashlib.md5(password.encode()).hexdigest()         # fast hash
user.password = base64.b64encode(password.encode())                # reversible
```

**Recovery steps:**
1. State: "VIOLATION: Weak password storage — `[file]:[line]`"
2. Identify all password storage calls in the codebase
3. Prepare migration to adaptive hash using the project's auth library
4. Confirm existing stored passwords require reset or migration

**Proposed fix:**
```python
import bcrypt
user.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

WAIT for human validation before proceeding

Present storage method and proposed fix
IF human approves
  → VALID: Replace password storage with adaptive hash — confirm migration plan for existing records
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

---

### 4. Session Not Invalidated or Regenerated

**Detection:** Logout handler does not invalidate the session token, or login handler does not regenerate the session ID before establishing the authenticated session.

**INVALID:**
```python
@app.route("/logout")
def logout():
    session.pop("user_id", None)   # clears data but token remains reusable
    return redirect("/login")
```

**Recovery steps:**
1. State: "VIOLATION: Session not invalidated — `[file]:[line]`"
2. Confirm whether session ID is regenerated on login
3. Prepare fix to invalidate session server-side on logout and regenerate session ID on login

**Proposed fix:**
```python
@app.route("/logout")
def logout():
    session.clear()
    session.modified = True        # force new session ID
    return redirect("/login")
```

WAIT for human validation before proceeding

Present logout/login handlers and proposed fix
IF human approves
  → VALID: Add session invalidation on logout and session ID regeneration on login
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

---

### 5. No Security Event Logging

**Detection:** Authentication or authorisation events (failed logins, permission denials, session invalidations) produced with no corresponding log entry — no security audit trail exists for incident investigation or compliance review.

**INVALID:**
```python
@app.route("/login", methods=["POST"])
def login():
    user = authenticate(request.form["username"], request.form["password"])
    if not user:
        return {"error": "Invalid credentials"}, 401   # failure discarded — no audit trail
    session["user_id"] = user.id
    return redirect("/dashboard")
```

**Recovery steps:**
1. State: "VIOLATION: Security event not logged — `[file]:[line]`"
2. Identify auth events lacking log entries: failed logins, permission denials, logouts, role changes
3. Prepare logging calls recording event type, timestamp, and actor — no PII in log values (see CG-DP5)

**Proposed fix:**
```python
@app.route("/login", methods=["POST"])
def login():
    user = authenticate(request.form["username"], request.form["password"])
    if not user:
        logger.warning("auth.failed", extra={"ip": request.remote_addr})
        return {"error": "Invalid credentials"}, 401
    logger.info("auth.success", extra={"user_id": user.id, "ip": request.remote_addr})
    session["user_id"] = user.id
    return redirect("/dashboard")
```

WAIT for human validation before proceeding

Present auth event locations and proposed logging additions
IF human approves
  → VALID: Add security event logging to auth handlers — no PII in log values (CG-DP5)
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

---


### 6. Missing SameSite Cookie Attribute

**Detection:** Session cookie created without an explicit `SameSite` attribute — browser default behaviour for SameSite varies by version; absent attribute does not prevent cross-origin cookie sends.

**INVALID:**
```python
response.set_cookie("session_id", token)   # no SameSite — cross-origin sends not blocked
```

**Recovery steps:**
1. State: "VIOLATION: Session cookie missing SameSite attribute — `[file]:[line]`"
2. Identify all session and authentication cookie creation calls in the codebase
3. Prepare fix to add `SameSite=Strict` (or `Lax` where cross-site navigation with an active session is required)

**Proposed fix:**
```python
response.set_cookie("session_id", token, samesite="Strict", httponly=True, secure=True)
```

WAIT for human validation before proceeding

Present cookie creation call and proposed fix
IF human approves
  → VALID: Add SameSite=Strict (or Lax with written justification) to session cookie
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

---


## Common Rationalisations (FORBIDDEN)

**Agent must refuse these justifications with mandatory counter-responses:**

| User Says | Agent Must Respond |
|-----------|-------------------|
| "It's just a prototype" | "No. Auth patterns are cheaper to establish now than to retrofit later. Applying correct pattern now." |
| "The endpoint isn't public" | "No. Internal endpoints need access control. Network position is not authorisation." |
| "We check permissions in the frontend" | "No. Client-side checks are not access control. Server-side enforcement required." |
| "bcrypt is too slow for our use case" | "Confirm the measured latency. If genuinely unacceptable, argon2id or scrypt offer tunable cost. Fast hashes are not an option." |
| "It's only internal users" | "No. Internal users can be compromised. Role-based access limits blast radius." |
| "We'll add proper auth before go-live" | "No. Fix now. Auth bolted on late introduces regressions and gaps." |
| "CORS is configured, so CSRF is not a risk" | "No. CORS restricts which origins read responses. CSRF exploits the browser sending cookies automatically — it is a separate attack. SameSite attribute and CSRF tokens are the defences." |

**If user persists after mandatory response:** Add a note to the relevant planning document recording the override and the reason given. Then continue.

## Enforcement Summary

**Agent operates under these non-negotiable constraints:**

1. **Compliance gate verification** — All CG-AU gates must pass before auth-related work is complete.
2. **Violation detection** — Agent detects violations and presents proposed fixes. No fix applied without human approval.
3. **Mandatory counter-responses** — Agent uses mandatory counter-responses to rationalisations. Override is documented and noted.

**Agent does NOT act without human approval for:**

- Extracting auth logic to middleware or services
- Adding or modifying access control checks
- Changing password storage mechanisms
- Modifying session handling logic

---
**END OF DOCUMENT:** Total sections: 7 | Purpose: Authentication and authorisation compliance gates, anti-patterns, and enforcement