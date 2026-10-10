"""Tests of the generation of the `hg help` pages.

The tests using the help of Mercurial also check that the internal API of
Mercurial used by the website still works after an update of Mercurial.
"""

import io
import re

from pathlib import Path

import pytest

import hg_help_pages
import sphinx_hg

from hg_help_pages import (
    heading,
    options_rst,
    parse_table,
    split_doc,
    strip_cli_hints,
    write_pages,
)

BASELINE = Path(__file__).parent / "data" / "help_urls_baseline.txt"

# Problems in the help of Mercurial or of the extensions, to be fixed there.
KNOWN_UPSTREAM_ISSUES = [
    "help/commands/topics.rst:45: ERROR: Unexpected indentation.",
    # hg-git does not support the latest Mercurial yet. Its help pages will be
    # back once it does, this line has to be removed then.
    "the extension 'hggit' cannot be loaded",
]


@pytest.fixture(scope="session")
def data():
    return hg_help_pages.help_data()


@pytest.fixture(scope="session")
def pages(data):
    return hg_help_pages.render_pages(data)


# -- RST helpers --------------------------------------------------------------


def test_heading():
    assert heading("hg add", "=") == "hg add\n======\n"
    assert heading("Dates", "#", overline=True) == "#####\nDates\n#####\n"


def test_split_doc():
    doc = "add files\n\n    Schedule files.\n\n      indented\n\n    "
    assert split_doc(doc) == ("add files", "Schedule files.\n\n  indented")
    assert split_doc("only a summary") == ("only a summary", "")


def test_strip_cli_hints():
    rst = (
        "Some text.\n\n\n.. container:: omitted\n\n"
        "    (some details hidden, use --verbose to show complete help)\n\n"
    )
    assert strip_cli_hints(rst) == "Some text."
    rst = "text\n\n(some details hidden, use --verbose to show complete help)"
    assert strip_cli_hints(rst) == "text"
    assert strip_cli_hints("(see the doc) kept") == "(see the doc) kept"


TABLE = """
options ([+] can be repeated):

 == =================== =========================
 -c --check CHECK [+]   add a check
    --option OPTION     pass an option to a check
 == =================== =========================
"""

TABLE_WITHOUT_SHORT_OPTIONS = """
options:

  =========== ======================
  --rev VALUE revision to update to
  --dest      repository (default: .)
  =========== ======================
"""


def test_parse_table():
    assert parse_table(TABLE) == [
        ["-c", "--check CHECK [+]", "add a check"],
        ["", "--option OPTION", "pass an option to a check"],
    ]
    assert parse_table(TABLE_WITHOUT_SHORT_OPTIONS) == [
        ["--rev VALUE", "revision to update to"],
        ["--dest", "repository (default: .)"],
    ]
    assert parse_table("\noptions:\n\n \n \n") == []


def test_options_rst():
    rst = options_rst(TABLE)
    assert "* - ``-c``\n     - ``--check CHECK [+]``\n     - add a check" in rst
    assert "* -\n     - ``--option OPTION``" in rst
    assert "can be repeated" in rst

    rst = options_rst(TABLE_WITHOUT_SHORT_OPTIONS)
    assert "* -\n     - ``--rev VALUE``\n     - revision to update to" in rst
    assert "can be repeated" not in rst

    assert options_rst("\noptions:\n\n \n \n") == ""


def test_write_pages(tmp_path):
    output = tmp_path / "help"
    changed = write_pages(output, {"commands/a.rst": "a", "commands/b.rst": "b"})
    assert sorted(p.name for p in changed) == ["a.rst", "b.rst"]

    # nothing is written when nothing changed
    assert write_pages(output, {"commands/a.rst": "a", "commands/b.rst": "b"}) == []

    # files which are not generated anymore are removed, others are kept
    (output / "commands" / "other.rst").write_text("not generated")
    changed = write_pages(output, {"commands/a.rst": "new"})
    assert sorted(p.name for p in changed) == ["a.rst", "b.rst"]
    assert (output / "commands" / "a.rst").read_text() == "new"
    assert not (output / "commands" / "b.rst").exists()
    assert (output / "commands" / "other.rst").exists()


# -- Help of Mercurial --------------------------------------------------------


def test_command_page(pages):
    rst = pages["commands/commit.rst"]
    assert rst.startswith(":orphan:\n\nhg commit\n=========\n")
    assert "commit the specified files or all outstanding changes\n-----" in rst
    assert "   hg commit [OPTION]... [FILE]...\n" in rst
    assert "Aliases: ``ci``" in rst
    assert "``--amend``" in rst
    assert "use --verbose" not in rst


def test_global_options(pages):
    """The global options are documented once, all the commands link to them."""
    assert "(hg-global-options)=\n## Global options\n" in pages["commands.md"]
    assert "``--repository REPO``" in pages["commands.md"]
    commands = [page for page in pages if page.startswith("commands/")]
    assert commands
    for page in commands:
        assert ".. rubric:: Options\n\n" in pages[page], page
        assert (
            "Every command also accepts the "
            ":ref:`global options <hg-global-options>`.\n"
        ) in pages[page], page
        assert "``--repository REPO``" not in pages[page], page


def test_commands_not_changed_by_extensions(pages):
    """Core commands are documented without the options of the extensions."""
    assert "--topic" not in pages["commands/commit.rst"]


def test_hidden_commands(data, pages):
    assert "commands/tip.rst" in pages
    assert "commands/parents.rst" in pages
    title, commands = data.command_categories[-1]
    assert title == "Deprecated and other commands"
    assert "tip" in [c.name for c in commands]
    assert not [page for page in pages if "debug" in page]


def test_topic_pages(pages):
    # the generated parts of the topics
    assert ":author:" in pages["topics/templating.rst"]
    assert "``ancestors(set[, depth])``" in pages["topics/revisions.rst"]
    for page, rst in pages.items():
        assert not re.search(r"^ *\.\. \w+marker", rst, re.M), page
        assert ":config-doc:" not in rst, page
        assert "missing help text" not in rst, page
    assert "topics/internals.rst" not in pages
    # the body is not indented, it would be a quote
    assert "\nTroubleshooting\n===============\n" in pages["topics/config.rst"]


def test_extension_pages(data, pages):
    rst = pages["extensions/rebase.rst"]
    assert "rebase extension" in rst
    assert ":doc:`rebase </help/commands/rebase>`" in rst
    assert "provided by the :doc:`rebase" in pages["commands/rebase.rst"]
    for name in hg_help_pages.THIRD_PARTY_EXTENSIONS:
        # an extension which does not work with this Mercurial is reported
        reported = any(f"extension {name!r}" in w for w in data.warnings)
        assert (f"extensions/{name}.rst" in pages) != reported
    assert "commands/topics.rst" in pages
    # third party extensions first, then the ones of Mercurial sorted by name
    names = [extension.name for extension in data.extensions]
    assert names[:2] == ["topic", "evolve"]
    bundled = [n for n in names if n not in hg_help_pages.THIRD_PARTY_EXTENSIONS]
    assert bundled == sorted(bundled)
    assert pages["extensions.md"].index("[topic]") < pages["extensions.md"].index(
        "[acl]"
    )


def test_indexes(data, pages):
    assert "```{rubric} Repository creation\n```" in pages["commands.md"]
    assert "- [clone](./commands/clone.rst): make a copy" in pages["commands.md"]
    assert "- [admin::verify](./commands/admin_verify.rst)" in pages["commands.md"]
    assert "- [config](./topics/config.rst): Configuration Files" in pages["topics.md"]
    assert "- [rebase](./extensions/rebase.rst)" in pages["extensions.md"]
    for index in ("commands.md", "topics.md", "extensions.md"):
        assert f"Mercurial {data.version}" in pages[index]


@pytest.mark.parametrize(
    "text, expected",
    [
        ("commit", "help/commands/commit"),
        ("commit --amend", "help/commands/commit"),
        ("ci", "help/commands/commit"),
        ("id", "help/commands/identify"),
        ("bookmark", "help/commands/bookmarks"),
        ("admin::verify", "help/commands/admin_verify"),
        ("pull -r X", "help/commands/pull"),
        ("help", "help/commands/help"),
        ("help config", "help/topics/config"),
        ("help -c config", "help/commands/config"),
        ("help config.merge-tools", "help/topics/config#merge-tools"),
        ("help config.paths.pushurl", "help/topics/config#paths"),
        ("help templates", "help/topics/templating"),
        ("help revsets", "help/topics/revisions"),
        ("help resolve", "help/commands/resolve"),
        ("help -e rebase", "help/extensions/rebase"),
        ("help share", "help/commands/share"),
        ("help -e share", "help/extensions/share"),
        ("rebase", "help/commands/rebase"),
        ("qnew", "help/commands/qnew"),
    ],
)
def test_resolve(data, text, expected):
    assert sphinx_hg.resolve(text, data) == (expected, True)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("help <command>", False),
        ("help COMMAND", False),
        ("help -v", False),
        ("help internals", False),
        ("debuginstall", False),
        ("nosuchcommand", True),
        ("help nosuchtopic", True),
    ],
)
def test_resolve_without_page(data, text, expected):
    assert sphinx_hg.resolve(text, data) == (None, expected)


# -- Website ------------------------------------------------------------------


@pytest.fixture(scope="session")
def website(tmp_path_factory):
    """Build a website with only the help pages, return (html dir, warnings)."""
    from sphinx.application import Sphinx

    source = tmp_path_factory.mktemp("source")
    build = tmp_path_factory.mktemp("build")
    (source / "conf.py").write_text(
        'extensions = ["myst_parser", "sphinx_hg"]\nhtml_theme = "basic"\n'
    )
    (source / "index.md").write_text(
        "# Test\n\n```{toctree}\nhelp/commands.md\nhelp/topics.md\n"
        "help/extensions.md\n```\n"
    )
    warnings = io.StringIO()
    app = Sphinx(
        srcdir=source,
        confdir=source,
        outdir=build / "html",
        doctreedir=build / "doctrees",
        buildername="html",
        status=None,
        warning=warnings,
    )
    app.build()
    lines = [line.replace(f"{source}/", "") for line in warnings.getvalue().split("\n")]
    return build / "html", [line for line in lines if line.strip()]


def test_existing_urls_still_exist(website):
    """The URLs of the help pages must never change."""
    html_dir, _ = website
    missing = []
    anchors = {}
    for line in BASELINE.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        page, _, anchor = line.partition("#")
        path = html_dir / page
        if not path.exists():
            missing.append(line)
            continue
        if page not in anchors:
            anchors[page] = set(re.findall(r' id="([^"]+)"', path.read_text()))
        if anchor and anchor not in anchors[page]:
            missing.append(line)
    assert not missing


def test_pages_are_valid(website):
    _, warnings = website
    unexpected = [
        line
        for line in warnings
        if "[hg.unknown]" not in line
        and not any(known in line for known in KNOWN_UPSTREAM_ISSUES)
    ]
    assert not unexpected
