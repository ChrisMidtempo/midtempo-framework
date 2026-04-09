# Test-Driven Development (TDD)

## Table of Contents

- [The Iron Law](#the-iron-law)
- [Principles](#principles)
  - [Test First](#1-test-first)
  - [Watch It Fail](#2-watch-it-fail)
  - [Minimal Code](#3-minimal-code)
  - [Verify Green](#4-verify-green)
  - [Refactor on Green Only](#5-refactor-on-green-only)
- [Workflow Cadence](#workflow-cadence)
- [Good Tests](#good-tests)
- [Why Order Matters](#why-order-matters)
- [Common Rationalisations](#common-rationalisations)
- [Red Flags](#red-flags--stop-and-start-over)
- [When Stuck](#when-stuck)
- [Final Rule](#final-rule)

---

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

If you didn't watch the test fail, you don't know if it tests the right thing.

**Violating the letter of the rules is violating the spirit of the rules.**

---

## Principles

### 1. Test First

Write tests before implementation. Tests define what the code should do.

**Write code before the test?** Delete it. Start over.

- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Don't look at it
- Delete means delete

Implement fresh from tests. Period.

### 2. Watch It Fail

**MANDATORY. Never skip.**

Run the test. Confirm:

- Test fails (not errors)
- Failure message is expected
- Fails because feature missing (not typos)

**Test passes immediately?** You're testing existing behaviour. Fix test.

**Test errors?** Fix error, re-run until it fails correctly.

### 3. Minimal Code

Write simplest code to pass the test.

<Good>
```typescript
async function retryOperation<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === 2) throw e;
    }
  }
  throw new Error('unreachable');
}
```
Just enough to pass
</Good>

<Bad>
```typescript
async function retryOperation<T>(
  fn: () => Promise<T>,
  options?: {
    maxRetries?: number;
    backoff?: 'linear' | 'exponential';
    onRetry?: (attempt: number) => void;
  }
): Promise<T> {
  // YAGNI
}
```
Over-engineered
</Bad>

Don't add features, refactor other code, or "improve" beyond the test.

### 4. Verify Green

After implementation:

- Test passes
- Other tests still pass
- Output pristine (no errors, warnings)

**Test fails?** Fix code, not test.

**Other tests fail?** Fix now.

### 5. Refactor on Green Only

After tests pass:

- Remove duplication
- Improve names
- Extract helpers

Keep tests green. Don't add behaviour.

---

## Workflow Cadence

**This file defines principles. The calling skill defines cadence.**

| Skill                  | Cadence                                                        |
| ---------------------- | -------------------------------------------------------------- |
| `/midtempo-framework/deliver.md`   | Batch phases: all tests → all implementations → refactor once  |
| `/midtempo-framework/refine.md` | Tight iteration: small refinements with immediate verification |
| `/midtempo-framework/bugs.md`      | Reproduce first: failing test → trace root cause → fix         |

The principles above apply regardless of cadence.

---

## Good Tests

| Quality          | Good                                | Bad                                                 |
| ---------------- | ----------------------------------- | --------------------------------------------------- |
| **Minimal**      | One thing. "and" in name? Split it. | `test('validates email and domain and whitespace')` |
| **Clear**        | Name describes behaviour            | `test('test1')`                                     |
| **Shows intent** | Demonstrates desired API            | Obscures what code should do                        |
| **Real code**    | Tests actual implementation         | Tests mock existence                                |

---

## Why Order Matters

**"I'll write tests after to verify it works"**

Tests written after code pass immediately. Passing immediately proves nothing:

- Might test wrong thing
- Might test implementation, not behaviour
- Might miss edge cases you forgot
- You never saw it catch the bug

Test-first forces you to see the test fail, proving it actually tests something.

**"Tests after achieve the same goals"**

No. Tests-after answer "What does this do?" Tests-first answer "What should this do?"

Tests-after are biased by your implementation. You test what you built, not what's required.

---

## Common Rationalisations

| Excuse                         | Reality                                                       |
| ------------------------------ | ------------------------------------------------------------- |
| "Too simple to test"           | Simple code breaks. Test takes 30 seconds.                    |
| "I'll test after"              | Tests passing immediately prove nothing.                      |
| "Already manually tested"      | Ad-hoc ≠ systematic. No record, can't re-run.                 |
| "Deleting X hours is wasteful" | Sunk cost fallacy. Keeping unverified code is technical debt. |
| "Keep as reference"            | You'll adapt it. That's testing after. Delete means delete.   |
| "Need to explore first"        | Fine. Throw away exploration, start with TDD.                 |
| "TDD will slow me down"        | TDD faster than debugging.                                    |
| "This is different because..." | No it isn't.                                                  |

---

## Red Flags — STOP and Start Over

- Code before test
- Test after implementation
- Test passes immediately
- Can't explain why test failed
- Rationalising "just this once"
- "Keep as reference" or "adapt existing code"

**All of these mean: Delete code. Start over with TDD.**

---

## When Stuck

| Problem                | Solution                                                        |
| ---------------------- | --------------------------------------------------------------- |
| Don't know how to test | Write wished-for API. Write assertion first. Ask human partner. |
| Test too complicated   | Design too complicated. Simplify interface.                     |
| Must mock everything   | Code too coupled. Use dependency injection.                     |
| Test setup huge        | Extract helpers. Still complex? Simplify design.                |

---

## Final Rule

```
Production code → test exists and failed first
Otherwise → not TDD
```

No exceptions without human partner's permission.

---
**END OF DOCUMENT:** Total sections: 10 | Purpose: Test-driven development principles and workflow
