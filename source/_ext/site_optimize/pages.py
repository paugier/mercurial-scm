"""Rewriting the pages."""

from __future__ import annotations

import posixpath
import re

from collections.abc import Callable

from .css import BUNDLE, is_external

_ATTRIBUTE_RE = re.compile(r"""([\w:-]+)(?:=(?:"([^"]*)"|'([^']*)'))?""")
_LINK_RE = re.compile(r"[ \t]*<link\b[^>]*>\n?")
_SCRIPT_RE = re.compile(r"[ \t]*<script\b([^>]*)>\s*</script>\n?")
_IMG_RE = re.compile(r"<img\b[^>]*?/?>")
_BUNDLE_VERSION_RE = re.compile(re.escape(BUNDLE) + r"\?v=[0-9a-f]+")


def attributes(tag: str) -> dict[str, str]:
    """Return the attributes of a tag.

    >>> attributes('<link rel="preload" crossorigin href="a.css?v=1" />')
    {'rel': 'preload', 'crossorigin': '', 'href': 'a.css?v=1'}
    """
    inside = tag.strip().strip("<>/").split(None, 1)
    if len(inside) < 2:
        return {}
    return {
        name.lower(): double or single
        for name, double, single in _ATTRIBUTE_RE.findall(inside[1])
    }


def local_path(url: str, page: str) -> str | None:
    """Return the path of a linked file, from the root of the website."""
    if not url or is_external(url):
        return None
    url = re.split(r"[?#]", url)[0]
    path = posixpath.normpath(posixpath.join(posixpath.dirname(page), url))
    return None if path.startswith("..") else path


def style_sheets(html: str, page: str) -> list[str]:
    """Return the paths of the local style sheets of the head of a page."""
    head = html.partition("</head>")[0]
    paths = []
    for link in _LINK_RE.findall(head):
        values = attributes(link)
        path = local_path(values.get("href", ""), page)
        if values.get("rel") == "stylesheet" and path and path != BUNDLE:
            paths.append(path)
    return paths


def optimize_head(
    html: str,
    page: str,
    bundled: list[str],
    version: str,
    is_removed: Callable[[str], bool] = lambda path: False,
) -> str:
    """Make the head of a page load as few things as possible.

    - The style sheets which are in the bundle are replaced by the bundle.
    - The fonts are not loaded before being needed.
    - The scripts are run once the page is parsed, in the same order, except
      `documentation_options.js`, which is needed by inline scripts.
    - The scripts which have been removed are not loaded.

    :param page: path of the page from the root of the website
    :param bundled: paths of the style sheets gathered in the bundle
    :param version: changes each time the bundle changes
    :param is_removed: tells if the file at the given path has been removed
    """
    head, separator, body = html.partition("</head>")
    if not separator:
        return html
    root = posixpath.relpath(".", posixpath.dirname(page) or ".")
    bundle = posixpath.normpath(posixpath.join(root, BUNDLE)) + f"?v={version}"
    done = bool(_BUNDLE_VERSION_RE.search(head))

    def link(match: re.Match) -> str:
        nonlocal done
        values = attributes(match.group(0))
        path = local_path(values.get("href", ""), page)
        rel = values.get("rel")
        if rel == "preload" and values.get("as") == "font":
            return ""
        if rel == "stylesheet" and path in bundled:
            if done:
                return ""
            done = True
            return f'    <link rel="stylesheet" type="text/css" href="{bundle}" />\n'
        return match.group(0)

    def script(match: re.Match) -> str:
        values = attributes(f"<script {match.group(1)}>")
        path = local_path(values.get("src", ""), page)
        if path is None or "defer" in values or "async" in values:
            return match.group(0)
        if is_removed(path):
            return ""
        if posixpath.basename(path) == "documentation_options.js":
            return match.group(0)
        return match.group(0).replace("<script", "<script defer", 1)

    head = _LINK_RE.sub(link, head)
    head = _SCRIPT_RE.sub(script, head)
    head = _BUNDLE_VERSION_RE.sub(f"{BUNDLE}?v={version}", head)
    return head + separator + body


def set_image_sizes(
    html: str, page: str, size: Callable[[str], tuple[int, int] | None]
) -> str:
    """Set the dimensions of the images and load the distant ones lazily.

    The first image of the content is likely to be visible when the page is
    displayed, all the ones below it are loaded when the reader gets close.

    :param page: path of the page from the root of the website
    :param size: returns the width and height of the image at the given path
        from the root of the website, None if unknown
    """
    content_images = 0

    def image(match: re.Match) -> str:
        nonlocal content_images
        tag = match.group(0)
        values = attributes(tag)
        path = local_path(values.get("src", ""), page)
        added = ""
        if path is not None and "width" not in values and "height" not in values:
            dimensions = size(path)
            if dimensions is not None:
                added += ' width="%d" height="%d"' % dimensions
        if path is not None and path.startswith("_images/"):
            content_images += 1
            if content_images > 1 and "loading" not in values:
                added += ' loading="lazy" decoding="async"'
        if not added:
            return tag
        end = "/>" if tag.endswith("/>") else ">"
        return tag[: -len(end)].rstrip() + added + (" />" if end == "/>" else ">")

    return _IMG_RE.sub(image, html)
