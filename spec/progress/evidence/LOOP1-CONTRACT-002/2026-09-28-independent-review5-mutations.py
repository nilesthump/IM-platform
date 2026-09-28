import copy
import importlib.util
from pathlib import Path
p=Path('contracts/websocket/verify.py')
spec=importlib.util.spec_from_file_location('wss_verify',p)
v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
base={s['id']:s for s in v.fixtures()['scenarios']}
checks=[]
s=copy.deepcopy(base['out-of-order-fanout'])
s['steps'][1]['in']['payload']['conversationId']=v.C2
s['steps'][1]['out'][0]['payload']['conversationId']=v.C2
checks.append(('cross-conversation-out-of-order',s))
for name,scenario in checks:
    try:
        v.check_scenario(scenario)
    except v.Invalid as exc:
        print('REJECT',name,exc)
    else:
        print('ACCEPT INVALID',name)
        raise SystemExit(1)