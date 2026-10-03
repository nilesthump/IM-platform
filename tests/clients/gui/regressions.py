"""Sequence all unchanged accepted native client regression families."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
scope=sys.argv[1]
if scope not in ('desktop','mobile'):raise RuntimeError('Native scope required')
for family in ('sqlite','send','sync'):
    mode=scope if family=='sync' else family+'-'+scope
    args=[sys.executable,'tests/clients/gui/native.py',mode,*sys.argv[2:]]
    print('Existing accepted '+family+' '+scope+' regression',flush=True)
    subprocess.run(args,cwd=ROOT,check=True)
