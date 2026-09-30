"""Make incremental builds give the same website as clean builds.

Sphinx only writes the pages of the documents which changed, and never removes
what it wrote. It is not enough for this website:

- All the pages show things which come from the other documents: the titles of
  the pages in the navigation, the categories, tags and archives of the news,
  the checksum of the scripts and the dimensions of the logo. When any of
  these changes, all the pages are written again. The documents are not read
  again, so this is much faster than a clean build.
- The pages of the documents, tags or categories which do not exist anymore
  are removed, as well as the images and the static files which are not used
  anymore.

What the previous build did is kept in `.incremental_build.json` in the output
directory.
"""

from __future__ import annotations

import hashlib
import json

from pathlib import Path

from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.util import logging
from sphinx.util.typing import ExtensionMetadata

logger = logging.getLogger(__name__)

STATE = ".incremental_build.json"

# what is in the description of a post but is not shown by the other pages
_POST_CONTENT = ("doctree", "excerpt")


def digest(value: object) -> str:
    """Return a short checksum of the representation of a value."""
    return hashlib.sha256(repr(value).encode()).hexdigest()[:16]


def navigation(env: BuildEnvironment) -> list:
    """Describe what the navigation shows: titles and tables of contents."""
    description = []
    for docname in sorted(env.tocs):
        title = env.titles[docname].astext() if docname in env.titles else ""
        toctrees = [
            sorted((key, repr(value)) for key, value in toctree.attributes.items())
            for toctree in env.tocs[docname].findall(addnodes.toctree)
        ]
        description.append((docname, title, toctrees))
    return description


def posts(env: BuildEnvironment) -> list:
    """Describe what the pages of the news show of all the posts."""
    description = []
    for docname, infos in sorted(getattr(env, "ablog_posts", {}).items()):
        for info in infos:
            shown = sorted(
                (key, repr(value))
                for key, value in info.items()
                if key not in _POST_CONTENT
            )
            description.append((docname, shown))
    return description


def static_files(directories: list[Path]) -> dict[str, str]:
    """Return the checksum of the static files, by path in `_static`.

    Like Sphinx does, a file of a directory replaces the file with the same
    path in the previous directories.
    """
    checksums = {}
    for directory in directories:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                content = path.read_bytes()
                relative = path.relative_to(directory).as_posix()
                checksums[relative] = hashlib.sha256(content).hexdigest()[:16]
    return checksums


def removed(previous: list[str] | dict, current: list[str] | dict) -> list[str]:
    """Return what the previous build made and this build does not make.

    >>> removed(["a", "b", "c"], ["c", "a", "d"])
    ['b']
    """
    return sorted(set(previous) - set(current))


def load_state(outdir: Path) -> dict:
    try:
        state = json.loads((outdir / STATE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return state if isinstance(state, dict) else {}


class IncrementalBuild:
    def __init__(self, app: Sphinx):
        self.app = app
        self.outdir = Path(app.outdir)
        self.previous = load_state(self.outdir)
        self.static: dict[str, str] = {}
        self.shared = ""
        # the pages written by this process, which are all the pages that are
        # not the one of a document since these are always written
        self.pages: set[str] = set()

    def static_directories(self) -> list[Path]:
        confdir = Path(self.app.confdir)
        return [confdir / path for path in self.app.config.html_static_path]

    def on_env_updated(self, app: Sphinx, env: BuildEnvironment) -> list[str]:
        """Ask to write all the pages when what they share changed."""
        self.static = static_files(self.static_directories())
        self.shared = digest((navigation(env), posts(env), sorted(self.static.items())))
        if self.shared == self.previous.get("shared"):
            return []
        if self.previous:
            logger.info("what all the pages share changed, writing all of them")
        return sorted(env.found_docs)

    def on_page_context(self, app, pagename, templatename, context, doctree) -> None:
        self.pages.add(pagename)

    def on_build_finished(self, app: Sphinx, exception: Exception | None) -> None:
        if exception is not None:
            return
        builder = app.builder
        pages = sorted(self.pages | app.env.found_docs)
        images = sorted({name for _docnames, name in app.env.images.values()})

        stale = [
            Path(builder.get_outfilename(page))
            for page in removed(self.previous.get("pages", []), pages)
        ]
        stale += [
            self.outdir / builder.imagedir / name
            for name in removed(self.previous.get("images", []), images)
        ]
        previous_static = self.previous.get("static", {})
        for name in removed(previous_static, self.static):
            path = self.outdir / "_static" / name
            # it could now be the file of a theme or of an extension
            if (
                path.is_file()
                and static_files([path.parent]).get(path.name)
                == (previous_static[name])
            ):
                stale.append(path)
        count = sum(self.remove(path) for path in stale)
        if count:
            logger.info(
                "removed %d files which are not part of the website anymore", count
            )

        state = {
            "shared": self.shared,
            "pages": pages,
            "images": images,
            "static": self.static,
        }
        (self.outdir / STATE).write_text(json.dumps(state, indent=1), encoding="utf-8")

    def remove(self, path: Path) -> bool:
        """Remove a file and the directories it leaves empty."""
        if not path.is_file():
            return False
        path.unlink()
        for parent in path.parents:
            if parent == self.outdir or any(parent.iterdir()):
                break
            parent.rmdir()
        return True


def on_builder_inited(app: Sphinx) -> None:
    if app.builder.format != "html":
        return
    build = IncrementalBuild(app)
    app.connect("env-updated", build.on_env_updated)
    app.connect("html-page-context", build.on_page_context)
    app.connect("build-finished", build.on_build_finished)


def setup(app: Sphinx) -> ExtensionMetadata:
    app.connect("builder-inited", on_builder_inited)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
