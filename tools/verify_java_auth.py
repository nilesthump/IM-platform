"""Execute one canonical blackbox runner against real Java/Go services, never skip.

Database must be disposable and already migrated by the independent migration tool.
Credentials are environment/file inputs and never printed. Generated configs/logs stay
outside the source tree. Each selected profile stops before the next one starts.
"""
from __future__ import annotations
import argparse
import contextlib
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[1]

def port():
    with socket.socket() as s:
        s.bind(('127.0.0.1',0))
        return s.getsockname()[1]

def wait_for(check, processes, timeout=60):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        for proc in processes:
            if proc.poll() is not None:
                raise RuntimeError(f'Role exited before readiness: {proc.returncode}')
        if check(): return
        time.sleep(.1)
    raise TimeoutError('Role readiness timed out; inspect external role logs')

def healthy(url):
    try:
        with urllib.request.urlopen(url+'/__infra/health',timeout=1) as response:
            return response.status==200
    except (ConnectionError,urllib.error.URLError,TimeoutError):
        return False  # Only bounded startup transport unavailability is retried.

def verify_role_exits(java, build, env, config, folder):
    for role in ('core', 'gateway'):
        for mode in ('normal', 'failure'):
            log = folder / f'exit-{role}-{mode}.log'
            command = [java, '-Dloader.main=im.platform.tests.auth.RoleExitProbe',
                       '-Dloader.path=' + str(build / 'test-classes'), '-cp', str(build / 'java-profile-1.0.0.jar'),
                       'org.springframework.boot.loader.launch.PropertiesLauncher', role, mode]
            with log.open('wb') as capture:
                result = subprocess.run(command, env=dict(env, IM_LISTEN_PORT='0', IM_CONFIG_FILE=str(config)),
                                        stdout=capture, stderr=subprocess.STDOUT, timeout=30)
            lines = log.read_text(encoding='utf8').splitlines()
            if f'ROLE_EXIT_READY {role} {mode}' not in lines:
                raise AssertionError(f'{role} failed to start for {mode} shutdown')
            errors = [line for line in lines if line.startswith('Service worker failed:')]
            expected = ['Service worker failed: java.lang.IllegalStateException'] if mode == 'failure' else []
            if result.returncode != int(mode == 'failure') or errors != expected:
                raise AssertionError(f'{role} {mode} shutdown failed, exit {result.returncode}')
            print(f'ROLE_EXIT {role} {mode} exit={result.returncode} PASS')

@contextlib.contextmanager
def profile(name, build, folder, env, java, cp, binding=None):
    processes=[];logs=[];stop=folder/'stop';url_file=folder/'url'
    core_port,gateway_port=port(),port()
    config=dict(postgresHost=env['PGHOST'],postgresPort=int(env['PGPORT']),postgresUser=env['PGUSER'],postgresDatabase=env['PGDATABASE'],postgresPasswordFile=str(folder/'pg-secret'),jwtSigningKeyFile=str(folder/'jwt-secret'),coreUrl=f'http://127.0.0.1:{core_port}',natsUrl=env['NATS_URL'])
    if env.get('JAVA_AUTH_DURATION_PROBE')=='1': config.update(accessTokenSeconds=73,refreshTokenSeconds=419)
    (folder/'pg-secret').write_text(env['PGPASSWORD'],encoding='utf8')
    (folder/'jwt-secret').write_text(env['JAVA_AUTH_SIGNING_KEY'],encoding='utf8')
    config_file=folder/'config.json';config_file.write_text(json.dumps(config),encoding='utf8')
    def start(command,child_env,cwd):
        log=open(folder/f'role-{len(logs)}.log','w',encoding='utf8');logs.append(log)
        child=subprocess.Popen(command,cwd=cwd,env=child_env,stdout=log,stderr=subprocess.STDOUT);processes.append(child)
    seed=[java,'-cp',cp,'im.platform.tests.auth.BindingFixture']
    if binding:
        subprocess.run([*seed,'prepare',str(config_file),str(binding)],env=env,check=True,timeout=30)
    try:
        if name=='java':
            if env.get('JAVA_AUTH_DURATION_PROBE')=='1':
                verify_role_exits(java,build,env,config_file,folder)
            subprocess.run([java,'-cp',cp,'im.platform.core.auth.OutboxFailureProbe',str(config_file)],env=env,check=True,timeout=15)
            subprocess.run([java,'-cp',cp,'im.platform.core.auth.OutboxRecoveryProbe',str(config_file)],env=env,check=True,timeout=30)
            subprocess.run([java,'-cp',cp,'im.platform.tests.auth.RevocationDeliveryProbe',str(config_file)],env=env,check=True,timeout=30)
            for role,p in [('core',core_port),('gateway',gateway_port)]:
                start([java,'-jar',str(build/'java-profile-1.0.0.jar'),role],dict(env,IM_CONFIG_FILE=str(config_file),IM_LISTEN_PORT=str(p)),ROOT)
            url=f'http://127.0.0.1:{gateway_port}'
            wait_for(lambda:healthy(url),processes)
        else:
            child_env=dict(env,JAVA_AUTH_PROFILE_HOST='1',JAVA_AUTH_SIGNING_KEY_FILE=str(folder/'jwt-secret'),JAVA_AUTH_URL_FILE=str(url_file),JAVA_AUTH_STOP_FILE=str(stop),DB_TEST_ENABLE='1')
            start(['go','test','./tests','-v','-run','^TestJavaAuthProfileHost$','-count=1','-timeout=4m'],child_env,ROOT/'backend/go')
            wait_for(url_file.exists,processes,120);url=url_file.read_text(encoding='utf8')
        yield url,config_file
        for proc in processes:
            if proc.poll() is not None: raise RuntimeError(f'Live role failed: {proc.returncode}')
    finally:
        if name=='go' and processes:
            stop.touch()
            try:
                code=processes[0].wait(timeout=10)
                if code: raise RuntimeError(f'Go fixture host failed: {code}')
            finally:
                if processes[0].poll() is None: processes[0].terminate();processes[0].wait(timeout=10)
        else:
            for proc in reversed(processes):
                if proc.poll() is None: proc.terminate()
            for proc in reversed(processes): proc.wait(timeout=15)
        for log in logs: log.close()
        if binding:
            subprocess.run([*seed,'cleanup',str(config_file),str(binding)],env=env,check=True,timeout=30)
        sensitive=folder/'sensitive-values.json'
        if sensitive.exists():
            values=json.loads(sensitive.read_text(encoding='utf8'))
            def check_log(text):
                if any(value and value in text for value in values): raise AssertionError('Credential material in role log')
            def check_log_file(path): check_log(path.read_text(encoding='utf8'))
            for log in logs: check_log_file(Path(log.name))
            # A separate captured-log mutation never modifies original role output.
            # Cover every actual submitted/issued value, including WSS-only tokens.
            mutation=folder/'disclosure-mutation.log'
            for value in values:
                mutation.write_text('EXPLICIT TEST MUTATION: '+value,encoding='utf8')
                try: check_log_file(mutation)
                except AssertionError as failure:
                    if str(failure)!='Credential material in role log': raise
                else: raise AssertionError('Log disclosure mutation undetected')
            print('DISCLOSURE role logs and injected leak control PASS')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--build-dir',type=Path,required=True)
    choice=parser.add_mutually_exclusive_group(required=True);choice.add_argument('--profile',choices=['java','go']);choice.add_argument('--profile-switch',action='store_true')
    args=parser.parse_args();build=args.build_dir.resolve()
    if build.is_relative_to(ROOT): raise ValueError('Build output must be outside repository')
    env=dict(os.environ)
    for key in ['PGHOST','PGPORT','PGUSER','PGDATABASE','PGPASSWORD','NATS_URL']:
        if not env.get(key): raise ValueError(f'{key} required; live tests cannot skip')
    env['JAVA_AUTH_SIGNING_KEY']=secrets.token_hex(32)
    java=str(Path(env['JAVA_HOME'])/'bin'/('java.exe' if os.name=='nt' else 'java')) if env.get('JAVA_HOME') else shutil.which('java')
    if not java: raise RuntimeError('Java required')
    cp=os.pathsep.join([str(build/'test-classes'),str(build/'classes'),(build/'classpath.txt').read_text(encoding='utf8').strip()])
    evidence=Path(tempfile.mkdtemp(prefix='java-auth-',dir=build));print(f'Live evidence directory: {evidence}',flush=True)
    def run(name,mode,state=None,db=None,binding=None):
        folder=evidence/f'{name}-{mode or "fixtures"}-{len(list(evidence.iterdir()))}';folder.mkdir()
        settings=dict(env,PGDATABASE=db or env['PGDATABASE'])
        if mode=='ttl': settings['JAVA_AUTH_DURATION_PROBE']='1'
        with profile(name,build,folder,settings,java,cp,binding) as (url,config):
            command=[java,'-cp',cp,'im.platform.tests.auth.AuthFixtureRunner',url,name,str(ROOT),str(config)]
            if mode: command += [mode] if mode=='ttl' else [mode,str(state)]
            if binding: command.append(str(binding))
            subprocess.run(command,env=env,check=True,timeout=120)
    if args.profile_switch:
        for first,second in [('go','java'),('java','go')]:
            state=evidence/f'{first}-account';run(first,'create',state);run(second,'login',state)
        print('PASS sequential same-database Go/Java credentials in both directions')
    else:
        # An ordinary login before rotating the disposable signing key supplies a
        # well-formed negative credential. Keep its bytes opaque to the fixture.
        issuer=env.get('JAVA_AUTH_ISSUER_DATABASE')
        if not issuer or issuer==env['PGDATABASE']: raise ValueError('Distinct migrated JAVA_AUTH_ISSUER_DATABASE required')
        if args.profile=='java': run('java','ttl')
        previous=evidence/'previous-key-token'
        binding=evidence/'issuer-session-token'
        try:
            run(args.profile,'issue',previous,db=issuer)
            env['JAVA_AUTH_SIGNING_KEY']=secrets.token_hex(32)
            run(args.profile,'issue',binding,db=issuer)
            run(args.profile,'fixtures',previous,binding=binding)
        finally:
            previous.unlink(missing_ok=True)
            binding.unlink(missing_ok=True)

if __name__=='__main__': main()
