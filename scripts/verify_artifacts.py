#!/usr/bin/env python3
"""Verify the completed notebook, current sources, CSVs and generated manuscript inputs."""
from pathlib import Path
import hashlib,json
import nbformat
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
nb=nbformat.read(ROOT/'SciGuard_JMLR_Reproducible_Analysis_MIMIC_IV.ipynb',4);nbformat.validate(nb)
code=[c for c in nb.cells if c.cell_type=='code']
assert nb.metadata.sciguard.execution_status in {'completed','completed_recorded_outputs'}
counts=[c.execution_count for c in code]
executed=[x for x in counts if x is not None]
assert len(executed)>=20
assert executed==sorted(executed) and len(set(executed))==len(executed)
assert not any(o.output_type=='error' for c in code for o in c.outputs)
manifest=json.loads((ROOT/'results/full/run_manifest.json').read_text())
assert manifest['status']=='completed_public_and_synthetic'
assert manifest['external_benchmark']=='completed_credentialed_data'
for name,expected in manifest['source_sha256'].items():
    path=ROOT/Path(name.replace('\\','/'))
    assert sha(path)==expected,name
for name,expected in manifest['input_sha256'].items():
    path=ROOT/Path(name.replace('\\','/'))
    assert sha(path)==expected,name
for name,expected in manifest['output_sha256'].items():assert sha(ROOT/'results/full'/name)==expected,name
provenance=json.loads((ROOT/'manuscript/generated/table_provenance.json').read_text())
for name,expected in provenance['source_csv_sha256'].items():assert sha(ROOT/'results/full'/name)==expected,name
pdfs=list((ROOT/'figures/full').glob('*.pdf'))+[ROOT/'manuscript/main_jmlr.pdf',ROOT/'SciGuard_Major_Revision_Response.pdf',ROOT/'SciGuard_Final_Review_Response.pdf']
pages={str(p.relative_to(ROOT)):len(PdfReader(p).pages) for p in pdfs}
log=(ROOT/'manuscript/main_jmlr.log').read_text()
assert 'Overfull' not in log
assert 'undefined' not in log
mimic_manifest=json.loads((ROOT/'results/mimic_local/mimic_manifest.json').read_text())
assert mimic_manifest['status']=='completed_credentialed_data'
for name,expected in mimic_manifest['output_sha256'].items():
    assert sha(ROOT/'results/mimic_local'/name)==expected,name
report={'status':'passed','code_cells':len(code),'embedded_pngs':sum('image/png' in o.get('data',{}) for c in code for o in c.outputs),'source_files_verified':len(manifest['source_sha256']),'result_csvs_verified':len(manifest['output_sha256']),'mimic_result_csvs_verified':len(mimic_manifest['output_sha256']),'pdf_pages':pages,'notebook_execution':dict(nb.metadata.sciguard),'clinical_data_execution':'completed_credentialed_data'}
(ROOT/'docs/artifact_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
