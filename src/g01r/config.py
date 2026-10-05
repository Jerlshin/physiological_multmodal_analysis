"""Frozen protocol configuration and repository paths."""
from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "g01r_protocol_v1.toml"
AUDIT_EVIDENCE = ROOT / "docs/research/dataset_exploration/evidence"
DESIGN_EVIDENCE = ROOT / "docs/research/experimental_design/evidence"
IMPL_DOCS = ROOT / "docs/research/baseline_implementation"
IMPL_EVIDENCE = IMPL_DOCS / "evidence"
DATA = ROOT / "data"
DERIVED = DATA / "derived" / "g01r"
RESULTS = ROOT / "results"
FREEZE_DIR = ROOT / "analysis_freeze"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class ProtocolConfig:
    """Typed, read-only view of the frozen TOML configuration."""

    raw: dict
    path: Path
    sha256: str
    overrides: dict = field(default_factory=dict)

    # -- convenient typed accessors -------------------------------------------------
    @property
    def fs(self) -> int:
        return int(self.raw["data"]["sampling_rate_hz"])

    @property
    def min_valid_samples(self) -> int:
        return int(round(self.raw["data"]["min_valid_seconds"] * self.fs))

    @cached_property
    def lambda_grid_rel(self) -> np.ndarray:
        m = self.raw["model"]
        return 10.0 ** np.linspace(m["lambda_log10_min"], m["lambda_log10_max"], int(m["lambda_n"]))

    @property
    def inference(self) -> dict:
        return self.raw["inference"]

    @property
    def resampling(self) -> dict:
        return self.raw["resampling"]

    @property
    def eeg(self) -> dict:
        return self.raw["features"]["eeg"]

    @property
    def ecg(self) -> dict:
        return self.raw["features"]["ecg"]

    @property
    def syn(self) -> dict:
        return self.raw["features"]["syn"]

    @property
    def raw_route(self) -> dict:
        return self.raw["features"]["raw_route"]

    @property
    def data(self) -> dict:
        return self.raw["data"]

    @property
    def population(self) -> dict:
        return self.raw["population"]

    @property
    def validation(self) -> dict:
        return self.raw["validation"]

    def with_overrides(self, **values) -> "ProtocolConfig":
        """Return a copy with dotted-key overrides (e.g. ``inference.n_permutations=99``).

        Overrides are for simulations, smoke tests and documented sensitivity runs only.
        They are recorded in the run metadata so an overridden run can never be mistaken
        for a frozen-configuration run.
        """
        import copy

        raw = copy.deepcopy(self.raw)
        for dotted, value in values.items():
            node = raw
            keys = dotted.split(".")
            for k in keys[:-1]:
                node = node[k]
            if keys[-1] not in node:
                raise KeyError(f"Unknown configuration key {dotted}")
            node[keys[-1]] = value
        merged = dict(self.overrides)
        merged.update(values)
        return ProtocolConfig(raw=raw, path=self.path, sha256=self.sha256, overrides=merged)

    @property
    def is_frozen(self) -> bool:
        return not self.overrides


REQUIRED = {
    ("inference", "delta"): 0.05,
    ("inference", "futility_threshold"): 0.10,
    ("inference", "futility_z"): 3.0,
    ("inference", "n_permutations"): 999,
    ("inference", "reps_permutation"): 10,
    ("inference", "ncv_reps"): 200,
    ("resampling", "outer_folds_A"): 10,
    ("resampling", "reps_A"): 50,
    ("resampling", "folds_BC"): 5,
    ("resampling", "reps_BC"): 20,
    ("model", "inner_folds"): 5,
    ("model", "lambda_n"): 13,
}


def load_config(path: Path | None = None) -> ProtocolConfig:
    path = Path(path or CONFIG_PATH)
    raw = tomllib.loads(path.read_text())
    cfg = ProtocolConfig(raw=raw, path=path, sha256=sha256_file(path))
    # Protocol invariants: refuse a silently edited frozen configuration.
    for (section, key), value in REQUIRED.items():
        if raw[section][key] != value:
            raise ValueError(f"Frozen protocol value changed: {section}.{key}={raw[section][key]!r}, expected {value!r}")
    if raw["inference"]["futility_threshold"] != 2 * raw["inference"]["delta"]:
        raise ValueError("Futility threshold must equal 2 * delta (EDD-014)")
    return cfg
