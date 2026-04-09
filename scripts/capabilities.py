"""Central capability definitions and defaults.

This module exports three constants. Do not modify them at runtime.

CAPABILITIES: Registry mapping capability names to metadata dicts with
'default' (bool) and 'description' (str) keys.

DEFAULT_CAPABILITIES: Derived export for backward compatibility, contains
only capability names and boolean defaults.

TEMPLATE_SKIP_RULES: Maps template path patterns to capability keys. The
generation pipeline evaluates this constant to decide which capability-conditional
templates to skip. Single-key entries (str) skip when the named capability is
falsy. Multi-key entries (list[str]) skip when all listed capabilities are falsy.
Add a new entry here to gate a new conditional template — no changes to
generate_docs.py required.
"""

# Capability registry with complete metadata.
# Source of truth for capability definitions.
CAPABILITIES: dict[str, dict[str, bool | str]] = {
    "hasUI": {
        "default": False,
        "description": "Whether the repository has UI components",
    },
    "hasDB": {
        "default": False,
        "description": "Whether the repository has database access",
    },
    "hasTypecheck": {
        "default": True,
        "description": "Whether the repository has type checking",
    },
    "isPublicFacing": {
        "default": False,
        "description": "Application serves public-facing traffic",
    },
    "handlesConfidentialData": {
        "default": False,
        "description": "Application processes confidential or sensitive data",
    },
    "hasAuthentication": {
        "default": False,
        "description": "Application implements authentication",
    },
}

# Backward-compatible export for existing config creation paths.
# Derived from CAPABILITIES registry.
DEFAULT_CAPABILITIES: dict[str, bool] = {
    name: meta["default"] for name, meta in CAPABILITIES.items()  # type: ignore[misc]
}

# Maps template path patterns to capability keys.
# Single-key entries (str): skip if the named capability is falsy.
# Multi-key entries (list[str]): skip if all listed capabilities are falsy.
# rules/security/secrets-management is absent — universal; always generate.
TEMPLATE_SKIP_RULES: dict[str, str | list[str]] = {
    "rules/db": "hasDB",
    "rules/security/input-validation": ["hasUI", "hasDB"],
    "rules/security/authentication": "hasAuthentication",
    "rules/security/data-protection": "handlesConfidentialData",
    "rules/security/public-hardening": "isPublicFacing",
}
