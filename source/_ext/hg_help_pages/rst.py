"""Helpers to write RST."""

from __future__ import annotations

import re

from textwrap import dedent


def heading(title: str, char: str, overline: bool = False) -> str:
    """Return a RST section title."""
    line = char * max(len(title), 1)
    if overline:
        return f"{line}\n{title}\n{line}\n"
    return f"{title}\n{line}\n"


def split_doc(doc: str) -> tuple[str, str]:
    """Split a docstring into its first line and its dedented body."""
    doc = doc.strip("\n")
    summary, _, body = doc.partition("\n")
    return summary.strip(), dedent(body).strip("\n")


_OMITTED_RE = re.compile(
    r"\n*\.\. container:: (?:not)?omitted\n\n +\(.*\)\n*|"
    r"\n*\((?:some details hidden, use --verbose|use 'hg help)[^)]*\)\n*"
)


def strip_cli_hints(rst: str) -> str:
    """Remove the hints which only make sense in a terminal.

    For example "(some details hidden, use --verbose to show complete help)".
    """
    return _OMITTED_RE.sub("\n\n", rst).strip("\n")


def parse_table(rst: str) -> list[list[str]]:
    """Return the rows of a table made by `mercurial.minirst.maketable`.

    The columns are found from the border of the table, so the content of the
    cells is free. An empty list is returned when the table has no row.
    """
    lines = [line for line in rst.splitlines() if line.strip()]
    borders = [i for i, line in enumerate(lines) if set(line.strip()) <= {"=", " "}]
    if len(borders) < 2:
        return []
    first, last = borders[0], borders[-1]
    spans = [m.span() for m in re.finditer(r"=+", lines[first])]
    # the last column is not limited by the border
    spans[-1] = (spans[-1][0], None)
    rows = []
    for index in range(first + 1, last):
        if index in borders:
            continue
        rows.append([lines[index][start:end].strip() for start, end in spans])
    return rows


def options_rst(table: str) -> str:
    """Turn a table of options of Mercurial into a RST table.

    The table of Mercurial cannot be used as it is: docutils reads a row
    without a short option as the continuation of the previous row.
    """
    rows = parse_table(table)
    if not rows:
        # no option, or only options which are not shown
        return ""
    rst = [".. list-table::", "   :widths: auto", "   :class: hg-options", ""]
    for row in rows:
        if len(row) == 2:
            # Mercurial drops the first column when no option has a short name
            row.insert(0, "")
        short, long, description = row
        rst.append(f"   * - ``{short}``" if short else "   * -")
        rst.append(f"     - ``{long}``")
        rst.append(f"     - {description}" if description else "     -")
    rst.append("")
    if any(long.endswith("[+]") for _, long, _ in rows):
        rst.append("Options marked ``[+]`` can be repeated.\n")
    return "\n".join(rst)


def page_name_conflicts(pages: list[str]) -> list[str]:
    """Return the page names used more than once."""
    seen = set()
    conflicts = []
    for page in pages:
        if page in seen:
            conflicts.append(page)
        seen.add(page)
    return conflicts
