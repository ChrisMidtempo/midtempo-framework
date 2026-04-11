> This is an example of a Plan document. It sits between Design and Tests: where the Design describes what to build, the Plan maps how to build it - module by module, in order - giving the Test Manifest a firm surface to write against.

# Security Config Model Planning Document

**Design doc**: `/planning/security-config-model-design.md`

**Status**: ✅ Completed

---

## Progress

- Plan: All sections written, alignment checked, exit gates passed
- Implementation: All 24 behaviours implemented and tested (393 tests passing, 92% coverage)
- Documentation: Complete - docstrings, design doc, plan doc updated

---

## 1. Objective

See security-config-model-design.md Section 1 (Problem Statement) and Section 2.1 (Goals).

Summary: Extend the capabilities registry with 3 security flags and add a `security` config section for domain-to-sub-document mapping.

---

## 2. Scope

See security-config-model-design.md Section 2 (Goals & Non-Goals) for complete scope definition.

**In Scope:**

- 3 security capability flags (`isPublicFacing`, `handlesConfidentialData`, `hasAuthentication`) in the `CAPABILITIES` registry
- `security` top-level config section with `patternProperties` validation (mirrors `instructions` pattern)
- Schema generation picks up new flags and security section automatically
- Config factory supports security section for test scenarios
- Backward compatibility — existing configs pass validation without changes

**Out of Scope:**

- Template conditionals using new flags — separate brainstorm
- Security rule sub-document content — downstream work
- Gate enforcement logic — depends on config model first
- Filter/SmartContext changes — not needed for config model
- UI/CLI for managing security config — YAGNI
- `generate_schema_capabilities.py` changes — auto-picks up registry changes; no modification needed
- `generate_docs.py` changes — `DEFAULT_CAPABILITIES` merge handles new flags automatically

---

## 3. Test Strategy: Module Distillation

This work touches five modules: `scripts/capabilities.py` (registry), `scripts/generate_schema.py` (schema generation), `schema/config.schema.json` (validation), `tests/helpers/config_factory.py` (factory), and `scripts/generate_docs.py` (integration).

| Module path | Capabilities covered | Test approach | Concerns |
|---|---|---|---|
| `scripts/capabilities.py` | `CAPABILITIES` contains 3 security flags; `DEFAULT_CAPABILITIES` derives correctly; registry length is 6 | Python dict import and inspection; no setup required | No runtime validation needed; structural correctness only |
| `scripts/generate_schema.py` | `generate_security_properties()` defined; security schema structure correct (`patternProperties`, required fields, `additionalProperties: false`) | Temp schema file; call `generate_schema()`; inspect output structure | Requires temp file I/O; validates schema generation logic |
| `schema/config.schema.json` | Schema accepts valid security capabilities (boolean flags, individually and combined); schema rejects invalid capabilities (non-boolean); schema accepts valid security section (one entry, multiple entries, empty); schema rejects missing `page`/`description`; schema rejects extra properties; schema rejects invalid domain key patterns; backward compatibility (config without security passes) | `create_valid_config()` factory + `jsonschema.validate()`; deliberately invalid configs trigger `ValidationError` | Depends on generated schema file; validates against real schema |
| `tests/helpers/config_factory.py` | `create_valid_config()` omits `security` when parameter not passed; `create_valid_config()` includes `security` when parameter passed; all existing factory functions remain valid | Direct function calls; dict key assertions | No setup; backward compatibility check only |
| `scripts/generate_docs.py` | `DEFAULT_CAPABILITIES` merge in config enrichment includes 3 security flags as `False` | Config with empty capabilities; verify merge result | Integration test; depends on all prior modules |

**Test execution order:**

1. `capabilities.py` — registry tests (leaf module, no dependencies)
2. `generate_schema.py` — schema generation tests (depends on capabilities registry)
3. Schema validation — security capabilities and security section (depends on generated schema)
4. `config_factory.py` — factory tests (depends on registry defaults)
5. `generate_docs.py` — integration tests (depends on all above)

**Test infrastructure:**

- `create_valid_config()` from `tests/helpers/config_factory.py` — produces schema-valid config dict for schema validation tests
- `jsonschema.validate()` — validates configs against real schema file
- Python stdlib `json`, `pathlib` — no new utilities required

---

## 4. Implementation Approach

### 4.0 Decision References

| Decision | Category | Choice | Constraint | Reversibility |
|----------|----------|--------|------------|---------------|
| Security flags live in capabilities | Data Model | Add `isPublicFacing`, `handlesConfidentialData`, `hasAuthentication` to `CAPABILITIES` registry | All 3 flags default to `false` | Simple rollback |
| Security section mirrors instructions | Data Model | `security` top-level section with `patternProperties` key→`{page, description}` | Must use `^[a-z][a-z0-9_-]*$` regex | Simple rollback |

> Extracted from design document Section 3.2 Decision Cards. Each decision's "Affects" field maps to components described below.

### 4.1 Capabilities Registry Extension

Add 3 entries to the `CAPABILITIES` dict in `scripts/capabilities.py`. Each entry follows the existing pattern: a key mapping to `{"default": False, "description": "..."}`.

`DEFAULT_CAPABILITIES` derives from `CAPABILITIES` via dict comprehension (line 33-34). New flags auto-propagate — no code change needed for the derived export.

`generate_docs.py` line 113 merges `DEFAULT_CAPABILITIES` into configs: `{**DEFAULT_CAPABILITIES, **config["capabilities"]}`. New flags appear in generated configs automatically.

### 4.2 Schema Generation — Security Section

`generate_schema.py` produces schema for both capabilities and instructions. Extend `generate_schema()` to also write a `security` section to the schema.

The security section structure is identical to instructions: a `patternProperties` object with `^[a-z][a-z0-9_-]*$` keys mapping to `{page, description}` entries with `additionalProperties: false`.

Add a `generate_security_properties()` function to `scripts/generate_schema.py` that returns the static security schema structure. This function takes no registry input — security domains are user-declared in config, not defined by a registry. The function returns the `patternProperties` object with security-specific property descriptions.

Update `generate_schema()` to call `generate_security_properties()` and write the result to `schema["properties"]["security"]`.

**Why a separate function instead of reusing `generate_instruction_properties()`:** `generate_instruction_properties()` validates registry entries and uses instruction-specific descriptions. Security has no registry and needs its own descriptions ("Path to security rule sub-document" vs "Path to instruction file"). A dedicated function keeps each concern explicit.

### 4.3 Schema Output

Running `npm run schema:generate` updates `schema/config.schema.json`. The updated schema contains:

1. `properties.capabilities.properties` — 6 boolean properties (3 existing + 3 new security flags)
2. `properties.security` — new `patternProperties` section for domain key→`{page, description}` mapping

The `security` property is not added to the `required` array — existing configs without it pass validation unchanged.

### 4.4 Config Factory Extension

Add an optional `security` parameter to `create_valid_config()` in `tests/helpers/config_factory.py`. When provided, the security dict is included in the returned config. When omitted, no `security` key appears — preserving backward compatibility for all existing test callers.

### 4.5 Data Flow

1. Developer adds 3 flags to `CAPABILITIES` registry in `scripts/capabilities.py`
2. Developer adds `generate_security_properties()` to `scripts/generate_schema.py`
3. Developer updates `generate_schema()` to write security section alongside capabilities and instructions
4. `npm run schema:generate` produces updated `schema/config.schema.json` with security capabilities and security section
5. Schema validates configs with new capability flags and optional `security` section
6. `generate_docs.py` merges `DEFAULT_CAPABILITIES` (now including security flags) into config at generation time — no code change needed

### 4.6 Backward Compatibility

- All 3 security flags default to `false` via `DEFAULT_CAPABILITIES` merge — existing configs unchanged
- `security` section is optional (not in `required` array) — existing configs pass validation
- `config_factory.py` security parameter is optional — existing test callers unaffected
- `generate_schema_capabilities.py` auto-picks up new capability flags from registry — no code change needed

---

## 5. Files Affected

### New Files

- `tests/test_security_config_model.py` — 24 test scenarios: registry tests (1.1–1.5), schema capability tests (2.1–2.5), schema security section tests (3.1–3.9), schema generation tests (4.1–4.5), config factory tests (5.1–5.3), integration test (6.1)

### Modified Files

- `scripts/capabilities.py` — Add 3 entries to `CAPABILITIES` dict: `isPublicFacing`, `handlesConfidentialData`, `hasAuthentication`. Each entry: `{"default": False, "description": "..."}`. `DEFAULT_CAPABILITIES` auto-derives via dict comprehension (line 33–34).

- `scripts/generate_schema.py` — Add `generate_security_properties()` function returning static `patternProperties` schema structure for security section. Update `generate_schema()` to write `schema["properties"]["security"]` from this function's output.

- `tests/helpers/config_factory.py` — Add optional `security: dict | None = None` parameter to `create_valid_config()`. When provided, include `security` key in returned config dict. When omitted, `security` key does not appear (backward compatible).

### Framework Integration

Configuration data model only. No new architectural layers, error handling patterns, or component boundaries. Existing patterns (registry-driven schema generation, config factory) extended following established conventions.

**Schema file generation:** `npm run schema:generate` produces `schema/config.schema.json` with 3 new boolean properties in `capabilities.properties` and a new `security` top-level property with `patternProperties` validation. Not hand-edited.

---

## 6. Dependencies

### Packages

No new packages required. All changes use existing Python stdlib, `jsonschema`, and Jinja2 (already present in `requirements.txt`).

### Environment Variables

None.

### External Services

None.

### Backward Compatibility

- All 3 security flags default to `false` via `DEFAULT_CAPABILITIES` merge — existing configs unchanged
- `security` section is optional (not in `required` array) — existing configs pass validation
- `config_factory.py` security parameter is optional — existing test callers unaffected
- `generate_schema.py` auto-picks up new capability flags from registry — no code change needed for schema generation

---

## 7. Type Definitions

No new Python types introduced. This work extends existing data structures (registry dict, schema object, config factory) without changing type signatures. All changes use standard Python types: `dict`, `bool`, `str`, `None`.

---

## 8. API Contracts

No API contracts introduced or changed. This work is configuration-only — no HTTP endpoints or RPC contracts affected.

---

## 9. Schema Compliance

All changes follow existing schema patterns:

- **Capability flag structure** — Matches existing pattern: `{"default": bool, "description": str}`
- **Security section structure** — Mirrors `instructions` pattern: `patternProperties` with `^[a-z][a-z0-9_-]*$` key validation and `{page, description}` entry structure
- **Backward compatibility** — New fields are optional or default to `false`; existing configs remain valid without modification
- **Schema generation** — Follows established registry-driven pattern used for capabilities and instructions

---

END OF DOCUMENT
