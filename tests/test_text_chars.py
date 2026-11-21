"""No em/en dashes or emojis in any text file: plain hyphens only.

CI gate for the `no-dashes-or-emojis` pre-commit hook, which `--no-verify` skips.
Walks the tree instead of `git ls-files`: the CI image has no git.
"""

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Same ranges as the pre-commit hook: en/em dash, symbols/dingbats, emoji.
BANNED = re.compile("[\u2013\u2014\u2600-\u27bf\U0001f300-\U0001faff]")
SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    ".next",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "__pycache__",
    "out",
    "build",
}
# Gitignored outputs at the repo root only: `web/lib/data/`-style dirs are source.
ROOT_SKIP_DIRS = {"data", "models", "plots"}
SKIP_FILES = {"uv.lock", "package-lock.json"}
# Rewritten by `next dev` with its own em dashes.
SKIP_PATHS = {"web/AGENTS.md"}


def text_files() -> list[Path]:
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        root_skip = ROOT_SKIP_DIRS if Path(dirpath) == ROOT else set()
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS | root_skip]
        files += [Path(dirpath) / f for f in filenames if f not in SKIP_FILES]
    return [f for f in files if f.relative_to(ROOT).as_posix() not in SKIP_PATHS]


def test_no_dashes_or_emojis():
    hits = []
    for path in text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # binary (images, GIFs)
        for number, line in enumerate(text.splitlines(), start=1):
            if BANNED.search(line):
                hits.append(f"{path.relative_to(ROOT).as_posix()}:{number}")
    assert not hits, f"Em/en dash or emoji found, use plain hyphens: {hits}"
