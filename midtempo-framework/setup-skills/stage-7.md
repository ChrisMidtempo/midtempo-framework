# Setup Style Guide Sub-Skill

## Overview

This sub-skill guides the client to create the `/midtempo-framework/instructions/style-guide.md` file through structured dialogue and codebase analysis.

**Goal:** Create style-guide.md documenting styling methodology, design tokens, component patterns, and visual standards for consistent design implementation.

**Target:** 400-600 lines total, regardless of design system size. Focus on styling patterns and usage guidance over exhaustive token catalogs or component documentation.

**Scope:** This file documents STYLING METHODOLOGY and DESIGN STANDARDS (colours, spacing, typography, component patterns). 

---

## The Process

### Non-Negotiable Rules

<CRITICAL_REQUIREMENT type="MANDATORY">

**CORE PRINCIPLE: Styling patterns over token catalogs, usage guidance over exhaustive listings.**

- You MUST target 400-600 lines total, regardless of design system size
- You MUST focus on styling patterns and usage guidance, not comprehensive catalogs
- You MUST scan the codebase for styling indicators before asking questions
- You MUST detect styling approach (CSS, Sass, CSS-in-JS, Tailwind, native mobile)
- You MUST identify design tokens and variables (colours, spacing, typography)
- You MUST identify component styling patterns from existing components
- You MUST draft sections based on evidence from code and configuration
- You MUST present each drafted section for validation before proceeding
- You MUST write validated content to `/midtempo-framework/instructions/style-guide.md` incrementally
- You MUST perform alignment check before marking complete (including line count check)
- You MUST follow the `/midtempo-framework/rules/writing.md` rules
- You MUST use UK English spelling throughout
- You MUST focus on WHAT/WHERE/HOW for styling, providing clear guidance for agents

**IMPORTANT:** If no styling detected, ask user for confirmation before proceeding.

</CRITICAL_REQUIREMENT>

---

### ENTRY GATE 

```
IF not sub-skill triggered from `setup.md`
  → STOP: This is a sub-skill and MUST NOT run independently
  → TELL: Human to run "Setup Stage 6 - `/midtempo-framework/setup.md`"
  → Do not proceed 

IF not read ALL of `/midtempo-framework/rules/writing.md`
  → INVALID: Read ALL of `/midtempo-framework/rules/writing.md` before proceeding

LS check if `/midtempo-framework/instructions/style-guide.md` exists
IF `style-guide.md` exists
  → EMPTY `style-guide.md` to create a fresh style-guide document before proceeding
```

## Phase 1: Styling Detection

### 1.1 Agent Actions (Silent)

```
SEARCH for styling indicators:
  - CSS files (*.css, *.scss, *.sass, *.less, styles/, stylesheets/)
  - CSS Modules (*.module.css, *.module.scss)
  - CSS-in-JS (styled-components, emotion, @mui/system, @emotion/styled, Stitches)
  - Utility frameworks (tailwind.config.js, uno.config.ts, @tailwindcss imports)
  - Preprocessors (sass, less, stylus configuration)
  - PostCSS (postcss.config.js)
  - SwiftUI styling (Color+Extensions.swift, ViewModifier files, custom modifiers)
  - Jetpack Compose (Color.kt, Theme.kt, Shape.kt, Typography.kt in ui/theme/)
  - UIKit (UIColor+Extensions.swift, Appearance.swift, Constants.swift)
  - Android Views (colors.xml, themes.xml, styles.xml in res/values/)
  - Design tokens (tokens.json, design-tokens/, theme.ts)

IDENTIFY styling methodology:
  - Plain CSS (separate .css files)
  - BEM methodology (block__element--modifier class names)
  - SCSS/Sass (variables, mixins, nesting)
  - CSS Modules (scoped styles per component)
  - CSS-in-JS (styled-components, emotion patterns)
  - Utility-first (Tailwind, UnoCSS class composition)
  - SwiftUI (declarative modifiers, custom ViewModifiers)
  - Jetpack Compose (Material3, custom composables)
  - Mixed approach (multiple methods)

IDENTIFY design tokens:
  - Colour palette (primary, secondary, greys, semantic colours)
  - Spacing scale (4px, 8px, 16px, etc.)
  - Typography (font families, sizes, weights, line heights)
  - Border radius values
  - Shadow definitions
  - Breakpoints (responsive design)
  - Z-index scale
  - Animation/transition timings

ANALYSE component styling patterns:
  - Component file structure (co-located styles, separate files)
  - Class naming conventions (BEM, camelCase, kebab-case)
  - Style composition patterns (extend, compose, inherit)
  - Conditional styling (props, state, variants)
  - Responsive patterns (media queries, container queries, adaptive layouts)
  - Dark mode / theming approach

FIND theme system:
  - Theme provider/context
  - Theme switching mechanism
  - Theme token structure
  - Platform appearance support (iOS dark mode, Android Material themes)
```

### 1.2 Present Detection Summary

**Output to human:**

```

Styling Detection Summary:

Styling approach found:
- [Primary approach]: [evidence - files, imports, patterns]
- [Secondary approach if mixed]: [evidence]

Design tokens location:
- Colours: [file path - X colours defined]
- Spacing: [file path or pattern]
- Typography: [file path - X font definitions]

Component styling pattern:
- [Pattern]: [evidence - how components are styled]
- Location: [co-located / separate directory]
- Naming: [convention observed]

Theme system:
- [Present/Absent]: [evidence if present]

Responsive design:
- [Breakpoints found]: [values]
- [Approach]: [media queries / container queries / adaptive]

[If NO styling detected:]
No styling indicators found. Does this repository have UI styling?

[If styling detected:]
Does this match your styling setup?

```

WAIT for human validation before proceeding

IF human approves
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

---

## 2. Phase 2 - Styling Methodology & File Organisation

**Draft section documenting the styling approach and how styles are organised.**

### 2.1 Agent Actions (silent) 

```
FOCUS ON:
  - Primary styling methodology (not every approach if mixed)
  - Core organizational patterns (not every directory)
  - Representative naming conventions (2-3 examples)

AVOID:
  - Listing every style file
  - Documenting every file type variation
  - Exhaustive rule listings

KEEP CONCISE:
  - Document file organization pattern, not every file
  - Show representative examples, not catalogs
```

### 2.2 Draft "1. Styling Methodology"

```
1. Styling Methodology

1.1 Primary Approach

[CSS/Sass/CSS-in-JS/Tailwind/SwiftUI/Jetpack Compose]

1.2 File Organisation

[pattern - how style files are organised]

1.3 Style Location

[directory or co-location pattern]

1.4 Naming Conventions

- Files: [naming pattern]
- Classes/identifiers: [BEM / camelCase / kebab-case / other]
- [Platform-specific]: [modifiers / composables / resources]

1.5 Style Scope

- [Global styles]: [where they live]
- [Component styles]: [pattern]
- [Utility classes/modifiers]: [where defined]

1.6 Import/Usage Pattern

[how styles are imported and applied]

1.7 Rules

- [Rule 1]
- [Rule 2]
- [Rule 3]
```

### 2.3 Present Draft

**Output to human:**

```

Styling Methodology (drafted from analysis):

1. Styling Methodology

[Draft section with evidence]

Evidence:
- Style files: [X] files found in [location]
- Approach: [framework/methodology detected]
- Pattern: [how styles are applied in components]
- Organisation: [directory structure]

Does this accurately describe the styling methodology?

```
WAIT for human validation before proceeding

IF human approves
  → VALID: Write to `/midtempo-framework/instructions/style-guide.md` with:
      - Title: `# [Repository Name] Style Guide`
      - Table of Contents section exactly as shown below (use this exact structure)
      - Then the Styling Stack section

  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present


#### 2.3.1 Table of Contents
```
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
```

### 2.4 Example (React with CSS Modules + Sass)

```
# Demo-Repo Style Guide

## Table of Contents

- [Styling Methodology](#1-styling-methodology)
- [Design Tokens](#2-design-tokens)
- [Layout Patterns](#3-layout-patterns)
- [Component Styling](#4-component-styling)
- [Typography](#5-typography)
- [Colour Usage](#6-colour-usage)
- [Responsive Design](#7-responsive-design)
- [Compliance Gates](#8-compliance-gates)
- [File References](#9-file-references)

---

## 1. Styling Methodology

### 1.1 Primary Approach

CSS Modules with Sass preprocessing

### 1.2 File Organisation

Co-located with components

### 1.3 Style Location

Each component has corresponding `.module.scss` file

### 1.4 Naming Conventions

- Files: `ComponentName.module.scss` (matches component filename)
- Classes: camelCase (`.primaryButton`, `.headerNav`)
- Sass variables: kebab-case (`$color-primary`, `$spacing-md`)

### 1.5 Style Scope

- Global styles: `src/styles/global.scss` (resets, base typography)
- Component styles: Co-located `.module.scss` files (scoped to component)
- Utility classes: `src/styles/utilities.scss` (layout helpers, text utilities)

### 1.6 Import/Usage Pattern

import styles from './Button.module.scss';
<button className={styles.primaryButton}>Click</button>

### 1.7 Rules

- All component styles MUST use CSS Modules (no global classes except utilities)
- Class names MUST be camelCase
- Avoid `@extend` (increases bundle size), use `@mixin` instead
- No inline styles except dynamic values (colours from props, calculated positions)
```

## 3. Phase 3 - Design Tokens & Variables

**Document the design system tokens - colours, spacing, typography.**

**CRITICAL:** Focus on token structure and usage patterns, not exhaustive token listings. For large design systems (50+ tokens per category), show representative examples (5-6 per category) that demonstrate the pattern, not every token value.

### 3.1 Agent Actions (silent) 

```
FOCUS ON:
  - Token organization structure
  - Access patterns and usage
  - Representative examples showing naming pattern (5-6 per category)

AVOID:
  - Listing every color token
  - Exhaustive spacing/typography catalogs
  - Complete token value tables

KEEP CONCISE:
  - Document how tokens are organised, not every token
  - Show token location and access pattern
  - Use representative examples demonstrating the pattern
```

### 3.2 Draft "2. Design Tokens"

```
2. Design Tokens

2.1 Colour Palette

2.1.1 Location

[file path]

2.1.2 Usage Examples

[usage examples]

2.2 Spacing Scale

2.2.1 Location

[file path or pattern]

2.2.3 Usage Examples

[how to apply spacing]

2.3 Typography

2.3.1 Location

[file path]

2.3.2 Usage Examples
- [Fonts]
- [Heading levels with sizes, weights, line heights]
- [Body text variants]
- [Small text / captions]

2.4 Other Tokens

2.4.1 Border Radius

[values and usage - ONLY if already exists in codebase]

2.4.2 Shadows

[shadow definitions - ONLY if already exists in codebase]

2.4.3 Transitions

[timing and easing values - ONLY if already exists in codebase]

2.4.4 Z-index Scale

[layering values if defined - ONLY if already exists in codebase]
```

### 3.2 Present Draft

**Output to human:**

```
Design Tokens (drafted from analysis):

2. Design Tokens

[Draft section with evidence]

Evidence:
- Colours: [file] defines [X] colour tokens
- Spacing: [pattern] observed across components
- Typography: [file] defines [X] font variants
- Analysis: [consistency observed / gaps found]

Does this capture all design tokens?

```

WAIT for human validation before proceeding

IF human approves
  → VALID: Write to `/midtempo-framework/instructions/style-guide.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

### 3. Example (SwiftUI)

```
2. Design Tokens

2.1 Colour Palette

2.1.1 Location

`App/Theme/Color+Theme.swift`

2.1.2 Usage Examples


Text("Hello")
    .foregroundColor(.textPrimary)
    .background(Color.surface)


2.2 Spacing Scale

2.2.1 Location

`App/Theme/Spacing.swift`

2.2.2 Usage Examples


VStack(spacing: Spacing.md) {
    Text("Title")
        .padding(Spacing.lg)
}

2.3 Typography

2.3.1 Location

`App/Theme/Font+Theme.swift`

2.3.2 Usage Examples

Text("Heading")
    .font(.heading1) // Custom font extension
    .fontWeight(.semibold)

Text("Body text")
    .font(.body)
    .foregroundColor(.textSecondary)

2.4 Other Tokens

2.4.1 Corner Radius

`App/Theme/CornerRadius.swift`

**Values**:
- `CornerRadius.sm = 4` - Small elements
- `CornerRadius.md = 8` - Buttons, inputs
- `CornerRadius.lg = 12` - Cards
- `CornerRadius.xl = 16` - Large containers

**Usage**:

RoundedRectangle(cornerRadius: CornerRadius.md)

2.4.2 Shadows

`App/Theme/Shadow.swift`

**Values**:
- `Shadow.sm` - Subtle elevation
- `Shadow.md` - Cards
- `Shadow.lg` - Modals

**Usage**:

card
    .shadow(color: Color.black.opacity(0.1), radius: 8, x: 0, y: 4)

2.4.3 Animations

`App/Theme/Animation+Theme.swift`

**Values**:
- `Animation.fast = .easeInOut(duration: 0.2)` - Quick interactions
- `Animation.standard = .easeInOut(duration: 0.3)` - Standard transitions
- `Animation.slow = .easeInOut(duration: 0.4)` - Complex animations

**Usage**:
button
    .animation(.fast, value: isPressed)

2.4.4 Z-index (Layering)

SwiftUI handles layering via `.zIndex()` modifier

**Conventions**:
- Base content: `zIndex(0)`
- Overlays: `zIndex(1)`
- Sheets/popovers: `zIndex(2)`
- Alerts: `zIndex(3)`

**Usage**:

overlay
    .zIndex(1)

```

---

## 4. Phase 4: Component Styling Patterns

**Document how components should be styled with examples.**

**CRITICAL:** Identify 3-5 recurring styling patterns across components, not individual component styles. For large component libraries (50+ components), focus on patterns that repeat (e.g., "variant props pattern", "size pattern"), not every component.

### 4.1 Agent Actions (silent) 

```
FOCUS ON:
  - Recurring patterns across multiple components (3-5 patterns)
  - 1-2 representative examples per pattern
  - How to apply patterns, not component inventory

AVOID:
  - Documenting every component
  - Multiple examples of same pattern
  - Component-by-component styling guide

KEEP CONCISE:
  - Show pattern, not component catalog
  - Representative examples demonstrating the pattern
  - Focus on patterns that help agents style new components
```

### 4.2 Draft "3. Component Styling Patterns"

```
3. Component Styling Patterns

3.1 Pattern Overview

3.1.1 Component Styling Approach

[how components are typically styled]

3.1.2 Common Patterns

- [Pattern 1]: [description and when to use]
- [Pattern 2]: [description and when to use]
- [Pattern 3]: [description and when to use]

3.2 Variant Patterns

3.2.1 How Variants Are Handled

[props / classes / modifiers / enums]

3.2.2 Example Variants

[primary/secondary buttons, card types, etc.]

3.3 State Styling
3.3.1 How States Are Styled

- Hover: [approach]
- Active/pressed: [approach]
- Focused: [approach]
- Disabled: [approach]
- Loading: [approach]
- Error: [approach]

3.3.2 Example Styled States

[example of a styled state]

3.4 Composition Patterns

3.4.1 Style Composition

[how styles are combined]

3.4.2 Conditional Styling

[how conditional styles are applied]

3.4.3 Dynamic Styles

[how runtime values affect styling]

3.5 Examples

[2-3 real examples from codebase showing patterns]

3.6 Rules

- [Rule 1]
- [Rule 2]
- [Rule 3]
```

### 4.3 Present Draft

**Output to human:**

```
Component Styling Patterns (drafted from component analysis):

3. Component Styling Patterns

[Draft section with evidence]

Evidence:
- Analysed [X] components
- Pattern: [common approach observed]
- Variants: [how variations are handled]
- States: [hover/focus/disabled patterns]

Does this capture component styling patterns?

```

WAIT for human validation before proceeding

IF human approves
  → VALID: Write to `/midtempo-framework/instructions/style-guide.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

### 4.4 Example (React with CSS Modules)

```
3. Component Styling Patterns

3.1 Pattern Overview
3.1.1 Component Styling Approach

**Component styling approach**: CSS Modules with co-located styles, composition via className prop

**Common patterns**:
- Base styles defined in module, variants via additional classes
- Conditional classes via `classnames` utility
- Container/element separation (`.card` wraps `.cardHeader`, `.cardBody`)

3.2 Variant Patterns

3.2.1 How Variants Are Handled

Props control which classes are applied

3.2.2 Example Variants

// Button.module.css
.button { /* base styles */ }
.primary { /* extends .button */ }
.secondary { /* extends .button */ }
.small { /* size modifier */ }
.large { /* size modifier */ }

// Button.tsx
<button className={classnames(styles.button, styles[variant], styles[size])}>

// Variant types
- Buttons: `primary`, `secondary`, `ghost`, `danger`
- Cards: `default`, `elevated`, `outlined`
- Inputs: `default`, `error`, `success`

3.3 State Styling

3.3.1 How States Are Styled

- Hover: Pseudo-class `.button:hover` in CSS Module
- Active: `.button:active` in CSS Module
- Focused: `.button:focus-visible` with focus ring
- Disabled: `.button:disabled` reduces opacity, removes interactions
- Loading: Additional `.loading` class, shows spinner
- Error: Additional `.error` class, shows error styling

3.3.2 Example Styled States

.button {
  // base styles

  &:hover:not(:disabled) {
    background-color: var(--color-primary-dark);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

3.4 Composition Patterns

3.4.1 Style Composition

Use `classnames` utility to combine classes

3.4.2 Conditional Styling

<div className={classnames(
  styles.card,
  elevated && styles.elevated,
  error && styles.error
)}>


3.4.3 Dynamic Styles

Inline styles only for runtime values

<div
  className={styles.card}
  style={{ backgroundColor: customColor }}
>

3.5 Examples

**Button component**:
import styles from './Button.module.scss';
import classnames from 'classnames';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
}

export function Button({ variant = 'primary', size = 'medium', disabled, ...props }: ButtonProps) {
  return (
    <button
      className={classnames(
        styles.button,
        styles[variant],
        styles[size]
      )}
      disabled={disabled}
      {...props}
    />
  );
}

**Card component**:
import styles from './Card.module.scss';

export function Card({ elevated = false, children }: CardProps) {
  return (
    <div className={classnames(styles.card, elevated && styles.elevated)}>
      {children}
    </div>
  );
}

**Rules**:
- Variants MUST be controlled via props, not arbitrary className prop
- All interactive elements MUST have hover, focus, and disabled states
- Focus styles MUST be visible (no `outline: none` without replacement)
- Disabled elements MUST have `cursor: not-allowed` and reduced opacity
- Loading states MUST disable interaction (pointer-events: none)
```

## 5. Phase 5 - Responsive & Adaptive Design

**Document responsive design approach (web) or adaptive design (mobile).**

**Focus on responsive approach and 3-5 common patterns.** Document breakpoint strategy, not every usage.

### 5.1 Agent Actions (silent) 

```
FOCUS ON:
  - Overall responsive approach
  - 3-5 common patterns (not every component's responsive behaviour)
  - Breakpoint strategy (not exhaustive usage catalog)

AVOID:
  - Documenting every responsive pattern for every component
  - Exhaustive breakpoint usage catalog

KEEP CONCISE:
  - Show how responsiveness works
  - Representative pattern examples
```

### 5.2 Draft "4. Responsive Design"

```
4. Responsive Design

4.1 Breakpoints

[values and device targets]

4.2 Responsive Approach

[media queries / container queries / fluid design / adaptive layouts]

4.3 Mobile-First

[yes/no and implications]

4.4 Common Patterns

- [Pattern 1]: [how layouts adapt]
- [Pattern 2]: [how components respond]
- [Pattern 3]: [how typography scales]

4.5 Platform Considerations

[iOS size classes / Android screen sizes / web viewports]

4.6 Rules

- [Rule 1]
- [Rule 2]
- [Rule 3]
```

### 5.3 Present Draft

**Output to human:**

```

Responsive Design (drafted from analysis):

4. Responsive Design

[Draft section with evidence]

Evidence:
- Breakpoints: [found in config/code]
- Pattern: [media queries / container queries / adaptive observed]
- Mobile support: [approach found in components]

Does this capture responsive design approach?

```
WAIT for human validation before proceeding

IF human approves
  → VALID: Write to `/midtempo-framework/instructions/style-guide.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

### 5.3 Example (SwiftUI)

```
4. Responsive Design

4.1 Size Classes

**Size classes**:
- Compact width: iPhone portrait, iPad split view
- Regular width: iPhone landscape (Plus/Max), iPad
- Compact height: iPhone landscape
- Regular height: iPhone portrait, iPad

4.2 Adaptive Approach

SwiftUI adaptivity via `@Environment(\.horizontalSizeClass)` and `@Environment(\.verticalSizeClass)`

4.3 Mobile-First

Yes - design for iPhone, adapt for iPad and larger screens

4.4 Common Patterns

**Size class-based layout**:

@Environment(\.horizontalSizeClass) var horizontalSizeClass

var body: some View {
    if horizontalSizeClass == .compact {
        // Vertical stack for iPhone portrait
        VStack { content }
    } else {
        // Horizontal layout for iPad/landscape
        HStack { content }
    }
}

**Dynamic spacing**:

VStack(spacing: horizontalSizeClass == .compact ? Spacing.sm : Spacing.lg) {
    // Content adapts spacing to screen size
}

**Conditional navigation**:

// TabView on iPhone, Sidebar on iPad
if horizontalSizeClass == .compact {
    TabView { views }
} else {
    NavigationSplitView { sidebar } detail: { detail }
}

**Responsive text**:

Text("Title")
    .font(horizontalSizeClass == .compact ? .title2 : .largeTitle)


4.5 Platform Considerations

**iOS/iPadOS**:
- Use size classes for layout adaptation
- Consider Safe Area insets (notch, home indicator)
- Test on iPhone SE, standard iPhone, Plus/Max, and iPad sizes
- Support both portrait and landscape orientations

**Dynamic Type**:
- Respect user font size preferences
- Use `.dynamicTypeSize()` modifier to constrain if needed
- Test with Accessibility Inspector

**Multitasking (iPad)**:
- Support Split View (1/3, 1/2, 2/3 layouts)
- Handle size class changes during Slide Over
- Gracefully adapt to small windows

4.6 Rules

- All layouts MUST adapt to size classes (not fixed sizes)
- Touch targets MUST be minimum 44x44pt
- Text MUST support Dynamic Type unless constrained
- Safe Area MUST be respected (use `.safeAreaInset()` or `.ignoresSafeArea()` intentionally)
- iPad layouts MUST not be stretched iPhone layouts (adapt navigation, use space effectively)
- Test on smallest device (iPhone SE) and largest (iPad Pro)
```

**After validation:** Append to `/midtempo-framework/instructions/style-guide.md`

---

## 6. Phase 6: Theme System & Dark Mode

**Document theming approach if present.**

**Focus on theming mechanism and structure, not every theme token.** Show how themes work with 3-5 examples, not complete token list.

### 6.1 Agent Actions (silent) 

```
FOCUS ON:
  - Theme switching mechanism
  - How theme values are accessed
  - Representative token examples (not complete theme catalog)

AVOID:
  - Listing every themeable property
  - Complete theme token catalog

KEEP CONCISE:
  - Document theming system, not every theme value
  - Show usage pattern with examples
```

### 6.2 Draft "5. Theme System" (if detected)

```
5. Theme System

5.1 Theme Implementation

[approach - context/provider/environment/Material]

5.2 Theme Location

[file path]

5.3 Theme Structure

[how themes are organised]

5.4 Theme Switching

[how users switch themes]

5.5 Dark Mode Support

[yes/no, how implemented]

5.6 Theme Tokens

[what can be themed]

5.7 Usage

[how components access theme values]

5.8 Rules

- [Rule 1]
- [Rule 2]
- [Rule 3]
```

### 6.2 Present Draft

**Output to human:**

```

Theme System (drafted from analysis):

5. Theme System

[Draft section with evidence - or skip if no theme system]

Evidence:
- Theme provider: [file/pattern]
- Dark mode: [supported/not supported]
- Switching: [mechanism found]

[If no theme system:]
No theme system detected. Styling uses static values.

Does this capture theming approach?

```

WAIT for human validation before proceeding

IF human approves
  → VALID: Write to `/midtempo-framework/instructions/style-guide.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

### 6.3 Example (React with Context)

```
5. Theme System

5.1 Theme Implementation
React Context with CSS variables

5.2 Theme Location
`src/contexts/ThemeContext.tsx`, `src/styles/themes.css`

5.4 Theme Structure

type Theme = 'light' | 'dark' | 'system';

interface ThemeContextValue {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  effectiveTheme: 'light' | 'dark'; // resolved theme
}

5.5 Theme Switching

const { setTheme } = useTheme();
setTheme('dark'); // or 'light' or 'system'

**Dark mode support**: Yes - system preference detection + manual override

5.6 Theme Tokens

All colours, some shadows

**Platform support**:
- Detects `prefers-color-scheme` media query
- Persists preference to localStorage
- Defaults to system theme

5.7 Usage

// Theme values via CSS variables (automatically switch)
.card {
  background-color: var(--color-surface);
  color: var(--color-text-primary);
}

// Access current theme in JS
const { effectiveTheme } = useTheme();
if (effectiveTheme === 'dark') {
  // theme-specific logic
}

5.8 Rules

- All colours MUST use CSS variables (no hardcoded hex values)
- Dark mode MUST be tested for all new components
- Focus indicators MUST be visible in both themes
- Images/illustrations may need theme-specific variants
```

---

## 7. Phase 7: Anti-Patterns & Best Practices

**Document what to avoid and best practices.**

**CRITICAL:** Limit to 5-7 most impactful anti-patterns and best practices. Focus on rules that agents need to know, not comprehensive style guide.

### 7.1 Agent Actions (silent) 

```
FOCUS ON:
  - Anti-patterns that would break styling system (5-7 items)
  - Critical best practices for consistency
  - Accessibility requirements

AVOID:
  - Exhaustive rule listings
  - Stylistic preferences (unless architectural)
  - Every possible mistake

KEEP CONCISE:
  - Most impactful rules only
  - Rules that affect styling architecture
  - Critical accessibility requirements
```

### 7.2 Draft "6. Anti-Patterns & Best Practices"

```
6. Anti-Patterns & Best Practices

6.1 Anti-Patterns to Avoid

6.1.1 Never

- [Anti-pattern 1]: [why it's wrong, what to do instead]
- [Anti-pattern 2]: [why it's wrong, what to do instead]
- [Anti-pattern 3]: [why it's wrong, what to do instead]

6.1.2 Platform-Specific

- [Platform]: [specific anti-patterns]

6.2 Best Practices

6.2.1 Do

- [Best practice 1]: [benefit]
- [Best practice 2]: [benefit]
- [Best practice 3]: [benefit]

6.2.2 Accessibility

- [Accessibility requirement 1]
- [Accessibility requirement 2]

6.2.3 Performance

- [Performance consideration 1]
- [Performance consideration 2]
```

### 7.3 Present Draft

**Output to human:**

```

Anti-Patterns & Best Practices:

6. Anti-Patterns & Best Practices

[Draft common anti-patterns from analysis]

[Draft best practices]

Are these aligned with your team's standards?

```

WAIT for human validation before proceeding

IF human approves
  → VALID: Write to `/midtempo-framework/instructions/style-guide.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

### 7.4 Example (React with CSS Modules)

```
6. Anti-Patterns to Avoid

**Never**:
- Hardcode colours: Use design tokens/theme values, NEVER `#3B82F6` inline
- Inline styles everywhere: Use CSS classes/modules/styled-components for reusability
- Fixed pixel heights: Use min-height or let content determine height
- Global styles for components: Scope styles to components (CSS Modules, CSS-in-JS)
- `!important` to override: Fix specificity issue, don't use !important
- Magic numbers: Use design token variables, not arbitrary `padding: 17px`
- Inconsistent spacing: Use spacing scale, not random values
- Neglect hover/focus: All interactive elements need visible states
- Skip dark mode: Test dark mode if theme system exists

## Best Practices

**Do**:
- Use design tokens consistently: Colours, spacing, typography from theme
- Mobile-first responsive: Start with mobile, enhance for desktop
- Component library: Build reusable styled components
- Semantic naming: Name by purpose (`.cardTitle`), not appearance (`.text18Bold`)
- Accessibility: Maintain colour contrast, focus indicators, semantic HTML
- Test responsiveness: Check all breakpoints/size classes
- Document variants: Component API should clearly show available styles

**Accessibility**:
- All interactive elements MUST have `:focus-visible` styles (never `outline: none` without replacement)
- All buttons/links MUST have `:hover` and `:active` states defined in CSS
- Status indicators MUST use icons or text labels, not colour alone (e.g., green/red status needs ✓/✗ icon)
- Form validation errors MUST include error message text, not just red borders
- Disabled states MUST set `cursor: not-allowed` and reduce opacity to 0.5-0.6

**Performance**:
- Avoid expensive CSS (complex gradients, multiple shadows)
- Use CSS containment for large lists
- Lazy load images below the fold
- Minimise style recalculations (avoid layout thrashing)
- Avoid inline styles (harder to cache)
```

---

## 8. Phase 8: Compliance Gates

**Distil verifiable rules from the style guide document.**

### 8.1 Agent Actions (Silent)

```
REVIEW content sections in style-guide.md:
  - Styling Methodology (§1) — approach, file organisation, naming conventions
  - Design Tokens (§2) — colour palette, spacing scale, typography
  - Component Styling Patterns (§3) — variant patterns, state styling, composition
  - Responsive Design (§4) — breakpoints, adaptive patterns
  - Theme System (§5) — dark mode, theme switching
  - Anti-Patterns & Best Practices (§6) — forbidden patterns, accessibility

SELECT 5 rules that are:
  - Verifiable by code inspection
  - Specific to this repository (not generic advice)
  - Focused on styling rules (token usage, responsive patterns, theme conventions)

WRITE rules using compliance gates format:
  - Checklist items with CG-N prefix
  - Each gate references its source section
  - One-line verifiable statements
```

### 8.2 Draft Compliance Gates

**Output to human:**

```
Compliance Gates:

8. Compliance Gates

> Delivery and review skills verify these gates. Each gate must pass for code touching this domain.

- [ ] **CG-1:** [Token rule — e.g., "Colours use design token variables, no hardcoded hex values"] (§2.1)
- [ ] **CG-2:** [Spacing rule — e.g., "Spacing uses scale variables, no arbitrary pixel values"] (§2.2)
- [ ] **CG-3:** [Component rule — e.g., "Component styles scoped via CSS Modules, no global class selectors"] (§3.1)
- [ ] **CG-4:** [Responsive rule — e.g., "Layouts adapt to all defined breakpoints, no fixed pixel widths"] (§4.1)
- [ ] **CG-5:** [Theme rule — e.g., "Dark mode tested for all new components using theme tokens"] (§5.5)

Target: 5 gates for style-guide.md (styling — token usage, responsive patterns, theme conventions)

Are these gates verifiable and correct?
```

WAIT for human validation before proceeding

IF human approves
  → VALID: Write to `/midtempo-framework/instructions/style-guide.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

---

## 9. Phase 9 - Alignment Check

**Review all sections for coherence.**

### 9.1 Check for Issues

```
READ all drafted sections from midtempo-framework/instructions/style-guide.md

CHECK:
1. Completeness — All styling aspects documented?
2. Consistency — Terminology consistent across sections?
3. Accuracy — Patterns match actual codebase?
4. Clarity — Can agent implement styles following this?
5. Conflicts — Any contradictions?
6. Platform coverage — Web/mobile patterns covered if applicable?
7. Design tokens — All tokens documented with usage?
8. Examples — Real examples included from codebase?
9. Evidence — All patterns backed by code?
10. Accessibility — Accessibility requirements stated?
11. Line count — Is document within 400-600 line target? If over, identify areas for condensing.
```

**SCALING GUIDANCE:**
- Small projects (< 20 components): Can detail individual component patterns
- Medium projects (20-50 components): Focus on recurring patterns, representative examples
- Large design systems (50+ components, 100+ tokens): MUST focus on patterns over catalogs, use token category descriptions instead of exhaustive listings, limit component examples to 2-3 that demonstrate patterns

### 9.2 Present Findings

**Output to human:**

```

Alignment Check Results:

Completeness: [all aspects covered / gaps found]
Consistency: [terminology consistent / inconsistencies found]
Accuracy: [matches codebase / corrections needed]
Clarity: [clear guidance / areas needing detail]
Conflicts: [none / issues found]
Platform coverage: [adequate / missing platform specifics]
Design tokens: [all documented / gaps in tokens]
Examples: [real examples included / need more examples]
Evidence: [backed by code / unsupported patterns]
Accessibility: [requirements stated / needs more detail]

[If issues found:]
Fixes needed:
1. [fix 1]
2. [fix 2]

Shall I apply these fixes?

[If no issues:]
Anything else to add?

```

**If fixes approved:** Apply and re-present

**If no issues:** Proceed to "§8b. Phase 8b: Compliance Gates"

---

## 10. Phase 10: Finalise Document

**Add file references section and complete.**

### 10.1 Add Final Section

```
9. File References

**Theme/tokens:**
- [theme file paths]
- [design token files]
- [colour/typography definitions]

**Component styles:**
- [component style directory]
- [example styled component]

**Configuration:**
- [CSS framework config if applicable]
- [preprocessor config]

**Example reference**: [Link to well-styled component that follows all patterns]

9.1 End Marker

---
**END OF DOCUMENT:** Total sections: 9 | Purpose: Styling methodology and design system

---

```

### Present Completion

**MANDATORY:** Produce this output EXACTLY.

```
---
                    STYLE GUIDE DOCUMENTATION COMPLETE

---

Documents created:
- midtempo-framework/instructions/style-guide.md — Styling methodology and standards

Sections completed:
✅ Styling Methodology (approach, file organisation, naming)
✅ Design Tokens (colours, spacing, typography, other tokens)
✅ Component Styling Patterns (variants, states, composition)
✅ Responsive Design (breakpoints, adaptive patterns)
✅ Theme System (dark mode, theming approach)
✅ Anti-Patterns & Best Practices (what to avoid, accessibility)
✅ Compliance Gates (5 verifiable styling rules)
✅ File References (quick lookup)

Summary:
- Styling approach: [approach]
- [X] design tokens documented
- [Y] component patterns documented
- Dark mode: [yes/no]
- Platform: [web/iOS/Android/multi-platform]

---

Start the next setup stage in a new conversation with:
Setup Phase 8 - /midtempo-framework/setup.md

---
```