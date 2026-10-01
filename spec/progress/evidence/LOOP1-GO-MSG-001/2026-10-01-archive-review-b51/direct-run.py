from review import *
run('hosted-direct',[PY,'-B',OUT/'direct-ci.py'])
run('clean-final',['git','status','--porcelain=v1','--untracked-files=all'])
