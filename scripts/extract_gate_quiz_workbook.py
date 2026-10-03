"""Read-only extraction with the bundled workspace Python/openpyxl runtime."""
import json
import hashlib
import platform
from importlib.metadata import version
from pathlib import Path
from openpyxl import load_workbook

root = Path(__file__).resolve().parents[1]
path = root/'docs/research/dataset_exploration/evidence/gate_closure_Education_questions.xlsx'
workbook = load_workbook(path, read_only=True, data_only=True)
values = {sheet.title:list(sheet.values) for sheet in workbook}
workbook.close()
path.with_suffix('.json').write_text(json.dumps(values,indent=2,default=str)+'\n')
metadata = dict(source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                python=platform.python_version(),openpyxl=version('openpyxl'),
                read_only=True,data_only=True,sheets=list(values),
                note='Workbook values extracted without editing; number/date formats can expose original Excel serialization, including ratio options stored as durations.')
(path.parent/'gate_closure_workbook_extraction.json').write_text(json.dumps(metadata,indent=2)+'\n')
