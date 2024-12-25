import subprocess

from dataclasses import dataclass
from importlib import resources

from mercurial import commands as hg_commands


@dataclass
class Command:
    """Mercurial command."""

    name: str
    short_doc: str

    def get_rst_doc(self):

        try:
            cmd = getattr(hg_commands, self.name)
        except AttributeError as err:
            print(err)
            rst = ""
        else:
            rst = cmd.__doc__

        return rst


class Topic(Command):

    def get_rst_doc(self):

        name = self.name
        if name == "templating":
            name = "templates"

        if name == "internals":
            return ""

        return resources.files("mercurial.helptext").joinpath(f"{name}.txt").read_text()


def parse_help_text(doc, cls=Command):
    kinds = {}
    for line in doc.split("\n"):
        if not line:
            continue
        if not line.startswith(" "):
            kind = []
            kinds[line] = kind
        else:
            name, short_doc = line.strip().split(" ", 1)
            short_doc = short_doc.strip()
            kind.append(cls(name, short_doc))
    return kinds


def prepare_source():

    process = subprocess.run(
        ["hg", "help", "--config", "extensions.hggit="],
        env={"HGRCPATH": ""},
        check=True,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )

    help_text = process.stdout
    commands_doc, topics_doc = help_text.split("additional help topics:")
    _, commands_doc = commands_doc.split("list of commands:")
    topics_doc, _ = topics_doc.split("(use 'hg help -v' to show built-in")

    commands_doc = parse_help_text(commands_doc)
    topics_doc = parse_help_text(topics_doc, cls=Topic)

    for title, kind in commands_doc.items():
        for command in kind:
            command.get_rst_doc()

    for title, kind in topics_doc.items():
        for command in kind:
            command.get_rst_doc()


if __name__ == "__main__":

    prepare_source()
