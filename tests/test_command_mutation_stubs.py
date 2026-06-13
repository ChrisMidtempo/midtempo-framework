"""Tests for mutation testing command stubs in commands/*.yml.j2 files.

Covers:
- T3.1: Commented `mutate` stub present in all 18 command files (parametrized)
- T3.2: `mutate` stub appears after `test_e2e` block in all 18 files (parametrized)
- T3.3: TypeScript/JavaScript `mutate` stub uses `npx stryker run` (parametrized)
- T3.4: Non-TypeScript/JavaScript, non-Swift `mutate` stubs include caveat text (parametrized, 13 files)
- T3.5: Swift `mutate` stub includes "last release September 2023" note
- T3.6: `mutate_diff` stub present in each of the 4 TypeScript/JavaScript files (parametrized)
- T3.7: `mutate_diff` stub absent from each of the 14 non-TypeScript/JavaScript files (parametrized)
- T3.8: 5 unchanged files contain neither `mutate` nor `mutate_diff` stub (parametrized)
"""

import pytest

from scripts.paths import COMMANDS_DIR

TS_JS_FILES = [
    "typescript.yml.j2",
    "typescript-npm.yml.j2",
    "javascript.yml.j2",
    "javascript-npm.yml.j2",
]

NON_TS_JS_NON_SWIFT_FILES = [
    "csharp.yml.j2",
    "go.yml.j2",
    "java-gradle.yml.j2",
    "java-maven.yml.j2",
    "kotlin.yml.j2",
    "kotlin-maven.yml.j2",
    "php.yml.j2",
    "python.yml.j2",
    "python-uv.yml.j2",
    "python-poetry.yml.j2",
    "ruby.yml.j2",
    "rust.yml.j2",
    "scala.yml.j2",
]

ALL_18_FILES = TS_JS_FILES + NON_TS_JS_NON_SWIFT_FILES + ["swift.yml.j2"]

NON_TS_JS_FILES = NON_TS_JS_NON_SWIFT_FILES + ["swift.yml.j2"]

UNCHANGED_FILES = [
    "clojure.yml.j2",
    "dart.yml.j2",
    "elixir.yml.j2",
    "flutter.yml.j2",
    "haskell.yml.j2",
]


@pytest.mark.parametrize("file_name", ALL_18_FILES)
def test_mutate_stub_present_in_command_file(file_name):
    """Commented `mutate` stub present in each of the 18 command files. (T3.1, B7)"""
    content = (COMMANDS_DIR / file_name).read_text()

    assert "# mutate:" in content, (
        f"{file_name}: commented '# mutate:' stub not found — "
        "add mutate stub in §3 Variants after test_e2e block"
    )


@pytest.mark.parametrize("file_name", ALL_18_FILES)
def test_mutate_stub_appears_after_test_e2e_block(file_name):
    """Commented `mutate` stub appears after the `test_e2e` block in each of the 18 files. (T3.2, B7)"""
    content = (COMMANDS_DIR / file_name).read_text()

    assert "# test_e2e:" in content, (
        f"{file_name}: '# test_e2e:' block not found — "
        "cannot verify stub placement without reference block"
    )
    assert "# mutate:" in content, f"{file_name}: '# mutate:' stub not found"

    test_e2e_pos = content.index("# test_e2e:")
    mutate_pos = content.index("# mutate:")

    assert mutate_pos > test_e2e_pos, (
        f"{file_name}: '# mutate:' stub must appear after '# test_e2e:' block — "
        "stub placement must follow the test_e2e commented block in §3 Variants"
    )


@pytest.mark.parametrize("file_name", TS_JS_FILES)
def test_ts_js_mutate_stub_uses_npx_stryker_run(file_name):
    """TypeScript/JavaScript `mutate` stub uses `npx stryker run` as command. (T3.3, B7)"""
    content = (COMMANDS_DIR / file_name).read_text()

    assert 'command: "npx stryker run"' in content, (
        f"{file_name}: mutate stub must use '\"npx stryker run\"' as command — "
        "other command strings are incorrect for TypeScript/JavaScript"
    )


@pytest.mark.parametrize("file_name", NON_TS_JS_NON_SWIFT_FILES)
def test_non_ts_js_mutate_stub_includes_caveat(file_name):
    """Non-TypeScript/JavaScript, non-Swift `mutate` stubs include caveat text. (T3.4, B7)"""
    content = (COMMANDS_DIR / file_name).read_text()

    assert "# not validated; review before use" in content, (
        f"{file_name}: mutate stub must include '# not validated; review before use' caveat — "
        "missing caveat could mislead consumers into using an untested command as-is"
    )


def test_swift_mutate_stub_includes_last_release_note():
    """Swift `mutate` stub includes 'last release September 2023' note. (T3.5, B7)"""
    content = (COMMANDS_DIR / "swift.yml.j2").read_text()

    assert "# not validated; review before use; last release September 2023" in content, (
        "swift.yml.j2: mutate stub must include 'last release September 2023' alongside caveat — "
        "warns consumers the tool may be abandoned"
    )


@pytest.mark.parametrize("file_name", TS_JS_FILES)
def test_mutate_diff_stub_present_in_ts_js_files(file_name):
    """`mutate_diff` stub present in each of the 4 TypeScript/JavaScript files. (T3.6, B8)"""
    content = (COMMANDS_DIR / file_name).read_text()

    assert "# mutate_diff:" in content, (
        f"{file_name}: commented '# mutate_diff:' stub not found — "
        "TypeScript/JavaScript files require both mutate and mutate_diff stubs"
    )


@pytest.mark.parametrize("file_name", NON_TS_JS_FILES)
def test_mutate_diff_stub_absent_from_non_ts_js_files(file_name):
    """`mutate_diff` stub absent from each of the 14 non-TypeScript/JavaScript files. (T3.7, B8)"""
    content = (COMMANDS_DIR / file_name).read_text()

    assert "# mutate_diff:" not in content, (
        f"{file_name}: '# mutate_diff:' stub must not be present — "
        "mutate_diff stub is for TypeScript/JavaScript files only"
    )


@pytest.mark.parametrize("file_name", TS_JS_FILES)
def test_mutate_targeted_stub_present_in_ts_js_files(file_name):
    """`mutate_targeted` stub present in each of the 4 TypeScript/JavaScript files.

    Stryker is the only mutation tool with a validated path-filter flag, so the
    targeted stub ships for the TypeScript/JavaScript family only. `mt.md.j2`
    falls back to the full `mutate` command for every other language.
    """
    content = (COMMANDS_DIR / file_name).read_text()

    assert "# mutate_targeted:" in content, (
        f"{file_name}: commented '# mutate_targeted:' stub not found — "
        "TypeScript/JavaScript files require a path-filter mutation stub"
    )


@pytest.mark.parametrize("file_name", TS_JS_FILES)
def test_ts_js_mutate_targeted_stub_uses_stryker_mutate_flag(file_name):
    """TypeScript/JavaScript `mutate_targeted` stub uses Stryker's `--mutate` flag."""
    content = (COMMANDS_DIR / file_name).read_text()

    assert 'command: "npx stryker run --mutate"' in content, (
        f"{file_name}: mutate_targeted stub must use '\"npx stryker run --mutate\"' — "
        "Stryker's --mutate flag scopes mutation to supplied paths"
    )


@pytest.mark.parametrize("file_name", NON_TS_JS_FILES)
def test_mutate_targeted_stub_absent_from_non_ts_js_files(file_name):
    """`mutate_targeted` stub absent from each of the 14 non-TypeScript/JavaScript files."""
    content = (COMMANDS_DIR / file_name).read_text()

    assert "# mutate_targeted:" not in content, (
        f"{file_name}: '# mutate_targeted:' stub must not be present — "
        "mutate_targeted stub is for the Stryker (TypeScript/JavaScript) family only"
    )


@pytest.mark.parametrize("file_name", UNCHANGED_FILES)
def test_unchanged_files_contain_no_mutation_stubs(file_name):
    """5 unchanged files contain neither `mutate` nor `mutate_diff` stub. (T3.8, B9)"""
    content = (COMMANDS_DIR / file_name).read_text()

    assert "# mutate:" not in content, (
        f"{file_name}: '# mutate:' stub must not be present — "
        "no mature mutation testing tooling exists for this language"
    )
    assert "# mutate_diff:" not in content, (
        f"{file_name}: '# mutate_diff:' stub must not be present — "
        "no mature mutation testing tooling exists for this language"
    )
    assert "# mutate_targeted:" not in content, (
        f"{file_name}: '# mutate_targeted:' stub must not be present — "
        "no mature mutation testing tooling exists for this language"
    )
