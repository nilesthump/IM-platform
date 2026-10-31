"""Actual Android runner, external subprocess/fs boundaries only; no ADB or credentials."""
import importlib.util,json,pathlib,subprocess,sys,tempfile,types,unittest
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parents[3]

class RuntimeCleanup(unittest.TestCase):
 def test_actual_main_preserves_operation_cleanup_and_report(self):
  for faults in [(),('body',),('nonzero',),('close',),('body','close'),('body','nonzero'),('report',),('body','report','close')]:
   with self.subTest(faults=faults),tempfile.TemporaryDirectory(prefix='group-harness-') as temp:
    folder=pathlib.Path(temp);source=ROOT/'tests/clients/group/runtime.py'
    spec=importlib.util.spec_from_file_location('group_runtime',source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    apk=folder/'dummy.apk';apk.write_bytes(b'boundary-only')
    credential=folder/'dummy.json';credential.write_text(json.dumps({who:{'username':'dummy','password':'dummy','userId':'10000000-0000-4000-8000-000000000001'} for who in 'ABCD'}))
    config=folder/'config.json';config.write_text(json.dumps({'serial':'emulator-5590','adb':'dummy-adb','endpoint':'https://localhost:8443','apk':str(apk),'test_apk':str(apk),'credential_file':str(credential)}))
    primary=RuntimeError('operation sentinel');cleanup=OSError('cleanup sentinel');report=OSError('report sentinel');calls=[];reported=[]
    write=pathlib.Path.write_text
    def output(path,text,*a,**kw):
     if path.name=='manifest.json':
      reported.append(json.loads(text))
      if 'report' in faults:raise report
     return write(path,text,*a,**kw)
    def run(args,**kw):
     args=list(map(str,args));calls.append(args);body=b'';code=0
     if 'instrument' in args:
      if 'body' in faults:raise primary
      body=b'INSTRUMENTATION_RESULT: result=PASS\nINSTRUMENTATION_CODE: -1\n'
     elif 'rm' in args:
      if 'close' in faults:raise cleanup
      if 'nonzero' in faults:code=37
     elif 'getprop' in args:body=b'1'
     elif 'install' in args:body=b'Success'
     elif 'pm' in args:body=b'package:/data/app/dummy/base.apk'
     elif 'exec-out' in args:body=apk.read_bytes()
     elif 'test' in args:code=1
     return types.SimpleNamespace(returncode=code,stdout=body,stderr=b'')
    error=None;answer=None;printed=[]
    with patch.object(module.subprocess,'run',run),patch.object(module.subprocess,'check_output',return_value='controlled-source\n'),patch.object(pathlib.Path,'write_text',output),patch.object(sys,'argv',[str(source),'--config',str(config),'--serial','emulator-5590','--out',str(folder/'result')]),patch('builtins.print',side_effect=lambda *args,**kw:printed.extend(map(str,args))):
     try:answer=module.main()
     except BaseException as caught:error=caught
    self.assertTrue(any('rm' in call for call in calls));self.assertTrue(reported)
    def leaves(e):
     return [item for child in e.exceptions for item in leaves(child)] if isinstance(e,BaseExceptionGroup) else [e]
    if faults:
     self.assertIsNotNone(error);errors=leaves(error)
     if 'body' in faults:self.assertTrue(any(e is primary for e in errors))
     if 'close' in faults:self.assertTrue(any(e is cleanup for e in errors))
     if 'report' in faults:self.assertTrue(any(e is report for e in errors))
     if 'nonzero' in faults:self.assertIn('37',' '.join(map(str,errors)))
     self.assertFalse(any('PASS' in line for line in printed))
     if 'report' not in faults:self.assertEqual(reported[0]['result'],'FAIL')
    else:self.assertIsNone(error);self.assertEqual(answer,0);self.assertEqual(reported[0]['result'],'PASS_LOCAL_ENTRY')

if __name__=='__main__':unittest.main()
