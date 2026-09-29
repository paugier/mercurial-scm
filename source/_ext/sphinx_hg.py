"""Roles used by the help of Mercurial, like :hg:`help config`."""

from docutils import nodes

from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.util.docutils import SphinxRole
from sphinx.util.typing import ExtensionMetadata

from hg_help_pages import HelpData, help_data

logger = logging.getLogger(__name__)


def resolve(text: str, data: HelpData) -> tuple[str | None, bool]:
    """Find the page documenting the content of a `hg` role.

    Return the path of the page from the root of the website, without
    extension and possibly followed by an anchor, or None when there is nothing
    to link to. The second value tells if a page should have been found.

    >>> resolve("commit --amend", data)
    ('help/commands/commit', True)
    >>> resolve("help config.merge-tools", data)
    ('help/topics/config#merge-tools', True)
    >>> resolve("help -e rebase", data)
    ('help/extensions/rebase', True)
    """
    words = text.split()
    if not words:
        return None, False

    if words[0] != "help" or len(words) == 1:
        page = data.command_pages.get(words[0])
        if page is not None:
            return f"help/commands/{page}", True
        return None, words[0] not in data.undocumented

    flags = [word for word in words[1:] if word.startswith("-")]
    names = [word for word in words[1:] if not word.startswith("-")]
    if not names or names[0].startswith("<") or names[0].isupper():
        # something like `help -v`, `help <command>` or `help COMMAND`
        return None, False
    name, _, section = names[0].partition(".")
    section = section.partition(".")[0]

    # same order as `hg help`: topics, then commands, then extensions
    kinds = ["topics", "commands", "extensions"]
    if "-e" in flags or "--extension" in flags:
        kinds = ["extensions"]
    elif "-c" in flags or "--command" in flags:
        kinds = ["commands"]
    pages = {
        "topics": data.topic_pages,
        "commands": data.command_pages,
        "extensions": data.extension_pages,
    }
    for kind in kinds:
        page = pages[kind].get(name)
        if page is not None:
            anchor = f"#{section}" if section and kind == "topics" else ""
            return f"help/{kind}/{page}{anchor}", True
    return None, name not in data.undocumented


class HgRole(SphinxRole):
    """A role for hg commands"""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        text = " ".join(self.text.split())
        label = f"`hg {text}`"
        target, expected = resolve(text, help_data())

        if target is None:
            if expected:
                logger.warning(
                    "no help page for :hg:`%s`",
                    text,
                    location=self.get_location(),
                    type="hg",
                    subtype="unknown",
                )
            return [nodes.inline(text=label)], []

        page, _, anchor = target.partition("#")
        to_base = "../" * self.env.docname.count("/")
        refuri = f"{to_base}{page}.html"
        if anchor:
            refuri += f"#{anchor}"
        return [nodes.reference(self.rawtext, label, refuri=refuri)], []


class ConfigDocRole(SphinxRole):
    """A role for `config-doc`

    The generated help pages do not use it: Mercurial replaces the role by the
    documentation of the config item. It is kept so that a page using it can
    still be built.
    """

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        return [], []


def setup(app: Sphinx) -> ExtensionMetadata:
    app.setup_extension("hg_help_pages")
    app.add_role("hg", HgRole())
    app.add_role("config-doc", ConfigDocRole())

    return {
        "version": "0.2",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
