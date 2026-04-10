> An example of a Decisions document. It's the starting point for any new piece of work: the framework interviews you about the idea, writes down what's been agreed, and uses it as the source of truth for the design doc that come next.

# Security Config Model — Decisions

**Status:** ✅ Completed

**Branch:** security-rules

---

## Understanding Summary

**Problem:** The capabilities system is locked to 3 boolean flags with no security configuration structure. Repos with different risk profiles cannot declare security properties or map security domains to sub-documents.

**Acceptance Criteria:**

- [ ] `capabilities` in schema accepts `isPublicFacing`, `handlesConfidentialData`, and `hasAuthentication` (all boolean)
- [ ] `capabilities.py` registry includes all 3 flags with `default: false`
- [ ] `security` section in schema validates domain key→page/description mapping (same pattern as `instructions`)
- [ ] `config_factory.py` produces configs with security section
- [ ] Existing configs without security section pass validation (backward compatible)
- [ ] Generation pipeline merges security capability defaults (same pattern as existing capabilities)
- [ ] Schema generation script picks up new flags automatically

**Out of Scope:**

- Template conditionals using new flags — separate brainstorm
- Security rule sub-document content — downstream work
- Gate enforcement logic — separate brainstorm
- Filter/SmartContext changes — not needed for config model
- UI/CLI for managing security config — YAGNI

**Constraints:**

- Registry-driven schema generation pattern (architecture §3.4)
- `additionalProperties: false` on capabilities schema block
- `instructions` patternProperties precedent for `security` section
- Backward compatibility for existing configs
- No new dependencies

---

## Approach Evaluation

### Approaches Considered

**Approach A — New registry module (`security.py`):** Add flags to `CAPABILITIES` registry, add `security` section schema via a new `SECURITY` registry in a new `security.py` module.

**Approach B — Extend existing `generate_schema.py`:** Add flags to `CAPABILITIES` registry, extend the existing schema generation to handle a `security` section using the same `instructions` patternProperties pattern. No new module.

**Approach C — Manual schema:** Add flags to `CAPABILITIES` registry, hand-write the `security` schema section directly in `config.schema.json`. No registry for security domains.

### Impact Assessment

| Criterion | Approach A (New module) | Approach B (Extend existing) | Approach C (Manual schema) |
|---|---|---|---|
| Complexity | 6 files, 1 new module | 5 files, 0 new abstractions | 4 files, 0 new abstractions |
| Breaking changes | None | None | None |
| Pattern alignment | Extends | Follows | Deviates |
| Reversibility | Simple rollback | Simple rollback | Simple rollback |
| New dependencies | None | None | None |

### Per-Approach Analysis

**Approach A:** Clean separation for security domains. Adds a module for a structure identical to `instructions` — more files without distinct behaviour. Assumes security domains diverge from instructions over time.

**Approach B:** Zero new abstractions. Reuses the proven `instructions` patternProperties structure. `generate_schema.py` already handles capabilities and instructions — adding security follows the same path. Assumes security domain mapping stays structurally identical to instructions.

**Approach C:** Fewest files touched. Breaks the registry-driven pattern (CG-2). Security schema drifts from single source of truth. Assumes security section rarely changes.

### Recommendation: Approach B — Extend Existing

**Reasoning:** The `security` section is structurally identical to `instructions` — both map domain keys to page/description metadata. Approach B reuses the `instructions` patternProperties pattern with no new abstractions, following architecture §3.4 (registry-driven schema generation).

**Validated against:**
- Architecture §3.4 — registry-driven schema generation
- Existing `instructions` patternProperties pattern
- Error handling §5.4 — no new error patterns needed

**Runner-up rejection:** Approach A adds a module without adding distinct behaviour. If security domains later need richer metadata, we extract a module then.

**Reversibility:** Simple rollback — all changes additive.

**Devil's advocate:** `generate_schema.py` becomes responsible for 3 concerns (capabilities, instructions, security). However, security follows the exact same pattern as instructions. The coupling is structural, not behavioural.

---

## Design

### Section 1: Problem & Goals

The capabilities system supports only 3 boolean flags (`hasUI`, `hasDB`, `hasTypecheck`) with `additionalProperties: false` locking the schema. Repos cannot declare security properties or map security domains to sub-documents.

**Primary goals:**

1. Capabilities accept 3 security flags (`isPublicFacing`, `handlesConfidentialData`, `hasAuthentication`) as independent booleans
2. A `security` config section maps domain keys to sub-document metadata

**Secondary goals:**

- Schema generation picks up new flags automatically via the existing registry pattern

**Out of scope:** Template conditionals, security rule content, enforcement logic, filter changes, CLI tooling. This covers the config model foundation only.

**Acceptance criteria:**

- Schema validates new capability flags and security domain mappings
- Existing configs without security section pass validation
- Generation pipeline merges security capability defaults

### Section 2: Solution & Decisions

Extend the existing registry-driven schema generation pattern. Add 3 security flags to the `CAPABILITIES` registry in `capabilities.py`. Add a `security` top-level section to `config.schema.json` using the same `patternProperties` structure as `instructions`. Extend `generate_schema.py` to generate the `security` schema section alongside capabilities and instructions.

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

### Section 3: Architecture & Data

**Components:**

| Component | Responsibility | Dependencies |
|-----------|---------------|--------------|
| `capabilities.py` | Registry — adds 3 security flags with metadata and defaults | None (leaf module) |
| `config.schema.json` | Schema — validates security flags in capabilities + `security` section structure | Generated from registries |
| `generate_schema.py` | Generation — produces `security` schema section from `instructions` patternProperties pattern | `capabilities.py`, `instructions.py` |
| `config_factory.py` | Testing — produces configs with security section for test scenarios | `capabilities.py` |

**Data flow:**

1. Developer adds security flags to `CAPABILITIES` registry in `capabilities.py`
2. `npm run schema:generate` runs `generate_schema.py` which reads registries and writes updated schema
3. Schema validates configs with new capability flags and optional `security` section
4. `generate_docs.py` merges `DEFAULT_CAPABILITIES` (now including security flags) into config at generation time

**Config structure (YAML):**

```yaml
capabilities:
  hasUI: true
  isPublicFacing: true
  handlesConfidentialData: true
  hasAuthentication: false

security:
  secrets-management:
    page: 'secrets-management.md'
    description: 'Credential handling and leak prevention'
  input-validation:
    page: 'input-validation.md'
    description: 'Input sanitisation and output encoding'
```

**Integration points:**

- `generate_docs.py` line 113 — existing `{**DEFAULT_CAPABILITIES, **config["capabilities"]}` merge picks up new flags with no code change
- `generate_schema_capabilities.py` — existing `generate_properties()` picks up new flags with no code change

### Section 4: Constraints

**Dependencies:** None. All changes use existing Python stdlib and Jinja2.

**Technical constraints:**

- **`additionalProperties: false` on capabilities** — New flags only appear in schema after running `npm run schema:generate`. Schema generation must run before validation accepts new flags.
- **Schema generation ordering** — `generate_schema.py` processes capabilities → instructions → security to maintain consistent output.
- **Backward compatibility** — The `security` section must be optional (not in `required` array). Existing configs without it pass validation unchanged. Security capability flags default to `false` via `DEFAULT_CAPABILITIES` merge.

**Security mitigations:**

- Schema validation prevents arbitrary keys in `security` entries — only `page` and `description` accepted (`additionalProperties: false` on each entry)
- `patternProperties` regex (`^[a-z][a-z0-9_-]*$`) prevents injection via domain keys

**Compatibility:**

- All 5 existing agent configs continue to pass validation without changes
- `config_factory.py` gains optional security section parameter — existing test calls unaffected

---

END OF DOCUMENT
