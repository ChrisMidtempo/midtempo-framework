#  Setup Orchestrator

## Table of Contents

- [⛔ Preliminary Gate: CLAUDE.md Check](#-preliminary-gate-agentsmd-check)
- [Overview](#1-overview)
  - [Entry Gate](#11-entry-gate)
- [Execution Plan](#2-execution-plan)
  - [List of Stages](#21-list-of-stages)
- [Stage 1: Command Alignment](#3-stage-1-command-alignment)
- [Stage 2: Purpose Document](#4-stage-2-purpose-document)
- [Stage 3: Architecture Design Instructions](#5-stage-3-architecture-design-instructions)
- [Stage 4: Error Handling](#6-stage-4-error-handling)
- [Stage 5: Database](#7-stage-5-database)
- [Stage 6: Frontend Design](#8-stage-6-frontend-design)
- [Stage 7: Style Guide](#9-stage-7-style-guide)
- [Stage 8: New Page Instructions](#10-stage-8-new-page-instructions)
- [Stage 9: Test Output Configuration](#11-stage-9-test-output-configuration)
  - [Entry Gate](#111-entry-gate)
  - [Logfile Benefit Output](#112-logfile-benefit-output)
  - [Language-Specific Examples](#113-language-specific-examples)
  - [Exit Gate](#114-exit-gate)
- [Setup Complete](#setup-complete)
- [Recovery Protocol](#recovery-protocol)

---

## ⛔ Preliminary Gate: CLAUDE.md Check

STOP. Before proceeding with setup:
  → CHECK: if `/CLAUDE.md` exists in the root directory of this repository
  → VERIFY: that it contains the Midtempo Framework rules** (starts with "# Agent Rules" and includes sections for Pre-Action Gate, Iron Laws, Workflow, Skill Router, etc.)

  → IF `CLAUDE.md` is missing from root OR contains different content
   → STOP: **HUMAN Action Required:** 
   → TELL: Human to move the Midtempo Framework's CLAUDE.md file from `/midtempo-framework/` into the root directory
   → WAIT: For human to confirm that the file has been move

   → IF Human has confirm that the file has been moved
   → VALID: Continue

**Why this matters:** The CLAUDE.md file in root is required for agents to follow the midtempo-framework's workflow rules. Without it in the correct location, the development process cannot function as designed.

## 1. Overview

This orchestrator validates and configures a repository for the Midtempo Framework. Run on first use to ensure all framework dependencies are configured.

**Context:** Validates command alignment, creates instruction files, and configures test output logging.

---

### 1.1 Entry Gate

```
READ `/midtempo-framework/midtempo-framework.yml` 
If YAML file has `setup: false` 
   → STOP: YAML config setup is false
   → ASK human how to proceed

If Human has not provided Stage # in prompt
   → STOP: Need Stage # to proceed
   → LIST: Stages from §2 - Execution Plan
   → ASK human how to proceed

ELSE → VALID Continue

```

## 2. Execution Plan

> **Core principle:** Each stage has an entry gate. Failed gates trigger sub-skills that guide the human to fix the issue.
> **Stage Activation:** Human should provide Stage # in prompt. If they haven't, start at Stage 1.
> **Recovery:** After each sub-skill completes, human begins next Stage in a new conversation.

### 2.1 List of Stages
```
Stage 1: Command Alignment
Stage 2: Purpose Document (mandatory)
Stage 3: Architecture (mandatory)
Stage 4: Error Handling (mandatory)
Stage 5: Database (conditional)
Stage 6: Frontend Design (conditional)
Stage 7: Style Guide (conditional)
Stage 8: New Page (conditional)
Stage 9: Finalisation (human tasks)
Complete: Framework ready for use
```

**To invoke a stage:** "Run setup Stage [N]" or "Setup Stage [N]: [Name]"

**Restart protocol:** After fixing issues via sub-skill, human runs "Run Setup Stage [N+1] `/midtempo-framework/setup.md`" in a new conversation to continue.

---

## 3. Stage 1: Command Alignment

**Goal:** Verify repository commands match the language command reference file.

### 3.1 Entry Gate

```
LS check for `/midtempo-framework/instructions/*.md` files OTHER than `setup.md`

IF other instruction files exist
   → STOP: Instructions folder already has instructions
   → PROVIDE: human with §2.1 List of Stages to call independently
   → ASK: human how to proceed [skip, trigger stage]
   → WAIT: for human response

ELSE
  → VALID: Run sub-skill `/midtempo-framework/setup-skills/stage-1.md`
```

### 3.2 Exit Gate

```
Confirm skip conditions met:
- Human has said Skip Stage 1

VALID → Display §3.3 Stage Complete Output
```

### 3.3 Stage Complete Output

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output after stage completes - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
</CRITICAL_REQUIREMENT>

```
---
                      STAGE 1 SKIPPED: COMMANDS ALREADY ALIGNED
---

Status: Skipping to next stage

Next step, run the following in a NEW CONVERSATION
Setup Stage 2 - /midtempo-framework/setup.md
---
```
---

## 4. Stage 2: Purpose Document

**Goal:** Create purpose.md documenting repository identity and operational boundaries.

**Type:** Mandatory (all repositories)

### 4.1 Entry Gate

```
LS check if purpose.md exists at `/midtempo-framework/instructions/purpose.md`

IF purpose.md exists
  → STOP: Purpose document already exists
  → ASK: Human what they want to do [suggest: re-write, skip]
  → WAIT: for human's response

IF purpose.md missing OR human says re-write
  → VALID: Run sub-skill `/midtempo-framework/setup-skills/stage-2.md`
```

### 4.2 Exit Gate

```
If skipped conditions met
- purpose.md MUST exist at `/midtempo-framework/instructions/purpose.md`
- Human says skip Stage 2

VALID → Display 4.3 Stage Skipped Output
```

### 4.3 Stage Skipped Output

```
---
                      STAGE 2 SKIPPED: PURPOSE DOCUMENT EXISTS
---

Status: purpose.md already exists - skipping to next stage.

Next step, run the following in a new conversation
Setup Stage 3 - /midtempo-framework/setup.md
---
```

---

## 5. Stage 3: Architecture Design Instructions

**Goal:** Ensure a current`architecture.md` instruction file exists.

**Type:** Mandatory

### 5.1 Entry Gate

```
LS check if `/midtempo-framework/instructions/purpose.md` exists
IF `purpose.md` does not exist
  → STOP: `purpose.md` must exist
  → INVALID: Complete "Stage 2: Purpose Document" first

LS check if `/midtempo-framework/instructions/architecture.md` exists
IF `architecture.md` exists
  → STOP: architecture document already exists
  → ASK: Human what they want to do [suggest: re-write, skip]
  → WAIT: for human's response

IF `architecture.md` missing OR human says re-write
  → VALID: Run sub-skill `/midtempo-framework/setup-skills/stage-3.md`
```

### 5.2 Exit Gate

```
IF skip conditions met:
- `architecture.md` exists
- Human has said Skip Stage 3

VALID → Display §5.3 Stage Skipped Output

```

### 5.3 Stage Skilled Output

```
---
                    STAGE 3 SKIPPED: ARCHITECTURE EXISTS
---

Status: architecture.md already exists - skipping to next stage

Next step, run the following in a new conversation
Setup Stage 4 - /midtempo-framework/setup.md
---
```

---

## 6. Stage 4: Error Handling

**Goal:** Ensure a current `error-handling.md` instruction file exists.

**Type:** Mandatory

### 6.1 Entry Gate

```
LS check if `/midtempo-framework/instructions/architecture.md` exists
IF `architecture.md` does not exist
  → STOP: `architecture.md` must exist
  → INVALID: Complete Stage 3 first

LS check if `/midtempo-framework/instructions/error-handling.md` exists
IF `error-handling.md` exists
  → STOP: error-handling document already exists
  → ASK: Human what they want to do [suggest: re-write, skip]
  → WAIT: for human's response

IF error-handling.md missing OR human says re-write
  → VALID: Run sub-skill `/midtempo-framework/setup-skills/stage-4.md`
```

### 6.2 Exit Gate

```
IF skip conditions met:
- `error-handling.md` exists
- Human has said Skip Stage 4

VALID → Display "§6.3 Stage Complete Output"
```

### 6.3 Stage Complete Output

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST produce this output after stage completes - include every section and field
- You MUST NOT skip, paraphrase, or omit any section
- You MUST format the output for readability
</CRITICAL_REQUIREMENT>

```
---
                   STAGE 4 SKIPPED: ERROR HANDLING EXISTS
---

Status: `error-handling.md` already exists - skipping to next stage.

Next step, run the following in a new conversation
Setup Stage 5 - /midtempo-framework/setup.md
---
```

---

## 7. Stage 5: Database

**Goal:** Ensure current `db.md` instruction file exists (if repository uses database).

**Type:** Conditional (if database functionality detected)

### 7.1 Entry Gate

```
LS check if `/midtempo-framework/instructions/error-handling.md` exists
IF `error-handling.md` does not exist
  → STOP: `error-handling.md` must exist
  → INVALID: Complete "Stage 4: Error Handling" first

LS check if `/midtempo-framework/instructions/db.md` exists
IF `db.md` exists
  → STOP: db document already exists
  → ASK: Human what they want to do [suggest: re-write, skip]
  → WAIT: for human's response

  IF Human says Re-write db instructions
    → VALID: run sub-skill `/midtempo-framework/setup-skills/stage-5.md`

  If Human says Skip Stage 5
    → INVALID: Skipping Stage 5
    → DISPLAY: "§7.3 Stage 7 Skipped Output" 
    → STOP: Wait for human to start next stage

READ "hasDB" state in `/midtempo-framework/midtempo-framework.yml`
IF `repo.hasDB: false`
  → STOP: `midtempo-framework.yml` settings state "No DB"
  → ASK: "Does this repository have a database>"
    IF human says NO
      → VALID: Display "§7.3 Stage Skipped Output"
      → STOP: Wait for human to start next stage
    IF human says YES
      → CHANGE: repo.hasUI to true
      → VALID: Run sub-skill `/midtempo-framework/setup-skills/stage-5.md`

ELSE

SEARCH codebase for "database indicators":
   - SQL files (*.sql)
   - ORM imports (SQLAlchemy, Prisma, TypeORM, Django ORM)
   - Database config files (database.yml, ormconfig.json)
   - Migration directories (migrations/, alembic/)

 IF no "database indicators" found
   → ASK USER: "Is a database planned for this repository?"
     A) No — database not planned
       → VALID: Display "§7.3 Stage Skipped Output"
     B) Yes — database exists but scan did not detect it
       → VALID: Run sub-skill /midtempo-framework/setup-skills/stage-5.md
     C) Yes — database is planned but not yet built
       → SET: DESIGN_MODE = true
       → INFORM USER: "Running in design mode — capturing design decisions rather than documenting existing code"
       → VALID: Run sub-skill /midtempo-framework/setup-skills/stage-5.md (DESIGN_MODE)

 IF "database indicators" found
   → VALID: Run sub-skill /midtempo-framework/setup-skills/stage-5.md
```

### 7.2 Exit Gate

```
Confirm skip conditions met:
- `/midtempo-framework/instructions/db.md` exists
- Human has said to Skip Stage 5

VALID → Display "§7.3 Stage Skipped Output"
```

### 7.3 Stage Skipped Output

```
---
                      DATABASE SETUP SKIPPED
---

Status: skipping to next stage.

Next step, run the following in a new conversation
Setup Stage 6 - /midtempo-framework/setup.md
---
```

---

## 8. Stage 6: Frontend Design

**Goal:** Ensure current frontend-design.md file exists (if repository has UI).

**Type:** Conditional (if hasUI)

### 8.1 Entry Gate

```
LS check if `/midtempo-framework/instructions/error-handling.md` exists
IF `error-handling.md` does not exist
  → STOP: `error-handling.md` must exist
  → INVALID: Complete "6. Stage 4: Error Handling" first

READ "hasUI" state in `/midtempo-framework/midtempo-framework.yml`
IF `repo.hasUI: false`
  → STOP: `midtempo-framework.yml` settings state "No UI"
  → ASK: "Does this repository have a UI (web/mobile pages)"
    IF human says NO
      → VALID: Display "§8.2.2 UI Stages Skipped Output"
    IF human says YES
      → CHANGE: repo.hasUI to true
      → VALID: Run sub-skill `/midtempo-framework/setup-skills/stage-6.md`

LS check if `/midtempo-framework/instructions/frontend-design.md` exists
IF `frontend-design.md` exists
  → STOP: frontend-design document already exists
  → ASK: Human what they want to do [suggest: re-write, skip]
  → WAIT: for human's response

  IF Human says Re-write frontend-design instructions
    → VALID: Run sub-skill `/midtempo-framework/setup-skills/stage-6.md`

  If Human says Skip Stage 6 
    → DISPLAY: "§8.2.1 Stage 6 Skipped Output" 
    → STOP: do not proceed

SEARCH codebase for ONE "style indicator":
  - CSS files (*.css, *.scss, *.sass, *.less)
  - CSS-in-JS files (*.styles.ts, styled-components)
  - Style directories (styles/, css/, stylesheets/)
  - Tailwind config files (tailwind.config.js)

IF NO "style indicator" found
  → ASK: "Is a UI planned for this repository?"
    A) No — UI not planned
      → VALID: Display "§8.2.2 UI Stages Skipped Output"
    B) Yes — UI exists but scan did not detect it
      → VALID: Run sub-skill `/midtempo-framework/setup-skills/stage-6.md`
    C) Yes — UI is planned but not yet built
      → SET: DESIGN_MODE = true
      → INFORM USER: "Running in design mode — capturing design decisions rather than documenting existing code"
      → VALID: Run sub-skill `/midtempo-framework/setup-skills/stage-6.md` (DESIGN_MODE)

IF one "style indicator" found
  → VALID: Run sub-skill `/midtempo-framework/setup-skills/stage-6.md`
```

### 8.2 Exit Gates

```
Confirm skip conditions met:
- IF human has said Skip Stage 6 
- OR IF human has confirmed that there is no UI

→ VALID: Display the correct output script

```

### 8.2.1 Stage 6 Skipped Output

```
---
                     STYLE GUIDE SKIPPED
---

Status: skipping to next stage.

Next step, run the following in a new conversation
Setup Stage 7 - /midtempo-framework/setup.md
---
```

### 8.2.2 UI Stages Skipped Output
```
---
                     UI STAGES SKIPPED
---

Status: No UI detected - skipping to Stage 9.

Next step, run the following in a new conversation
Setup Stage 9 - /midtempo-framework/setup.md
---
```

---

## 9. Stage 7: Style Guide

**Goal:** Ensure current style-guide.md file exists (if repository has UI).

**Type:** Conditional (if hasUI)

### 9.1 Entry Gate

```
LS check if `/midtempo-framework/instructions/frontend-design.md` exists
IF `frontend-design.md` does not exist
  → STOP: `frontend-design.md` must exist
  → INVALID: Complete "8. Stage 6: Frontend Design" first

LS check if `/midtempo-framework/instructions/style-guide.md` exists
IF `style-guide.md` exists
  → STOP: style-guide document already exists
  → ASK: Human what they want to do [suggest: re-write, skip]
  → WAIT: for human's response

  IF Human says Re-write style-guide instructions
    → VALID: Run sub-skill `/midtempo-framework/setup-skills/stage-7.md`

  If Human says Skip Stage 7
    → DISPLAY: "§8.2.1 Stage 7 Skipped Output"
    → STOP: do not proceed

VALID: Run sub-skill `/midtempo-framework/setup-skills/stage-7.md`
```

### 9.2 Exit Gates

```
Confirm skip conditions met:
- IF human has said Skip Stage 7
- OR IF human has confirmed that there is no CSS/styling

→ VALID: Display "§9.3 Stage 7 Skipped Output"

```

#### 9.3 Stage 7 Skipped Output

```
---
                     STYLE GUIDE SKIPPED
---

Status: skipping to next stage.

Next step, run the following in a new conversation
Setup Stage 8 - /midtempo-framework/setup.md
---
```

---

## 10. Stage 8: New Page Instructions

**Goal:** Ensure new-page.md instruction file exists if repository has UI elements.

**Type:** Conditional (if UI elements detected)

### 10.1 Entry Gate

```
LS check if `/midtempo-framework/instructions/style-guide.md` exists
If `style-guide.md` does not exist
  → STOP: `style-guide.md` must exist
  → INVALID: Complete "§9. Stage 7: Style Guide" first

LS check if midtempo-framework/instructions/new-page.md exists
IF `new-page.md` exists
  → STOP: new-page document already exists
  → ASK: Human what they want to do [suggest: re-write, skip]
  → WAIT: for human's response

  IF Human says Re-write new-page instructions
    → VALID: Run sub-skill `/midtempo-framework/setup-skills/stage-6.md`

  If Human says Skip Stage 8
    → INVALID: Skipping Stage 8
    → DISPLAY: "§10.3 Stage 8 Skipped Output" 

ELSE
 → RUN sub-skill /midtempo-framework/setup-skills/stage-6.md
```

### 10.2 Exit Gate

```
Confirm skip conditions met:
→ Human has said skip Stage 8

VALID → Display "§10.3 Stage 8 Skipped Output"
```

### 10.3 Stage 8 Skipped Output

```
---
                      NEW PAGE INSTRUCTIONS SKIPPED
---

Status: skipping to next stage

Next step, run the following in a new conversation
Setup Stage 9 - /midtempo-framework/setup.md
---
```

---


## 11. Stage 9: Test Output Configuration

**Goal:** Configure test output logging and finalise framework setup.

### 11.1 Entry Gate

```
READ `/midtempo-framework/midtempo-framework.yml`
CHECK if repo.logfile has a value

IF repo.logfile exists AND has value
  → CHECK if logfile exists and has content
       
IF repo.logfile is empty, OR logfile missing or empty
    → DISPLAY: "§11.2 Logfile Benefit Output"
      
DISPLAY: "§11.4 Exit Gate"
```

### 11.2 Logfile Benefit Output

**If logfile not configured, explain benefits to human:**

```
---
                    LOGFILE CONFIGURATION
---

During development, test states are checked at Entry and Exit gates.
If the test output is saved to a logfile, then Entry gates can verify state 
against that document, rather than re-running tests every time.

**With logfile configured:**
- Entry gates read cached results → FAST
- Only run tests when making changes
- Avoid redundant test runs between phases

**Process:**
- Update unit testing to fork output to a file (recommended `planning/last-test.log`)
- Update the `midtempo-framework.yml`
  
  repo:
    logfile: path/to/test.log


[Show language-specific methods based on repo.language from midtempo-framework.yml]

---
```

### 11.3 Language-Specific Examples

**Implementation methods:**
1. Shell script wrapper that captures output
2. pytest plugin configuration
3. Task runner integration (npm scripts, Makefile)

**For TypeScript/JavaScript:**

**Implementation methods:**
1. Package.json script with output redirection
2. Jest/Vitest reporter configuration
3. Task runner integration

### 11.4 Exit Gate

**Display final setup instructions for HUMAN:**

```
---
                    STAGE 9 COMPLETE: SETUP FINALISATION
---

Framework setup is complete (final steps require HUMAN action)

1. Review midtempo-framework.yml
   - Change `setup: true` to `setup: false`
   - Uncomment any generated instruction files in the config
   - Ensure that all available tooling/commands are correctly described

2. If you have uncommented or added commands - Rebuild the framework
   - Re-submit the midtempo-framework.yml document to the template generator
   - Replace the `midtempo-framework/` contents with the new Agent skills (note: you MUST retain the `instructions/` folder) 

  > Note: no need to rebuild if all you've changed is "setup to false"

3.  Move the new CLAUDE.md to repository root
   - mv midtempo-framework/CLAUDE.md ./CLAUDE.md
   - Make sure it has today's date

4. Review the documents in the `/midtempo-framework/instructions/` folder
   - Ensure the agent has instructions that accurately represent the repo's standards

> Note that the instruction documents are **never** overwritten by the templating system (unlike the other files in the midtempo-framework folder). 
>
> It is important that they evolve as the codebase changes, and should be reviewed periodically.
>
> You can use `setup.md` skill to re-run the setup service at any time - either remove the instruction documents first, or re-write any/all as desired.
>
> Try not to let these documents become too large or lose coherence.  They are a core component of the agent's capability - the clearer they documents are, the more likely they are to produce quality work.


5. Commit setup changes
   - Review all generated instruction files
   - Commit with message: "chore: complete midtempo framework setup"
   - Ask the other members of your team to pull the new skills
     (note: Only run one set-up per repo, not one-per-user!)

---
                    FRAMEWORK READY FOR USE ✅
---

Once the framework has been re-generated, you can now use the framework skills.

Best place to start is with the /midtempo-framework/README.md


**Recommended: Establish Clean Baselines**

Before starting feature work, consider running these setup skills to establish clean baselines:

- `/midtempo-framework/setup-skills/fix-tests.md` — Fix broken tests, separate unit/integration, configure coverage
- `/midtempo-framework/setup-skills/fix-linting.md` — Achieve zero lint errors and warnings
- `/midtempo-framework/setup-skills/fix-docs.md` — Resolve documentation generation issues

---
```

---

## Setup Complete

Stage 9 displays the final completion message with human tasks because:
- It's the last stage of the setup process
- It includes critical human actions required to finalise setup
- It provides clear "ready to use" confirmation

**There is no separate "Setup Complete" invocation needed.**

After Stage 9 completes and the human finishes their tasks, the framework is ready to use.

---

## Recovery Protocol

**When a gate fails:**

1. Orchestrator calls appropriate sub-skill
2. Sub-skill guides human to fix issue
3. Sub-skill completes with success message
4. Human runs setup again in a **new conversation** starting at next stage
5. Example: "Run Setup Stage 4 - `/midtempo-framework/setup.md`" (skips Stages 1-3)

**Why new conversation:**
- Avoids repeating completed stages
- Maintains clean context
- Clear progress tracking

**Progress tracking:**
- Each stage output shows what passed
- Human knows exactly where to resume
- No ambiguity about state

---
**END OF DOCUMENT:** Total sections: 12 | Purpose: Setup orchestrator for midtempo framework configuration