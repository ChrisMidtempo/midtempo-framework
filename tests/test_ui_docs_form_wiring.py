"""Tests for docs-modal wiring in ui/js/form.js.

Covers:
- form.js imports init from docs-modal.js (B16)
- docs-modal.js does not import from form.js — coupling direction (B16)
- form.js calls docsModalInit() at DOMContentLoaded (B15)
"""

import re
from pathlib import Path

FORM_FILE = Path("ui/js/form.js")
DOCS_MODAL_FILE = Path("ui/js/docs-modal.js")


class TestFormDocsModalWiring:
    """B15, B16 — form.js imports and calls the docs modal init function."""

    def test_form_js_imports_init_from_docs_modal(self):
        """form.js contains an import of init (or docsModalInit) from ./docs-modal.js. (B16, T5.1)"""
        content = FORM_FILE.read_text()
        assert re.search(
            r"import\s+\{[^}]*init[^}]*\}\s+from\s+['\"]./docs-modal\.js['\"]",
            content,
        ), "form.js must import { init ... } from './docs-modal.js'"

    def test_docs_modal_does_not_import_from_form_js(self):
        """docs-modal.js contains no import from form.js — coupling must flow one way only. (B16, T5.2)

        Known-pass: the scaffolding and implementation must not introduce a reverse dependency.
        Pre-approved as a coupling direction enforcement check.
        """
        content = DOCS_MODAL_FILE.read_text()
        assert "form.js" not in content, (
            "docs-modal.js must not import from form.js — "
            "companion modules are dependencies of form.js, not peers"
        )

    def test_form_js_calls_docs_modal_init_at_dom_content_loaded(self):
        """form.js calls docsModalInit() inside the DOMContentLoaded event listener. (B15, T5.3)"""
        content = FORM_FILE.read_text()
        assert "docsModalInit" in content, "form.js must call docsModalInit() at DOMContentLoaded"
        assert re.search(
            r"DOMContentLoaded.{0,500}docsModalInit",
            content,
            re.DOTALL,
        ), "docsModalInit() must be called inside the DOMContentLoaded listener in form.js"


class TestConfigurationLinkWiring:
    """event-wiring.js wires the configuration anchor link to openModalAt."""

    def test_event_wiring_imports_open_modal_at_from_docs_modal(self):
        """event-wiring.js imports openModalAt from ./docs-modal.js."""
        content = Path("ui/js/event-wiring.js").read_text()
        assert re.search(
            r"import\s+\{[^}]*openModalAt[^}]*\}\s+from\s+['\"]./docs-modal\.js['\"]",
            content,
        ), "event-wiring.js must import { openModalAt } from './docs-modal.js'"

    def test_event_wiring_wires_click_on_configuration_link(self):
        """event-wiring.js queries docs-link-configuration and wires a click to openModalAt."""
        content = Path("ui/js/event-wiring.js").read_text()
        assert "openModalAt" in content, (
            "event-wiring.js must call openModalAt to wire the configuration link"
        )
        assert "docs-link-configuration" in content, (
            "event-wiring.js must query for the docs-link-configuration element"
        )
