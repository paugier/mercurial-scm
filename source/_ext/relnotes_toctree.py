"""Table of contents of the release notes.

The release notes are the pages `relnotes/<version>.md`. Only the most recent
ones are listed in the menu, the other ones are listed on an archive page::

    ```{relnotes-toctree} recent
    ```

    ```{relnotes-toctree} older
    ```

The options are the ones of the `toctree` directive. The number of recent
release notes is set by `relnotes_recent` in `conf.py`.
"""

from __future__ import annotations

import re

from pathlib import Path

from docutils.statemachine import StringList
from sphinx.application import Sphinx
from sphinx.directives.other import TocTree
from sphinx.util.typing import ExtensionMetadata

DIRECTORY = "relnotes"
# page listing the release notes which are not in the menu anymore
ARCHIVE = "/relnotes-archive"

_VERSION_RE = re.compile(r"\d+(\.\d+)*")


def sorted_versions(names: list[str]) -> list[str]:
    """Return the names which are versions, the most recent one first."""
    versions = [name for name in names if _VERSION_RE.fullmatch(name)]
    return sorted(versions, key=lambda v: [int(n) for n in v.split(".")], reverse=True)


def split_versions(names: list[str], recent: int) -> tuple[list[str], list[str]]:
    """Return the recent versions and the older ones."""
    versions = sorted_versions(names)
    return versions[:recent], versions[recent:]


class ReleaseNotesTocTree(TocTree):
    """A `toctree` of the recent release notes or of the older ones."""

    required_arguments = 1
    has_content = False

    def run(self):
        kind = self.arguments[0]
        if kind not in ("recent", "older"):
            raise self.error(f"expected 'recent' or 'older', got {kind!r}")
        # a new release changes both lists
        self.env.note_reread()

        directory = Path(self.env.srcdir) / DIRECTORY
        names = [
            path.stem
            for path in directory.iterdir()
            if path.suffix in self.config.source_suffix
        ]
        recent, older = split_versions(names, self.config.relnotes_recent)
        entries = [f"/{DIRECTORY}/{version}" for version in recent]
        if kind == "older":
            entries = [f"/{DIRECTORY}/{version}" for version in older]
        elif older:
            entries.append(ARCHIVE)

        source, _line = self.get_source_info()
        self.content = StringList(entries, source=source)
        self.arguments = []
        return super().run()


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_config_value("relnotes_recent", 10, "env", types=[int])
    app.add_directive("relnotes-toctree", ReleaseNotesTocTree)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
