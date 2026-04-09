#!/usr/bin/env python3
"""Test red (malicious) YAML configs against the validator and report findings.

Runs each red-*.yml file in planning/assets/ through validate_config and reports
whether it was correctly rejected, unexpectedly accepted, or triggered an error
outside of normal validation (e.g. a crash or unsafe YAML load).

Exit code 0 if all files behaved as documented (reject or known-pass-by-design).
Exit code 1 if any file produced an unexpected result.
"""

import sys
from pathlib import Path

import yaml
from jsonschema import ValidationError

# Ensure repo root is on sys.path so scripts/ imports resolve
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_config import validate_config  # noqa: E402

ASSETS_DIR = REPO_ROOT / "planning" / "assets"

# These files are expected to PASS schema validation by design.
# The risk they represent is in server-side execution or browser rendering,
# not in schema structure. Document the reason so the report is clear.
KNOWN_PASS_BY_DESIGN = {
    "red-command-injection.yml": (
        "command strings are free-form in schema; "
        "risk is shell=True in server (CG-IV4), not schema validation"
    ),
    "red-xss-in-strings.yml": (
        "HTML tags are valid strings; "
        "risk is innerHTML vs textContent in browser (CG-IV6), not schema validation"
    ),
    "red-path-traversal-logfile.yml": (
        "logfile accepts any string in schema; "
        "risk is server writing to arbitrary paths, not schema validation"
    ),
    "red-command-key-special-chars.yml": (
        "command key names are unconstrained in schema (additionalProperties); "
        "keys appear as literal text in output only — no filesystem or shell exposure confirmed"
    ),
    "red-instruction-page-path-traversal.yml": (
        "page value rendered as literal text in generated markdown, never opened from disk; "
        "regression test for this boundary — if generator ever inlines instruction files, revisit"
    ),
}

RESET = "\033[0m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
DIM = "\033[2m"


def _colour(text: str, code: str) -> str:
    return f"{code}{text}{RESET}"


def run() -> int:
    """Run all red config files and report findings. Returns exit code."""
    red_files = sorted(ASSETS_DIR.glob("red-*.yml"))

    if not red_files:
        print(_colour(f"No red-*.yml files found in {ASSETS_DIR}", YELLOW))
        return 1

    print(_colour(f"\nRed Config Security Test — {len(red_files)} files\n", BOLD))
    print(f"{'File':<45} {'Result':<10} Detail")
    print("-" * 100)

    unexpected = []

    for path in red_files:
        name = path.name

        try:
            validate_config(path)
            # File passed validation
            if name in KNOWN_PASS_BY_DESIGN:
                reason = KNOWN_PASS_BY_DESIGN[name]
                print(
                    f"{name:<45} "
                    f"{_colour('PASS*', YELLOW):<20} "
                    f"{_colour(f'by design — {reason}', DIM)}"
                )
            else:
                print(
                    f"{name:<45} "
                    f"{_colour('PASS', RED):<20} "
                    f"{_colour('UNEXPECTED — file passed but should have been rejected', BOLD)}"
                )
                unexpected.append((name, "passed validation unexpectedly"))

        except yaml.YAMLError as exc:
            # YAML itself failed to parse — still a rejection, expected for yaml-bomb etc.
            short = str(exc).splitlines()[0][:80]
            print(
                f"{name:<45} "
                f"{_colour('REJECT', GREEN):<20} "
                f"YAMLError: {short}"
            )

        except (ValueError, ValidationError) as exc:
            # validate_config raises raw ValidationError; enhanced variant raises ValueError
            short = str(exc).splitlines()[0][:80]
            print(
                f"{name:<45} "
                f"{_colour('REJECT', GREEN):<20} "
                f"{short}"
            )

        except Exception as exc:
            # Unexpected crash — this itself is a finding
            short = f"{type(exc).__name__}: {str(exc)[:60]}"
            print(
                f"{name:<45} "
                f"{_colour('CRASH', RED):<20} "
                f"{_colour(short, BOLD)}"
            )
            unexpected.append((name, short))

    print("-" * 100)

    known_pass_count = sum(1 for f in red_files if f.name in KNOWN_PASS_BY_DESIGN)
    reject_count = len(red_files) - len(unexpected) - known_pass_count
    print(
        f"\n{_colour(f'{reject_count} rejected', GREEN)}  |  "
        f"{_colour(f'{known_pass_count} pass by design', YELLOW)}  |  "
        f"{_colour(f'{len(unexpected)} unexpected', RED if unexpected else DIM)}\n"
    )

    if unexpected:
        print(_colour("UNEXPECTED RESULTS — investigate before shipping:\n", BOLD))
        for name, detail in unexpected:
            print(f"  {_colour('!', RED)} {name}: {detail}")
        print()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(run())
