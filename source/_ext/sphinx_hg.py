import os

from docutils import nodes

from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxRole
from sphinx.util.typing import ExtensionMetadata


class HgRole(SphinxRole):
    """A role for hg commands"""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        link = True

        text = self.text
        if text == "help resolve":
            text = "resolve"
        elif text == "help export":
            text = "export"
        elif text == "help <command>":
            link = False
        elif text == "help templates":
            text = "help templating"
        elif text == "debug-repair-issue-6528":
            link = False
        elif text.startswith("help internals"):
            # not yet in the website
            link = False
        elif text == "config merge-tools":
            text = "help config.merge-tools"

        if not link:
            node = nodes.inline(text=f"`hg {self.text}`")
            return [node], []

        source = self.inliner.document.attributes["source"]
        rel_source = source.split(os.sep + "source" + os.sep, 1)[1]
        levels = rel_source.count("/")
        to_base = "../" * levels

        if text.startswith("help "):
            _, topic = text.split("help ", 1)

            if "." in topic:
                topic, section = topic.split(".", 1)
                if "." in section:
                    section, _ = section.split(".", 1)
                section = "#" + section
            else:
                section = ""
            refuri = to_base + f"_generated/topics/{topic}.html{section}"
        else:
            command = text.split(" ", 1)[0]
            refuri = to_base + f"_generated/commands/{command}.html"

        node = nodes.reference(self.text, f"`hg {self.text}`", refuri=refuri)

        return [node], []


class ConfigDocRole(SphinxRole):
    """A role for `config-doc`"""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        # I (paugier) don't understand the config-doc role
        # (used in mercurial/helptext/config.txt)
        return [], []


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_role("hg", HgRole())
    app.add_role("config-doc", ConfigDocRole())

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
