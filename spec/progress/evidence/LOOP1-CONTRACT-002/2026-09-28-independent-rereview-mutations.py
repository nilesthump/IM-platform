import copy
import importlib.util
import pathlib

path = pathlib.Path('contracts/websocket/verify.py')
spec = importlib.util.spec_from_file_location('wss_verify', path)
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
base = {s['id']: s for s in w.fixtures()['scenarios']}

def run(name, case_id, edit):
    scenario = copy.deepcopy(base[case_id])
    edit(scenario)
    try:
        w.check_scenario(scenario)
    except w.Invalid as exc:
        print(f'REJECT {name}: {exc}')
        return True
    print(f'ACCEPT INVALID {name}')
    return False

def move_before(s, event):
    s['timeline'].remove(event)
    s['timeline'].insert(s['timeline'].index('COMMIT'), event)

checks = [
    ('wrong-conversation-delivery', 'wrong-conversation-fanout', lambda s: s['steps'][0]['out'].append(copy.deepcopy(s['steps'][0]['in']))),
    ('omitted-revocation', 'revoked-socket', lambda s: s['steps'][0]['out'].clear()),
    ('omitted-invalid-signature-rejection', 'invalid-signature-bind', lambda s: s['steps'][0]['out'].clear()),
    ('created-before-commit', 'durable-send-and-created', lambda s: move_before(s, 'MESSAGE_CREATED')),
    ('ack-before-commit', 'durable-send-and-created', lambda s: move_before(s, 'SUCCESS_ACK')),
    ('rollback-success', 'rollback-before-ack', lambda s: s['steps'][0]['out'].append(w.ack())),
    ('unstable-retry', 'idempotent-retry', lambda s: s['steps'][1]['out'][0]['payload'].update(messageId=w.M2)),
    ('nonmember-success', 'non-member-send', lambda s: s['steps'][0]['out'].append(w.ack())),
    ('preauth-success', 'unauthenticated-send', lambda s: s['steps'][0]['out'].append(w.ack())),
    ('omitted-valid-bind-ack', 'bind-valid-session', lambda s: s['steps'][0]['out'].clear()),
    ('valid-bind-wrong-state', 'bind-valid-session', lambda s: s['expect'].update(socket='UNAUTHENTICATED')),
    ('stale-epoch-success-state', 'stale-epoch-bind', lambda s: s['expect'].update(socket='AUTHENTICATED')),
]
results = [run(*check) for check in checks]
print(f'REJECTED {sum(results)}/{len(results)} invalid behavior mutations')
raise SystemExit(0 if all(results) else 1)
