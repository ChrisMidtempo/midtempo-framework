# Agentic Framework Style Guide

## Table of Contents

- [Styling Methodology](#1-styling-methodology)
- [Design Tokens](#2-design-tokens)
- [Component Styling Patterns](#3-component-styling-patterns)
- [Responsive Design](#4-responsive-design)
- [Theme System](#5-theme-system)
- [Anti-Patterns & Best Practices](#6-anti-patterns--best-practices)
- [Compliance Gates](#7-compliance-gates)
- [File References](#8-file-references)

---

## 1. Styling Methodology

### 1.1 Primary Approach

Plain CSS with CSS custom properties. No preprocessor, no framework, no build step. All presentation in a single static file.

### 1.2 File Organisation

Single file: `ui/css/style.css`
Served as a static asset by the FastAPI server alongside `index.html` and `form.js`.

### 1.3 Style Location

`ui/css/style.css` — all layout, form styles, error states, and modal presentation. No co-located styles. No inline styles anywhere.

### 1.4 Naming Conventions

- Files: single file (`style.css`)
- Classes: kebab-case (`.form-panel`, `.yaml-panel`, `.error-banner`)
- IDs: kebab-case (`#entry-screen`, `#editor`, `#modal`) — defined in `index.html`, referenced in `form.js` and `style.css`
- CSS custom properties: kebab-case with semantic prefix (`--colour-brand`, `--space-200`, `--font-size-md`)

### 1.5 Style Scope

- Global styles: `ui/css/style.css` (the only stylesheet)
- Component styles: selectors scoped by landmark ID or class within `style.css`
- No utility classes — layout helpers written as needed

### 1.6 Import/Usage Pattern

```html
<!-- index.html -->
<link rel="stylesheet" href="style.css">
```

Design tokens referenced via CSS custom property:

```css
.primary-button {
  background-color: var(--colour-brand);
  color: var(--colour-text-on-brand);
  padding: var(--space-150) var(--space-300);
  border-radius: var(--radius-small);
}
```

### 1.7 Rules

- All presentation MUST live in `style.css` — no inline styles in `index.html` or `form.js`
- All colours MUST use `--colour-*` custom properties — no hardcoded hex values
- All spacing MUST use `--space-*` tokens — no arbitrary pixel values
- Never add a second stylesheet

---

## 2. Design Tokens

### 2.1 Colour Palette

#### 2.1.1 Location

`ui/css/style.css` — `:root` block, sourced from midtempo.orchestrator brand tokens.

#### 2.1.2 Usage Examples

```css
/* Brand */
--colour-brand: #5bc0de          /* primary action colour */
--colour-brand-strong: #4097b1   /* hover state for brand elements */
--colour-brand-soft: #cceffa     /* tinted backgrounds */

/* Backgrounds */
--colour-background: #f4f6fb     /* page background */
--colour-surface: #ffffff        /* card/panel surface */
--colour-surface-subtle: #f8f9fd /* nested surface */

/* Text */
--colour-text: #1f2937           /* body text */
--colour-text-strong: #0c1016    /* headings */
--colour-text-subtle: #4b5563    /* secondary text */
--colour-text-muted: #6b7280     /* placeholder, disabled label */
--colour-text-on-brand: #fff     /* text on brand-coloured backgrounds */

/* Borders */
--colour-border: #d5d9e3
--colour-border-subtle: #eaeaea
--colour-border-strong: #b7bdcd

/* Semantic states */
--success-strong: #0f9d58
--danger-strong: #dc2626
--warning-strong: #f59e0b

/* Focus */
--focus-ring: rgba(64, 151, 177, 0.32)
```

### 2.2 Spacing Scale

#### 2.2.1 Location

`ui/css/style.css` — `:root` block.

#### 2.2.2 Usage Examples

```css
--space-050: 4px   /* icon gaps, tight padding */
--space-100: 8px   /* compact spacing */
--space-150: 12px  /* button vertical padding */
--space-200: 16px  /* standard section padding */
--space-300: 24px  /* panel gaps */
--space-400: 32px  /* section separation */
--space-500: 48px  /* large layout gaps */
```

### 2.3 Typography

#### 2.3.1 Location

`ui/css/style.css` — `:root` block.

#### 2.3.2 Usage Examples

```css
/* Families */
--font-family-sans: "Inter", "Segoe UI", "Helvetica Neue", Arial, sans-serif
--font-family-mono: "SF Mono", "Monaco", "Inconsolata", "Fira Code", "Consolas", monospace

/* Sizes */
--font-size-xs: 12px   /* labels, captions */
--font-size-sm: 14px   /* secondary text, help text */
--font-size-md: 16px   /* body (base) */
--font-size-lg: 20px   /* subheadings */
--font-size-xl: 24px   /* section headings */
--font-size-xxl: 32px  /* page title */

/* Weights */
--font-weight-medium: 500
--font-weight-semibold: 600

/* Line heights */
--line-height-tight: 1.2
--line-height-normal: 1.5
```

The YAML panel uses `--font-family-mono`. All other text uses `--font-family-sans`.

### 2.4 Other Tokens

#### 2.4.1 Border Radius

```css
--radius-tiny: 3px     /* tags, badges */
--radius-small: 6px    /* buttons, inputs */
--radius-medium: 10px  /* cards, panels */
--radius-large: 16px   /* modal */
```

#### 2.4.2 Shadows

```css
--shadow-soft: 0 10px 24px rgba(15, 23, 42, 0.12)    /* panels */
--shadow-md: 0 4px 12px rgba(15, 23, 42, 0.15)        /* cards */
--shadow-overlay: 0 18px 36px rgba(15, 23, 42, 0.25)  /* modal */
```

#### 2.4.3 Layout

```css
--layout-width: 1200px  /* max-width for the editor split panel */
```

---

## 3. Component Styling Patterns

### 3.1 Pattern Overview

#### 3.1.1 Component Styling Approach

Global class selectors in `style.css`, scoped by landmark ID where needed. No scoping mechanism — selectors must be specific enough to avoid collisions.

#### 3.1.2 Common Patterns

- **Landmark scoping:** styles nested under `#editor`, `#form-panel`, `#modal` to constrain scope
- **State classes:** JS adds/removes classes (`.loading`, `.error`, `.hidden`) to reflect `form.js` state
- **Disabled styling:** applied via `[disabled]` attribute selector on buttons and inputs

### 3.2 Variant Patterns

#### 3.2.1 How Variants Are Handled

Separate classes per variant. No prop system — variants are fixed HTML elements with fixed classes.

#### 3.2.2 Example Variants

```css
.btn-primary {
  background-color: var(--colour-brand);
  color: var(--colour-text-on-brand);
}

.btn-secondary {
  background-color: transparent;
  border: 1px solid var(--colour-border-strong);
  color: var(--colour-text);
}
```

### 3.3 State Styling

#### 3.3.1 How States Are Styled

- Hover: `:hover` pseudo-class
- Focus: `:focus-visible` with `--focus-ring` outline
- Disabled: `[disabled]` attribute selector + `.btn-disabled` class
- Loading: `.loading` class toggled by `setLoading()` in `form.js`
- Error: `.error` class on field wrapper; `.error-banner` for global errors

#### 3.3.2 Example

```css
.btn-primary:hover:not([disabled]) {
  background-color: var(--colour-brand-strong);
}

.btn-primary:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}

.btn-primary[disabled] {
  background-color: var(--colour-button-disabled);
  cursor: not-allowed;
  opacity: 0.6;
}

.field-wrapper.error input {
  border-color: var(--danger-strong);
}

.error-banner {
  background-color: var(--danger-soft);
  border: 1px solid var(--danger-border-strong);
  color: var(--danger-strong);
}
```

### 3.4 Composition Patterns

#### 3.4.1 Style Composition

Multiple classes on a single element where needed:

```html
<button class="btn btn-primary loading">Generating...</button>
```

#### 3.4.2 Conditional Styling

`form.js` adds/removes classes to reflect state — `style.css` defines what each class looks like. No inline styles from JS.

#### 3.4.3 Dynamic Styles

No dynamic styles. All visual states are pre-defined CSS classes.

### 3.5 Examples

**YAML panel** — monospace, scrollable, read-only display:

```css
#yaml-panel {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  background-color: var(--colour-surface-subtle);
  border-left: 1px solid var(--colour-border);
  overflow-y: auto;
  padding: var(--space-200);
}
```

**Modal** — overlay with centred card:

```css
#modal {
  position: fixed;
  inset: 0;
  background-color: var(--colour-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-card {
  background-color: var(--colour-surface);
  border-radius: var(--radius-large);
  box-shadow: var(--shadow-overlay);
  padding: var(--space-400);
}
```

### 3.6 Rules

- State classes (`.loading`, `.error`, `.hidden`) MUST be toggled by `form.js` — never inline styles
- All interactive elements MUST have `:hover`, `:focus-visible`, and `[disabled]` states
- Error messages MUST use `--danger-*` tokens — never custom red values
- Focus styles MUST use `--focus-ring` — never `outline: none` without a visible replacement

---

## 4. Responsive Design

### 4.1 Breakpoints

```css
--breakpoint-md: 768px   /* tablet — stack panels vertically */
--breakpoint-lg: 1024px  /* desktop — split-panel layout */
```

### 4.2 Responsive Approach

Mobile-first. Base styles target narrow viewports; `min-width` media queries enhance for wider screens.

### 4.3 Mobile-First

Yes. The entry screen and form stack vertically by default. The split-panel editor layout activates at `--breakpoint-lg`.

### 4.4 Common Patterns

- **Split panel collapse:** `#editor` switches from side-by-side to stacked at 1024px — YAML panel moves below form panel
- **Max-width container:** `#editor` constrained to `--layout-width: 1200px`, centred with `margin: 0 auto`
- **Full-width inputs:** form fields fill their container at all sizes

### 4.5 Rules

- Base styles MUST target mobile — never assume wide viewport
- The split-panel layout MUST collapse below 1024px
- Touch targets MUST be minimum 44px tall (applies to buttons and inputs)
- No horizontal scrolling at any viewport width

---

## 5. Theme System

No theme system. The UI uses static CSS custom property values — no theme switching, no dark mode, no runtime theme context.

Colour tokens use semantic names (`--colour-brand`, `--colour-surface`) which makes a future dark mode straightforward to add via a `[data-theme="dark"]` selector override, but this is not currently planned.

---

## 6. Anti-Patterns & Best Practices

### 6.1 Anti-Patterns to Avoid

#### 6.1.1 Never

- **Hardcode colour values:** use `--colour-*` tokens — never `#5bc0de` or `rgb()` inline
- **Inline styles from JS:** `form.js` MUST only add/remove classes — never `element.style.*`
- **Add a second stylesheet:** all presentation lives in `style.css`; no `<style>` blocks in `index.html`
- **Use `!important`:** fix selector specificity instead
- **Magic spacing numbers:** use `--space-*` tokens — never `padding: 13px`
- **Suppress focus:** never `outline: none` without replacing with `--focus-ring` styles

### 6.2 Best Practices

#### 6.2.1 Do

- **Scope by landmark ID** when a selector could collide (`#form-panel .field-label` not `.field-label`)
- **Use semantic colour tokens** — `--colour-text-subtle` for secondary text, not a substitute token
- **Pre-define all states** — every interactive element needs `:hover`, `:focus-visible`, and `[disabled]` before delivery

#### 6.2.2 Accessibility

- All interactive elements MUST have a visible `:focus-visible` style using `--focus-ring`
- Colour alone MUST NOT convey state — error fields need both `--danger-strong` border and an error message
- Disabled elements MUST have `cursor: not-allowed` and `opacity: 0.6`

#### 6.2.3 Performance

- Avoid deeply nested selectors (max 3 levels)
- Declare all `:root` custom properties once at the top of `style.css`

---

## 7. Compliance Gates

> Delivery and review skills verify these gates. Each gate must pass for code touching this domain.

- [ ] **CG-1:** All colours use `--colour-*` custom properties — no hardcoded hex or rgb() values in `style.css` (§2.1)
- [ ] **CG-2:** All spacing uses `--space-*` tokens — no arbitrary pixel values (§2.2)
- [ ] **CG-3:** All presentation lives in `style.css` — no inline styles in `index.html` or set via `element.style.*` in `form.js` (§1.4, §6.1)
- [ ] **CG-4:** All interactive elements define `:hover`, `:focus-visible`, and `[disabled]` states — no bare button or input styles (§3.3)
- [ ] **CG-5:** Split-panel layout collapses below 1024px — no fixed side-by-side layout at narrow viewports (§4.4)

---

## 8. File References

**Design tokens:**
- `ui/css/style.css` — `:root` block; all custom properties defined here
- Source: `midtempo.orchestrator/src/styles/variables.css` — brand token origin

**UI source files:**
- `ui/css/style.css` — all presentation
- `ui/index.html` — landmark IDs and stylesheet link
- `ui/js/form.js` — class toggling (`.loading`, `.error`, `.hidden`)

**Design document:**
- `planning/static-config-form-design.md` — authoritative source for layout, flow, and error handling decisions

**Example reference:** `#yaml-panel` and `#modal` selectors (§3.5) demonstrate the landmark-scoped, token-driven pattern to follow for all new styles.

---
**END OF DOCUMENT:** Total sections: 8 | Purpose: Styling methodology and design system
