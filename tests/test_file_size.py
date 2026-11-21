"""File size limit for source files in every language, repo-wide.

Twin of `web/lib/fileSize.test.ts`: same languages, limits and exemptions,
so a repo with only one of Python or Node still checks every file.
Counts lines that are not blank and not comment lines. Over WARN_LOC warns, over MAX_LOC fails.
Tests and generated files are exempt: tests keep explicit setup.
Walks the tree instead of `git ls-files`: the CI image has no git.
"""

import os
import re
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WARN_LOC = 100
MAX_LOC = 150
# Comment prefix per language. CSS stays on `//` `/*`: `#id` and `--token` are code there.
HASH = ("#",)
C_STYLE = ("//", "/*", "*")
SQL = ("--", "/*", "*")
COMMENT_PREFIXES = {
    **dict.fromkeys(["py", "pyi", "sh", "bash", "ps1", "r", "rb"], HASH),
    **dict.fromkeys(
        [
            "ts",
            "tsx",
            "mts",
            "cts",
            "js",
            "jsx",
            "mjs",
            "cjs",
            "css",
            "scss",
            "go",
            "rs",
            "java",
            "kt",
            "cs",
            "swift",
            "c",
            "h",
            "cpp",
            "hpp",
            "php",
        ],
        C_STYLE,
    ),
    **dict.fromkeys(["sql", "ddl"], SQL),
}
SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    ".next",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "__pycache__",
    "tests",
    "test",
    # Build outputs: setuptools copy of shirin/, Next static export.
    "build",
    "out",
}
# Gitignored outputs at the repo root only: nested `data/` dirs are source.
ROOT_SKIP_DIRS = {"data", "models", "plots"}
GENERATED = {"database.types.ts", "next-env.d.ts", "schema.sql"}
TEST_FILE = re.compile(r"(^test_.*|.*_test|.*\.(test|spec))\.[^.]+$|^conftest\.py$")


def count_loc(path: Path, prefixes: tuple[str, ...]) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()
    return sum(1 for line in lines if line.strip() and not line.lstrip().startswith(prefixes))


def source_files() -> list[tuple[Path, tuple[str, ...]]]:
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        root_skip = ROOT_SKIP_DIRS if Path(dirpath) == ROOT else set()
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS | root_skip]
        for name in filenames:
            prefixes = COMMENT_PREFIXES.get(name.rsplit(".", 1)[-1].lower())
            if prefixes and name not in GENERATED and not TEST_FILE.match(name):
                files.append((Path(dirpath) / name, prefixes))
    return files


def test_source_files_within_size_limit():
    too_long = []
    for path, prefixes in source_files():
        loc = count_loc(path, prefixes)
        name = path.relative_to(ROOT).as_posix()
        if loc > MAX_LOC:
            too_long.append(f"{name}: {loc} LOC")
        elif loc > WARN_LOC:
            warnings.warn(f"{name}: {loc} LOC > {WARN_LOC}. Consider splitting.", stacklevel=1)
    assert not too_long, f"Files over {MAX_LOC} LOC, split them: {too_long}"
