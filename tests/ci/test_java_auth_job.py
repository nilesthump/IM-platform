"""Guard real runtime acceptance wiring after the Java S0 exception expires."""
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[2]

def validate(text):
    preparation=text.split('name: Prepare disposable Java profile configuration',1)[1].split('      - name:',1)[0]
    for binding in ["$config.publicOrigin = 'https://localhost:18444'",'[System.IO.File]::WriteAllText($configPath, ($config | ConvertTo-Json))']:
        if binding not in preparation: raise ValueError('Java TLS smoke Origin binding missing')
    java=text.split('\n  java:\n',1)[1].split('\n  web:\n',1)[0]
    for required in ['postgres:16','nats:2.10-alpine','mvn -B','contracts/database/migrate.py up','--profile java','--profile go','--profile-switch']:
        if required not in java: raise ValueError('Java live acceptance missing '+required)
    if 'InfraPlaceholder' in java or 'check_s0_boundary.py java' in java:
        raise ValueError('Expired Java placeholder acceptance')

class JavaAuthJobTest(unittest.TestCase):
    def test_missing_origin_binding_rejected(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        for binding in ["$config.publicOrigin = 'https://localhost:18444'",'[System.IO.File]::WriteAllText($configPath, ($config | ConvertTo-Json))']:
            with self.subTest(binding=binding),self.assertRaises(ValueError): validate(workflow.replace(binding,''))
    def test_real_job(self): validate((ROOT/'.github/workflows/ci.yml').read_text())
    def test_missing_runtime_rejected(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        for value in ['--profile java','--profile go','--profile-switch','contracts/database/migrate.py up']:
            with self.subTest(value=value),self.assertRaises(ValueError): validate(workflow.replace(value,'REMOVED'))
    def test_placeholder_rejected(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text().replace('Build Java Auth and canonical runner','InfraPlaceholder')
        with self.assertRaises(ValueError): validate(workflow)
