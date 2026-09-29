"""Bounded local AI startup. Never install software or download models implicitly."""
import json
import os
import shutil
import subprocess
import threading
import time
import urllib.request
from pathlib import Path


def request_json(url,body=None,timeout=3):
    request=urllib.request.Request(url,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=timeout) as response:
        return json.loads(response.read(2*1024*1024))


class AIRuntime:
    def __init__(self):
        self.lock=threading.Lock()
        self.busy=False
        self.failure=None

    def status(self,settings):
        base={'provider':'local','model':settings['model']}
        if self.busy:return {**base,'state':'starting'}
        try:
            names=[m['name'] for m in request_json(settings['ollamaUrl']+'/api/tags').get('models',[])]
        except (OSError,ValueError):return {**base,'state':self.failure or 'offline'}
        if not settings['model'] or settings['model'] not in names:
            return {**base,'state':'choose_model','models':names}
        if self.failure:return {**base,'state':self.failure}
        try: loaded=[m['name'] for m in request_json(settings['ollamaUrl']+'/api/ps').get('models',[])]
        except (OSError,ValueError):loaded=[]
        return {**base,'state':'ready' if settings['model'] in loaded else 'available'}

    def start(self,settings):
        with self.lock:
            if self.busy:return {'state':'starting'}
            self.busy=True;self.failure=None
        threading.Thread(target=self._start,args=(dict(settings),),daemon=True).start()
        return {'state':'starting'}

    def _start(self,settings):
        try:
            try:request_json(settings['ollamaUrl']+'/api/tags')
            except OSError:
                # Only the default local endpoint is started by this adapter.
                if settings['ollamaUrl'] not in ('http://127.0.0.1:11434','http://localhost:11434'):
                    self.failure='endpoint_unreachable';return
                candidate=Path(os.environ.get('LOCALAPPDATA',''))/'Programs/Ollama/ollama.exe'
                executable=shutil.which('ollama') or (str(candidate) if candidate.is_file() else None)
                if not executable:self.failure='not_installed';return
                subprocess.Popen([executable,'serve'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),close_fds=True)
                for _ in range(30):
                    try:request_json(settings['ollamaUrl']+'/api/tags',timeout=1);break
                    except OSError:time.sleep(.5)
                else:self.failure='start_failed';return
            names=[m['name'] for m in request_json(settings['ollamaUrl']+'/api/tags').get('models',[])]
            if not settings['model'] or settings['model'] not in names:return
            request_json(settings['ollamaUrl']+'/api/generate',{'model':settings['model'],'prompt':'','stream':False,'keep_alive':'10m'},timeout=120)
        except (OSError,ValueError,KeyError):self.failure='start_failed'
        finally:self.busy=False
