# New Page Instructions

## Overview

This is a single-page application. There are no routes and no separate HTML pages. The UI has two views — the entry screen and the editor — both rendered from `ui/index.html` and toggled by `form.js`.

If you need to add a new **view or section**, extend the existing single-page structure. Do not add a second HTML file, a router, or a navigation layer.

---

## Adding a New View

A "view" is a landmark section in `index.html` that is shown or hidden by `form.js`.

### 1. Add the landmark to `index.html`

Add a new landmark element with a stable kebab-case ID inside the page body, hidden by default:

```html
<section id="my-new-view" class="hidden">
  <!-- content -->
</section>
```

### 2. Style it in `style.css`

Scope styles to the landmark ID. Use design tokens — no hardcoded values.

```css
#my-new-view {
  padding: var(--space-300);
  background-color: var(--colour-surface);
}
```

### 3. Wire the transition in `form.js`

Show and hide views by toggling the `.hidden` class. Do not use `display` inline styles.

```js
function showMyNewView() {
  document.getElementById('entry-screen').classList.add('hidden');
  document.getElementById('my-new-view').classList.remove('hidden');
}
```

Add event listeners in the **Event wiring** group at the bottom of `form.js`.

---

## Rules

- One HTML file only — `ui/index.html`
- No second JS file — extend `form.js`
- No inline styles — all presentation in `style.css`
- All state changes go through `setState()` — see `frontend-design.md §2.2`
- Use `.hidden` class for show/hide — not `display` or `visibility` inline styles
- IDs in HTML: kebab-case; functions in JS: camelCase verb-first

---

## File References

- `ui/index.html` — add landmark elements here
- `ui/css/style.css` — add scoped styles here
- `ui/js/form.js` — add transition logic and event wiring here
- `agentic-framework/instructions/frontend-design.md` — component structure and composition patterns
- `agentic-framework/instructions/style-guide.md` — design tokens and state styling

---
**END OF DOCUMENT:** Total sections: 4 | Purpose: Instructions for adding new views to the single-page UI
