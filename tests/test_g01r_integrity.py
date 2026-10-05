"""G01-R integrity: frozen population, outcome firewall, feature-table invariants, tracking and the freeze gate."""
import json
import re
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pandas as pd

import g01r.freeze as freeze
from g01r.config import AUDIT_EVIDENCE, DERIVED, ROOT, load_config
from g01r.outcomes import OUTCOME_COLUMNS, OutcomeAccessDenied, load_real_outcomes, synthetic_outcomes
from g01r.population import ELIGIBILITY_COLUMNS, FILES_COLUMNS, TENSOR_COLUMNS, Population, verify_against_frozen_manifest
from g01r.tracking import RunTracker

CFG = load_config()
SRC = ROOT / "src" / "g01r"
OUTCOME_NAME = re.compile(r"score|correct_total|exact|partial|quiz|outcome")
OUTCOME_TOKENS = ["normalized_exact_score", "normalized_partial_score", "exact_correct_total", "recomputed_total",
                  "quiz_items", "quiz_video_outcomes", "exploratory_exposure_summaries", "canonical_manifest",
                  "item_difficulty", "outcome_by_video"]


@contextmanager
def absent_authorization():
    """Point the gate at a non-existent authorization record, whatever the repository state."""
    saved = freeze.AUTHORIZATION
    with tempfile.TemporaryDirectory() as d:
        freeze.AUTHORIZATION = Path(d) / "AUTHORIZATION.json"
        try:
            yield
        finally:
            freeze.AUTHORIZATION = saved


class FrozenPopulation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pop = Population(CFG)

    def test_reproduces_frozen_manifest_and_counts(self):
        report = verify_against_frozen_manifest(self.pop.cells, CFG)
        self.assertEqual(report["PAS_E34_core"], {"people": 68, "cells": 259, "videos": 8})
        s = self.pop.summary()
        self.assertEqual(s["PAS_E34_core_alpha30"], {"people": 68, "cells": 234, "videos": 7})
        self.assertEqual(s["E3_core"], {"people": 29, "cells": 148, "videos": 6})
        self.assertEqual(s["E4_core"], {"people": 39, "cells": 111, "videos": 3})

    def test_no_e2_and_no_person_overlap_e4_e5(self):
        c = self.pop.cells
        self.assertFalse((c.experiment == 2).any())
        e4 = set(c[c.E4_core].qualified_participant_id)
        e5 = set(c[c.E5_core].qualified_participant_id)
        self.assertFalse(e4 & e5)

    def test_whitelists_contain_no_outcome_columns(self):
        for cols in (TENSOR_COLUMNS, ELIGIBILITY_COLUMNS, FILES_COLUMNS):
            self.assertFalse([c for c in cols if OUTCOME_NAME.search(c)])


class OutcomeFirewall(unittest.TestCase):
    def test_only_outcomes_module_names_outcome_sources(self):
        offenders = []
        for p in SRC.rglob("*.py"):
            if p.name == "outcomes.py":
                continue
            text = p.read_text()
            for tok in OUTCOME_TOKENS:
                if tok in text:
                    offenders.append(f"{p.relative_to(ROOT)}: {tok}")
        self.assertEqual(offenders, [])

    def test_eligibility_reads_are_column_whitelisted(self):
        for p in SRC.rglob("*.py"):
            if p.name == "outcomes.py":
                continue
            for m in re.finditer(r"gate_closure_behavioral_eligibility\.parquet\"?,?\s*([^)]*)\)", p.read_text()):
                self.assertIn("columns=", m.group(1), f"{p.name} reads the eligibility table without a whitelist")

    def test_real_outcomes_locked_without_authorization(self):
        aset = Population(CFG).analysis_set("PAS_E34_core")
        with self.assertRaises(OutcomeAccessDenied):
            load_real_outcomes(aset, "exact", None)
        fake = freeze.Authorization(record={}, record_sha256="x", verified=False)
        with self.assertRaises(OutcomeAccessDenied):
            load_real_outcomes(aset, "exact", fake)
        # A forged object claiming verification is refused: the loader re-reads the record itself.
        forged = freeze.Authorization(record={}, record_sha256="x", verified=True)
        with absent_authorization():
            with self.assertRaises(OutcomeAccessDenied):
                load_real_outcomes(aset, "exact", forged)

    def test_no_authorization_record_exists_in_repository(self):
        if freeze.AUTHORIZATION.exists():
            self.skipTest("The user has written the authorization record (post-freeze state)")
        with self.assertRaises(OutcomeAccessDenied):
            freeze.load_authorization(CFG)

    def test_missing_authorization_is_refused_in_any_repository_state(self):
        with absent_authorization():
            with self.assertRaises(OutcomeAccessDenied):
                freeze.load_authorization(CFG)

    def test_synthetic_outcomes_are_valid_scores_and_deterministic(self):
        aset = Population(CFG).analysis_set("PAS_E34_core")
        y1 = synthetic_outcomes(aset, np.random.default_rng(1))
        y2 = synthetic_outcomes(aset, np.random.default_rng(1))
        self.assertTrue(np.array_equal(y1, y2))
        self.assertTrue(((y1 >= 0) & (y1 <= 1)).all())
        self.assertTrue(np.allclose(y1 * 12, np.round(y1 * 12)))


@unittest.skipUnless((DERIVED / "features" / "processed" / "exposure_features.parquet").exists(), "features not extracted")
class FeatureTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = pd.read_parquet(DERIVED / "features" / "processed" / "exposure_features.parquet")
        cls.pop = Population(CFG)

    def test_no_outcome_columns(self):
        self.assertFalse([c for c in self.f.columns if OUTCOME_NAME.search(c)])

    def test_every_analysis_cell_has_a_feature_row(self):
        keys = ["experiment", "participant_id", "session", "local_stimulus_id"]
        merged = self.pop.cells[keys].merge(self.f[keys], on=keys, how="left", indicator=True)
        self.assertTrue((merged._merge == "both").all())

    def test_quality_equals_audit_definitions(self):
        keys = ["experiment", "participant_id", "session", "local_stimulus_id"]
        rows = []
        for e in (1, 3, 4, 5):
            a = pd.read_parquet(AUDIT_EVIDENCE / f"files_exp{e}.parquet", columns=keys + ["modality", "status", "eeg_16hz_median_db", "correction_fraction"])
            rows.append(a[a.status == "author_processed"])
        a = pd.concat(rows)
        m = self.f.merge(a[a.modality == "eeg"][keys + ["eeg_16hz_median_db"]], on=keys, how="left")
        m = m.merge(a[a.modality == "gaze"][keys + ["correction_fraction"]].rename(columns={"correction_fraction": "g"}), on=keys, how="left")
        ok = m.eeg_16hz_median_db.notna()
        self.assertTrue(np.allclose(m.Q_eeg_16hz_excess[ok], m.eeg_16hz_median_db[ok]))
        ok = m.g.notna()
        self.assertTrue(np.allclose(m.Q_gaze_correction[ok], m.g[ok]))

    def test_primary_set_core_features_present(self):
        core = self.pop.cells[self.pop.cells.PAS_E34_core]
        keys = ["experiment", "participant_id", "session", "local_stimulus_id"]
        m = core[keys].merge(self.f, on=keys)
        self.assertTrue(m.eeg_present.all() and m.ecg_present.all() and m.gaze_present.all())


class Tracking(unittest.TestCase):
    def test_run_record_and_mlflow_mirror(self):
        with tempfile.TemporaryDirectory() as d:
            tr = RunTracker("unit-test", "demo", CFG, tags=dict(stage="test"), root=Path(d) / "runs",
                            mlflow_dir=Path(d) / "mlflow")
            with tr:
                tr.log_params(dict(a=1, nested=dict(b="x")))
                tr.log_metrics(dict(skill=0.1, nested=dict(p=0.04), label="not numeric"))
                tr.log_json("result.json", dict(x=np.float64(1.5), y=np.array([1, 2])))
                tr.set_identity(split_identity="abc")
            meta = json.loads((tr.dir / "run.json").read_text())
            for k in ("run_id", "config", "protocol", "git", "code", "environment", "data", "identity", "status"):
                self.assertIn(k, meta)
            self.assertEqual(meta["status"], "FINISHED")
            self.assertEqual(meta["config"]["sha256"], CFG.sha256)
            self.assertEqual(meta["identity"]["split_identity"], "abc")
            metrics = json.loads((tr.dir / "metrics.json").read_text())
            self.assertEqual(metrics, {"skill": 0.1, "nested.p": 0.04})
            if isinstance(meta.get("mlflow"), dict):
                import mlflow
                mlflow.set_tracking_uri(meta["mlflow"]["tracking_uri"])
                run = mlflow.tracking.MlflowClient().get_run(meta["mlflow"]["run_id"])
                self.assertAlmostEqual(run.data.metrics["skill"], 0.1)
                self.assertEqual(run.data.tags["g01r.config_sha256"], CFG.sha256)

    def test_failed_run_is_recorded(self):
        with tempfile.TemporaryDirectory() as d:
            tr = RunTracker("unit-test", "boom", CFG, root=Path(d), use_mlflow=False)
            with self.assertRaises(RuntimeError):
                with tr:
                    raise RuntimeError("x")
            self.assertEqual(json.loads((tr.dir / "run.json").read_text())["status"], "FAILED")


class ConfirmatoryCommand(unittest.TestCase):
    def test_run_refuses_without_authorization(self):
        # The authorization path is redirected, so this test can never start a real-outcome run,
        # even after the user has written analysis_freeze/AUTHORIZATION.json.
        from g01r.cli import main
        with absent_authorization():
            with self.assertRaises(OutcomeAccessDenied):
                main(["run", "--analysis", "H1_H2", "--workers", "1"])

    def test_registry_covers_every_prespecified_analysis(self):
        from g01r.registry import REGISTRY
        ids = {s.id for s in REGISTRY}
        for required in ("H1_H2", "H3_1_partial", "H3_2_eye30", "H3_2_eye70", "H3_3_four", "H3_4_raw", "H3_5_alpha",
                         "H3_6_gpa", "H3_7_cell", "D_state", "D_BC", "D_CAS", "D_E5", "D_transport", "D_E1",
                         "X_explanatory", "S_identity_probe"):
            self.assertIn(required, ids)
        h1 = next(s for s in REGISTRY if s.id == "H1_H2")
        self.assertEqual([t.id for t in h1.tests], ["H1", "H2a", "H2b", "H2c", "H2d"])
        self.assertEqual((h1.tests[0].base, h1.tests[0].full), ("M2", "M5"))
        self.assertEqual(h1.set_name, "PAS_E34_core")
        self.assertEqual(h1.outcome, "exact")


class Documentation(unittest.TestCase):
    def test_local_links_resolve(self):
        missing = []
        for folder in (ROOT / "docs/research/baseline_implementation", ROOT / "analysis_freeze"):
            for md in folder.glob("*.md"):
                for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", md.read_text()):
                    if target.startswith("http"):
                        continue
                    if not (md.parent / target).exists():
                        missing.append(f"{md.name} -> {target}")
        self.assertEqual(missing, [])


class FreezeGate(unittest.TestCase):
    def test_manifest_requires_frozen_configuration(self):
        with self.assertRaises(ValueError):
            freeze.build_manifest(CFG.with_overrides(**{"inference.n_permutations": 9}), include_caches=False)

    def test_authorization_logic_in_isolation(self):
        with tempfile.TemporaryDirectory() as d:
            saved = (freeze.FREEZE_DIR, freeze.MANIFEST, freeze.AUTHORIZATION, freeze.ACCESS_LOG, freeze.verify_manifest,
                     freeze.uncommitted_bound_files)
            try:
                freeze.FREEZE_DIR = Path(d)
                freeze.MANIFEST = Path(d) / "freeze_manifest.json"
                freeze.AUTHORIZATION = Path(d) / "AUTHORIZATION.json"
                freeze.ACCESS_LOG = Path(d) / "log.jsonl"
                freeze.MANIFEST.write_text("{}")
                freeze.verify_manifest = lambda cfg, include_caches=True: []
                freeze.uncommitted_bound_files = lambda: ["src/g01r/models.py"]
                with self.assertRaises(RuntimeError):
                    freeze.authorize(CFG, "https://osf.io/example", "tester", "statement")   # freeze not committed
                self.assertFalse(freeze.AUTHORIZATION.exists())
                freeze.uncommitted_bound_files = lambda: []
                path = freeze.authorize(CFG, "https://osf.io/example", "tester", "statement")
                auth = freeze.load_authorization(CFG)
                self.assertTrue(auth.verified)
                self.assertTrue(auth.record["git_commit"])
                with self.assertRaises(RuntimeError):
                    freeze.authorize(CFG, "x", "y", "z")                     # append-only
                freeze.MANIFEST.write_text('{"changed": true}')
                with self.assertRaises(OutcomeAccessDenied):
                    freeze.load_authorization(CFG)                            # manifest changed after authorization
                freeze.MANIFEST.write_text("{}")
                freeze.verify_manifest = lambda cfg, include_caches=True: ["code changed"]
                with self.assertRaises(OutcomeAccessDenied):
                    freeze.load_authorization(CFG)                            # working tree drifted
            finally:
                (freeze.FREEZE_DIR, freeze.MANIFEST, freeze.AUTHORIZATION, freeze.ACCESS_LOG, freeze.verify_manifest,
                 freeze.uncommitted_bound_files) = saved

    def test_derived_caches_are_bound_append_only(self):
        with tempfile.TemporaryDirectory() as d:
            saved = (freeze.DERIVED, freeze.CACHE_INDEX)
            try:
                freeze.DERIVED = Path(d) / "derived"
                freeze.CACHE_INDEX = Path(d) / "derived_cache_index.json"
                syn = freeze.DERIVED / "syn_cache" / "S" / "processed"
                syn.mkdir(parents=True)
                (syn / "a.parquet").write_bytes(b"frozen entry")
                (syn / "b.parquet.123.tmp").write_bytes(b"partial write, never indexed")
                frozen = {"derived_caches": freeze.write_derived_cache_index()}
                self.assertEqual(frozen["derived_caches"]["entries"], {"syn_cache": 1, "corrca_stats": 0})
                self.assertEqual(freeze.verify_derived_caches(frozen), [])
                (syn / "c.parquet").write_bytes(b"entry written by the confirmatory run")
                self.assertEqual(freeze.verify_derived_caches(frozen), [])          # additions allowed
                (syn / "a.parquet").write_bytes(b"modified")
                self.assertTrue(freeze.verify_derived_caches(frozen))              # changed entry refused
                (syn / "a.parquet").unlink()
                self.assertTrue(freeze.verify_derived_caches(frozen))              # deleted entry refused
                self.assertTrue(freeze.verify_derived_caches({}))                  # unbound manifest refused
            finally:
                freeze.DERIVED, freeze.CACHE_INDEX = saved

    def test_frozen_documents_include_the_environment_lock(self):
        self.assertIn("requirements-baseline.lock", freeze.FROZEN_DOCUMENTS)
        self.assertTrue((ROOT / "requirements-baseline.lock").exists())


if __name__ == "__main__":
    unittest.main()
