# Fix Log File Skill

## Overview

This skill generates a test runner wrapper script that writes test output to the `repo.logfile` path, then wires it up as the primary test command. The log file is how the framework checks test state at the start of each fresh conversation without rerunning the full suite.

**Goal:** The log file path configured in `repo.logfile` exists after every test run, contains full output, and the `midtempo-framework.yml` test command writes to it.

**No TDD required.** This is infrastructure, not production code.

---

## Non-Negotiable Rules

<CRITICAL_REQUIREMENT type="MANDATORY">

- You MUST read `midtempo-framework.yml` before doing anything
- You MUST identify the language and current test command before generating any script
- You MUST run the wrapper after generating it and verify the log file is created
- You MUST fix any failure before declaring complete - do not hand off a broken script
- You MUST NOT modify production code or tests
- You MUST NOT skip the verification loop
- You MUST update `midtempo-framework.yml` to use the wrapper as the test command

**End state:** Running the test command produces the configured log file with full test output.

</CRITICAL_REQUIREMENT>

---

## Entry Gate

```
READ midtempo-framework.yml completely

EXTRACT:
  - repo.language
  - repo.logfile (target log path)
  - commands.test (current test command)
  - commands.test_unit (if defined)
  - commands.test_integration (if defined)

CHECK repo.logfile:
  IF repo.logfile is NOT defined or empty:
    → ASK human: "Where should the test log be written? (e.g. planning/last-test-ran.log)"
    → WAIT for answer
    → Use the human's answer as [LOG_PATH] for this skill
    → ADD to midtempo-framework.yml under repo:
        logfile: [LOG_PATH]

  IF repo.logfile is defined:
    → Use configured path as [LOG_PATH]

CHECK if a test log wrapper already exists:
  INSPECT the current commands.test command

  IF it calls a script file:
    → READ that script file
    → ASSESS whether it writes output to a log file
    → GOTO §3. Verify and Heal

  IF it calls a test runner directly (jest, pytest, go test, etc.):
    → GOTO §1. Assess Language and Runner
```

---

## 1. Assess Language and Runner

```
READ midtempo-framework.yml → repo.language

IDENTIFY test runner from repo.language and commands.test:

  TypeScript / JavaScript (jest or vitest):
    Runner: Jest or Vitest
    Wrapper type: TypeScript (.ts) or JavaScript (.js)
    Detect: check package.json for "jest" or "vitest" in dependencies/devDependencies

  Python / python-poetry / python-uv (pytest):
    Runner: pytest
    Wrapper type: Python (.py)
    Detect: check pyproject.toml or setup.cfg for pytest config

  Go:
    Runner: go test
    Wrapper type: Shell script (.sh)

  Ruby:
    Runner: RSpec or minitest
    Wrapper type: Shell script (.sh)

  Java-gradle / Java-maven / Kotlin / Kotlin-maven / Scala:
    Runner: JUnit via Gradle or Maven
    Wrapper type: Shell script (.sh)

  Rust:
    Runner: cargo test
    Wrapper type: Shell script (.sh)

  C# (csharp):
    Runner: dotnet test
    Wrapper type: Shell script (.sh)

  PHP:
    Runner: phpunit
    Wrapper type: Shell script (.sh)

  Elixir:
    Runner: mix test
    Wrapper type: Shell script (.sh)

  Swift:
    Runner: swift test
    Wrapper type: Shell script (.sh)

  Dart / Flutter:
    Runner: dart test / flutter test
    Wrapper type: Shell script (.sh)

  Clojure:
    Runner: lein test
    Wrapper type: Shell script (.sh)

  Haskell:
    Runner: cabal test or stack test
    Wrapper type: Shell script (.sh)

PRESENT assessment to human:

**ASSESSMENT**

Language: [language]
Test runner: [runner]
Current test command: [command]
Wrapper type: [TypeScript | Python | Shell]
Log path: [LOG_PATH]

Ready to generate wrapper?

WAIT for human confirmation.
```

---

## 2. Generate Wrapper Script

### 2.1 TypeScript / JavaScript (Jest or Vitest)

```
DETECT package manager: npm / yarn / pnpm
DETECT if TypeScript is available (tsconfig.json present)
DETECT Jest or Vitest from package.json

GENERATE file: build-scripts/run-tests-with-log.ts (or .js if no TypeScript)

Script requirements:
  - Creates planning/ directory if it does not exist
  - Writes a lock file at planning/.test-runner.lock containing the process PID
  - On exit (normal, SIGINT, SIGTERM): removes the lock file
  - If lock file already exists: reads PID, prints error, exits with code 1
  - Opens a write stream to [LOG_PATH]
  - Spawns the test runner with stdio piped
  - Two output modes:
      Summary mode (no positional args): terminal shows FAIL lines, failure details,
        summary footer, and coverage table only - suppresses PASS lines and per-test names
      Targeted mode (positional args = file patterns): terminal shows full output for
        matched files, auto-adds --coverage for per-file stats
  - Log stream receives full output, ANSI codes stripped, npm/node noise filtered
  - On close: flushes streams, ends log stream, exits with runner's exit code

GENERATE npm script entry in package.json:
  "test:log": "npx ts-node build-scripts/run-tests-with-log.ts"
  (or "node build-scripts/run-tests-with-log.js" if no TypeScript)

UPDATE midtempo-framework.yml:
  Set commands.test (and any test variant commands) to invoke the wrapper script
  Update descriptions to reflect that output is written to [LOG_PATH]

NOTE: Updating midtempo-framework.yml requires a framework rebuild to take effect.
Tell the human: "After saving midtempo-framework.yml, rebuild the framework - use the CLI or midtempo.com depending on your setup."

PRESENT generated script AND the full list of yml changes to human for review.
WAIT for approval.
```

### 2.2 Python (pytest)

```
DETECT Python version (python3 or python)
DETECT pytest location (venv, poetry, uv, or global)
DETECT coverage plugin: pytest-cov

GENERATE file: scripts/run_tests_with_log.py

Script requirements:
  - Creates planning/ directory if it does not exist
  - Writes a lock file at planning/.test-runner.lock containing the process PID
  - On exit and on SIGINT/SIGTERM: removes the lock file
  - If lock file already exists: reads PID, prints error, exits with code 1
  - Spawns pytest via subprocess with stdout and stderr piped
  - Passes through all command-line arguments to pytest
  - Two output modes:
      Summary mode (no positional args): terminal shows FAILED lines, error details,
        and the short summary section only - suppresses individual test names
      Targeted mode (positional args = file/module paths): terminal shows full output
  - Writes full output (ANSI stripped) to [LOG_PATH]
  - Exits with pytest's exit code

DETECT how pytest is invoked from commands.test (python -m pytest / pytest / poetry run pytest / uv run pytest)
USE same invocation pattern inside the script.

GENERATE a runner command that matches the project's Python environment:
  poetry:  "poetry run python scripts/run_tests_with_log.py"
  uv:      "uv run python scripts/run_tests_with_log.py"
  venv:    ".venv/bin/python scripts/run_tests_with_log.py"
  global:  "python3 scripts/run_tests_with_log.py"

UPDATE midtempo-framework.yml:
  Set commands.test (and any test variant commands) to invoke the wrapper script
  Update descriptions to reflect that output is written to [LOG_PATH]

NOTE: Updating midtempo-framework.yml requires a framework rebuild to take effect.
Tell the human: "After saving midtempo-framework.yml, rebuild the framework - use the CLI or midtempo.com depending on your setup."

PRESENT generated script AND the full list of yml changes to human for review.
WAIT for approval.
```

### 2.3 Shell Script (Go, Ruby, Java, Rust, C#, PHP, Elixir, Swift, Dart, Clojure, Haskell)

```
EXTRACT the current test command from commands.test in midtempo-framework.yml

GENERATE file: scripts/run-tests-with-log.sh

Script content:

  #!/usr/bin/env bash
  set -euo pipefail

  LOG_FILE="[LOG_PATH]"
  LOCK_FILE="planning/.test-runner.lock"
  mkdir -p "$(dirname "$LOG_FILE")" planning

  # Lock file: prevent concurrent runs
  if [ -f "$LOCK_FILE" ]; then
    echo "Test runner already active (PID $(cat "$LOCK_FILE")). Aborting." >&2
    exit 1
  fi
  echo $$ > "$LOCK_FILE"
  trap 'rm -f "$LOCK_FILE"' EXIT INT TERM

  # Run tests, capture full output to log, summary to terminal
  # Pass any arguments through to the test runner
  [CURRENT_TEST_COMMAND] "$@" 2>&1 | tee "$LOG_FILE"

MAKE the script executable: chmod +x scripts/run-tests-with-log.sh

NOTE: The shell wrapper captures all output. It does not filter per-test names.
For noisy runners, add quiet flags to the underlying test command in the yml instead.
Refer to fix-tests.md for configuring quiet output flags per runner.

UPDATE midtempo-framework.yml:
  Set commands.test (and any test variant commands) to invoke the wrapper script
  Update descriptions to reflect that output is written to [LOG_PATH]

NOTE: Updating midtempo-framework.yml requires a framework rebuild to take effect.
Tell the human: "After saving midtempo-framework.yml, rebuild the framework - use the CLI or midtempo.com depending on your setup."

PRESENT generated script AND the full list of yml changes to human for review.
WAIT for approval.
```

---

## 3. Verify and Heal

```
AFTER writing the script and updating midtempo-framework.yml:

VERIFY §A - Script is executable
  CHECK file exists at generated path
  CHECK file has correct shebang or is valid TS/JS/Python
  IF TypeScript: check ts-node or tsx is available
  IF Python: check the interpreter path resolves

  HEAL: If interpreter missing → adjust shebang or runner command to match available tooling

VERIFY §B - Run the wrapper
  RUN the new test command (as defined in midtempo-framework.yml)

  ALLOW test failures - we are checking the log, not the suite result.
  The runner must complete and produce the log regardless of pass/fail.

VERIFY §C - Log file created
  CHECK [LOG_PATH] exists
  CHECK file is non-empty

  IF missing or empty:
    → READ script output for errors
    → CHECK log path directory exists
    → CHECK script has write permission to that path
    → FIX and re-run
    → REPEAT until log file is created

VERIFY §D - Log contains test output
  RUN: tail -20 [LOG_PATH]

  CHECK output contains recognisable test output:
    - Jest/Vitest: "Tests:", "Test Suites:", "PASS" or "FAIL"
    - pytest: "passed", "failed", "error", or "no tests ran"
    - go test: "ok", "FAIL", or "--- FAIL"
    - Other runners: any suite result or failure line

  IF log contains only noise (npm warnings, node startup messages):
    → Adjust the noise filter in the script
    → Re-run and re-check

VERIFY §E - yml command updated
  READ midtempo-framework.yml
  CONFIRM commands.test.command points to the wrapper script

  IF not updated:
    → Update now
    → Re-read to confirm

PRESENT verification results:

**VERIFICATION RESULTS**

§A Script executable: [PASS / FAIL - details]
§B Wrapper ran: [PASS / FAIL - details]
§C Log created: [PASS / FAIL - path: [LOG_PATH]]
§D Log contains test output: [PASS / FAIL]
§E yml command updated: [PASS / FAIL]

IF any FAIL: fix and re-run that check before proceeding.
IF all PASS: proceed to §4. Complete.
```

---

## 4. Complete

```
RUN: tail -5 [LOG_PATH]

CONFIRM the last 5 lines show recognisable test output.
```

**LOG FILE WRAPPER COMPLETE**

Log path: `[LOG_PATH]`
Wrapper: [path to generated script]
Test command: [updated command in yml]

---

**How the log is used**

Each delivery phase opens in a fresh conversation. At the start of Red, Green, and Refactor phases, the framework runs:

```bash
tail -5 [LOG_PATH]
```

This gives the agent current test state in under a second, without rerunning the suite. On large repos this saves significant time across a full delivery pipeline.

---