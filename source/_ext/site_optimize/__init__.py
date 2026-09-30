"""Reduce the size of the website and the loading time of its pages.

Once the HTML pages are written, this extension:

- gathers the style sheets of the pages in a single one, without the rules
  which cannot apply to any page,
- reduces the icon fonts to the icons used by the style sheet,
- stops loading the scripts and the fonts before the first rendering,
- sets the dimensions of the images, so that the layout of the page does not
  change when they are loaded,
- removes the files which are not used by the pages.

Nothing is modified in place: the files made by this extension have their own
names and the original ones are removed, so that Sphinx can copy them again
in the next build.

The class names built by scripts at runtime cannot be found, they have to be
listed in `site_optimize_safelist` in `conf.py`, as regular expressions.

Modules:

- ``css``: reading, purging and gathering the style sheets
- ``fonts``: reducing the icon fonts to the icons in use
- ``pages``: rewriting the pages
- ``build``: running all of this on the built website
"""

from __future__ import annotations

from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata

from .build import REMOVED, Optimizer, optimize
from .css import (
    BUNDLE,
    Purger,
    escape_non_ascii,
    html_names,
    is_external,
    relative_url,
    script_names,
)
from .fonts import FONTS, FontFaces, subset_font
from .pages import (
    attributes,
    optimize_head,
    set_image_sizes,
    style_sheets,
)

__all__ = [
    "BUNDLE",
    "FONTS",
    "REMOVED",
    "FontFaces",
    "Optimizer",
    "Purger",
    "attributes",
    "escape_non_ascii",
    "html_names",
    "is_external",
    "optimize",
    "optimize_head",
    "relative_url",
    "script_names",
    "set_image_sizes",
    "setup",
    "style_sheets",
    "subset_font",
]


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_config_value("site_optimize", True, "")
    app.add_config_value("site_optimize_safelist", [], "")
    app.add_config_value("site_optimize_subset_fonts", [r"fontawesome"], "")
    app.add_config_value("site_optimize_remove", REMOVED, "")
    # once all the other extensions have written their files
    app.connect("build-finished", optimize, priority=900)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
