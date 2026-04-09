# [Feature Name] Planning Document

**Design doc**: `/planning/[feature-name]-design.md`  
**Status**: Draft

---

## Progress

- Phase [N]: [Brief description of what was delivered/changed in this phase]
- Phase [N-1]: [Previous phase completion notes]

**Current focus**: [What's being worked on right now]

---

## 1. Objective

See [feature name]-design.md Section 1 (Problem Statement) and Section 2.1 (Goals).

Summary: [One Line Summary].
---

## 2. Scope

See [feature name]-design.md Section 2 (Goals & Non-Goals) for complete scope definition.

In Scope Summary:
[bullet list of in-scope titles]


Out of Scope Summary:
[bullet list of out-of-scope titles]

---

## 3. Test Strategy: Module Distillation

Read from the design document before writing this section:

- §3.3 Architecture/Components — module inventory: path, responsibility, dependencies
- §3.6 Error Handling — error concerns per module
- §3.7 Security — security concerns per module
- §3.8 Performance — performance concerns per module

**Distillation table** — one row per module from §3.3. Each cell: a phrase, not a scenario.

| Module path | Capabilities covered | Test approach | Concerns |
|-------------|---------------------|---------------|----------|
| `path/to/module.ext` | [Scope items this module implements] | unit / integration / special setup | [From §3.6–3.8, or — if none] |
| `path/to/another.ext` | [Capabilities] | unit | — |

> If §3.3 responsibility descriptions are vague, surface the vagueness here
> rather than passing it through.

**Test execution order** (dependency order from §3.3 Dependencies column):

1. `path/to/module.ext` — [reason for position]
2. `path/to/another.ext` — [reason]

---

## 4. Implementation Approach

[Technical design showing how the solution works. Include:]

- Architecture decisions and patterns
- Data flow between components
- Key algorithms or business logic
- Integration points with existing systems
- Security/performance considerations

### 4.0 Decision References

| Decision | Category | Choice | Constraint | Reversibility |
| -------- | -------- | ------ | ---------- | ------------- |
| [Name]   | [Cat]    | [What] | [Limit]    | [Type]        |

> Extracted from design document Section 3.2 Decision Cards. Each decision's "Affects" field maps to components described below.

### 4.1 Frontend Design & Component Structure

All UI work for this feature MUST conform to the frontend-design rules (see `/midtempo-framework/instructions/frontend-design.md`)

[Describe in detail the design and component structure]

### [Optional: Subsection for complex areas]

[Detailed explanation of a specific technical approach]

---

## 5. Files Affected

### New Files

- `/path/to/new/file.extension` - [Brief description of purpose]
- `/path/to/different/files.extension` - [Brief description of purpose]

> For every new UI component, clearly state its atomic layer (atom/molecule/organism/template/page) and ensure the import hierarchy is adhered to. 
### Modified Files

- `path/to/existing/file.ext` — [What changes and why]
- `path/to/another/file.ext` — [Specific modifications needed]

### Framework Integration (for new pages only)
Read `/midtempo-framework/instructions/new-page.md`

---

## 6. Dependencies

### Packages

- `package-name@version` — [Why it's needed, what it provides]
- `another-package` — [Already in package.json / needs adding]

### Environment Variables

- `ENV_VAR_NAME` — [Purpose, default value, required/optional]
- `ANOTHER_VAR` — [Description and usage]

### External Services

- [Service name] — [What we need from it, any setup required]

---

## 7. Type Definitions

[If introducing new types or significant type changes]
```
// src/types/[types-file-name].ext

TYPE NewType:
  property: string
  another_property: number

UNION UnionType: "option_a" | "option_b" | "option_c"
```

---

## 8. API Contracts

[If creating or modifying API endpoints, document the contract.]

### POST /api/tracks/:id/biography

**Request**: `{ biography: string, source?: string }`
**Success (200)**: `{ id: number, biography: string, updated_at: string }`
**Error (404)**: `{ error: string }`

---

### GET /api/search/artists

**Request**: Query params `?name=string&limit=number`
**Success (200)**: `{ artists: Artist[], total: number }`
**Error (400)**: `{ error: string, validation: Record<string, string> }`

---
## 9. UI Compliance

- ALL components MUST adhere to our `/midtempo-framework/instructions/frontend-design.md` rules
- ALL styling elements MUST follow rules in `/midtempo-framework/instructions/style-guide.md`
---

END OF DOCUMENT