"""What is documented on the website."""

from __future__ import annotations

import functools

from dataclasses import dataclass, field


class HelpGenerationError(Exception):
    """The help pages cannot be generated."""


@dataclass
class Command:
    """A Mercurial command and its help page."""

    name: str
    aliases: list[str]
    summary: str
    category: str | None
    rst: str
    # name of the extension providing the command, None for core commands
    extension: str | None = None

    @property
    def page(self) -> str:
        result = self.name.replace("::", "_")
        if self.extension is not None:
            result = self.extension + "." + result
        return result


@dataclass
class Topic:
    """A help topic and its help page."""

    name: str
    aliases: list[str]
    title: str
    category: str
    rst: str

    @property
    def page(self) -> str:
        return self.name


@dataclass
class Extension:
    """An extension and its help page."""

    name: str
    summary: str
    rst: str
    commands: list[Command] = field(default_factory=list)

    @property
    def page(self) -> str:
        return self.name


@dataclass
class HelpData:
    """Everything documented on the website."""

    version: str
    # (category title, commands), in the order of `hg help`
    command_categories: list[tuple[str, list[Command]]]
    # (category title, topics), in the order of `hg help`
    topic_categories: list[tuple[str, list[Topic]]]
    extensions: list[Extension]
    global_options: str
    # names which exist in Mercurial but have no page on the website
    undocumented: set[str]
    # problems which do not prevent the generation of the pages
    warnings: list[str] = field(default_factory=list)

    @property
    def commands(self) -> list[Command]:
        """All the commands, the ones of the extensions included."""
        result = [c for _, cmds in self.command_categories for c in cmds]
        for extension in self.extensions:
            result.extend(extension.commands)
        return result

    @property
    def topics(self) -> list[Topic]:
        return [t for _, topics in self.topic_categories for t in topics]

    @functools.cached_property
    def command_pages(self) -> dict[str, str]:
        """Map the names and aliases of the commands to their page."""
        pages = {}
        for command in self.commands:
            for name in command.aliases:
                pages.setdefault(name, command.page)
        # a name always wins over the alias of another command
        for command in self.commands:
            pages[command.name] = command.page
        return pages

    @functools.cached_property
    def topic_pages(self) -> dict[str, str]:
        """Map the names and aliases of the topics to their page."""
        pages = {}
        for topic in self.topics:
            for name in [topic.name, *topic.aliases]:
                pages.setdefault(name, topic.page)
        return pages

    @functools.cached_property
    def extension_pages(self) -> dict[str, str]:
        return {e.name: e.page for e in self.extensions}
