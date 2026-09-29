"""Reading the help of Mercurial.

The environment of Mercurial is set by the package, which has to be imported
before any Mercurial module.
"""

from __future__ import annotations

import functools

from textwrap import dedent

from mercurial import (
    commands as hg_commands,
    encoding,
    extensions as hg_extensions,
    help as hg_help,
    initialization,
    pycompat,
    ui as uimod,
    util as hg_util,
)
from mercurial.main_script import cmd_finder

from .model import Command, Extension, HelpData, HelpGenerationError, Topic
from .rst import (
    heading,
    options_rst,
    page_name_conflicts,
    split_doc,
    strip_cli_hints,
)

# Extensions which are not distributed with Mercurial but are documented on the
# website. They are dependencies of the website (see pyproject.toml). They are
# listed first, in this order, on the page of the extensions.
#
# hg-git (`hggit`) does not support the latest Mercurial yet: it cannot be
# loaded, so it has currently no help page and the build only warns about it.
# Its help pages will be back, without any change here, once a version of
# hg-git supporting the latest Mercurial is released and locked in pdm.lock.
THIRD_PARTY_EXTENSIONS = ("topic", "evolve", "hggit")

# Show the options flagged as deprecated, experimental or advanced, as
# `hg help --verbose` does.
VERBOSE_OPTIONS = False


def _str(value: bytes) -> str:
    return value.decode("utf-8")


def mercurial_version() -> str:
    return _str(hg_util.version())


def _check_environment() -> None:
    if b"HGPLAIN" not in encoding.environ or encoding.environ.get(b"HGRCPATH"):
        raise HelpGenerationError(
            "Mercurial was imported before hg_help_pages: the help could be "
            "translated or depend on the local configuration. "
            "Import hg_help_pages first."
        )


def _names(key: bytes) -> list[str]:
    """The name and the aliases of a command, from its key in a command table."""
    return [_str(name) for name in cmd_finder.parse_aliases(key)]


def _is_debug(name: str) -> bool:
    return name.startswith("debug")


def _render_command(ui, key: bytes, entry, extension: str | None = None) -> Command:
    """Build the page of a command from its entry in a command table."""
    name, *aliases = _names(key)
    func = entry[0]

    doc = pycompat.getdoc(func) or b"(no help text available)"
    doc = hg_help.sub_config_item_help(ui, doc)
    summary, body = split_doc(_str(doc))

    if len(entry) > 2 and entry[2]:
        synopsis = _str(entry[2])
        if not synopsis.startswith("hg"):
            synopsis = f"hg {name} {synopsis}"
    else:
        synopsis = f"hg {name}"

    rst = [":orphan:\n", heading(f"hg {name}", "=")]
    rst.append(heading(summary, "-"))
    rst.append(f".. code-block:: text\n\n   {synopsis}\n")
    if aliases:
        rst.append("Aliases: " + ", ".join(f"``{a}``" for a in aliases) + "\n")
    if extension is not None:
        rst.append(
            f"This command is provided by the "
            f":doc:`{extension} </help/extensions/{extension}>` extension.\n"
        )
    if body:
        rst.append(body + "\n")
    if entry[1]:
        table = hg_help.optrst(b"options", entry[1], VERBOSE_OPTIONS, ui)
        options = options_rst(_str(table))
        if options:
            rst.append(".. rubric:: Options\n")
            rst.append(options)

    category = getattr(func, "helpcategory", None)
    return Command(
        name=name,
        aliases=aliases,
        summary=summary,
        category=category,
        rst="\n".join(rst),
        extension=extension,
    )


def _render_topic(ui, entry) -> Topic:
    """Build the page of a topic from its entry in `help.helptable`."""
    names, title, loader = entry[0:3]
    names = [_str(n) for n in names]
    category = entry[3] if len(entry) > 3 and entry[3] else None
    category = category or hg_help.TOPIC_CATEGORY_NONE

    # the loader also fills the generated parts of the topic
    body = _str(loader(ui)) if callable(loader) else ""
    body = strip_cli_hints(dedent(body))

    rst = [":orphan:\n", heading(_str(title), "#", overline=True), body + "\n"]
    return Topic(
        name=names[0],
        aliases=names[1:],
        title=_str(title),
        category=_str(category),
        rst="\n".join(rst),
    )


def _render_extension(
    ui, name: str, module, core_pages: set[str], undocumented: set[str]
) -> Extension:
    """Build the page of a loaded extension and the pages of its commands."""
    doc = hg_help.ext_help(ui, module) or b"(no help text available)"
    summary, body = split_doc(_str(doc))

    commands = []
    for key, entry in sorted(getattr(module, "cmdtable", {}).items()):
        if _is_debug(_names(key)[0]):
            undocumented.update(_names(key))
            continue
        command = _render_command(ui, key, entry, extension=name)
        if command.page in core_pages:
            # the extension changes a core command, which has its page
            continue
        commands.append(command)

    rst = [":orphan:\n", heading(f"{name} extension", "#", overline=True)]
    rst.append(summary + "\n")
    if body:
        rst.append(strip_cli_hints(body) + "\n")
    if commands:
        rst.append(".. rubric:: Commands\n")
        for command in commands:
            rst.append(
                f"- :doc:`{command.name} </help/commands/{command.page}>`: "
                f"{command.summary}"
            )
        rst.append("")
    return Extension(name=name, summary=summary, rst="\n".join(rst), commands=commands)


def _documented_extensions(ui) -> list[str]:
    """The third party extensions, then the ones listed by `hg help extensions`."""
    names = list(THIRD_PARTY_EXTENSIONS)
    for name, summary in sorted(hg_extensions.disabled().items()):
        if any(keyword in summary for keyword in hg_help._exclkeywords):
            continue
        names.append(_str(name))
    return names


def _step(what: str, function, *args, **kwargs):
    """Call a function, telling what was documented if it fails."""
    try:
        return function(*args, **kwargs)
    except Exception as exc:
        raise HelpGenerationError(
            f"cannot generate the help of {what} "
            f"(Mercurial {mercurial_version()}): {type(exc).__name__}: {exc}"
        ) from exc


def collect() -> HelpData:
    """Read the help of Mercurial.

    Core commands and topics are read before the extensions are loaded since
    extensions change the commands of Mercurial.
    """
    _check_environment()
    # commands, template keywords... are only registered once this is called
    initialization.init()
    ui = uimod.ui.load()
    undocumented = set()

    # core commands
    table = dict(hg_commands.table)
    shown, _summaries, _synonyms = hg_help._getcategorizedhelpcmds(ui, table, None)
    shown = {_str(name) for names in shown.values() for name in names}
    by_category = {}
    hidden = []
    for key, entry in sorted(table.items()):
        if _is_debug(_names(key)[0]):
            undocumented.update(_names(key))
            continue
        command = _step(f"the command {_str(key)!r}", _render_command, ui, key, entry)
        if command.name in shown:
            category = command.category or hg_help.registrar.command.CATEGORY_NONE
            by_category.setdefault(category, []).append(command)
        else:
            hidden.append(command)
    command_categories = [
        (_str(hg_help.CATEGORY_NAMES[category]), by_category.pop(category))
        for category in hg_help.CATEGORY_ORDER
        if category in by_category
    ]
    # categories unknown to `CATEGORY_ORDER`
    for category, commands in sorted(by_category.items()):
        command_categories.append((_str(category), commands))
    if hidden:
        command_categories.append(("Deprecated and other commands", hidden))

    global_options = options_rst(
        _str(
            hg_help.optrst(
                b"global options", hg_commands.globalopts, VERBOSE_OPTIONS, ui
            )
        )
    )

    # core topics
    def read_topics(known: set[str]) -> dict[str, list[Topic]]:
        topics = {}
        for entry in hg_help.helptable:
            name = _str(entry[0][0])
            if name in known:
                continue
            known.add(name)
            if name == "internals":
                undocumented.add(name)
                continue
            topic = _step(f"the topic {name!r}", _render_topic, ui, entry)
            topics.setdefault(topic.category, []).append(topic)
        return topics

    known_topics = set()
    topics = read_topics(known_topics)

    # extensions
    names = _documented_extensions(ui)
    for name in names:
        ui.setconfig(b"extensions", name.encode(), b"", b"hg-website")
    ui.pushbuffer(error=True)
    try:
        hg_extensions.loadall(ui)
    finally:
        load_output = _str(ui.popbuffer())
    loaded = dict(hg_extensions.extensions(ui))
    core_pages = {c.page for _, commands in command_categories for c in commands}
    extensions = []
    warnings = []
    for name in names:
        module = loaded.get(name.encode())
        if module is None:
            # Not installed, or not compatible with this version of Mercurial.
            # This must not prevent the website from being built.
            reasons = [line for line in load_output.splitlines() if name in line]
            warnings.append(
                f"the extension {name!r} cannot be loaded with Mercurial "
                f"{mercurial_version()}, it is not documented: "
                f"{' '.join(reasons) or 'unknown reason'}"
            )
            continue
        extension = _step(
            f"the extension {name!r}",
            _render_extension,
            ui,
            name,
            module,
            core_pages,
            undocumented,
        )
        extensions.append(extension)

    # topics added by the extensions
    for category, extension_topics in read_topics(known_topics).items():
        topics.setdefault(category, []).extend(extension_topics)
    topic_categories = [
        (_str(hg_help.TOPIC_CATEGORY_NAMES[category.encode()]), topics.pop(category))
        for category in map(_str, hg_help.TOPIC_CATEGORY_ORDER)
        if category in topics
    ]
    for category, category_topics in sorted(topics.items()):
        topic_categories.append((category, category_topics))

    data = HelpData(
        version=mercurial_version(),
        command_categories=command_categories,
        topic_categories=topic_categories,
        extensions=extensions,
        global_options=global_options,
        undocumented=undocumented,
        warnings=warnings,
    )
    for kind, pages in (
        ("commands", [c.page for c in data.commands]),
        ("topics", [t.page for t in data.topics]),
    ):
        conflicts = page_name_conflicts(pages)
        if conflicts:
            raise HelpGenerationError(
                f"several {kind} would be written to the same page: {conflicts}"
            )
    return data


@functools.cache
def help_data() -> HelpData:
    """The help of Mercurial, read once per process."""
    try:
        return collect()
    except HelpGenerationError:
        raise
    except Exception as exc:
        raise HelpGenerationError(
            f"cannot read the help of Mercurial {mercurial_version()}, its "
            f"internal API probably changed: {type(exc).__name__}: {exc}"
        ) from exc
