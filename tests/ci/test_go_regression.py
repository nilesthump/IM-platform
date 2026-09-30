import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from ci.classify import classify
ROOT=Path(__file__).resolve().parents[2]
class GoRegressionTests(unittest.TestCase):
    def test_role_smoke_change_and_deletion_select_actual_jobs(self):
        for p in ['tests/go/live_role_smoke.py','tests/go/deleted.py']:
            m=classify([p]);self.assertTrue(all(m[x] for x in ['go','deploy','architecture','source_go']))
            self.assertFalse(m['java'])
    def test_recursive_live_go_verification_and_role_smoke_present(self):
        s=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn("find backend/go -name '*.go' -type f",s)
        for cmd in ['go build ./...','go vet ./...','go test -race -count=1 ./...','python3 tests/go/live_role_smoke.py']:
            self.assertIn(cmd,s)
        self.assertIn("DB_TEST_ENABLE: '1'",s)
    def test_websocket_upgrade_eof_terminates(self):
        spec=importlib.util.spec_from_file_location('role_smoke',ROOT/'tests/go/live_role_smoke.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        class Closed:
            def settimeout(self,*a):pass
            def sendall(self,*a):pass
            def recv(self,*a):return b''
        with patch.object(m.socket,'create_connection',return_value=Closed()),patch.object(m.CTX,'wrap_socket',return_value=Closed()):
            with self.assertRaises(EOFError):m.WS()
