import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "source" / "_ext"))

# has to be imported before any Mercurial module
import hg_help_pages  # noqa: E402, F401
