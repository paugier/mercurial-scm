import subprocess

from dataclasses import dataclass
from importlib import resources
from pathlib import Path

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


def save_file(path, content):
    if path.exists():
        if path.read_text() == content:
            return
    path.write_text(content)


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

    md_commands = ["# Commands\n"]

    source_dir = Path(__file__).absolute().parent
    generated_dir = source_dir / "_generated"
    generated_dir.mkdir(exist_ok=True)

    commands_dir = generated_dir / "commands"
    commands_dir.mkdir(exist_ok=True)
    path_commands_md = commands_dir.with_suffix(".md")
    for title, kind in commands_doc.items():
        for command in kind:
            command.get_rst_doc()
    md_commands = "\n".join(md_commands)
    save_file(path_commands_md, md_commands)

    topics_dir = generated_dir / "topics"
    topics_dir.mkdir(exist_ok=True)
    path_topics_md = topics_dir.with_suffix(".md")
    md_topics = ["# Additional help topics\n"]
    for title, kind in topics_doc.items():
        for command in kind:
            if command.name == "internals":
                continue
            command.get_rst_doc()
    md_topics = "\n".join(md_topics)
    save_file(path_topics_md, md_topics)


if __name__ == "__main__":

    prepare_source()
