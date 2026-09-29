"""Generate the ``hg help`` pages of the website.

The pages are built from Mercurial's own help machinery, imported as a Python
library, so that they contain what ``hg help <name>`` shows: synopsis, aliases,
options and the generated parts of the topics (template keywords, revset
predicates, config items...).

Only the Mercurial installed next to Sphinx is used. No ``hg`` executable is
run and no configuration file is read, so the result does not depend on the
machine building the website.

URL stability: existing pages must never move. A command lives in
``help/commands/<name>`` (with ``::`` replaced by ``_``), a topic in
``help/topics/<first name of the topic>`` and an extension in
``help/extensions/<name>``. Aliases never get a page of their own.

This package is a Sphinx extension (pages are generated on ``builder-inited``)
and can also be run directly, from ``source/_ext``::

    python -m hg_help_pages [output directory]

Modules:

- ``model``: what is documented
- ``rst``: helpers to write RST
- ``reader``: reading the help of Mercurial
- ``writer``: writing the pages
"""

from __future__ import annotations

import os

from pathlib import Path

# Mercurial reads its environment once, when `mercurial.encoding` is imported,
# and translates some messages at import time. This has to be set before any
# Mercurial module is imported.
os.environ["HGPLAIN"] = "1"
os.environ["HGRCPATH"] = ""
os.environ["HGENCODING"] = "UTF-8"

from .model import (  # noqa: E402
    Command,
    Extension,
    HelpData,
    HelpGenerationError,
    Topic,
)
from .reader import (  # noqa: E402
    THIRD_PARTY_EXTENSIONS,
    collect,
    help_data,
    mercurial_version,
)
from .rst import (  # noqa: E402
    heading,
    options_rst,
    parse_table,
    split_doc,
    strip_cli_hints,
)
from .writer import generate, render_pages, write_pages  # noqa: E402

__all__ = [
    "THIRD_PARTY_EXTENSIONS",
    "Command",
    "Extension",
    "HelpData",
    "HelpGenerationError",
    "Topic",
    "collect",
    "generate",
    "heading",
    "help_data",
    "mercurial_version",
    "options_rst",
    "parse_table",
    "render_pages",
    "setup",
    "split_doc",
    "strip_cli_hints",
    "write_pages",
]


def _on_builder_inited(app) -> None:
    from sphinx.errors import ExtensionError
    from sphinx.util import logging

    logger = logging.getLogger(__name__)
    try:
        changed = generate(Path(app.srcdir) / "help")
    except HelpGenerationError as exc:
        raise ExtensionError(str(exc)) from exc
    data = help_data()
    for warning in data.warnings:
        logger.warning(warning, type="hg", subtype="extension")
    logger.info(
        "hg help pages for Mercurial %s: %d commands, %d topics, "
        "%d extensions (%d files updated)",
        data.version,
        len(data.commands),
        len(data.topics),
        len(data.extensions),
        len(changed),
    )


def setup(app):
    # all the pages are read again when Mercurial changes, for their links
    app.add_config_value("hg_help_mercurial_version", mercurial_version(), "env")
    app.connect("builder-inited", _on_builder_inited)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
