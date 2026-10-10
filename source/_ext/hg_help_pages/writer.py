"""Writing the pages."""

from __future__ import annotations

from pathlib import Path

from .model import Command, HelpData
from .reader import help_data
from .rst import GLOBAL_OPTIONS_LABEL

# list of the generated files, to remove the ones which are not generated anymore
MANIFEST_NAME = "MANIFEST"


def _index(title: str, data: HelpData, categories, directory: str) -> list[str]:
    md = [f"# {title}\n", f"Documentation of Mercurial {data.version}.\n"]
    for category, items in categories:
        md.append("```{rubric} " + category + "\n```")
        for item in items:
            description = item.summary if isinstance(item, Command) else item.title
            md.append(f"- [{item.name}](./{directory}/{item.page}.rst): {description}")
        md.append("")
    return md


def render_pages(data: HelpData) -> dict[str, str]:
    """Return the content of the generated files, by relative path."""
    pages = {}
    for command in data.commands:
        pages[f"commands/{command.page}.rst"] = command.rst
    for topic in data.topics:
        pages[f"topics/{topic.page}.rst"] = topic.rst
    for extension in data.extensions:
        pages[f"extensions/{extension.page}.rst"] = extension.rst

    md = _index("Commands", data, data.command_categories, "commands")
    if data.global_options:
        md.append(f"({GLOBAL_OPTIONS_LABEL})=")
        md.append("## Global options\n")
        md.append("These options are accepted by all commands.\n")
        md.append("```{eval-rst}\n" + data.global_options + "\n```")
    pages["commands.md"] = "\n".join(md)

    md = _index("Additional topics", data, data.topic_categories, "topics")
    pages["topics.md"] = "\n".join(md)

    md = ["# Extensions\n", f"Documentation of Mercurial {data.version}.\n"]
    md.append(
        "Extensions are not enabled by default, "
        "see [how to enable them](./topics/extensions.rst).\n"
    )
    for extension in data.extensions:
        md.append(
            f"- [{extension.name}](./extensions/{extension.page}.rst): "
            f"{extension.summary}"
        )
    pages["extensions.md"] = "\n".join(md) + "\n"
    return pages


def write_pages(output_dir: Path, pages: dict[str, str]) -> list[Path]:
    """Write the generated files and return the ones which changed.

    Files written by a previous run and not generated anymore are removed.
    Other files are never touched.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = output_dir / MANIFEST_NAME
    previous = set()
    if manifest.exists():
        previous = set(manifest.read_text(encoding="utf-8").split("\n")) - {""}

    changed = []
    for relative, content in pages.items():
        path = output_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_text(encoding="utf-8") == content:
            continue
        path.write_text(content, encoding="utf-8")
        changed.append(path)

    for relative in sorted(previous - set(pages)):
        path = (output_dir / relative).resolve()
        if output_dir.resolve() in path.parents and path.is_file():
            path.unlink()
            changed.append(path)

    content = "\n".join(sorted(pages)) + "\n"
    if not manifest.exists() or manifest.read_text(encoding="utf-8") != content:
        manifest.write_text(content, encoding="utf-8")
    return changed


def generate(output_dir: Path) -> list[Path]:
    """Generate the help pages in a directory, return the changed files."""
    return write_pages(Path(output_dir), render_pages(help_data()))
