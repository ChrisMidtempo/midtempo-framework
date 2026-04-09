"""Filter system for Jinja2 template rendering.

Provides SmartContext wrapper class and filter implementations for template
and macro access to configuration values.
"""

from typing import Any

from jinja2 import pass_context


class _InstructionsNamespace:
    """Dict wrapper supporting attribute access for template conditionals.

    Allows templates to use `{% if instructions.db %}` syntax. Returns empty dict
    for missing keys so conditionals evaluate false gracefully.
    """

    def __init__(self, data: dict) -> None:
        """
        Initialise namespace with instruction metadata dict.

        Args:
            data: Dict mapping instruction names to their metadata
        """
        self._data = data

    def __getattr__(self, name: str) -> dict[str, Any]:
        """Return instruction metadata or empty dict for missing keys."""
        result: dict[str, Any] = self._data.get(name, {})
        return result

    def __contains__(self, name: str) -> bool:
        """Support 'in' operator for dict-style checks."""
        return name in self._data

    def __getitem__(self, name: str) -> dict[str, Any]:
        """Support subscript access for dict-style access."""
        result: dict[str, Any] = self._data[name]
        return result

    def get(self, name: str, default: Any = None) -> Any:
        """Support dict-style get method."""
        return self._data.get(name, default)


class SmartContext:
    """Context wrapper providing filter methods to globally-loaded macros.

    Enables macros loaded via make_module() to call filter methods (cmd, category,
    instructions) directly without template pre-resolution. Wraps context dict and
    provides both attribute/dictionary access to context variables and method-based
    access to filter implementations.
    """

    def __init__(self, data: dict[str, Any], filter_implementations: dict[str, Any]) -> None:
        """
        Initialise SmartContext with context data and filter implementations.

        Args:
            data: Context dictionary with configuration variables
            filter_implementations: Dict mapping filter names to implementation functions
        """
        self._data = data
        self._filters = filter_implementations

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to context dict."""
        if name.startswith("_"):
            # Allow access to private attributes like _data and _filters
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        return self._data[name]

    def __getitem__(self, name: str) -> Any:
        """Support subscript access for dict-style access."""
        return self._data[name]

    def __contains__(self, name: str) -> bool:
        """Support 'in' operator for dict-style checks."""
        return name in self._data

    def get(self, name: str, default: Any = None) -> Any:
        """Support dict-style get method."""
        return self._data.get(name, default)

    def cmd(self, cmd_name: str) -> str:
        """Call cmd filter - accessible as ctx.cmd('test')."""
        cmd_impl = self._filters["cmd"]
        return cmd_impl(self._data, cmd_name)  # type: ignore[no-any-return]

    def category(self, cat_name: str) -> list[tuple[str, str, str]]:
        """Call category filter - accessible as ctx.category('test')."""
        category_impl = self._filters["category"]
        return category_impl(self._data, cat_name)  # type: ignore[no-any-return]

    def instructions(self, instruction_name: str) -> str:
        """Call instructions filter - accessible as ctx.instructions('purpose')."""
        instructions_impl = self._filters["instructions"]
        return instructions_impl(self._data, instruction_name)  # type: ignore[no-any-return]


def _discover_scoped_commands(commands: dict[str, Any], command_name: str) -> list[tuple[str, str]]:
    """Discover scoped command variants (e.g., backend_lint, frontend_lint)."""
    scoped_commands = []
    for key, cmd_def in commands.items():
        if "_" in key and key.endswith(f"_{command_name}"):
            scope = key.rsplit("_", 1)[0]  # Extract scope prefix
            scoped_commands.append((scope, cmd_def["command"]))
    return scoped_commands


def _order_by_language_declaration(
    scoped_commands: list[tuple[str, str]], repo_language: dict[str, str]
) -> list[tuple[str, str]]:
    """Order scoped commands by repo.language declaration order."""
    scope_to_lang = {scope: lang for lang, scope in repo_language.items()}

    # Validate all scopes are mapped
    for cmd_scope, _ in scoped_commands:
        if cmd_scope not in scope_to_lang:
            raise KeyError(f"Scope '{cmd_scope}' not found in repo.language values")

    # Build ordered results following repo.language declaration order
    ordered_results = []
    for lang, scope in repo_language.items():
        for cmd_scope, cmd_str in scoped_commands:
            if cmd_scope == scope:
                ordered_results.append((cmd_str, lang))
                break  # Only one command per scope
    return ordered_results


def _cmd_impl(context: dict[str, Any], cmd_name: str) -> str:
    """
    Implementation function for command string resolution.

    Shared by _cmd_filter (template interface) and SmartContext.cmd() (macro interface).
    Contains core logic for resolving command strings from configuration.

    Args:
        context: Context dict with commands configuration
        cmd_name: Name of command to resolve

    Returns:
        Resolved command string

    Raises:
        KeyError: If command not found in config
    """
    commands = context["commands"]

    # Fast path: exact key lookup (O(1)) for mono-language configs
    if cmd_name in commands:
        value = commands[cmd_name]
        command_str: str = value["command"]

        # Defensive guard: raise clear error if null value bypassed validation
        if command_str is None:
            raise ValueError(
                f"Command '{cmd_name}' has null value. "
                f"This should be prevented by schema validation."
            )

        return command_str

    # Guard check: only core commands support pattern matching
    if cmd_name not in ["lint", "test", "typecheck"]:
        raise KeyError(f"Command '{cmd_name}' not found in config")

    # Pattern matching: discover scoped variants
    scoped_commands = _discover_scoped_commands(commands, cmd_name)
    if not scoped_commands:
        raise KeyError(f"Command '{cmd_name}' not found in config")

    # Order by repo.language declaration and format output
    repo_language = context["repo"]["language"]
    ordered_results = _order_by_language_declaration(scoped_commands, repo_language)
    formatted = ", ".join(f"`{cmd}` ({lang})" for cmd, lang in ordered_results)
    return formatted


def _category_impl(context: dict[str, Any], cat_name: str) -> list[tuple[str, str, str]]:
    """
    Implementation function for category filtering.

    Shared by _category_filter (template interface) and SmartContext.category() (macro interface).
    Contains core logic for filtering commands by category.

    Args:
        context: Context dict with commands configuration
        cat_name: Category name to filter by

    Returns:
        List of (key, command, description) tuples for matching commands
    """
    commands = context["commands"]
    result: list[tuple[str, str, str]] = []

    for key, value in commands.items():
        # Schema guarantees all commands are dicts with category field
        if value.get("category") == cat_name:
            command_str: str = value["command"]

            # Defensive guard: skip commands with null values
            # (should be prevented by schema validation)
            if command_str is None:
                continue

            description: str = value.get("description", "")
            result.append((key, command_str, description))

    return result


def _instructions_impl(context: dict[str, Any], inst_name: str) -> str:
    """
    Implementation function for instruction path formatting.

    Shared by _instructions_filter (template interface) and SmartContext.instructions()
    (macro interface). Contains core logic for formatting instruction paths.

    Args:
        context: Context dict with instructions configuration
        inst_name: Instruction name to format

    Returns:
        Formatted instruction path string

    Raises:
        KeyError: If instruction not found in config
    """
    instructions = context.get("instructions", {})

    if inst_name not in instructions:
        raise KeyError(
            f"Instruction '{inst_name}' not found in config. "
            f"Add to midtempo-framework.yml: instructions.{inst_name}"
        )

    page_value: str = instructions[inst_name]["page"]
    description: str = instructions[inst_name]["description"]
    return f"`/midtempo-framework/instructions/{page_value}` # {description}"


@pass_context
def _cmd_filter(context: dict[str, Any], command_name: str) -> str:
    """
    Jinja2 filter to resolve command string from config context.

    Thin wrapper around _cmd_impl() for template use. Delegates to shared
    implementation function for consistency with SmartContext.cmd().

    Args:
        context: Template context dict (injected by @pass_context)
        command_name: Name of command to resolve from config

    Returns:
        Resolved command string, or formatted multi-command output for scoped variants

    Raises:
        KeyError: If command not found in config or malformed
    """
    return _cmd_impl(context, command_name)


@pass_context
def _category_filter(context: dict[str, Any], category_name: str) -> list[tuple[str, str, str]]:
    """
    Jinja2 filter to extract commands matching a specific category.

    Thin wrapper around _category_impl() for template use. Delegates to shared
    implementation function for consistency with SmartContext.category().

    Args:
        context: Template context dict (injected by @pass_context)
        category_name: Category to filter commands by

    Returns:
        List of (key, command, description) tuples for matching commands

    Raises:
        KeyError: If commands dict not in context
    """
    return _category_impl(context, category_name)


@pass_context
def _instructions_filter(context: dict[str, Any], instruction_name: str) -> str:
    """Jinja2 filter to resolve instruction page from config context.

    Thin wrapper around _instructions_impl() for template use. Delegates to shared
    implementation function for consistency with SmartContext.instructions().

    Args:
        context: Template context dict (injected by @pass_context)
        instruction_name: Name of instruction to resolve from config

    Returns:
        Formatted path string with description comment

    Raises:
        KeyError: If instruction not declared in config
    """
    return _instructions_impl(context, instruction_name)
