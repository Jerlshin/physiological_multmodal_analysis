"""Experiment tracking: an append-only file run store (source of truth) mirrored to MLflow.

Every run writes ``results/runs/<experiment>/<run_id>/`` containing ``run.json`` (configuration
hash and overrides, protocol commit, git commit and dirty state, code hash, environment, data
and split identity, seeds, outcome source, analysis specification, status and timing),
``params.json``, ``metrics.json`` and artifacts. The same run is mirrored to a local MLflow
tracking store (SQLite backend, ``results/mlflow/``) with identical params, metrics, tags and
artifacts. If MLflow is unavailable the file store alone is complete.
"""
from __future__ import annotations

import json
import os
import shutil
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .config import RESULTS, ProtocolConfig
from .provenance import code_hash, data_identity, environment, git_state

os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")
os.environ.setdefault("GIT_PYTHON_REFRESH", "quiet")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _jsonable(obj):
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return _jsonable(obj.tolist())
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        return v if np.isfinite(v) else None
    if isinstance(obj, float):
        return obj if np.isfinite(obj) else None
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, Path):
        return str(obj)
    return obj


_MLFLOW_KEY = __import__("re").compile(r"[^A-Za-z0-9_\-. :/]")


def mlflow_key(key: str) -> str:
    """MLflow-safe key (the file store keeps the original key)."""
    return _MLFLOW_KEY.sub("_", key.replace("->", "_to_"))[:250]


def flatten(d: dict, prefix: str = "") -> dict:
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            out.update(flatten(v, key))
        else:
            out[key] = v
    return out


class RunTracker:
    def __init__(self, experiment: str, run_name: str, cfg: ProtocolConfig, tags: dict | None = None,
                 root: Path | None = None, use_mlflow: bool = True, mlflow_dir: Path | None = None):
        self.experiment, self.run_name, self.cfg = experiment, run_name, cfg
        self.tags = dict(tags or {})
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.run_id = f"{stamp}_{uuid.uuid4().hex[:8]}"
        self.dir = (root or RESULTS / "runs") / experiment / f"{run_name}__{self.run_id}"
        self.use_mlflow = use_mlflow
        self.mlflow_dir = mlflow_dir or RESULTS / "mlflow"
        self._mlflow = None
        self.params, self.metrics = {}, {}
        self.meta = {}

    # ------------------------------------------------------------------ lifecycle
    def __enter__(self):
        self.dir.mkdir(parents=True, exist_ok=False)
        (self.dir / "artifacts").mkdir()
        self.meta = dict(
            run_id=self.run_id, experiment=self.experiment, run_name=self.run_name, status="RUNNING",
            start_utc=_now(), end_utc=None,
            config=dict(path=str(self.cfg.path), sha256=self.cfg.sha256, frozen=self.cfg.is_frozen,
                        overrides=_jsonable(self.cfg.overrides)),
            protocol=dict(path=self.cfg.raw["meta"]["protocol_path"], version=self.cfg.raw["meta"]["protocol_version"],
                          commit=self.cfg.raw["meta"]["protocol_commit"]),
            git=git_state(), code=code_hash()["sha256"], environment=environment(), data=data_identity(),
            tags=self.tags, identity={},
        )
        self._write_meta()
        if self.use_mlflow:
            self._start_mlflow()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.meta["status"] = "FAILED" if exc_type else "FINISHED"
        self.meta["end_utc"] = _now()
        if exc_type:
            self.meta["error"] = "".join(traceback.format_exception(exc_type, exc, tb))[-4000:]
        self._write_meta()
        (self.dir / "params.json").write_text(json.dumps(_jsonable(self.params), indent=2) + "\n")
        (self.dir / "metrics.json").write_text(json.dumps(_jsonable(self.metrics), indent=2) + "\n")
        if self._mlflow is not None:
            mlflow = self._mlflow
            try:
                mlflow.log_artifact(str(self.dir / "run.json"))
                mlflow.log_artifact(str(self.dir / "params.json"))
                mlflow.log_artifact(str(self.dir / "metrics.json"))
                mlflow.end_run(status="FAILED" if exc_type else "FINISHED")
            except Exception as e:  # tracking must never mask a scientific error
                self.meta.setdefault("mlflow_errors", []).append(repr(e))
                self._write_meta()
        return False

    def _write_meta(self):
        (self.dir / "run.json").write_text(json.dumps(_jsonable(self.meta), indent=2) + "\n")

    def _start_mlflow(self):
        try:
            import mlflow
        except Exception as e:
            self.meta["mlflow"] = f"unavailable: {e!r}"
            self._write_meta()
            return
        store = self.mlflow_dir
        store.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"sqlite:///{store / 'mlflow.db'}")
        exp = mlflow.get_experiment_by_name(self.experiment)
        exp_id = exp.experiment_id if exp else mlflow.create_experiment(
            self.experiment, artifact_location=(store / "artifacts" / self.experiment).as_uri())
        run = mlflow.start_run(experiment_id=exp_id, run_name=self.run_name)
        self._mlflow = mlflow
        self.meta["mlflow"] = dict(tracking_uri=mlflow.get_tracking_uri(), experiment_id=exp_id, run_id=run.info.run_id)
        tags = {"g01r.run_id": self.run_id, "g01r.config_sha256": self.cfg.sha256,
                "g01r.config_frozen": str(self.cfg.is_frozen), "g01r.protocol_commit": self.meta["protocol"]["commit"],
                "g01r.git_commit": str(self.meta["git"]["commit"]), "g01r.git_dirty": str(self.meta["git"]["dirty"]),
                "g01r.code_sha256": self.meta["code"]}
        tags.update({f"g01r.{k}": str(v) for k, v in self.tags.items()})
        mlflow.set_tags(tags)
        self._write_meta()

    # ------------------------------------------------------------------ logging
    def set_identity(self, **identity):
        self.meta["identity"].update(_jsonable(identity))
        self._write_meta()
        self._mirror_call("set_tags", {mlflow_key(f"identity.{k}"): str(v)[:5000] for k, v in flatten(_jsonable(identity)).items()})

    def log_params(self, params: dict):
        flat = flatten(_jsonable(params))
        self.params.update(flat)
        if self._mlflow is not None:
            self._mirror_call("log_params", {mlflow_key(k): str(v)[:6000] for k, v in flat.items()})

    def log_metrics(self, metrics: dict, prefix: str = ""):
        flat = {k: v for k, v in flatten(_jsonable(metrics), prefix).items()
                if isinstance(v, (int, float)) and not isinstance(v, bool) and v is not None}
        self.metrics.update(flat)
        if self._mlflow is not None and flat:
            self._mirror_call("log_metrics", {mlflow_key(k): float(v) for k, v in flat.items()})

    def _mirror_call(self, method: str, payload: dict):
        """Mirror to MLflow; a tracking failure is recorded but never masks or aborts the analysis."""
        if self._mlflow is None or not payload:
            return
        try:
            getattr(self._mlflow, method)(payload)
        except Exception as e:
            self.meta.setdefault("mlflow_errors", []).append(f"{method}: {e!r}"[:500])
            self._write_meta()

    def artifact_path(self, name: str) -> Path:
        return self.dir / "artifacts" / name

    def log_json(self, name: str, obj):
        path = self.artifact_path(name)
        path.write_text(json.dumps(_jsonable(obj), indent=2) + "\n")
        self._mirror(path)
        return path

    def log_frame(self, name: str, frame: pd.DataFrame):
        path = self.artifact_path(name)
        if name.endswith(".csv"):
            frame.to_csv(path, index=False)
        else:
            frame.to_parquet(path, index=False)
        self._mirror(path)
        return path

    def log_array(self, name: str, array: np.ndarray):
        path = self.artifact_path(name)
        np.save(path, array)
        self._mirror(path)
        return path

    def log_file(self, src: Path, name: str | None = None):
        path = self.artifact_path(name or Path(src).name)
        shutil.copy2(src, path)
        self._mirror(path)
        return path

    def _mirror(self, path: Path):
        if self._mlflow is not None:
            try:
                self._mlflow.log_artifact(str(path), artifact_path="artifacts")
            except Exception as e:
                self.meta.setdefault("mlflow_errors", []).append(repr(e))
