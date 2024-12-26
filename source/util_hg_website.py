import subprocess

from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from textwrap import dedent

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
            rst = self.name + "\n"
        else:
            rst = cmd.__doc__

        if rst is None:
            return ":orphan:\n"

        title, content = rst.split("\n", 1)

        title = "hg " + self.name + ": " + title
        rst = ":orphan:\n" + title + "\n" + "=" * len(title) + "\n" + dedent(content)

        return rst


class Topic(Command):

    def get_rst_doc(self):
        name = self.name
        if name == "templating":
            name = "templates"
        rst = resources.files("mercurial.helptext").joinpath(f"{name}.txt").read_text()
        title = self.short_doc
        rst = ":orphan:\n" + title + "\n" + "-" * len(title) + "\n\n" + rst
        return rst


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

    source_dir = Path(__file__).absolute().parent
    generated_dir = source_dir / "_generated"
    generated_dir.mkdir(exist_ok=True)

    commands_dir = generated_dir / "commands"
    commands_dir.mkdir(exist_ok=True)
    path_commands_md = commands_dir.with_suffix(".md")
    md = ["# Commands\n"]
    for title, kind in commands_doc.items():
        md.append("```{rubric} " + title + "\n```")
        for command in kind:
            md.append(
                f"- [{command.name}](./commands/{command.name}.rst): {command.short_doc}"
            )
            save_file(commands_dir / f"{command.name}.rst", command.get_rst_doc())
    md = "\n".join(md)
    save_file(path_commands_md, md)

    topics_dir = generated_dir / "topics"
    topics_dir.mkdir(exist_ok=True)
    path_topics_md = topics_dir.with_suffix(".md")
    md = ["# Additional help topics\n"]
    for title, kind in topics_doc.items():
        md.append("```{rubric} " + title + "\n```")
        for command in kind:
            if command.name == "internals":
                continue
            md.append(
                f"- [{command.name}](./topics/{command.name}.rst): {command.short_doc}"
            )
            save_file(topics_dir / f"{command.name}.rst", command.get_rst_doc())
    md = "\n".join(md)
    save_file(path_topics_md, md)


if __name__ == "__main__":

    prepare_source()
