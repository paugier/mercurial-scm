"""Reducing the icon fonts to the icons in use."""

from __future__ import annotations

import hashlib
import posixpath
import re

from collections.abc import Iterable
from pathlib import Path

from .css import (
    BUNDLE,
    compact,
    declaration,
    rebase_urls,
    relative_url,
    split_list,
)

# directory of the reduced fonts from the root of the website
FONTS = "_static/fonts"


class FontFaces:
    """Rewrite the `@font-face` rules to use fonts loaded by `woff2` only.

    The fonts whose path matches `subset` are reduced to the characters of
    the style sheet, this is done later since the characters are only known
    when the style sheet is complete.
    """

    def __init__(self, subset: Iterable[str] = ()):
        self.subset = [re.compile(pattern) for pattern in subset]
        # paths of the fonts to reduce, with their placeholder in the rules
        self.fonts: dict[str, str] = {}

    def __call__(self, declarations: list, path: str) -> str:
        parts = []
        for item in declarations:
            if item.type != "declaration":
                continue
            if item.lower_name != "src":
                parts.append(declaration(item))
                continue
            sources = [compact(source) for source in split_list(item.value)]
            modern = [source for source in sources if "woff2" in source]
            source = rebase_urls((modern or sources)[0], path)
            url = re.search(r'url\("([^"?#]+)', source)
            if modern and url and any(p.search(url.group(1)) for p in self.subset):
                font = posixpath.normpath(posixpath.join("_static", url.group(1)))
                placeholder = self.fonts.setdefault(font, f"@@font{len(self.fonts)}@@")
                source = placeholder + source + placeholder
            parts.append(f"src:{source}")
        return f"@font-face{{{';'.join(parts)}}}"

    def resolve(self, css: str, codepoints: set[int], outdir: Path) -> str:
        """Write the reduced fonts and complete the rules using them.

        The rules of the fonts without any of the characters are removed.
        """
        for font, placeholder in self.fonts.items():
            name = subset_font(outdir / font, outdir / FONTS, codepoints)
            mark = re.escape(placeholder)
            if name is None:
                css = re.sub(rf"@font-face\{{[^}}]*{mark}[^}}]*\}}", "", css)
                continue
            url = relative_url(BUNDLE, posixpath.relpath(f"{FONTS}/{name}", "_static"))
            source = f'url("{url}") format("woff2")'
            css = re.sub(rf"{mark}.*?{mark}", lambda _: source, css)
        return css


def subset_font(font: Path, directory: Path, codepoints: set[int]) -> str | None:
    """Write a font reduced to the given characters.

    Return the name of the file written in the directory, or None when the font
    has none of the characters.
    """
    import logging as std_logging

    from fontTools import subset
    from fontTools.ttLib import TTFont

    std_logging.getLogger("fontTools").setLevel(std_logging.WARNING)
    with TTFont(font, recalcTimestamp=False) as content:
        wanted = codepoints & set(content.getBestCmap())
        if not wanted:
            return None
        options = subset.Options(flavor="woff2", layout_features=["*"])
        options.timing = False
        subsetter = subset.Subsetter(options)
        subsetter.populate(unicodes=wanted)
        subsetter.subset(content)
        directory.mkdir(parents=True, exist_ok=True)
        temporary = directory / (font.name + ".tmp")
        subset.save_font(content, temporary, options)
    digest = hashlib.sha256(temporary.read_bytes()).hexdigest()[:8]
    name = f"{font.stem}.{digest}.woff2"
    temporary.replace(directory / name)
    return name
