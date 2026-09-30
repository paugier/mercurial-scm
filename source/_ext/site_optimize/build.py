"""Running all the reductions on the built website."""

from __future__ import annotations

import hashlib
import re
import shutil

from pathlib import Path

import imagesize

from sphinx.application import Sphinx
from sphinx.util import logging

from .css import BUNDLE, Purger, escape_non_ascii, html_names, script_names
from .fonts import FONTS, FontFaces
from .pages import optimize_head, set_image_sizes, style_sheets

logger = logging.getLogger(__name__)

# files which are only useful to build the themes or not used by the pages
REMOVED = [
    r"\.map$",
    r"\.(ttf|eot|woff)$",
    r"\.(po|mo)$",
    r"\.LICENSE\.txt$",
    r"webpack-macros\.html$",
    r"^_sphinx_design_static/",
    # the icons are displayed by the style sheet, not by the script
    r"^_static/vendor/fontawesome/",
    r"^_static/images/logo_(binder|colab|deepnote|jupyterhub)\.",
]


class Optimizer:
    def __init__(self, outdir: Path, config):
        self.outdir = outdir
        self.safelist = config.site_optimize_safelist
        self.subset = config.site_optimize_subset_fonts
        self.remove = config.site_optimize_remove
        self._sizes: dict[str, tuple[int, int] | None] = {}

    def run(self) -> None:
        pages = {
            path.relative_to(self.outdir).as_posix(): path.read_text(encoding="utf-8")
            for path in sorted(self.outdir.rglob("*.html"))
            if "_static" not in path.relative_to(self.outdir).parts
        }
        bundled = self.bundled_style_sheets(pages)
        self.imported = []
        version = self.write_bundle(bundled, pages) if bundled else None
        if version is None:
            version = self.current_version()
        for page, html in pages.items():
            optimized = set_image_sizes(html, page, self.image_size)
            if version is not None:
                optimized = optimize_head(
                    optimized, page, bundled, version, self.is_removed
                )
            if optimized != html:
                (self.outdir / page).write_text(optimized, encoding="utf-8")
        self.clean(bundled + self.imported)

    def bundled_style_sheets(self, pages: dict[str, str]) -> list[str]:
        """Return the style sheets to gather, the ones of the first new page.

        The pages which are not written again by an incremental build do not
        list them anymore, but some pages are always written.
        """
        for page in sorted(pages, key=lambda page: (page.count("/"), page)):
            paths = style_sheets(pages[page], page)
            if paths:
                return paths
        return []

    def current_version(self) -> str | None:
        bundle = self.outdir / BUNDLE
        if not bundle.exists():
            return None
        return hashlib.sha256(bundle.read_bytes()).hexdigest()[:8]

    def read(self, path: str) -> str:
        return (self.outdir / path).read_text(encoding="utf-8")

    def write_bundle(self, bundled: list[str], pages: dict[str, str]) -> str:
        used = set()
        for html in pages.values():
            used |= html_names(html)
        for script in self.outdir.rglob("*.js"):
            relative = script.relative_to(self.outdir).as_posix()
            if relative == "searchindex.js" or self.is_removed(relative):
                continue
            used |= script_names(script.read_text(encoding="utf-8"))

        font_faces = FontFaces(self.subset)
        purger = Purger(used, self.safelist, font_faces)
        before = 0
        parts = []
        for path in bundled:
            css = self.read(path)
            before += len(css.encode())
            logger.debug("style sheet: %s", path)
            parts.append(purger.purge(css, path, self.read))
        self.imported = purger.imported
        css, codepoints = escape_non_ascii("".join(parts))

        shutil.rmtree(self.outdir / FONTS, ignore_errors=True)
        css = font_faces.resolve(css, codepoints, self.outdir)
        (self.outdir / BUNDLE).write_text(css, encoding="utf-8")
        logger.info(
            "style sheets: %d files of %.0f kB gathered in %s of %.0f kB",
            len(bundled),
            before / 1000,
            BUNDLE,
            len(css) / 1000,
        )
        return self.current_version()

    def image_size(self, path: str) -> tuple[int, int] | None:
        if path not in self._sizes:
            self._sizes[path] = None
            file = self.outdir / path
            if file.is_file():
                try:
                    width, height = imagesize.get(file)
                except Exception:
                    width = height = -1
                if width > 0 and height > 0:
                    self._sizes[path] = (round(width), round(height))
        return self._sizes[path]

    def is_removed(self, path: str) -> bool:
        return any(re.search(pattern, path) for pattern in self.remove)

    def clean(self, bundled: list[str]) -> None:
        """Remove the files which are not used by the pages."""
        removed = size = 0
        for file in sorted(self.outdir.rglob("*")):
            relative = file.relative_to(self.outdir).as_posix()
            if not file.is_file() or relative == BUNDLE:
                continue
            if relative in bundled or self.is_removed(relative):
                removed += 1
                size += file.stat().st_size
                file.unlink()
        for directory in sorted(self.outdir.rglob("*"), reverse=True):
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()
        logger.info("removed %d unused files of %.0f kB", removed, size / 1000)


def optimize(app: Sphinx, exception: Exception | None) -> None:
    if exception is not None or app.builder.name not in ("html", "dirhtml"):
        return
    if not app.config.site_optimize:
        return
    Optimizer(Path(app.outdir), app.config).run()
