# Fix Documentation Skill

## Overview

This skill resolves documentation generation errors and warnings in batches. Each batch runs in a separate conversation to manage context effectively.

**Goal:** Resolve all doc generation errors and warnings, working in manageable batches.

**Important:** No supporting `planning/` documentation exists for this work. Full understanding of each function and its usage is required before writing any documentation.

**Progress file:** `planning/docs-fix-progress.md` tracks state between conversations.

---

## The Process

### Non-Negotiable Rules

<CRITICAL_REQUIREMENT type="MANDATORY">

**CORE PRINCIPLE: Understand before documenting. One batch per conversation.**

- You MUST run docs command first to identify ALL errors and warnings
- You MUST understand each function AND where it is used before adding documentation
- You MUST work in batches of 5-10 issues maximum per conversation
- You MUST update progress file after each batch
- You MUST follow `/midtempo-framework/rules/writing.md` for all documentation content
- You MUST use UK English spelling throughout
- You MUST NOT assume function purpose from name alone
- You MUST NOT copy-paste generic descriptions
- You MUST NOT skip understanding usage context
- You MUST start a new conversation for each batch

**Why one batch per conversation?** Understanding requires reading both definition AND usage. Too much in one conversation causes context drift and quality degradation.

</CRITICAL_REQUIREMENT>

---

## ENTRY GATE

```
STOP: No docs command defined in midtempo-framework.yml.

This skill requires a docs command. Add to commands section:

  docs:
    command: "[your doc generation command]"
    description: "Generate documentation"
    category: "docs"

Re-run after adding command and testing to make sure it runs.

```

### Writing Rules Summary

- **Active voice:** "The function returns X" not "X is returned"
- **Be specific:** "retries 3 times" not "retries several times"
- **Omit needless words:** "to" not "in order to"
- **UK English:** colour, behaviour, organisation, analyse

---