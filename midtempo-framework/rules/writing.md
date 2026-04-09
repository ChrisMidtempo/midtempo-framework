# Writing Style Rules

## Table of Contents

- [Declaration Gate (MANDATORY)](#declaration-gate-mandatory)
- [Rules (Strunk's Elements of Style)](#rules-strunks-elements-of-style)
- [Forbidden Words](#forbidden-words)
- [UK English](#uk-english)
- [Enforcement](#enforcement)
- [Applies To](#applies-to)

---

## Declaration Gate (MANDATORY)

**Before writing any prose (planning docs, README, comments, docstrings, error messages):**

Output this statement verbatim:
```
I have read the rules - active voice, omit needless words, be specific
```

These rules are mandatory. If not followed, the prose must be rewritten.

---

## Rules (Strunk's Elements of Style)

| Rule                | Bad                                          | Good                          |
| ------------------- | -------------------------------------------- | ----------------------------- |
| Omit needless words | "in order to", "for the purpose of"          | "to"                          |
| Active voice        | "X is returned by the function"              | "The function returns X"      |
| Be specific         | "retries several times"                      | "retries 3 times"             |
| Positive form       | "don't process rows that aren't empty"       | "skip empty rows"             |
| No hedge words      | "basically", "actually", "really", "quite"   | delete them                   |
| No weasel words     | "might", "could potentially", "may possibly" | state what happens or doesn't |

**Self-test:** Read your sentence. Remove a word. Does meaning change? No → delete the word.

---

## Forbidden Words

- "in order to" → use "to"
- "for the purpose of" → use "to" or "for"
- "basically", "actually", "really", "quite", "just"
- "might", "could potentially", "may possibly"
- "it is important to note that", "it should be noted that", "please note that"

---

## UK English

Use UK spelling: "colour", "behaviour", "organisation", "analyse", "optimise"

---

## Enforcement

**If prose written without declaration:**

1. STOP immediately
2. State: "VIOLATION: Writing gate declaration missing"
3. OUTPUT declaration verbatim
4. CONTINUE with writing process

**If prose violates rules:**

1. Identify violations
2. Rewrite following the rules
3. Apply self-test
4. Verify declaration present

---

## Applies To:

Delivery plans; test manifests; design and decision documentation; documentation comments; code comments; error messages; README.md; and agent skills.

---
**END OF DOCUMENT:** Total sections: 6 | Purpose: Writing style rules for documentation and code