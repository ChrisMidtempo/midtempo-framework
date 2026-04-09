# Agentic Framework Frontend Design

## Table of Contents

- [Organisation](#1-organisation)
- [Composition Patterns](#2-composition-patterns)
- [Component Structure](#3-component-structure)
- [State & Data Patterns](#4-state--data-patterns)
- [Compliance Gates](#5-compliance-gates)
- [Quick Reference](#6-quick-reference)

---

## 1. Organisation

### 1.1 Approach

Flat file structure — one file per concern. No component framework, no build step, no module bundler. Files are served as static assets by the FastAPI server.

### 1.2 Directory Structure

```
ui/
  index.html          # Page shell; loads CDN deps; references style.css and form.js
  style.css           # All presentation: layout, form styles, error states, modal
  form.js             # Coordinator: state, event wiring, server calls
  docs-modal.js       # Documentation modal: open/close, tabs, fetch, cache
  command-modal.js    # Command builder rows and command-entry modal
  name-field.js       # Name field validation, preview, init button, file upload, language select
  event-wiring.js     # DOMContentLoaded event wiring
  schema.json         # Symlink to schema/config.schema.json; fetched at runtime
  languages.json      # Built by build_ui_manifest.py; consumed by form.js on load
server/
  app.py              # FastAPI app; serves ui/ as static files; POST and GET endpoints
  models.py           # Pydantic request models (InitRequest, GenerateRequest)
```

### 1.3 form.js Internal Structure

`form.js` is the coordinator. It owns state and event wiring. Function groups in order:

```
  State              — single state object; mutation functions; derived instructions
  Entry routing      — New / Existing flow decision and transition
  Form population    — populate fields from state object
  Validation         — ajv validation; error rendering per field
  YAML panel         — js-yaml serialisation; panel refresh
  Server calls       — fetch() wrappers: /api/init, /api/generate
  Modal              — download modal: render, show, close
  Event wiring       — all addEventListener calls (runs on DOMContentLoaded)
```

Companion modules (`name-field.js`, `command-modal.js`) are imported into `form.js` via ES module `import`. They do not import from `form.js`. State is injected into `command-modal.js` via `init(state, setState)` at `DOMContentLoaded`.

### 1.4 Placement Rules

- Browser logic → `form.js` and named companion modules (see §1.5)
- Presentation → `style.css` only
- Structure and CDN script tags → `index.html` only
- Never inline styles in `index.html`, `form.js`, or companion modules
- Never inline scripts in `index.html`

### 1.5 Companion Module Rules

Companion modules are permitted when a function group grows beyond the 500-line file limit or forms a cohesive, self-contained responsibility. Rules:

- One concern per companion module — named by concern (`name-field.js`, `command-modal.js`)
- No imports from `form.js` — companion modules are dependencies of `form.js`, not peers
- State access via injection — if state is needed, accept `(state, setState)` via an `init()` export
- All exports are explicit — no default exports; named exports only
- `index.html` loads only `form.js` as `type="module"` — companion modules are resolved by the ES module graph

Current companion modules:

| File | Concern |
|---|---|
| `ui/js/name-field.js` | Name field validation, preview, init button, file upload, language select |
| `ui/js/command-modal.js` | Command builder rows and command-entry modal |
| `ui/js/docs-modal.js` | Documentation modal: open/close, tab activation, fetch-on-demand, in-memory cache |

### 1.6 Evidence

- §3.3 component table: one file per concern (design doc)
- §3.4 state shape: single in-memory object in `form.js`
- Both flows (New/Existing) handled within `form.js` (§3.5)

---

## 2. Composition Patterns

### 2.1 Primary Patterns

The UI uses three composition patterns:
- Event-driven DOM manipulation — user actions trigger state mutations, which trigger DOM updates
- Derived state — dependent values computed from primary state on every change; never stored independently
- Fetch/respond — server calls return data that flows into state, then into the DOM via the same update path

### 2.2 Event-Driven DOM Manipulation

**When to use:** All user interactions (field input, button click, file selection, flow choice)

**Structure:**
- User action fires a DOM event
- Event listener calls a state mutation function
- State mutation calls `refreshYAML()` and, where relevant, `refreshErrors()`
- DOM reflects new state

**Example:**

```js
// Event listener (wiring section)
nameField.addEventListener('input', () => {
  setState({ name: nameField.value });
});

// State mutation
function setState(patch) {
  Object.assign(state, patch);
  deriveInstructions();
  refreshYAML();
  refreshValidation();
}
```

**Evidence:** §3.5 — "panel 2 updates live"; ajv validates on every change (design doc)

### 2.3 Derived State

**When to use:** The `instructions` object — computed from capability flag values; never edited directly by the user

**Structure:**
- Primary state holds capability flags
- `deriveInstructions()` recomputes `instructions` on every `setState()` call
- Derived value written back to `state.instructions` before `refreshYAML()` runs
- No separate event or trigger required

**Example:**

```js
function deriveInstructions() {
  state.instructions = buildInstructionsFromCapabilities(
    state.capabilities
  );
}
```

**Evidence:** §3.4 — "auto-derived from capabilities; not user-edited" (design doc)

### 2.4 Fetch/Respond

**When to use:** `/api/init` (New flow initialisation) and `/api/generate` (zip generation)

**Structure:**
- UI disables the triggering button and shows loading state
- `fetch()` POSTs to server endpoint
- On success: response flows into state via `setState()`; button re-enables
- On error: error message rendered via `textContent`; button re-enables
- No intermediate caching; no retry logic

**Example:**

```js
async function callInit(name, language) {
  setLoading(initBtn, true);
  try {
    const res = await fetch('/api/init', { method: 'POST', ... });
    const data = await res.json();
    if (!res.ok) { renderBannerError(data.error); return; }
    populateFromYml(data.yml);
  } finally {
    setLoading(initBtn, false);
  }
}
```

**Evidence:** §3.5 user journeys; §3.6 error table (design doc)

### 2.5 Rules

- One `setState()` path — all state changes go through `setState()`; no direct DOM writes that bypass state
- `deriveInstructions()` always runs inside `setState()`; never called independently
- Error messages always rendered via `textContent`, never `innerHTML`
- Loading state always cleared in a `finally` block
- Never nest fetch calls; server calls are flat and sequential

---

## 3. Component Structure

### 3.1 File Organisation

Three source files with hard boundaries. No additional files. Static assets (`schema.json`, `languages.json`) are data, not source.

### 3.2 index.html Structure

Page shell only. Contains:
- `<head>`: meta, title, stylesheet link
- CDN script tags: ajv and js-yaml (at end of body)
- Structural landmark elements with stable IDs referenced by `form.js`
- `<script type="module" src="form.js">`

Contains no logic, no inline styles, no data.

Landmark IDs required by `form.js` and companion modules:

```
#entry-screen      — initial flow choice view
#editor            — split-panel view (hidden until flow chosen)
#form-panel        — left panel: all form fields
#yaml-panel        — right panel: live YAML output
#modal             — download modal (hidden until generate succeeds)
#app-header        — persistent header fixed above both screens; contains Documentation button
#docs-modal        — documentation modal (hidden by default); owned by docs-modal.js
```

### 3.3 form.js Function Conventions

- One function per responsibility; max 75 lines per function
- Functions within a group are cohesive; no cross-group side effects except via `setState()`
- No class syntax; plain functions and a single module-level state object

### 3.4 Naming Conventions

- Functions: camelCase, verb-first (`populateForm`, `refreshYAML`, `renderBannerError`, `setLoading`)
- State keys: match schema field names exactly (`name`, `repo`, `capabilities`, `commands`, `instructions`)
- DOM element variables: camelCase, noun-first (`nameField`, `initBtn`, `yamlPanel`, `generateBtn`)
- IDs in HTML: kebab-case (`#entry-screen`, `#yaml-panel`, `#modal`)

### 3.5 What Lives Where

| Concern | File |
|---|---|
| Page structure, landmark IDs | `index.html` |
| CDN dependency loading | `index.html` |
| All interactive behaviour | `form.js` |
| State object and mutations | `form.js` |
| Layout, spacing, visual states | `style.css` |
| Validation rules | `schema.json` |
| Language command defaults | `languages.json` |

### 3.6 Evidence

- §3.3 component table: explicit one-responsibility-per-file assignment (design doc)
- §3.5 UX — landmark elements implied by entry screen → editor transition
- §3.4 state object keys match schema field names

---

## 4. State & Data Patterns

### 4.1 State Types

- **Session state:** single in-memory object in `form.js`; lost on page refresh; no `localStorage`, no server persistence
- **Derived state:** `instructions` object; computed from `capabilities`; never stored independently
- **Load-time data:** `schema.json` and `languages.json` fetched once on `DOMContentLoaded`; held in module-level constants

### 4.2 State Object Shape

Mirrors the schema structure exactly:

```js
const state = {
  name: "",
  repo: { title: "", language: {}, logfile: null, agentFile: "AGENTS" },
  capabilities: {
    hasUI: false, hasDB: false, hasTypecheck: false,
    isPublicFacing: false, handlesConfidentialData: false,
    hasAuthentication: false
  },
  commands: {},
  instructions: {}   // derived — never set directly
};
```

### 4.3 When to Use What

| Scenario | Pattern |
|---|---|
| Field value changes | `setState()` with patch object |
| Capability flag toggled | `setState()` → `deriveInstructions()` |
| New flow: init response | `populateFromYml()` → `setState()` |
| Existing flow: yml upload | js-yaml parse → `populateFromYml()` |
| Generate response (zip) | modal only; no state change |
| Validation errors | ajv result → `renderFieldErrors()` |

### 4.4 Data Fetching

Two fetch calls, both in the Server calls group of `form.js`:

**POST /api/init**
- Triggered by: Initialise button (New flow)
- Input: `{ name, language }`
- Success: yml string → `js-yaml.load()` → `populateFromYml()`
- Failure: banner error via `textContent`

**POST /api/generate**
- Triggered by: Generate button (enabled when schema-valid)
- Input: state object (full config)
- Success: zip blob → Blob URL → modal download link
- Failure: banner error via `textContent`; Generate re-enables

`schema.json` and `languages.json` fetched once on `DOMContentLoaded` via `Promise.all()`; UI initialisation blocked until both resolve.

### 4.5 State Location Rules

- Form field values → state object via `setState()`; never read back from the DOM
- `instructions` → always derived; never in user-editable fields
- Validation errors → DOM only (not in state); re-run on every `setState()` call
- Zip Blob URL → modal only; revoked after modal closes
- No state outside the module-level `state` object and the two load-time constants (`schema`, `languages`)

---

## 5. Compliance Gates

> Delivery and review skills verify these gates. Each gate must pass for code touching this domain.

- [ ] **CG-1:** All browser logic lives in `form.js` — no script tags other than CDN deps and `form.js` in `index.html`; no inline scripts or styles anywhere (§1.4)
- [ ] **CG-2:** All state changes go through `setState()` — no direct DOM writes that set visible content without a corresponding state update; `instructions` never set directly on state (§2.5)
- [ ] **CG-3:** Error messages rendered via `textContent`, not `innerHTML` — applies to field errors, banner errors, and modal content derived from server responses (§2.5)
- [ ] **CG-4:** Loading state cleared in a `finally` block for both `/api/init` and `/api/generate` — button never left permanently disabled after a server error (§2.4)
- [ ] **CG-5:** `schema.json` and `languages.json` fetched once on `DOMContentLoaded` via `Promise.all()` — no repeat fetches on user interaction; UI does not initialise until both resolve (§4.4)

---

## 6. Quick Reference

### 6.1 Decision Tree

**Adding browser behaviour:**
1. Reads or writes state? → goes in State group, via `setState()`
2. Responds to a user action? → goes in Event wiring group
3. Calls the server? → goes in Server calls group
4. Updates the DOM? → called from `setState()`, not directly

**Adding a new form field:**
1. Add element with stable ID to `index.html` (`#form-panel`)
2. Add key to state object (match schema field name exactly)
3. Populate in `populateFromYml()`
4. Wire event listener in Event wiring group
5. `schema.json` drives ajv validation — no manual validation logic

**Handling a new error condition:**
1. Server errors → banner via `renderBannerError()` using `textContent`
2. Field errors → inline via `renderFieldErrors()` using `textContent`
3. Never use `innerHTML` for user-derived content

### 6.2 File References

**UI source files:**
- `ui/index.html` — page shell and landmark IDs
- `ui/css/style.css` — all presentation
- `ui/js/form.js` — all browser logic

**Data files:**
- `ui/json/schema.json` — symlink to `schema/config.schema.json`
- `ui/json/languages.json` — built by `scripts/build_ui_manifest.py`

**Server:**
- `server/app.py` — FastAPI app; static file serving; endpoints
- `server/models.py` — `InitRequest`, `GenerateRequest`

**Design document:**
- `planning/static-config-form-design.md` — authoritative source for flow decisions, error handling, and security requirements

---
**END OF DOCUMENT:** Total sections: 6 | Purpose: Component architecture and composition patterns
