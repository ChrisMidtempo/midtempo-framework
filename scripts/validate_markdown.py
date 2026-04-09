"""Post-generation markdown validator."""

import re
from pathlib import Path

from markdown_it import MarkdownIt


def check_code_block_tags(markdown_path: Path) -> list[str]:
    """
    Check for code blocks missing language tags.

    Args:
        markdown_path: Path to markdown file

    Returns:
        List of violations with file:line context
    """
    content = markdown_path.read_text()
    violations = []

    # Track whether we're inside a code block
    in_code_block = False

    lines = content.split("\n")
    for line_num, line in enumerate(lines, 1):
        # Check if line contains code fence (```)
        if line.strip().startswith("```"):
            if not in_code_block:
                # Opening fence - check for language tag
                fence_content = line.strip()[3:].strip()  # Remove ``` and check what follows
                if not fence_content:
                    # No language tag
                    violations.append(
                        f"{markdown_path.name}:line {line_num}: Code block missing language tag"
                    )
                in_code_block = True
            else:
                # Closing fence
                in_code_block = False

    return violations


def check_template_syntax_leaks(markdown_path: Path) -> list[str]:
    """
    Check for unrendered template syntax in markdown.

    Args:
        markdown_path: Path to markdown file

    Returns:
        List of template syntax leaks with file:line context
    """
    content = markdown_path.read_text()
    leaks = []

    # Pattern to find Jinja2 template syntax
    # Matches {{ ... }} or {% ... %}
    template_patterns = [
        (r"\{\{", "{{"),  # Variable syntax
        (r"\{%", "{%"),  # Statement syntax
    ]

    lines = content.split("\n")
    for line_num, line in enumerate(lines, 1):
        for pattern, syntax_type in template_patterns:
            if re.search(pattern, line):
                leaks.append(
                    f"{markdown_path.name}:line {line_num}: Template syntax leak detected: {syntax_type}"
                )
                break  # Only report once per line

    return leaks


def validate_markdown_syntax(markdown_path: Path) -> bool:
    """
    Validate markdown syntax.

    Args:
        markdown_path: Path to markdown file

    Returns:
        True if valid, raises exception if invalid
    """
    # Read markdown file
    content = markdown_path.read_text()

    # Parse markdown to validate syntax
    md = MarkdownIt()
    md.parse(content)

    # If parsing succeeds without exception, markdown is valid
    return True


def validate_internal_links(markdown_path: Path, base_dir: Path) -> bool:
    """
    Validate internal links in markdown file resolve correctly.

    Args:
        markdown_path: Path to markdown file
        base_dir: Base directory for resolving relative links

    Returns:
        True if all links valid

    Raises:
        Exception: If broken links found
    """
    # Read markdown file
    content = markdown_path.read_text()

    # Extract all markdown links: [text](url)
    link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
    links = re.findall(link_pattern, content)

    # Check each link
    broken_links = []
    for _link_text, link_url in links:
        # Skip external links (http://, https://, etc.)
        if link_url.startswith(("http://", "https://", "mailto:", "#")):
            continue

        # Remove anchor if present (e.g., file.md#section -> file.md)
        link_path = link_url.split("#")[0]

        if not link_path:
            # Pure anchor link (#section) - skip validation
            continue

        # Resolve relative path from base_dir
        target_path = (base_dir / link_path).resolve()

        # Check if file exists
        if not target_path.exists():
            broken_links.append(link_url)

    if broken_links:
        raise ValueError(f"Broken internal links found: {', '.join(broken_links)}")

    return True
