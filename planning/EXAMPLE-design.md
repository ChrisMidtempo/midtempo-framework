> This is an example of a Design document — produced after Decisions, it translates the agreed idea into a concrete technical shape: the components involved, how they fit together, and the contracts between them. This doc becomes the feature's single source of truth.
>
> Note the end-of-delivery Implementation Summary and, at the end of the file, a post-delivery [refinement](#refinement---security-domain-path-routing). 

# Security Config Model Design Document

**Status**: ✅ Completed

---

## Implementation Summary

**Completed**: 15/02/2026

**Files Modified:**
- `scripts/capabilities.py` - Added 3 security capability flags to registry
- `scripts/generate_schema.py` - Added `generate_security_properties()` function
- `tests/helpers/config_factory.py` - Added optional `security` parameter
- `schema/config.schema.json` - Generated schema with security section

**Files Created:**
- `tests/test_security_config_model.py` - 411 lines, 24 test scenarios covering all behaviours

**Implementation Matched Design:**
The implementation followed the design exactly with no deviations. All three security capability flags (`isPublicFacing`, `handlesConfidentialData`, `hasAuthentication`) were added to the `CAPABILITIES` registry with `default: False`. The `security` section mirrors the `instructions` pattern with `patternProperties` validation. Schema generation picks up new flags automatically. All backward compatibility requirements met - existing configs pass validation without changes.

**Test Coverage:**
- 24 behaviours tested across 6 modules
- 393 tests passing, 92% coverage
- Registry, schema validation, schema generation, config factory, and integration all verified

**No Architectural Changes:**
Implementation added data model elements only. No new architectural layers, error handling patterns, or component boundaries introduced. Existing patterns (registry-driven schema generation, config factory) extended following established conventions.

---

## 1. Problem Statement

### 1.1 Current Situation

The capabilities system supports 3 boolean flags (`hasUI`, `hasDB`, `hasTypecheck`) with `additionalProperties: false` locking the schema. Repos cannot declare security properties or map security domains to sub-documents.

**Evidence:**

- Schema rejects unknown capability keys — adding security flags requires schema changes
- No config section exists for mapping security domains to rule sub-documents
- Repos with different risk profiles (public-facing vs internal, confidential data vs open) share the same boolean surface

### 1.2 Root Cause

The capabilities schema was designed for build-tool flags, not security properties. `additionalProperties: false` prevents extension without explicit schema changes. No domain-mapping pattern exists outside `instructions`.

---

## 2. Goals & Non-Goals

### 2.1 Goals

**Primary:**

1. Capabilities accept 3 security flags (`isPublicFacing`, `handlesConfidentialData`, `hasAuthentication`) as independent booleans with `default: false`
2. A `security` config section maps domain keys to sub-document metadata (page + description)

**Secondary:**

- Schema generation picks up new flags automatically via the existing registry pattern

### 2.2 Explicitly Out of Scope

- Template conditionals using new flags
  - **Reason:** Separate brainstorm — this covers config model only
- Security rule sub-document content
  - **Reason:** Downstream work after config model exists
- Gate enforcement logic
  - **Reason:** Separate brainstorm — depends on config model being in place first
- Filter/SmartContext changes
  - **Reason:** Not needed for config model
- UI/CLI for managing security config
  - **Reason:** YAGNI

### 2.3 Acceptance Criteria

- `capabilities` in schema accepts `isPublicFacing`, `handlesConfidentialData`, and `hasAuthentication` (all boolean)
- `capabilities.py` registry includes all 3 flags with `default: false`
- `security` section in schema validates domain key→page/description mapping (same pattern as `instructions`)
- `config_factory.py` produces configs with security section
- Existing configs without security section pass validation (backward compatible)
- Generation pipeline merges security capability defaults (same pattern as existing capabilities)
- Schema generation script picks up new flags automatically

---

## 3. Proposed Solution

### 3.1 Overview

Extend the existing registry-driven schema generation pattern to support security configuration. Add 3 security flags (`isPublicFacing`, `handlesConfidentialData`, `hasAuthentication`) to the `CAPABILITIES` registry in `capabilities.py`. Add a `security` top-level section to `config.schema.json` using the same `patternProperties` structure as `instructions`. Extend `generate_schema.py` to produce the `security` schema section alongside capabilities and instructions.

No new modules, abstractions, or dependencies. The `security` section is structurally identical to `instructions` — both map domain keys to page/description metadata. All changes are additive and backward compatible.

### 3.2 Key Design Decisions

#### Decision 1: Security flags live in capabilities

**Category:** Data Model
**Choice:** Add `isPublicFacing`, `handlesConfidentialData`, and `hasAuthentication` to the existing `CAPABILITIES` registry.
**Rationale:** Security flags are boolean repo properties — same nature as `hasUI` and `hasDB`. The registry pattern auto-propagates to schema via `generate_schema_capabilities.py`. No new abstraction needed.

**Rejected:**

- Separate security flags object: Fragments boolean properties across two schema locations
- Enum-based risk tier: Loses independent axis granularity (public-facing AND confidential are orthogonal)

**Plan Handoff:**

- **Affects:** `capabilities.py`, `config.schema.json`
- **Constraint:** All 3 flags default to `false`
- **Reversibility:** Simple rollback

#### Decision 2: Security section mirrors instructions pattern

**Category:** Data Model
**Choice:** Add a `security` top-level config section using `patternProperties` with key→`{page, description}` structure, identical to `instructions`.
**Rationale:** The `instructions` pattern is proven, schema-validated, and understood by the generation pipeline. Security domain mapping has the same shape — a domain key pointing to a sub-document page with a description.

**Rejected:**

- Nested under capabilities: Capabilities are booleans; domain mappings are a different concern
- Array of security rules: Loses key-based lookup; harder to reference individual domains

**Plan Handoff:**

- **Affects:** `config.schema.json`, `generate_schema.py`
- **Constraint:** Must use same `patternProperties` regex as instructions (`^[a-z][a-z0-9_-]*$`)
- **Reversibility:** Simple rollback

---

### 3.3 Architecture

**Components:**

| Component | Responsibility | Dependencies |
|-----------|---------------|--------------|
| `capabilities.py` | Registry — adds 3 security flags with metadata and defaults | None (leaf module) |
| `config.schema.json` | Schema — validates security flags in capabilities + `security` section structure | Generated from registries |
| `generate_schema.py` | Generation — produces `security` schema section from `instructions` patternProperties pattern | `capabilities.py`, `instructions.py` |
| `config_factory.py` | Factory — produces configs with security section for test scenarios | `capabilities.py` |

**Data Flow:**

1. Developer adds security flags to `CAPABILITIES` registry in `capabilities.py`
2. `npm run schema:generate` runs `generate_schema.py` which reads registries and writes updated schema
3. Schema validates configs with new capability flags and optional `security` section
4. `generate_docs.py` merges `DEFAULT_CAPABILITIES` (now including security flags) into config at generation time

**Integration Points:**

- `generate_docs.py` line 113
  - **Interface:** `{**DEFAULT_CAPABILITIES, **config["capabilities"]}` merge
  - **Contract:** New flags picked up with no code change — merge spreads all registry defaults
- `generate_schema_capabilities.py`
  - **Interface:** `generate_properties()` function
  - **Contract:** Iterates `CAPABILITIES` registry — new flags auto-included in schema output

---

### 3.4 Data Model

**New Entities:**

```yaml
# Capabilities registry additions (capabilities.py)
isPublicFacing:
  type: boolean
  default: false
  description: "Application serves public-facing traffic"

handlesConfidentialData:
  type: boolean
  default: false
  description: "Application processes confidential or sensitive data"

hasAuthentication:
  type: boolean
  default: false
  description: "Application implements authentication"
```

```yaml
# Security section structure (config.schema.json)
security:
  <domain-key>:          # matches ^[a-z][a-z0-9_-]*$
    page: string         # required — path to security rule sub-document
    description: string  # required — human-readable domain summary
```

**Modified Entities:**

- `CAPABILITIES` registry in `capabilities.py`
  - **Changes:** 3 new boolean entries added to existing registry dict
  - **Reason:** Security flags follow the same boolean property pattern as existing capabilities
- `config.schema.json`
  - **Changes:** New `security` top-level property with `patternProperties` validation
  - **Reason:** Mirrors `instructions` section structure for domain key→metadata mapping

**State Requirements:**

- All state persists in YAML config files and JSON schema — no runtime state
- Security flags default to `false` via `DEFAULT_CAPABILITIES` merge — transient at generation time
- Security domain mappings are declarative config — no derived state

---

### 3.5 User Experience

N/A — This feature changes the config model only. No UI, CLI, or interactive user journey involved.

**Developer Journey:**

1. Developer adds security capability flags to their repo's YAML config (e.g. `isPublicFacing: true`)
2. Developer optionally adds `security` section mapping domain keys to rule sub-documents
3. `npm run schema:generate` validates the config against the updated schema
4. Generation pipeline merges security defaults and produces output with security properties

**Config Changes:**

- New optional boolean flags in `capabilities` section
  - **Reason:** Declares security properties for the repo
- New optional `security` top-level section
  - **Reason:** Maps security domains to sub-document metadata

---

### 3.6 Error Handling & Edge Cases

**Error Scenarios:**

| Error Condition | Expected Behaviour | User Experience |
|---|---|---|
| Unknown capability flag in config | Schema validation rejects config | Clear error: `additionalProperties: false` names the invalid key |
| Security domain key fails regex | Schema validation rejects config | Clear error: key does not match `^[a-z][a-z0-9_-]*$` |
| Security entry missing `page` or `description` | Schema validation rejects config | Clear error: required property missing |
| Security entry has extra properties | Schema validation rejects config | Clear error: `additionalProperties: false` on entry |

**Edge Cases:**

- Empty `security` section (`security: {}`)
  - **Handling:** Valid — schema allows zero domain entries. Section is optional with no minimum items.
- Config omits `security` section entirely
  - **Handling:** Valid — `security` is not in the `required` array. Backward compatible with existing configs.
- All 3 security flags left at default (`false`)
  - **Handling:** Valid — `DEFAULT_CAPABILITIES` merge provides defaults. No config change needed for repos without security concerns.

---

### 3.7 Security & Privacy

**Security Considerations:**

- Schema injection via domain keys
  - **Mitigation:** `patternProperties` regex (`^[a-z][a-z0-9_-]*$`) restricts keys to lowercase alphanumeric with hyphens/underscores. No special characters, spaces, or path traversal sequences accepted.
- Arbitrary properties in security entries
  - **Mitigation:** `additionalProperties: false` on each security entry — only `page` and `description` accepted.
- Security flags misrepresenting repo risk profile
  - **Mitigation:** Flags default to `false` (secure default). Repos opt in to security properties explicitly.

**Privacy Implications:**

- No personal data involved. Security flags and domain mappings describe repo properties, not user data.
  - **Approach:** N/A — config model contains no sensitive information.

---

### 3.8 Performance Mitigations

**Data Model Efficiency:**

- N/A — No database. Config is static YAML validated against JSON Schema at generation time.

**Query & Data Access Patterns:**

- N/A — No queries. Schema generation reads registry dicts in memory.

**Caching Strategy:**

- N/A — No caching needed. Schema generation runs once per `npm run schema:generate` invocation.

**Algorithmic Choices:**

- Registry iteration is O(n) where n = number of capability flags (currently 6). Negligible.
- `patternProperties` regex matching is O(k) per domain key where k = key length. Negligible.

**Explicitly Not Optimising:**

- Schema generation speed — runs infrequently as a dev-time command, not at runtime.

---

## 4. Dependencies & Constraints

### 4.1 External Dependencies

- None. All changes use existing Python stdlib and Jinja2.

### 4.2 Technical Constraints

- `additionalProperties: false` on capabilities
  - **Impact:** New flags only appear in schema after running `npm run schema:generate`. Schema generation must run before validation accepts new flags.
- Schema generation ordering
  - **Impact:** `generate_schema.py` processes capabilities → instructions → security to maintain consistent output.
- Backward compatibility
  - **Impact:** The `security` section must be optional (not in `required` array). Existing configs without it pass validation unchanged. Security capability flags default to `false` via `DEFAULT_CAPABILITIES` merge.

### 4.3 Compatibility Requirements

- All 5 existing agent configs
  - **Requirement:** Pass validation without changes after schema update
  - **Reason:** Additive-only changes — no existing fields modified or removed
- `config_factory.py` test helper
  - **Requirement:** Existing test calls produce valid configs without passing security parameters
  - **Reason:** Security section parameter is optional — existing callers unaffected

---

## 5. Testing Strategy Principles

### 5.1 Testability Requirements

- Registry entries testable via direct dict inspection — no IO needed
- Schema validation testable via `jsonschema.validate()` against generated schema
- Config factory testable by asserting output structure matches expected shape

### 5.2 Test Coverage Areas

**Functional:**

- 3 new capability flags accepted by schema with correct types and defaults
- `security` section validates domain key→`{page, description}` entries
- `security` section rejects invalid keys, missing properties, and extra properties
- Config factory produces configs with and without security section

**Non-Functional:**

- Backward compatibility — existing configs pass validation after schema update

**Integration:**

- `generate_schema.py` produces schema containing security section from registries
- `generate_docs.py` merges security capability defaults into generated output

### 5.3 Test Data Requirements

- Valid config fixtures with security flags enabled and `security` section populated
- Valid config fixtures without security section (backward compatibility)
- Invalid config fixtures with bad domain keys, missing fields, and extra properties

---

## 6. Migration

### 6.1 Migration Requirements

**Data Migration:**

- No data migration needed. All changes are additive. Existing YAML configs remain valid without modification.

**Feature Migration:**

- No feature transition needed. New capability flags default to `false`. The `security` section is optional. Repos adopt security config at their own pace.

---

## 7. Open Questions

No open questions — all resolved during design.

---

## 8. References

**Related Documents:**

- Decisions document: `/planning/security-config-model-decisions.md`
- Investigation: `/planning/investigations/security-rules-orchestrator-rec-1-config-model.md`

---

## Refinement - Security Domain Path Routing

**16/02/2026** - Route security domain file paths based on configuration source (explicit vs auto-detected)

**Context**

Security domain documentation gets regenerated from templates (`/midtempo-framework/rules/security/`), preventing repos from maintaining bespoke security rules that persist across regeneration. The `instructions/` folder is client-maintained and never regenerated, making it the correct location for repo-specific bespoke documentation.

**Changes**

- Explicit security config in `.yml` → macros read from `/midtempo-framework/instructions/{page}`
- Auto-detected security domains → macros read from `/midtempo-framework/rules/security/{domain}.md`
- Updated `conditional_security_reads()` macro with conditional path routing
- Updated `verify_compliance_gates_security()` macro with conditional path routing

**Rationale**

Repos requiring bespoke security documentation cannot use regenerated templates. By routing explicit security config to the `instructions/` folder, repos can define custom security rules that persist across framework regeneration whilst maintaining auto-detection for standard use cases.

**Testing**

- `tests/test_macros.py:198-226` - Explicit config routes to instructions/
- `tests/test_macros.py:229-264` - Auto-detected routes to rules/security/

---

## Approval

**Design Review:**

- [x] Technical feasibility verified
- [x] Security reviewed
- [x] Performance mitigations appropriate
- [x] Testing approach sound
- [x] Dependencies identified
- [x] Trade-offs acceptable
- [x] Open questions resolved or assigned

**Next step:** Create planning document using `write-plan.md` skill

---

END OF DOCUMENT
