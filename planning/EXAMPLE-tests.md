> A worked example of a Test Manifest. Where the Plan described the order of work, this document pins down what "done" looks like: every behaviour, every edge case, every rule the code will be held to.

# Test Manifest: Security Config Model

**Planning doc**: `/planning/security-config-model-plan.md`

**Status**: ✅ Completed

---

## Alignment Checklist

Before completing document, verify:

- [x] **Symmetric coverage**: If the implementation modifies N modules, there are test scenarios for each
- [x] **Algorithm alignment**: Every code path in Section 4 (Implementation Approach) has a corresponding test
- [x] **Error path coverage**: Each distinct error condition (schema validation failure, missing required field, etc.) has at least one test
- [x] **Required field parity**: If schema requires `page` and `description`, validation tests exist for missing `page` and missing `description`

---

## Coverage Target

This iteration targets the following modules from the planning document:

- `scripts/capabilities.py` — Registry contains 3 security flags with correct metadata; `DEFAULT_CAPABILITIES` includes all 3; registry length is 6
- `scripts/generate_schema.py` — `generate_security_properties()` function defined; produces correct schema structure with `patternProperties`, required fields, `additionalProperties: false`
- `schema/config.schema.json` — Schema validation for capabilities (boolean types, individually and combined) and security section (valid entries, required fields, extra properties, key patterns, backward compatibility)
- `tests/helpers/config_factory.py` — `create_valid_config()` omits `security` when not passed; includes `security` when passed; existing factory calls remain valid
- `scripts/generate_docs.py` — `DEFAULT_CAPABILITIES` merge includes all 3 security flags as `False`

| ID | Behaviour | Module | Plan Section |
|----|-----------|--------|--------------|
| B1 | Registry contains `isPublicFacing` with `default: False` and string description | `scripts/capabilities.py` | §3 Test 1.1 |
| B2 | Registry contains `handlesConfidentialData` with `default: False` and string description | `scripts/capabilities.py` | §3 Test 1.2 |
| B3 | Registry contains `hasAuthentication` with `default: False` and string description | `scripts/capabilities.py` | §3 Test 1.3 |
| B4 | `DEFAULT_CAPABILITIES` includes all 3 security flags as `False` | `scripts/capabilities.py` | §3 Test 1.4 |
| B5 | Registry has exactly 6 entries (3 existing + 3 new) | `scripts/capabilities.py` | §3 Test 1.5 |
| B6 | Schema accepts boolean security capability flags individually and combined | `schema/config.schema.json` | §3 Tests 2.1–2.4 |
| B7 | Schema rejects non-boolean value for security capability flag | `schema/config.schema.json` | §3 Test 2.5 |
| B8 | Schema accepts valid security section with one or multiple domain entries | `schema/config.schema.json` | §3 Tests 3.1–3.2 |
| B9 | Schema accepts empty security section (`security: {}`) | `schema/config.schema.json` | §3 Test 3.3 |
| B10 | Config without security section passes validation (backward compatible) | `schema/config.schema.json` | §3 Test 3.4 |
| B11 | Schema rejects security entry missing `page` | `schema/config.schema.json` | §3 Test 3.5 |
| B12 | Schema rejects security entry missing `description` | `schema/config.schema.json` | §3 Test 3.6 |
| B13 | Schema rejects security entry with extra properties | `schema/config.schema.json` | §3 Test 3.7 |
| B14 | Schema rejects security domain key with uppercase | `schema/config.schema.json` | §3 Test 3.8 |
| B15 | Schema rejects security domain key starting with number | `schema/config.schema.json` | §3 Test 3.9 |
| B16 | `generate_schema()` writes security section to schema output | `scripts/generate_schema.py` | §3 Test 4.1 |
| B17 | Security schema section has correct `patternProperties` regex | `scripts/generate_schema.py` | §3 Test 4.2 |
| B18 | Security schema section requires `page` and `description` | `scripts/generate_schema.py` | §3 Test 4.3 |
| B19 | Security schema section has `additionalProperties: false` | `scripts/generate_schema.py` | §3 Test 4.4 |
| B20 | Schema generation preserves existing capabilities and instructions sections | `scripts/generate_schema.py` | §3 Test 4.5 |
| B21 | `create_valid_config()` without security parameter produces config without security key | `tests/helpers/config_factory.py` | §3 Test 5.1 |
| B22 | `create_valid_config()` with security parameter includes security section | `tests/helpers/config_factory.py` | §3 Test 5.2 |
| B23 | Existing factory calls remain valid without changes (backward compatibility) | `tests/helpers/config_factory.py` | §3 Test 5.3 |
| B24 | Capability defaults merge includes security flags | `scripts/generate_docs.py` | §3 Test 6.1 |

---

## Test Scenarios

Progress: Reviewed — PASS (15/02/2026)

### Module: `scripts/capabilities.py` — ✓ Reviewed — all gates passed

**Test file:** `tests/test_security_config_model.py`

#### Test 1.1: Registry contains `isPublicFacing` with correct metadata

**Plan Reference:** B1 — Registry contains `isPublicFacing` with `default: False` and string description

**Concern:** —

**Dependencies:** none

**Complexity:** Low — Single dict lookup, no setup

**Description:** Verifies `isPublicFacing` exists in `CAPABILITIES` with expected default and description type.

**GIVEN:**
- `CAPABILITIES` imported from `scripts.capabilities`

**WHEN:**
- Access `CAPABILITIES["isPublicFacing"]`

**THEN:**
- Key `"default"` equals `False`
- Key `"description"` is a non-empty `str`

#### Test 1.2: Registry contains `handlesConfidentialData` with correct metadata

**Plan Reference:** B2 — Registry contains `handlesConfidentialData` with `default: False` and string description

**Concern:** —

**Dependencies:** none

**Complexity:** Low — Single dict lookup, no setup

**Description:** Verifies `handlesConfidentialData` exists in `CAPABILITIES` with expected default and description type.

**GIVEN:**
- `CAPABILITIES` imported from `scripts.capabilities`

**WHEN:**
- Access `CAPABILITIES["handlesConfidentialData"]`

**THEN:**
- Key `"default"` equals `False`
- Key `"description"` is a non-empty `str`

#### Test 1.3: Registry contains `hasAuthentication` with correct metadata

**Plan Reference:** B3 — Registry contains `hasAuthentication` with `default: False` and string description

**Concern:** —

**Dependencies:** none

**Complexity:** Low — Single dict lookup, no setup

**Description:** Verifies `hasAuthentication` exists in `CAPABILITIES` with expected default and description type.

**GIVEN:**
- `CAPABILITIES` imported from `scripts.capabilities`

**WHEN:**
- Access `CAPABILITIES["hasAuthentication"]`

**THEN:**
- Key `"default"` equals `False`
- Key `"description"` is a non-empty `str`

---

#### Test 1.4: `DEFAULT_CAPABILITIES` includes all 3 security flags as `False`

**Plan Reference:** B4 — `DEFAULT_CAPABILITIES` includes all 3 security flags as `False`

**Concern:** —

**Dependencies:** none

**Complexity:** Low — Dict inspection, no setup

**Description:** Verifies the derived `DEFAULT_CAPABILITIES` export contains all 3 security flags with `False` values.

**GIVEN:**
- `DEFAULT_CAPABILITIES` imported from `scripts.capabilities`

**WHEN:**
- Inspect keys `isPublicFacing`, `handlesConfidentialData`, `hasAuthentication`

**THEN:**
- All 3 keys present with value `False`

---

#### Test 1.5: Registry has exactly 6 entries

**Plan Reference:** B5 — Registry has exactly 6 entries (3 existing + 3 new)

**Concern:** —

**Dependencies:** none

**Complexity:** Low — Single length check

**Description:** Verifies registry contains 6 total entries (3 original + 3 security).

**GIVEN:**
- `CAPABILITIES` imported from `scripts.capabilities`

**WHEN:**
- Check `len(CAPABILITIES)`

**THEN:**
- Length equals 6

---

### Module: `schema/config.schema.json` — ✓ Reviewed — all gates passed

**Test file:** `tests/test_security_config_model.py`

#### Test 2.1: Schema accepts `isPublicFacing` set to true

**Plan Reference:** B6 — Schema accepts boolean security capability flags individually and combined

**Concern:** —

**Dependencies:** filesystem — schema file; function — `create_valid_config()` from `tests/helpers/config_factory.py`

**Complexity:** Medium — Requires valid config creation and schema validation

**Description:** Verifies schema accepts a config with `isPublicFacing: True` in capabilities.

**GIVEN:**
- `create_valid_config({"isPublicFacing": True})`
- Schema loaded from `schema/config.schema.json`

**WHEN:**
- Validate config against schema using `jsonschema.validate()`

**THEN:**
- Validation passes (no exception raised)

#### Test 2.2: Schema accepts `handlesConfidentialData` set to true

**Plan Reference:** B6 — Schema accepts boolean security capability flags individually and combined

**Concern:** —

**Dependencies:** filesystem — schema file; function — `create_valid_config()`

**Complexity:** Medium

**Description:** Verifies schema accepts a config with `handlesConfidentialData: True` in capabilities.

**GIVEN:**
- `create_valid_config({"handlesConfidentialData": True})`

**WHEN:**
- Validate config against schema

**THEN:**
- Validation passes

---

#### Test 2.3: Schema accepts `hasAuthentication` set to true

**Plan Reference:** B6 — Schema accepts boolean security capability flags individually and combined

**Concern:** —

**Dependencies:** filesystem — schema file; function — `create_valid_config()`

**Complexity:** Medium

**Description:** Verifies schema accepts a config with `hasAuthentication: True` in capabilities.

**GIVEN:**
- `create_valid_config({"hasAuthentication": True})`

**WHEN:**
- Validate config against schema

**THEN:**
- Validation passes

---

#### Test 2.4: Schema accepts all 3 security flags combined

**Plan Reference:** B6 — Schema accepts boolean security capability flags individually and combined

**Concern:** —

**Dependencies:** filesystem — schema file; function — `create_valid_config()`

**Complexity:** Medium

**Description:** Verifies schema accepts all 3 security flags set to `True` simultaneously.

**GIVEN:**
- `create_valid_config({"isPublicFacing": True, "handlesConfidentialData": True, "hasAuthentication": True})`

**WHEN:**
- Validate config against schema

**THEN:**
- Validation passes

---

#### Test 2.5: Schema rejects non-boolean value for security flag

**Plan Reference:** B7 — Schema rejects non-boolean value for security capability flag

**Concern:** —

**Dependencies:** filesystem — schema file; function — `create_valid_config()`

**Complexity:** Medium

**Description:** Verifies schema rejects a string value where a boolean is expected.

**GIVEN:**
- `create_valid_config({"isPublicFacing": "yes"})`

**WHEN:**
- Validate config against schema

**THEN:**
- `ValidationError` raised

#### Test 3.1: Schema accepts valid security section with one domain entry

**Plan Reference:** B8 — Schema accepts valid security section with one or multiple domain entries

**Concern:** —

**Dependencies:** filesystem — schema file; function — `create_valid_config()`

**Complexity:** Medium

**Description:** Verifies schema accepts a config with a single valid security domain entry.

**GIVEN:**
- `create_valid_config(security={"owasp-top-10": {"page": "owasp.md", "description": "OWASP Top 10 rules"}})`

**WHEN:**
- Validate config against schema

**THEN:**
- Validation passes

---

#### Test 3.2: Schema accepts valid security section with multiple domain entries

**Plan Reference:** B8 — Schema accepts valid security section with one or multiple domain entries

**Concern:** —

**Dependencies:** filesystem — schema file; function — `create_valid_config()`

**Complexity:** Medium

**Description:** Verifies schema accepts a config with 2+ domain entries.

**GIVEN:**
- `create_valid_config(security={"owasp-top-10": {"page": "owasp.md", "description": "OWASP Top 10"}, "auth-rules": {"page": "auth.md", "description": "Auth rules"}})`

**WHEN:**
- Validate config against schema

**THEN:**
- Validation passes

---

#### Test 3.3: Schema accepts empty security section

**Plan Reference:** B9 — Schema accepts empty security section (`security: {}`)

**Concern:** —

**Dependencies:** filesystem — schema file; function — `create_valid_config()`

**Complexity:** Medium

**Description:** Verifies schema accepts an empty security section.

**GIVEN:**
- `create_valid_config(security={})`

**WHEN:**
- Validate config against schema

**THEN:**
- Validation passes

---

#### Test 3.4: Config without security section passes validation

**Plan Reference:** B10 — Config without security section passes validation (backward compatible)

**Concern:** —

**Dependencies:** filesystem — schema file; function — `create_valid_config()`

**Complexity:** Medium

**Description:** Verifies backward compatibility — configs without security section pass validation.

**GIVEN:**
- `create_valid_config()` with no security parameter

**WHEN:**
- Validate config against schema

**THEN:**
- Validation passes

---

#### Test 3.5: Schema rejects security entry missing `page`

**Plan Reference:** B11 — Schema rejects security entry missing `page`

**Concern:** —

**Dependencies:** filesystem — schema file; function — `create_valid_config()`

**Complexity:** Medium

**Description:** Verifies schema rejects a security entry that omits the required `page` field.

**GIVEN:**
- `create_valid_config(security={"domain": {"description": "desc"}})`

**WHEN:**
- Validate config against schema

**THEN:**
- `ValidationError` raised

---

#### Test 3.6: Schema rejects security entry missing `description`

**Plan Reference:** B12 — Schema rejects security entry missing `description`

**Concern:** —

**Dependencies:** filesystem — schema file; function — `create_valid_config()`

**Complexity:** Medium

**Description:** Verifies schema rejects a security entry that omits the required `description` field.

**GIVEN:**
- `create_valid_config(security={"domain": {"page": "file.md"}})`

**WHEN:**
- Validate config against schema

**THEN:**
- `ValidationError` raised

---

#### Test 3.7: Schema rejects security entry with extra properties

**Plan Reference:** B13 — Schema rejects security entry with extra properties

**Concern:** —

**Dependencies:** filesystem — schema file; function — `create_valid_config()`

**Complexity:** Medium

**Description:** Verifies `additionalProperties: false` blocks extra fields.

**GIVEN:**
- `create_valid_config(security={"domain": {"page": "f.md", "description": "d", "extra": "x"}})`

**WHEN:**
- Validate config against schema

**THEN:**
- `ValidationError` raised

---

#### Test 3.8: Schema rejects security domain key with uppercase

**Plan Reference:** B14 — Schema rejects security domain key with uppercase

**Concern:** —

**Dependencies:** filesystem — schema file; function — `create_valid_config()`

**Complexity:** Medium

**Description:** Verifies `patternProperties` regex rejects uppercase domain keys.

**GIVEN:**
- `create_valid_config(security={"OWASP": {"page": "f.md", "description": "d"}})`

**WHEN:**
- Validate config against schema

**THEN:**
- `ValidationError` raised

---

#### Test 3.9: Schema rejects security domain key starting with number

**Plan Reference:** B15 — Schema rejects security domain key starting with number

**Concern:** —

**Dependencies:** filesystem — schema file; function — `create_valid_config()`

**Complexity:** Medium

**Description:** Verifies `patternProperties` regex rejects keys starting with a digit.

**GIVEN:**
- `create_valid_config(security={"2fa-rules": {"page": "f.md", "description": "d"}})`

**WHEN:**
- Validate config against schema

**THEN:**
- `ValidationError` raised

---

### Module: `scripts/generate_schema.py` — ✓ Reviewed — all gates passed

**Test file:** `tests/test_security_config_model.py`

#### Test 4.1: `generate_schema()` writes security section to schema output

**Plan Reference:** B16 — `generate_schema()` writes security section to schema output

**Concern:** Requires temp file I/O; validates schema generation logic

**Dependencies:** filesystem — temp schema file

**Complexity:** High

**Description:** Verifies `generate_schema()` produces a schema containing `properties.security` with `patternProperties` structure.

**GIVEN:**
- Temp schema file with existing capabilities and instructions sections
- `CAPABILITIES` registry populated with security flags

**WHEN:**
- Call `generate_schema()` with temp schema path
- Read output schema from temp file

**THEN:**
- `schema["properties"]["security"]` exists
- Contains `patternProperties` key

---

#### Test 4.2: Security schema section has correct `patternProperties` regex

**Plan Reference:** B17 — Security schema section has correct `patternProperties` regex

**Concern:** —

**Dependencies:** filesystem — temp schema file

**Complexity:** High

**Description:** Verifies the security section uses `^[a-z][a-z0-9_-]*$` as the regex.

**GIVEN:**
- Temp schema file; `generate_schema()` called

**WHEN:**
- Inspect `schema["properties"]["security"]["patternProperties"]`

**THEN:**
- Key `^[a-z][a-z0-9_-]*$` present

---

#### Test 4.3: Security schema section requires `page` and `description`

**Plan Reference:** B18 — Security schema section requires `page` and `description`

**Concern:** —

**Dependencies:** filesystem — temp schema file

**Complexity:** High

**Description:** Verifies security entry schema declares both fields as required.

**GIVEN:**
- Temp schema file; `generate_schema()` called

**WHEN:**
- Inspect security entry schema's `required` array

**THEN:**
- `"required": ["page", "description"]`

---

#### Test 4.4: Security schema section has `additionalProperties: false`

**Plan Reference:** B19 — Security schema section has `additionalProperties: false`

**Concern:** —

**Dependencies:** filesystem — temp schema file

**Complexity:** High

**Description:** Verifies both the security object and entry object set the flag.

**GIVEN:**
- Temp schema file; `generate_schema()` called

**WHEN:**
- Inspect security schema structure

**THEN:**
- Security object has `"additionalProperties": false`
- Security entry object has `"additionalProperties": false`

---

#### Test 4.5: Schema generation preserves existing capabilities and instructions

**Plan Reference:** B20 — Schema generation preserves existing capabilities and instructions sections

**Concern:** —

**Dependencies:** filesystem — temp schema file with pre-existing sections

**Complexity:** High

**Description:** Verifies schema generation with security does not alter existing sections.

**GIVEN:**
- Temp schema with existing capabilities (`hasUI`, `hasDB`, `hasTypecheck`) and instructions
- Full `CAPABILITIES` registry including security flags
- `generate_schema()` called

**WHEN:**
- Read output schema from temp file

**THEN:**
- Capabilities properties unchanged
- Instructions section unchanged
- Security section added alongside both

---

### Module: `tests/helpers/config_factory.py` — ✓ Reviewed — all gates passed

**Test file:** `tests/test_security_config_model.py`

#### Test 5.1: `create_valid_config()` without security parameter omits `security` key

**Plan Reference:** B21 — `create_valid_config()` without security parameter produces config without security key

**Concern:** —

**Dependencies:** none

**Complexity:** Low

**Description:** Verifies the factory omits the `security` key when no security parameter is passed.

**GIVEN:**
- `create_valid_config()` called with no security argument

**WHEN:**
- Inspect returned dict

**THEN:**
- `"security"` not in returned dict

---

#### Test 5.2: `create_valid_config()` with security parameter includes `security` section

**Plan Reference:** B22 — `create_valid_config()` with security parameter includes security section

**Concern:** —

**Dependencies:** none

**Complexity:** Low

**Description:** Verifies the factory includes the `security` key when a security parameter is passed.

**GIVEN:**
- `create_valid_config(security={"auth": {"page": "auth.md", "description": "Auth rules"}})`

**WHEN:**
- Inspect returned dict

**THEN:**
- `"security"` in returned dict
- Value matches input

---

#### Test 5.3: Existing factory calls remain valid without changes

**Plan Reference:** B23 — Existing factory calls remain valid without changes (backward compatibility)

**Concern:** —

**Dependencies:** none

**Complexity:** Low

**Description:** Verifies all existing factory functions produce valid configs without security parameter.

**GIVEN:**
- Existing factory functions called: `create_valid_config()`, `create_config_with_language()`, etc.

**WHEN:**
- Inspect returned dicts

**THEN:**
- All return valid configs without errors
- No `security` key in returned dicts

---

### Module: `scripts/generate_docs.py` (Integration) — ✓ Reviewed — all gates passed

**Test file:** `tests/test_security_config_model.py`

#### Test 6.1: Capability defaults merge includes security flags

**Plan Reference:** B24 — Capability defaults merge includes security flags

**Concern:** —

**Dependencies:** function — `DEFAULT_CAPABILITIES` from `scripts.capabilities`

**Complexity:** High

**Description:** Verifies that the `DEFAULT_CAPABILITIES` merge produces enriched capabilities with all 3 security flags set to `False`.

**GIVEN:**
- Config with empty capabilities: `{"capabilities": {}}`
- `DEFAULT_CAPABILITIES` populated with 3 security flags

**WHEN:**
- Invoke merge: `{**DEFAULT_CAPABILITIES, **config["capabilities"]}`

**THEN:**
- Enriched config contains `isPublicFacing: False`
- Enriched config contains `handlesConfidentialData: False`
- Enriched config contains `hasAuthentication: False`

---

## Integration Test Scenarios (Service-Dependent)

No service dependencies. All tests use in-memory dict operations, file I/O on temp files, or static imports. No external APIs, databases, or network calls.

---

## Error/Exception Scenarios

Error paths covered by approved scenarios:

- **Test 2.5** — Schema rejects non-boolean capability value; asserts `ValidationError` raised
- **Test 3.5–3.9** — Schema rejects invalid security section (missing required fields, extra properties, invalid key patterns); each asserts `ValidationError` raised
- All capability and security section tests exercise both success and failure paths

---

## Security Test Scenarios

This work does not introduce security-sensitive boundaries (no auth, no secrets, no PII). No new security domains apply.

---

## Notes for Implementation

### Factories (reuse from codebase)

- `create_valid_config()` at `tests/helpers/config_factory.py` — produces a schema-valid config dict for all schema validation tests

### Fixtures (reuse from codebase)

None beyond standard `pytest` fixtures.

### Helpers (reuse from codebase)

- `jsonschema.validate()` — validates configs against real schema file
- Python stdlib `json` — no new utilities required

### Other Notes

- Tests 1.1–6.1 read files directly or call factory/validation functions; no server required
- All tests in `tests/test_security_config_model.py`; no separate test files needed
- Tests are order-independent; file reads and function calls are stateless

---

## Validation

### Coverage Matrix

| Behaviour | Scenarios | Complexity | Status |
|-----------|-----------|------------|--------|
| B1 | T1.1 | 1 Low | ✓ Covered |
| B2 | T1.2 | 1 Low | ✓ Covered |
| B3 | T1.3 | 1 Low | ✓ Covered |
| B4 | T1.4 | 1 Low | ✓ Covered |
| B5 | T1.5 | 1 Low | ✓ Covered |
| B6 | T2.1–T2.4 | 4 Medium | ✓ Covered |
| B7 | T2.5 | 1 Medium | ✓ Covered |
| B8 | T3.1–T3.2 | 2 Medium | ✓ Covered |
| B9 | T3.3 | 1 Medium | ✓ Covered |
| B10 | T3.4 | 1 Medium | ✓ Covered |
| B11 | T3.5 | 1 Medium | ✓ Covered |
| B12 | T3.6 | 1 Medium | ✓ Covered |
| B13 | T3.7 | 1 Medium | ✓ Covered |
| B14 | T3.8 | 1 Medium | ✓ Covered |
| B15 | T3.9 | 1 Medium | ✓ Covered |
| B16 | T4.1 | 1 High | ✓ Covered |
| B17 | T4.2 | 1 High | ✓ Covered |
| B18 | T4.3 | 1 High | ✓ Covered |
| B19 | T4.4 | 1 High | ✓ Covered |
| B20 | T4.5 | 1 High | ✓ Covered |
| B21 | T5.1 | 1 Low | ✓ Covered |
| B22 | T5.2 | 1 Low | ✓ Covered |
| B23 | T5.3 | 1 Low | ✓ Covered |
| B24 | T6.1 | 1 High | ✓ Covered |

**Complexity summary:** 8 Low, 14 Medium, 6 High  
**Orphan scenarios:** None

### Duplicate Resolution

No semantic duplicates detected. Each test covers a distinct behaviour or input variation.

### Rules Alignment

- All assertions test real behaviour — file content, schema validation, dict structure (CG-1) ✓
- No test-only methods required in production code (CG-2) ✓
- Mocks applied at I/O level only (temp schema files for generation tests) (CG-3) ✓
- Mock responses mirror real structures (temp schemas match production format) (CG-4) ✓
- Each test is isolated and order-independent — file reads are stateless; dict operations deterministic (CG-5) ✓
- Coverage complete — success, error, and boundary conditions for each module (CG-6) ✓

---

END OF DOCUMENT
