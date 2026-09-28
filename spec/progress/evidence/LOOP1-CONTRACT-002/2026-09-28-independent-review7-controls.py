"""Independent focused checks for remaining WSS verifier risk."""
import copy
import importlib.util
from pathlib import Path

path = Path('contracts/websocket/verify.py')
spec = importlib.util.spec_from_file_location('wss_verify', path)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

cases = {case['id']: case for case in v.fixtures()['scenarios']}

def rejects_schema(label, change):
    schema = copy.deepcopy(v.SCHEMA)
    change(schema)
    try:
        v.lint_schema(schema, root=schema)
    except v.Invalid:
        print(f'REJECT {label}')
        return
    raise AssertionError(f'ACCEPTED {label}')

def rejects_case(label, case_id, change):
    case = copy.deepcopy(cases[case_id])
    change(case)
    try:
        v.check_scenario(case)
    except v.Invalid:
        print(f'REJECT {label}')
        return
    raise AssertionError(f'ACCEPTED {label}')

rejects_schema('empty enum', lambda s: s['$defs']['Error']['properties']['code'].update(enum=[]))
rejects_schema('invalid format', lambda s: s['$defs']['Id'].update(format='not-a-format'))
rejects_schema('boolean minimum', lambda s: s['$defs']['Committed']['properties']['seq'].update(minimum=True))
rejects_schema('boolean maxLength', lambda s: s['$defs']['TextContent']['properties']['text'].update(maxLength=True))
rejects_schema('negative maxProperties', lambda s: s['$defs']['Ping']['allOf'][1]['properties']['payload'].update(maxProperties=-1))
rejects_schema('dangling ref', lambda s: s['$defs']['MessageSend']['allOf'][1]['properties'].update(requestId={'$ref': '#/$defs/Missing'}))
rejects_schema('non-schema child', lambda s: s['$defs']['TextContent']['properties'].update(text=7))
rejects_case('out-of-order same message ID', 'out-of-order-fanout', lambda s: (s['steps'][1]['in']['payload'].update(messageId=v.M2), s['steps'][1]['out'][0]['payload'].update(messageId=v.M2)))
rejects_case('out-of-order permanent gap', 'out-of-order-fanout', lambda s: s['expect'].update(contiguousSeqAfterSync=1))
rejects_case('out-of-order altered transaction', 'out-of-order-fanout', lambda s: s['timeline'].append('SUCCESS_ACK'))
print('REJECTED 10/10 focused invalid controls')
