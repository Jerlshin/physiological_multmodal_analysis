"""Freeze a copy of src/cairn for one closure simulation run (as Stage 1 did, S1-D19).

The copy is imported first on PYTHONPATH, so later edits to src/cairn cannot reach the run's worker pools.
Its ``paths.py`` is the Stage-1 snapshot variant that finds the repository root from inside the evidence tree;
every other file is byte-identical to src/cairn at snapshot time. The run manifest records all file hashes.

    python docs/research/novel_method/closure/scripts/snapshot.py <run_dir>
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SRC = ROOT / "src/cairn"
PATHS_VARIANT = '''
def _repo_root() -> Path:
    """The repository holding this package: src/cairn, or a run's code snapshot inside the evidence tree."""
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / ".git").exists() and (p / "src").is_dir():
            return p
    return here.parents[2]


ROOT = _repo_root()'''


def snapshot(run_dir: Path) -> Path:
    dst = Path(run_dir) / "code_snapshot" / "cairn"
    if dst.exists():
        raise FileExistsError(f"{dst} exists: a run's snapshot is never overwritten")
    dst.mkdir(parents=True)
    for p in sorted(SRC.glob("*.py")):
        shutil.copy2(p, dst / p.name)
    paths = (dst / "paths.py").read_text()
    old = "ROOT = Path(__file__).resolve().parents[2]"
    assert paths.count(old) == 1
    (dst / "paths.py").write_text(paths.replace(old, PATHS_VARIANT.strip("\n"), 1))
    return dst


if __name__ == "__main__":
    print(snapshot(Path(sys.argv[1])))
