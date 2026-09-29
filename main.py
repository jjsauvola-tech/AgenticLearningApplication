"""ALA Windows launcher. The executable includes Python and document readers."""
import argparse
import json
import os
import subprocess
import sys
import webbrowser
import threading
import time
import re
from pathlib import Path
from ala.server import AppServer

def launch_browser(url):
    if os.name=='nt':
        candidates=[Path(os.environ.get(k,''))/'Microsoft/Edge/Application/msedge.exe' for k in ('PROGRAMFILES(X86)','PROGRAMFILES','LOCALAPPDATA')]
        for p in candidates:
            if p.is_file():
                subprocess.Popen([str(p),'--app='+url],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                return
    webbrowser.open(url)

def main():
    args=argparse.ArgumentParser()
    args.add_argument('--data-dir')
    args.add_argument('--no-browser',action='store_true')
    args.add_argument('--port',type=int,default=0)
    args.add_argument('--runtime-file')
    opt=args.parse_args()
    root=Path(getattr(sys,'_MEIPASS',Path(__file__).parent))
    data=Path(opt.data_dir or os.environ.get('ALA_DATA_DIR') or (Path(os.environ.get('LOCALAPPDATA',Path.home()))/'ALA'))
    from ala.lifecycle import AlreadyRunning, atomic_json
    import urllib.request
    data.mkdir(parents=True, exist_ok=True)
    instance_file = data/'instance.json'
    previous = {}
    try: previous = json.loads(instance_file.read_text(encoding='utf-8'))
    except (OSError,ValueError): pass
    # Keep bookmarked windows connected across source upgrades on this machine.
    preferred_port = opt.port or previous.get('port',0)
    if not isinstance(preferred_port,int) or not 0 <= preferred_port <= 65535: preferred_port=0
    def new_server():
        try: result=AppServer(data,root/'web',preferred_port)
        except OSError as error:
            if opt.port or error.errno not in (48,98,10048) and getattr(error,'winerror',None)!=10048: raise
            result=AppServer(data,root/'web',0)
        prior_token=str(previous.get('url','')).partition('#')[2]
        if re.fullmatch(r'[A-Za-z0-9_-]{43}',prior_token): result.token=prior_token
        return result
    try:
        server=new_server()
    except AlreadyRunning:
        # Another launcher may still be starting; never create a second writer.
        for attempt in range(50):
            try:
                runtime=json.loads(instance_file.read_text(encoding='utf-8'))
                base,token=runtime['url'].split('#',1)
                request=urllib.request.Request(base+'api/ping',headers={'X-ALA-Token':token})
                with urllib.request.urlopen(request,timeout=1) as response:
                    if response.status!=200: raise RuntimeError('not_ready')
                if opt.runtime_file: atomic_json(opt.runtime_file,runtime)
                if not opt.no_browser: launch_browser(runtime['url'])
                return
            except (OSError,ValueError,KeyError,RuntimeError):
                # The owner may be shutting down. Acquire only after its OS lock
                # is released; never trust a stale runtime file as ownership.
                try:
                    server=new_server()
                    break
                except AlreadyRunning:
                    time.sleep(.1)
        else:
            raise RuntimeError('ALA is already running but unavailable. Existing data was not opened by a second process.')
    url='http://127.0.0.1:'+str(server.server_port)+'/#'+server.token
    from ala import __version__
    from ala.build import build_id
    runtime={'url':url,'port':server.server_port,'pid':os.getpid(),'version':__version__,'build':build_id(root)}
    atomic_json(instance_file,runtime)
    if opt.runtime_file: atomic_json(opt.runtime_file,runtime)
    if not opt.no_browser: launch_browser(url)
    # Browser timers are throttled in background tabs and during sleep.
    # Only explicit shutdown ends the local service.
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__=='__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    main()
