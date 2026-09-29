"""Generate the help pages without Sphinx."""

from __future__ import annotations

import sys

from pathlib import Path

from . import generate, help_data


def main(argv: list[str]) -> int:
    default = Path(__file__).absolute().parent.parent.parent / "help"
    output_dir = Path(argv[1]) if len(argv) > 1 else default
    changed = generate(output_dir)
    data = help_data()
    for warning in data.warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    print(
        f"Mercurial {data.version}: {len(data.commands)} commands, "
        f"{len(data.topics)} topics, {len(data.extensions)} extensions "
        f"in {output_dir} ({len(changed)} files updated)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
