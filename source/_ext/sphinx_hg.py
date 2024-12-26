import os

from docutils import nodes

from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxRole
from sphinx.util.typing import ExtensionMetadata


class HgRole(SphinxRole):
    """A role for hg commands"""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:

        source = self.inliner.document.attributes["source"]
        rel_source = source.split(os.sep + "source" + os.sep, 1)[1]
        levels = rel_source.count("/")
        to_base = "../" * levels

        if self.text.startswith("help "):
            _, topic = self.text.split("help ", 1)
            refuri = to_base + f"_generated/topics/{topic}.html"
        else:
            refuri = to_base + f"_generated/commands/{self.text}.html"

        node = nodes.reference(self.text, f"hg {self.text}", refuri=refuri)

        return [node], []


def setup(app: Sphinx) -> ExtensionMetadata:

    app.add_role("hg", HgRole())

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
