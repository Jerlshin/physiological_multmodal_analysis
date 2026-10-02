"""Explicit re-audit after corrected event-boundary semantics; sources untouched."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from bbbd_audit.io import EVIDENCE,DATA
from bbbd_audit.audit import run
for exp in [2,4,5]:
    p=EVIDENCE/f'audit_exp{exp}.json'
    if p.exists():p.rename(DATA/'temporary_cache'/f'audit_exp{exp}_before_event_boundary_fix.json')
run((2,4,5))
