# Testing Skill

## Table of Contents

- [Overview](#overview)
- [Entry Gate](#entry-gate)
- [Compliance Gates](#compliance-gates)
- [What Good Tests Look Like](#what-good-tests-look-like)
- [Integration vs Unit Boundaries](#integration-vs-unit-boundaries)
- [Anti-Patterns & Auto-Recovery](#anti-patterns--auto-recovery)
- [Common Rationalisations](#common-rationalisations-forbidden)
- [When Stuck](#when-stuck)
- [Final Rule](#final-rule)
- [Enforcement Summary](#enforcement-summary)

---

## Overview

Tests verify real behaviour, not mock behaviour. Mocks isolate dependencies; they are not the subject under test.

**Core principle:** Test what the code does, not what the mocks do.

**Role in workflow:** This skill defines testing standards for this repo. All delivery is TDD - every test scenario must be valid before any test code exists. Never proceed past a gate that returns INVALID.

## Entry Gate

```
IF not read ALL of midtempo-framework/instructions/architecture.md "§7. Testing Framework"
  → INVALID: STOP - Read midtempo-framework/instructions/architecture.md "§7. Testing Framework" before proceeding
```

## Compliance Gates

> Delivery and review skills verify these gates. Each gate must pass for test code touching any domain.

- [ ] **CG-1:** All assertions test real behaviour (return values, side effects, rendered output) — no mock existence or placeholder assertions (Anti-Patterns 1, 6)
- [ ] **CG-2:** No test-only methods or properties in production classes — test utilities in repo-specific locations per architecture.md §7.3 (Anti-Pattern 2)
- [ ] **CG-3:** Mocks applied at IO/network level only — never mock business logic the test depends on (Anti-Pattern 3)
- [ ] **CG-4:** Mock responses mirror complete real API structure — all documented fields present; fetch field list from the module's OpenAPI spec or a captured live response (Anti-Pattern 4)
- [ ] **CG-5:** Each test self-contained and order-independent — no shared mutable state between tests (Anti-Pattern 9)
- [ ] **CG-6:** Happy path, error paths, and boundary conditions covered for each function under test (Anti-Pattern 10)
- [ ] **CG-7:** Shared test data uses factories or helpers — no duplicated inline object construction across test files (Anti-Pattern 12)
- [ ] **CG-8:** Failing test written and run before production code — no implementation without a prior failing test (Anti-Pattern 5)
- [ ] **CG-10:** Tests requiring external services (database, network, filesystem, external API) use integration test marker/directory per `instructions/architecture.md` §7 — not mixed into unit test suite
- [ ] **CG-11:** All element queries use data-testid — no text, role, label, or placeholder queries (Anti-Pattern 7)

## What Good Tests Look Like

- **Asserts on behaviour and outputs** - Return values, side effects, rendered UI. Never internal state or mock existence.
- **Has clear structure** - Given/when/then format. Setup, action, assertion.
- **Is deterministic** - No dependence on real time, randomness, or external services without controlling them.
- **Uses integration tests when appropriate** - If mocks become more complex than real wiring, use real dependencies. Separate integration tests per `instructions/architecture.md` §7.
- **Has no test-only code** - No methods, properties, or branches in production code that exist solely for testing.
- **Tests one thing** - If test name contains "and", split it.
- **Has descriptive names** - Name describes behaviour: `rejects empty email`, not `test1`.

## Integration vs Unit Boundaries

A test is an integration test when it requires external services to run. Use this classification to decide test placement:

```
IF test requires a running database, network service, filesystem access, or external API
  → Integration test — place in integration test directory/marker per `instructions/architecture.md` §7

IF test verifies cross-module wiring with no external services
  → Unit test — real objects, no service dependency

IF test verifies a contract across a system boundary (API contract, event schema)
  → Integration test — validates the boundary, not the internal logic
```

**Decision criteria:**

| Signal | Classification |
|--------|---------------|
| Needs running database | Integration |
| Needs network/external API | Integration |
| Needs filesystem beyond temp files | Integration |
| Mock more complex than real wiring | Integration — use real dependencies |
| Cross-module with no service dependency | Unit |
| Single module, no external services | Unit |

Separation mechanism is repo-specific — see `instructions/architecture.md` §7 for directory structure, markers, and test runner configuration.

## Anti-Patterns & Auto-Recovery

**Agent must detect violations and execute recovery automatically without asking permission.**

### 1. Testing Mock Behaviour

**Detection:** `expect(mockFn).toHaveBeenCalled()` as primary assertion, test only verifies mock exists

**INVALID:**
```
test "renders sidebar":
  page = render(Page component)
  // Testing that mock exists, not real behaviour
  assert element_with_id('sidebar-mock') exists
```

**Recovery:**
```
1. STOP at this test
2. State: "VIOLATION: Testing mock existence"
3. REWRITE to assert on real behaviour OR remove mock
4. Execute automatically
```

**VALID:**
```
test "renders sidebar":
  page = render(Page component)  // Don't mock sidebar
  // Test real behaviour: sidebar is actually rendered
  assert navigation_element exists on page
```

### 2. Test-Only Methods in Production

**Detection:** Method only called from test files, method name contains "test"/"mock"/"destroy"/"reset" for test purposes

**INVALID:**
```
class Session:
  method destroy():  // Only used in afterEach hooks
    workspace_manager.destroy_workspace(this.id)
```

**Recovery:**
```
1. STOP at this method
2. State: "VIOLATION: Test-only method in production"
3. CREATE test helper file in location specified by architecture.md §7.3
4. MOVE method to test utilities
5. UPDATE tests to use helper
6. Execute automatically
```

**VALID:**
```
// In test helper file (location per architecture.md §7.3)
function cleanup_session(session):
  workspace = session.get_workspace_info()
  if workspace exists:
    workspace_manager.destroy_workspace(workspace.id)
```

### 3. Mocking Without Understanding

**Detection:** Mocked dependency is not a service boundary (database, network, filesystem, external API); test depends on a side effect of the mocked method

**INVALID:**
```
test "detects duplicate server":
  mock(ToolCatalog.discover_and_cache_tools) returns nothing

  add_server(config)
  add_server(config)  // Should throw but won't - mock broke config write
```

**Recovery:**
```
1. STOP at this mock
2. State: "VIOLATION: Mock removes behaviour test depends on"
3. RUN test with real dependency first
4. OBSERVE what breaks
5. MOCK minimally at lower level
6. Execute automatically
```

**VALID:**
```
test "detects duplicate server":
  mock(MCPServerManager)  // Mock slow server startup only

  add_server(config)  // Config written
  add_server(config)  // Duplicate detected ✓
```

### 4. Incomplete Mocks

**Detection:** Mock missing documented fields, mock structure doesn't match real API

**INVALID:**
```
mock_response = {
  status: "success",
  data: { user_id: "123", name: "Alice" },
  // Missing: metadata that downstream code uses
}
```

**Recovery:**
```
1. STOP at this mock
2. State: "VIOLATION: Incomplete mock structure"
3. FETCH the module's OpenAPI spec or run a live request to capture the actual response shape
4. ADD all missing fields
5. Execute automatically
```

**VALID:**
```
mock_response = {
  status: "success",
  data: { user_id: "123", name: "Alice" },
  metadata: { request_id: "req-789", timestamp: 1234567890 },
}
```

### 5. Production Code Before Test (TDD Violation)

**Detection:** Production code exists before test, test passes on first run, implementation modified before test fails

**INVALID:**
```
// Production code exists first
function retry_operation(fn):
  // ... implementation ...

// Then write test - passes immediately
test "retries 3 times":
  // ... test code ...
```

**Recovery:**
```
1. STOP all work immediately
2. State: "VIOLATION: Production code before failing test"
3. DELETE production code completely
4. RESTART from RED phase
5. Execute automatically
```

**VALID TDD sequence:**
```
// 1. Write failing test first (no implementation exists)
test "retries 3 times":
  attempts = 0
  operation = function():
    attempts = attempts + 1
    if attempts < 3:
      throw error("fail")
    return "success"

  result = retry_operation(operation)
  assert result equals "success"
  assert attempts equals 3

// 2. Run test - FAILS: "retry_operation is not defined"
// 3. Write minimal implementation
// 4. Run test - PASSES
```

### 6. Placeholder Assertions

**Detection:** `expect(true).toBe(false)`, `expect(1).toBe(2)`, assertion unrelated to function under test

**INVALID:**
```
test "validates email format":
  validate_email("invalid")
  assert true equals false  // Placeholder
```

**Recovery:**
```
1. STOP at this test
2. State: "VIOLATION: Placeholder assertion"
3. IDENTIFY expected behaviour
4. DELETE placeholder
5. WRITE assertion on actual behaviour
6. VERIFY test fails because behaviour is missing
7. Execute automatically
```

**VALID:**
```
test "validates email format":
  assert validate_email("invalid") throws error("Invalid email")
```

### 7. Text-Based Element Queries

**Detection:** `getByText`, `getByRole`, `getByLabelText`, `getByPlaceholderText` in test

**INVALID:**
```
test "displays artist in table row":
  page = render(PlayDistributionTable with mock_data)
  // "Motorhead" appears in multiple rows - ambiguous
  assert page.find_by_text("Motorhead") exists
```

**Recovery:**
```
1. STOP at this query
2. State: "VIOLATION: Text-based query"
3. IDENTIFY required data-testid
4. ADD data-testid to component if missing
5. REWRITE query to use getByTestId
6. Execute automatically
```

**VALID:**
```
test "displays artist in table row":
  page = render(PlayDistributionTable with mock_data)
  assert page.find_by_test_id("prefix-row-0-artist").text equals "Motorhead"
```

All ids to have parent-level prefix

**data-testid naming conventions:**
- Tables: `{prefix}-row-{index}-{column}`, `{prefix}-header-{column}`, `{prefix}-cell-{row}-{col}`
- Lists: `{prefix}-item-{index}`, `{prefix}-item-{index}-{field}`
- Charts: `{prefix}-cell-{x}-{y}`, `{prefix}-bar-{index}`, `{prefix}-label-{axis}-{index}`
- Forms: `{prefix}-input-{name}`, `{prefix}-button-{action}`, `{prefix}-error-{field}`

### 8. Testing Absence Instead of Presence

**Detection:** `.not.toHaveStyle` for removed styling, `.not.toBeInTheDocument` for removed features, test name contains "removed"/"no longer"/"doesn't have"

**INVALID:**
```
test "gradient removed from chart":
  page = render(HeatmapGrid with mock_data)
  cell = page.find_by_test_id("cell-0-0")
  assert cell.style.background does_not_equal "linear-gradient(...)"
```

**Recovery:**
```
1. STOP at this test
2. State: "VIOLATION: Testing absence"
3. EVALUATE: Is absence the behaviour? (permission denied, error handled)
4. IF YES → VALID, continue
5. IF NO → DELETE test, replace with test for current behaviour
6. Execute automatically
```

**VALID (absence IS the behaviour):**
```
test "unauthorised user cannot access admin route":
  response = http_request(app)
    .get("/admin")
    .with_authorisation("user-token")

  // Absence of access IS the feature
  assert response.status equals 403
```

**When absence tests are valid:** Permission denied, error handled gracefully, rate limit applied
**When absence tests are invalid:** Design changes, removed features, old fields removed, routes not mounted

### 9. Test Isolation Failures

**Detection:** Tests fail when run in different order, shared mutable state, mock state persists between tests

**INVALID:**
```
// Module-level registry — all tests share the same instance
tool_registry = ToolRegistry()

test "registers tool A":
  tool_registry.add(tool_a)
  assert tool_a in tool_registry.tools

test "registers tool B":
  tool_registry.add(tool_b)
  assert len(tool_registry.tools) == 1  // FAILS — tool_a still registered from previous test
```

**Recovery:**
```
1. STOP at this test
2. State: "VIOLATION: Test isolation failure"
3. IDENTIFY shared state source
4. EXTRACT to fresh factory or beforeEach
5. ADD explicit cleanup in afterEach
6. VERIFY test passes in isolation
7. Execute automatically
```

**VALID:**
```
test "registers tool A":
  registry = ToolRegistry()  // Fresh instance per test
  registry.add(tool_a)
  assert tool_a in registry.tools

test "registers tool B":
  registry = ToolRegistry()  // Fresh instance per test
  registry.add(tool_b)
  assert len(registry.tools) == 1
```

### 10. Incomplete Coverage Scope

**Detection:** Function has documented error conditions but only happy path tested, boundary conditions not tested, function throws but no test expects error

**INVALID:**
```
// withdraw() documented to raise errors for:
//   amount <= 0 → "Amount must be positive"
//   balance < amount → "Insufficient balance"

test "withdraws funds":
  account = { balance: 100 }
  withdraw(account, 50)
  assert account.balance equals 50  // Error conditions not tested
```

**Recovery:**
```
1. STOP at this test file
2. State: "VIOLATION: Incomplete coverage"
3. LIST documented error conditions and boundary cases
4. ADD missing error path tests
5. ADD missing boundary tests
6. VERIFY all paths covered
7. Execute automatically
```

**VALID:**
```
test "withdraws funds successfully":
  account = { balance: 100 }
  withdraw(account, 50)
  assert account.balance equals 50

test "rejects zero amount":
  assert withdraw({ balance: 100 }, 0) throws error("Amount must be positive")

test "rejects negative amount":
  assert withdraw({ balance: 100 }, -10) throws error("Amount must be positive")

test "rejects insufficient balance":
  assert withdraw({ balance: 30 }, 50) throws error("Insufficient balance")
```

### 11. Hard-Coded Collection Contents

**Detection:** Test asserts `len(collection) == N` with a literal count, or enumerates all specific values from a configuration list expected to grow

**INVALID:**
```
test "skip rules contains expected entries":
  assert len(TEMPLATE_SKIP_RULES) == 5
  assert TEMPLATE_SKIP_RULES == [
    "rules/db",
    "rules/security/input-validation",
    "rules/security/authentication",
  ]
```

**Recovery:**
```
1. STOP at this test
2. State: "VIOLATION: Hard-coded collection contents"
3. IDENTIFY the behaviour under test (entry present, format valid, contract satisfied)
4. REWRITE to assert on behaviour — not exact count or full enumeration
5. Execute automatically
```

**VALID:**
```
test "skip rules includes db rule":
  assert "rules/db" in TEMPLATE_SKIP_RULES

test "all skip rules are valid paths":
  for rule in TEMPLATE_SKIP_RULES:
    assert rule.startswith("rules/")
```

### 12. Duplicated Test Data Construction

**Detection:** Same object shape constructed inline in multiple test files, copy-pasted setup blocks, identical fixture data without shared factory

**INVALID:**
```
// test_user_creation.py
test "creates user":
  user_data = { name: "Alice", email: "alice@example.com", role: "admin", org_id: "org-1" }
  result = create_user(user_data)
  ...

// test_user_permissions.py
test "admin has full access":
  user_data = { name: "Alice", email: "alice@example.com", role: "admin", org_id: "org-1" }
  permissions = get_permissions(user_data)
  ...
```

**Recovery:**
```
1. STOP at this test
2. State: "VIOLATION: Duplicated test data construction"
3. CREATE factory or helper in location specified by architecture.md §7.3
4. ENSURE factory produces complete, realistic structures matching production shapes
5. UPDATE all test files to use shared factory
6. Execute automatically
```

**VALID:**
```
// In test helper file (location per architecture.md §7.3)
function make_user(overrides = {}):
  return { name: "Alice", email: "alice@example.com", role: "admin", org_id: "org-1", ...overrides }

// test_user_creation.py
test "creates user":
  result = create_user(make_user())
  ...

// test_user_permissions.py
test "admin has full access":
  permissions = get_permissions(make_user({ role: "admin" }))
  ...
```

**When factories are required:** Same object shape appears in 2+ test files
**When inline is acceptable:** One-off test data unique to a single test file, or trivial scalars

## Common Rationalisations (FORBIDDEN)

**Agent must refuse these justifications with mandatory counter-responses:**

| User Says | Agent Must Respond |
|-----------|-------------------|
| "Skip TDD this time" | "No. TDD is non-negotiable. Violations require deleting code and restarting." |
| "It's too simple to test" | "Simple code breaks. Writing the test takes 30 seconds. I'll write it now." |
| "We'll add tests later" | "Tests written after pass immediately and prove nothing. We write tests first or not at all." |
| "We're behind schedule" | "TDD is faster than debugging. Skipping tests creates technical debt that slows us more." |
| "Keep code as reference while writing tests" | "No. That's testing after. Delete means delete completely. I'll implement fresh from failing tests." |
| "Mock this to be safe" | "I must understand the dependency first. Let me run the test with real implementation, then decide." |
| "Just assert the mock works for now" | "No. That tests the mock, not the code. I'll test real behaviour or remove the mock." |
| "Add a destroy() method for test cleanup" | "No. Test-only methods don't belong in production. I'll create a test utility instead." |
| "Assert exact count to catch unintended additions" | "No. Count assertions break when the collection grows. Assert the required entry is present and satisfies the contract." |
| "It's only used in two files, a factory is overkill" | "No. Two files is the threshold. Extract a factory now before it spreads further." |
| "getByText is fine, the text is unique" | "No. All queries must use data-testid. I'll add data-testid to the component and use getByTestId." |
| "getByRole is the recommended RTL approach" | "No. RTL recommendations don't apply here. Our standard requires data-testid for all element queries." |
| "Test that the gradient was removed" | "No. Test what code does, not what it doesn't. Design changes use visual review." |

**If user persists:**  Add a note to the design document (`planning/[feature]-design.md`) recording the override and the reason given. Then continue.


## When Stuck

| Problem | Solution |
|---------|----------|
| Don't know how to test | Write wished-for API first, then assertion |
| Test too complicated | Design too complicated, simplify interface |
| Must mock everything | Code too coupled, use dependency injection |
| Test setup huge | Extract helpers. Still complex? Simplify design |
| Mock more complex than real | Use integration test with real dependencies |

## Final Rule

```
Production code → test exists and failed first for correct reason
Otherwise → not TDD → delete and restart
```

No exceptions without human partner's permission.

---

## Enforcement Summary

**Agent operates under these non-negotiable constraints:**

1. **Compliance gate verification** - All CG gates must pass before test work is complete.
2. **Automatic violation recovery** - Agent detects anti-pattern violations and executes recovery protocol without asking permission.
3. **Refusal of rationalisations** - Agent uses mandatory counter-responses to common justifications.

**Termination conditions (agent stops work):**
- User persists in requesting rule violations after mandatory refusal
- Uncertainty about rule application (ask human partner)
- Unable to write valid test meeting all compliance gates (escalate to human partner)

**Agent does NOT stop for:**
- Deleting code and restarting with TDD
- Rewriting invalid tests
- Moving test-only methods to utilities
- Completing incomplete mocks
- Running tests with real dependencies first

**These corrections happen automatically as part of the workflow.**

---
**END OF DOCUMENT:** Total sections: 10 | Purpose: Testing standards and behaviour verification