"""File size limit for Python source, the counterpart of ESLint `max-lines` in web/.

Counts lines that are not blank and not `#` comments. Over WARN_LOC warns, over MAX_LOC fails.
Tests are exempt: they keep explicit setup.
"""

import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIRS = ["shirin", "scripts", "web/scripts"]
WARN_LOC = 150
MAX_LOC = 200


def count_loc(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()
    return sum(1 for line in lines if line.strip() and not line.lstrip().startswith("#"))


def test_source_files_within_size_limit():
    files = [f for d in SOURCE_DIRS for f in (ROOT / d).rglob("*.py")]
    too_long = []
    for path in files:
        loc = count_loc(path)
        name = path.relative_to(ROOT).as_posix()
        if loc > MAX_LOC:
            too_long.append(f"{name}: {loc} LOC")
        elif loc > WARN_LOC:
            warnings.warn(f"{name}: {loc} LOC > {WARN_LOC}. Consider splitting.", stacklevel=1)
    assert not too_long, f"Files over {MAX_LOC} LOC, split them: {too_long}"
