#!/bin/sh
# Closure-phase exit checks (run from the repository root). Logs go to docs/research/novel_method/closure/evidence/.
set -u
E=docs/research/novel_method/closure/evidence
date -u +%Y-%m-%dT%H:%M:%SZ > $E/exit_time.txt
(PYTHONPATH=src .venv/bin/python -m g01r verify-freeze; echo "exit $?") > $E/verify_freeze_exit.log 2>&1
(PYTHONPATH=src PYTHONWARNINGS=ignore .venv-cairn/bin/python -W ignore -m unittest discover -s tests; echo "exit $?") > $E/unittest_exit.log 2>&1
(PYTHONPATH=src PYTHONWARNINGS=ignore .venv-cairn/bin/python -W ignore -m cairn verify --out $E/verify_exit.json; echo "exit $?") > $E/verify_exit.log 2>&1
(shasum -a 256 -c docs/research/novel_method/stage0/SHA256SUMS; echo "exit $?") > $E/stage0_sha256_check_exit.log 2>&1
(PYTHONPATH=src .venv-cairn/bin/python -m cairn run --scope development; echo "exit $?") > $E/gate_refusal_exit.log 2>&1
(PYTHONPATH=src .venv-cairn/bin/python -m cairn run --scope locked_primary --config x --anchors x --out x; echo "exit $?") >> $E/gate_refusal_exit.log 2>&1
(ls analysis_freeze_cairn 2>&1; wc -l analysis_freeze/outcome_access_log.jsonl docs/research/external_john2025/evidence/outcome_access_log.jsonl;
 shasum -a 256 analysis_freeze/outcome_access_log.jsonl docs/research/external_john2025/evidence/outcome_access_log.jsonl) > $E/access_logs_exit.log 2>&1
# Stage-1 record: src/cairn changed by design in this phase; the Stage-1-exit code is archived and must verify
(cd $E/stage1_exit_code/cairn && for f in *.py; do want=$(grep "src/cairn/$f\$" ../../../../stage1/SHA256SUMS | cut -c1-64); got=$(shasum -a 256 $f | cut -c1-64); [ "$want" = "$got" ] && echo "$f OK" || echo "$f MISMATCH"; done) > $E/stage1_exit_code_check_exit.log 2>&1
(grep -v "src/cairn/" docs/research/novel_method/stage1/SHA256SUMS | shasum -a 256 -c; echo "exit $?") > $E/stage1_sha256_check_exit.log 2>&1
shasum -a 256 src/cairn/*.py tests/*.py requirements-*.lock docs/research/novel_method/research_plan.md docs/research/novel_method/closure/design_config.json > $E/exit_sha256.txt
echo done
