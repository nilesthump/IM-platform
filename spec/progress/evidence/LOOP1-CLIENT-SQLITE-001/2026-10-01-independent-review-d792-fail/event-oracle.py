import copy,json,runpy
oracle=runpy.run_path('contracts/plugin-api/verify.py')
c=next(c for c in json.load(open('contracts/fixtures/sync-plugin/golden.json',encoding='utf-8'))['cases'] if c['id']=='user-friend.changed')
c=copy.deepcopy(c)
c['steps'].append(copy.deepcopy(c['steps'][0]))
c['steps'][1]['page']['events'][0]['revision']+=1
c['steps'][1]['page']['nextCursor']='conflicting-cursor'
try:
 oracle['run'](c)
 print('Unexpected canonical acceptance')
 raise SystemExit(1)
except oracle['Invalid'] as e:
 print('Canonical REJECTED:',e)
