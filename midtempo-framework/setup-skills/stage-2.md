# Setup Purpose Sub-Skill

## Overview

This sub-skill guides the human to create the `/midtempo-framework/instructions/purpose.md` file through structured dialogue.

**Goal:** Create purpose.md documenting repository identity, purpose, and operational boundaries.

**Target:** 150-250 lines total, regardless of repository complexity. Focus on high-level purpose and capabilities, not exhaustive feature catalogues.

---

## The Process

### Non-Negotiable Rules

<CRITICAL_REQUIREMENT type="MANDATORY">

**CORE PRINCIPLE: High-level purpose over exhaustive catalogues.**

- You MUST target 150-250 lines total, regardless of repository complexity
- You MUST focus on primary capabilities (5-7 max), grouping minor features
- You MUST limit process flow to high-level steps (5-7 max)
- You MUST draft sections based on context gathered — only ask questions when truly unclear
- You MUST present each drafted section for validation/correction before proceeding
- You MUST write validated content to `/midtempo-framework/instructions/purpose.md` incrementally
- You MUST perform alignment check before marking this process complete (including line count check)
- You MUST follow the `/midtempo-framework/rules/writing.md` rules
- You MUST use UK English spelling throughout
- You MUST provide smart suggestions based on evidence from the repository

</CRITICAL_REQUIREMENT>

---

### ENTRY GATE 

```
IF not read ALL of `/midtempo-framework/rules/writing.md`
  → INVALID: STOP - Read `/midtempo-framework/rules/writing.md` before proceeding

LS check if `/midtempo-framework/instructions/purpose.md` exists
IF `purpose.md` exists
  → REWRITE: true
  → EMPTY `purpose.md` to create a fresh purpose document

```

## 1. Phase 1 - Context Gathering

**Do not skip to questions.** Gather context silently first.

### 1.1 Agent Actions (Silent)

```
SCAN repository:
  - Read `/midtempo-framework/midtempo-framework.yml` to identify project tooling
  - Read README.md (user-facing description)
  - Scan for main directories (src/, scripts/, lib/, app/, cmd/)
  - Identify entry points (main.*, index.*, __init__.py, etc.)
  - Check for configuration (config/, .env.example, settings.*)
  - Scan for templates/generators (jinja-templates/, templates/)
  - Check for validation (schema/, validators/)
  - Look for build/generation scripts

ANALYSE and DRAFT:
  - What does this repository do? (from README, scripts, entry points)
  - Repository type? (CLI tool, library, web app, generator system)
  - Core mechanism? (what's the technical approach?)
  - Primary capabilities? (what can it do?)
  - Key inputs/outputs? (what goes in, what comes out?)
  - Main components? (what are the building blocks?)
  - Boundaries? (what does it NOT do?)
```

### 1.2 Output Context Summary

**Output to human:**

```
Based on repository analysis:

Repository: [name from midtempo-framework/midtempo-framework.yml]
Language(s): [from midtempo-framework/midtempo-framework.yml &/or inferred repo languages]
Type: [inferred from structure - CLI tool/library/generator/web app]

Evidence:
- [key file 1]: [what it reveals]
- [key file 2]: [what it reveals]
- [directory structure]: [what it reveals]

1. System Identity

1.1 Overview

[Repository name] is a [type inferred from structure] that [purpose from README/analysis].

1.2 Core mechanism

[inferred from tech stack - e.g., "Jinja2 templating + YAML configuration + Python generation scripts"]

1.3 Output

[what system produces - e.g., "Complete workflow documentation tailored to repository capabilities"]

Does this match your understanding? Please correct anything wrong.

```

WAIT for human validation before proceeding

IF human approves
  → VALID: Write to `/midtempo-framework/instructions/purpose.md` with:
     - Title: `# [Repository Name] Purpose`
     - Table of Contents section exactly as shown in the example above (use this exact structure)
     - Then the System Identity section
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present


### 1.3 Example (this repository)

```markdown
# Midtempo Framework Purpose

## Table of Contents

- [System Identity](#1-system-identity)
  - [Overview](#11-overview)
  - [Core Mechanism](#12-core-mechanism)
  - [Output](#13-output)
- [What This System Does](#2-what-this-system-does)
  - [Primary Capabilities](#21-primary-capabilities)
  - [Inputs](#22-inputs)
  - [Outputs](#23-outputs)
- [How It Works](#3-how-it-works)
  - [Process Flow](#31-process-flow)
  - [Key Components](#32-key-components)
- [System Boundaries](#4-system-boundaries)
  - [The System DOES](#41-the-system-does)
  - [The System Does NOT](#42-the-system-does-not)

---

## 1. System Identity

### 1.1 Overview

This is a self-referential framework that generates frameworks for other repositories.

### 1.2 Core mechanism

Jinja2 templating + YAML configuration + Python generation scripts

### 1.3 Output

Complete workflow documentation tailored to repository capabilities

Evidence used:
- purpose.md clearly states "self-referential framework"
- jinja-templates/ directory contains .j2 template files
- scripts/generate_docs.py is main generation script
- schema/config.schema.json defines configuration structure
```


---

## 2. Phase 2 - What This System Does

**Draft capabilities based on scripts, entry points, and README.**

### 2.1 Draft "2. What This System Does"

**Analyse and draft:**

```
IDENTIFY capabilities from:
  - Script names and their functions (scripts/*)
  - CLI commands or API endpoints
  - README features section
  - Configuration options

FOCUS ON:
  - Primary capabilities only (5-7 maximum)
  - Core functionality, not every feature
  - Group minor features under broader capabilities

AVOID:
  - Exhaustive feature listings
  - Every configuration option as separate capability
  - Listing every script/command individually

GROUPING STRATEGY:
  - Complex systems (20+ scripts/features): Group related features
  - Example: "Data validation" instead of listing 5 validation scripts
  - Example: "Report generation" instead of listing 10 report types

DETERMINE inputs from:
  - Command-line arguments
  - Configuration files (.yml, .json, .toml)
  - Input directories or files
  - API request formats

DETERMINE outputs from:
  - Generated files or directories
  - API responses
  - Console output
  - Modified files
```

### 2.2 Output Draft

**Output to human:**

```
What This System Does (drafted from analysis):

2. What This System Does

2.1 Primary capabilities

[5-7 primary capabilities maximum - group related features]

- [capability 1 - from script/command]
- [capability 2 - from script/command]
- [capability 3 - from README]
- [capability 4 - grouped minor features]
- [capability 5 - from entry points]

2.2 Inputs

[configuration files, templates, schemas - from analysis]

2.3 Outputs

[generated files, documentation - from scripts/README]

Evidence:
- scripts/generate_docs.py: Suggests generation capability
- schema/config.schema.json: Shows configuration input
- Output directory structure in README.md
- CLI commands in package.json scripts

Does this capture what the system does? Any capabilities missing or incorrectly stated?
```

WAIT for human validation before proceeding

IF human approves
  → VALID: Append to `/midtempo-framework/instructions/purpose.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

### 2.3 Example (this repository)

```markdown
2. What This System Does

2.1 Primary capabilities

- Generate workflow documentation from Jinja2 templates
- Validate configurations against JSON schema
- Validate template syntax and detect issues
- Render templates with conditional inclusion
- Track generation metadata for regeneration

2.2 Inputs

midtempo-framework.yml config, Jinja2 templates, language command defaults

2.3 Outputs

Complete workflow documentation in namespaced directory

Evidence:
- scripts/generate_docs.py: Main generation capability
- scripts/validate_config.py: Configuration validation
- scripts/validate_templates.py: Template validation
- purpose.md documents 5-step generation flow
```


---

## 3. Phase 3 - How It Works

**Draft process flow from entry points and component structure.**

### 3.1 Draft "3. How It Works"

**Analyse and draft:**

```
TRACE execution flow from:
  - Main entry points (main.py, index.ts, etc.)
  - Script execution order
  - Function call chains
  - README workflow descriptions

FOCUS ON:
  - High-level process flow only (5-7 steps maximum)
  - Main execution path, not every conditional branch
  - 3-5 key components maximum

AVOID:
  - Detailed step-by-step implementation
  - Every sub-step or variation
  - Exhaustive component listings
  - Internal implementation details

KEEP CONCISE:
  - Document what happens, not how it's implemented
  - Use broad steps that describe stages, not actions
  - Example: "Validate inputs" not "Check file exists, parse JSON, validate schema, check required fields"

IDENTIFY components from:
  - Directory structure (src/, lib/, scripts/)
  - Module imports
  - Class/function organisation
  - README architecture descriptions
```

### 3.2 Present Draft

**Output to human:**

```
How It Works (drafted from code analysis):

3. How It Works

3.1 Process flow

[5-7 high-level steps maximum]

1. [Step 1 - from entry point]
2. [Step 2 - from execution trace]
3. [Step 3 - from main logic]
4. [Step 4 - from output generation]
5. [Step 5 - if needed]

3.2 Key components

[3-5 key components maximum]

- [component 1]: [purpose - from directory/module]
- [component 2]: [purpose - from directory/module]
- [component 3]: [purpose - from directory/module]

Evidence:
- Entry point: [file path and what it does]
- Directory structure: [what it reveals]
- README describes: [workflow description]

Is this process flow accurate? Any steps missing or out of order?
```

WAIT for human validation before proceeding

IF human approves
  → VALID: Append to `/midtempo-framework/instructions/purpose.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

### 3.3 Example (this repository)

```
3. How It Works

3.1 Process flow

1. Validate configuration against JSON schema
2. Validate template syntax
3. Render templates with config context
4. Apply conditional inclusion (hasUI, hasDB)
5. Write to namespaced directory with metadata

3.2 Key components

- jinja-templates/: Template source files organised by category
- scripts/: Validation and generation scripts
- schema/: Configuration schema definition

Evidence:
- purpose.md documents 5-step generation flow
- scripts/generate_docs.py is main orchestrator
- Directory structure mirrors generation mapping
```

---

## 4. Phase 4 - System Boundaries

**Draft boundaries from what the system does and doesn't touch.**

### 4.1 Draft "4. System Boundaries"

**Analyse and draft:**

```
DETERMINE responsibilities from:
  - What the scripts/code actually do
  - What configuration controls
  - What validation checks exist
  - What the system outputs

DETERMINE non-responsibilities from:
  - What's clearly missing (no auth code = not responsible)
  - What's delegated (calls external APIs)
  - What's out of scope in README
  - What dependencies handle
```

### 4.2 Present Draft

**Output to human:**

```
System Boundaries (drafted from analysis):

4. System Boundaries

4.1 The system DOES

- [responsibility 1 - from code]
- [responsibility 2 - from validation]
- [responsibility 3 - from generation]

4.2 The system does NOT

- [non-responsibility 1 - no evidence of this]
- [non-responsibility 2 - delegated to dependency]
- [non-responsibility 3 - out of scope]

Evidence:
- System handles: [list what code actually does]
- System does not: [list what's clearly absent]
- Dependencies handle: [external responsibilities]

Are these boundaries correct? Anything the system does that's missing?
```

WAIT for human validation before proceeding

IF human approves
  → VALID: Append to `/midtempo-framework/instructions/purpose.md`
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

### 4.3 Example (this repository)

```
4. System Boundaries

4.1 The system DOES

- Generate workflow documentation
- Validate configurations and templates
- Ensure markdown correctness
- Track generation metadata
- Enable parallel batch processing

4.2 The system does NOT

- Modify source code (generates documentation only)
- Manage dependencies (repository responsibility)
- Handle deployment (out of scope)
- Store runtime state (idempotent generation)

Evidence:
- purpose.md explicitly states boundaries
- No code modifies source files, only generates docs
- Scripts validate but don't execute tests
- No deployment or dependency management code
```

---

## 5. Phase 5 - Alignment Check

**Review all drafted sections for coherence.**

### 5.1 Check for Issues

```
READ all drafted sections from `/midtempo-framework/instructions/purpose.md`

CHECK:
1. Conflicts — Does one section contradict another?
2. Omissions — Is anything from analysis not captured?
3. Terminology — Are concepts named consistently?
4. Completeness — Do all sections have content?
5. Clarity — Is the purpose clear to someone unfamiliar with the repo?
6. Evidence alignment — Do stated capabilities match actual code?
7. Line count — Is document within 150-250 line target? If over, identify areas for condensing.

```

**SCALING GUIDANCE:**
- Small repos (< 10 scripts/features): Can detail individual capabilities
- Medium repos (10-30 features): Group related capabilities, focus on primary (5-7)
- Large repos (30+ features): MUST group features, high-level process flow only

> Note: Do not add commands, process, detailed architecture, or examples. These are covered elsewhere in the framework - this is **purely** a 'what does this service do' document.

### 5.2 Present Findings

**Output to human:**

```
Alignment Check Results:

Reviewing all sections for coherence...

Conflicts: [none / list any found with suggested fixes]
Omissions: [none / list anything discussed but missing]
Terminology: [consistent / list inconsistencies with corrections]
Completeness: [all sections complete / list gaps]
Clarity: [clear / areas needing clarification]
Evidence: [capabilities match code / discrepancies found]

[If issues found:]
Recommended fixes:
1. [specific fix for issue 1]
2. [specific fix for issue 2]

Shall I apply these fixes?

[If no issues found:]
Anything else to add to our purpose document?
```

WAIT for human validation before proceeding

IF human approves
  → VALID: Proceed to Phase 6
  → Continue to next section
IF human requests changes
  → REVISE: Update and re-present

---

## 6. Phase 6: Write purpose.md

**After alignment verified, finalise document.**

### 6.1 Create Final Document

```
CONSOLIDATE sections written to midtempo-framework/instructions/purpose.md

DO NOT ADD File References section (this is handled in `stage-3.md` - architecture)

APPEND end marker to file:

---
**END OF DOCUMENT:** Total sections: 4 | Purpose: System purpose and boundaries | Last updated: [DD/MM/YYYY]

```

### 6.2 Exit Gate


## Exit Gate

```

Criteria:
- `/midtempo-framework/instructions/purpose.md exists
- All 4 sections have content
- Alignment check passed
- No conflicts or omissions
- UK English spelling used
- Document within 150-250 line budget
- Primary capabilities limited to 5-7 (features grouped if needed)
- Process flow limited to 5-7 high-level steps
- Focus on purpose/identity, not exhaustive documentation

```
### 7.3 Present Completion

**MANDATORY:** IF Exit Gate passes, produce this output EXACTLY. Format, but do not skip or paraphrase.

```
---
                      PURPOSE DOCUMENT COMPLETE
---

Documents created:
- midtempo-framework/instructions/purpose.md — Final consolidated document

Sections completed:
✅ System Identity
✅ What This System Does
✅ How It Works
✅ System Boundaries

Alignment check: [passed/issues resolved]

Summary:
- [X] sections drafted from repository analysis
- [Y] evidence points used
- [Z] validations performed

---
Next Steps:

Review the generated midtempo-framework/instructions/purpose.md and confirm that it accurately represents this service.

Start the next setup stage in a new conversation with:
Setup Stage 3 - /midtempo-framework/setup.md

---
```