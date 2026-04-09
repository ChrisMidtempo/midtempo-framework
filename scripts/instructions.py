"""Instruction registry with example instruction entries.

This module exports INSTRUCTIONS constant mapping instruction names to metadata
with page (file path) and description (human-readable purpose). Instructions are
client-declared in config. Registry serves as documentation and schema generation
source.

INSTRUCTIONS: Registry mapping instruction names to metadata dicts with 'page'
(str) and 'description' (str) keys.
"""

# Instruction registry with example instruction entries.
# Source for schema generation - not used for config merging.
INSTRUCTIONS: dict[str, dict[str, str]] = {
    "db": {
        "page": "db.md",
        "description": "Database patterns and conventions",
    },
    "api": {
        "page": "api.md",
        "description": "API design and implementation guidelines",
    },
    "error-handling": {
        "page": "error-handling.md",
        "description": "Error handling strategies and patterns",
    },
}
