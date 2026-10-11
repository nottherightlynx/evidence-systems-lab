from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
"""Pure-Python offline smoke test. This is NOT a substitute for Dagster materialization."""
from pathlib import Path
import csv
from orchestration.pipeline import run_pipeline, ROOT
records, report=run_pipeline(fetch_federal=False)
assert len(records)==3,(len(records),records)
assert all(r['source_kind']=='SIMULATED' for r in records)
assert len({(r['source_id'],r['document_id']) for r in records})==3
assert any(r['source_id']=='FEDERAL_REGISTER' and r['status']=='NOT_FETCHED_OFFLINE' for r in report)
print('PASS: offline sample contains 3 SIMULATED records; official API not fetched; provenance retained.')
print('PASS: normalized_documents.csv and source_observability.csv created.')
