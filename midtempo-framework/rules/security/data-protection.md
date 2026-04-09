# Data Protection

## Table of Contents

- [Overview](#overview)
- [Compliance Gates](#compliance-gates)
- [Anti-patterns and Auto-recovery](#anti-patterns-and-auto-recovery)
- [Common Rationalisations](#common-rationalisations-forbidden)
- [Enforcement Summary](#enforcement-summary)

---

## Overview

Data protection covers how the system stores, accesses, transmits, and disposes of confidential data — including personally identifiable information (PII), financial records, personal addresses, and any other classified sensitive material. Breaches involving confidential data cannot be undone; regulatory and legal consequences persist long after the technical fix.

**Core principle:** Confidential data is classified, minimised, encrypted, and access-logged throughout its lifecycle. No confidential data persists beyond its declared retention period.

**Role in workflow:** These rules apply to all work that stores, reads, transmits, or deletes confidential data. Agent verifies all compliance gates before declaring data-related work complete.

## Compliance Gates

> Delivery and review skills verify these gates. Each gate must pass for work touching confidential data.

- [ ] **CG-DP1:** Confidential data fields identified in code — comments, type annotations, or schema definitions classify fields containing PII, financial data, or personal addresses at the point of definition
- [ ] **CG-DP2:** PII and sensitive fields encrypted at rest — no plaintext storage of national ID numbers, payment card data, personal addresses, or other directly identifying fields
- [ ] **CG-DP3:** Data minimisation applied — only fields required for the stated purpose stored or returned; no speculative collection
- [ ] **CG-DP4:** Data retention enforced — records past the declared retention period deleted or anonymised; no indefinite retention of personal data
- [ ] **CG-DP5:** Confidential data absent from logs, error messages, and API responses — no PII in log output, stack traces, or debug responses
- [ ] **CG-DP6:** Audit log records read and write access to confidential data — actor, action, data type, and timestamp captured

## Anti-patterns and Auto-recovery

**Agent must detect violations, present the proposed fix, and wait for human approval before making any changes.**

### 1. Plaintext Storage of Confidential Data

**Detection:** Personal data field stored in a database column or file without encryption, with no classification comment or annotation at the point of definition.

**INVALID:**
```python
user.email = request.form["email"]          # stored as plaintext
user.national_id = request.form["nid"]      # no classification, no encryption
```

**Recovery steps:**
1. State: "VIOLATION: Plaintext confidential field — `[field]` in `[file]:[line]`"
2. Identify all unclassified or unencrypted confidential fields in the schema
3. Add classification comment or annotation at point of definition
4. Prepare encryption wrapper before storage using the project's encryption library

**Proposed fix:**
```python
# PII: email address — encrypted at rest
user.email = encrypt(request.form["email"])
# PII: national ID — encrypted at rest
user.national_id = encrypt(request.form["nid"])
```

WAIT for human validation before proceeding

Present field locations and proposed encryption fix
IF human approves
  → VALID: Add classification annotations and apply encryption before storage
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

---

### 2. Confidential Data in Log Output or Error Responses

**Detection:** Log statement that includes a variable holding personal data, or an error response that returns PII in its body.

**INVALID:**
```python
logger.info(f"User registered: {user.email} at {user.address}")
return {"error": f"No account found for {email}"}
```

**Recovery steps:**
1. State: "VIOLATION: Confidential data in output — `[file]:[line]`"
2. Identify what personal data is exposed
3. Prepare replacement that logs non-identifying context only and returns generic error messages to callers

**Proposed fix:**
```python
logger.info(f"User registered: user_id={user.id}")
return {"error": "No account found"}
```

WAIT for human validation before proceeding

Present log statement or error response and proposed fix
IF human approves
  → VALID: Replace output — remove PII from log statements and error responses
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

---

### 3. Over-collection of Personal Data

**Detection:** Form, API endpoint, or database schema collects fields not used in the stated operation — data gathered speculatively or carried over from an earlier design.

**INVALID:**
```python
class RegistrationForm(Form):
    email = StringField()
    name = StringField()
    date_of_birth = DateField()     # not required for registration
    phone_number = StringField()    # not required for registration
    postal_address = StringField()  # not required for registration
```

**Recovery steps:**
1. State: "VIOLATION: Over-collection — `[fields]` in `[file]`"
2. List collected fields against the stated purpose of the operation
3. Identify fields not needed for the operation
4. Prepare schema or form changes to remove unnecessary fields

WAIT for human validation before proceeding

Present collected fields vs required fields for the operation
IF human approves
  → VALID: Remove fields not required — update schema, form, and any downstream consumers
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

---

### 4. No Retention Enforcement

**Detection:** Personal data records exist with no created_at timestamp, no deletion or anonymisation mechanism, and no scheduled cleanup — data retained indefinitely by default.

**INVALID:**
```python
class UserRecord(Base):
    id = Column(Integer, primary_key=True)
    email = Column(String)          # no created_at, no deleted_at
    address = Column(String)        # no retention trigger
    # no cleanup task defined
```

**Recovery steps:**
1. State: "VIOLATION: No retention enforcement — `[table/model]`"
2. Identify the declared retention period from the project policy
3. Prepare created_at timestamp column if absent
4. Prepare deletion or anonymisation function and scheduled trigger

**Proposed fix:**
```python
class UserRecord(Base):
    id = Column(Integer, primary_key=True)
    email = Column(String)
    address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    # scheduled task: anonymise records where created_at < retention_cutoff
```

WAIT for human validation before proceeding

Present model definition and retention policy, propose enforcement mechanism
IF human approves
  → VALID: Add created_at timestamp and scheduled anonymisation or deletion task
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

## Common Rationalisations (FORBIDDEN)

**Agent must refuse these justifications with mandatory counter-responses:**

| User Says | Agent Must Respond |
|-----------|-------------------|
| "It's internal data, not personal" | "No. Classify now. Internal data containing names, addresses, or IDs is PII regardless of who holds it." |
| "Logs are only seen by developers" | "No. Logs are exported, shared, and breached. Remove PII from log output now." |
| "We need all the fields for future use" | "No. Collect only what the current operation requires. Future requirements justify future collection." |
| "Retention is handled by the database team" | "No. Retention must be enforced in code. A policy without a deletion or anonymisation mechanism is not enforced." |
| "It's pseudonymised, not personal data" | "Confirm irreversibility. If a lookup table can re-identify the record, it is personal data. Apply the same protections." |
| "Encryption makes the queries too slow" | "Measure the actual overhead. Encryption at rest does not require query-time decryption for all fields. Identify which fields need indexed plaintext and encrypt the rest." |

**If user persists after mandatory response:** Add a note to the relevant planning document recording the override and the reason given. Then continue.

## Enforcement Summary

**Agent operates under these non-negotiable constraints:**

1. **Compliance gate verification** — All CG-DP gates must pass before data-related work is complete.
2. **Violation detection** — Agent detects violations and presents proposed fixes. No fix applied without human approval.
3. **Mandatory counter-responses** — Agent uses mandatory counter-responses to rationalisations. Override is documented and noted.

**Agent does NOT act without human approval for:**

- Adding or modifying field classification annotations
- Applying encryption to stored fields
- Removing fields from schemas, forms, or API responses
- Adding retention timestamps or scheduled deletion tasks
- Modifying log statements to remove personal data

---
**END OF DOCUMENT:** Total sections: 7 | Purpose: Data protection compliance gates, anti-patterns, and enforcement